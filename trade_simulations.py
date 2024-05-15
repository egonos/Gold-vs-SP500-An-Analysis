import pandas as pd
import numpy as np
from tqdm import tqdm
from data import *
import mplfinance as mpf
import matplotlib.pyplot as plt

def display_EMA(df, start = 100,end = 200):
    """
    A function to display the EMA Crossover Strategy within a period

    Parameters
    ----------
    start: int
        The start (row) of the display period
    end: int
        The end (row) of the display period 
    """
        
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df = df.rename(columns={"Close/Last": "Close"})
    
    df["EMA 3"] = df["Close"].ewm(span = 3, adjust = False).mean()
    df["EMA 5"] = df["Close"].ewm(span = 5, adjust = False).mean()

    EMA = [mpf.make_addplot(df.iloc[start:end,:]["EMA 3"], color = "darkorange", label = "EMA 3"),
        mpf.make_addplot(df.iloc[start:end,:]["EMA 5"], color = "blue", label = "EMA 5")]
    
    plt.figure()
    mpf.plot(df.iloc[100:200,:],type = "candle",volume = False, style = "charles",addplot = EMA)
    plt.show()
    plt.rcdefaults()


def simulate_control_group(df, etf_purchased = 20, expense_rate=0.00095):
    """
    Simulates the nominal and real returns of a control group.
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    etf_purchased : int
        The number of ETFs purchased.
    expense_rate: float
        The expense rate of SPY ETF.
    
    Returns
    -------
    results: pd.DataFrame
        The result of the control group simulations
    """
    
    #20 years investment periods
    investment_periods = range(1950, 2023)
    data = []

    for year in investment_periods:
        buy_price = df[(df.Year == year) & (df["Month"] == 1)].Close.mean() / 10
        sell_price = df[(df.Year == year) & (df["Month"] == 12)].Close.mean() / 10
        portfolio_value_start = buy_price * etf_purchased
        portfolio_value_end = sell_price * etf_purchased
        expenses = portfolio_value_start * expense_rate * 335/365
        capital_earned = portfolio_value_end - portfolio_value_start - expenses
        nominal_return = capital_earned / portfolio_value_start * 100
        data.append((year, portfolio_value_start, portfolio_value_end - expenses,expenses, capital_earned, nominal_return))

    results = pd.DataFrame(data = data,
                           columns = ["Period","Capital Invested","Final Capital","Expenses","Capital Gained", "(%)Annual_Return_Without_Dividends"]
                           ).set_index("Period")
    
    return results
        


def simulate_trade_EMA(df, etf_purchased=20, expense_rate=0.00095, EMA1 = 12, EMA2 =26, verbose = False):
    """
    Computes EMA Crossover Trading over price data
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    etf_purchased : int
        The number of ETFs purchased.
    expense_rate: float
        The expense rate of SPY ETF.
    EMA1: int
        Span of the fast EMA.
    EMA2: int
        Span of the slow EMA.
    verbose: bool
        To show a summary of the trading process.
    
    Returns
    -------
    results: pd.DataFrame
        The results of the simulation

    """

    #dataframe operations
    df = df.copy().reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["ETF Price"] = df.Close / 10  
    df[f"EMA{str(EMA1)}"] = df['Close'].ewm(span=EMA1, adjust=False).mean()
    df[f"EMA{str(EMA2)}"] = df['Close'].ewm(span=EMA2, adjust=False).mean()

    #buy-sell signals
    df["Buy"] = (df[f"EMA{str(EMA1)}"] > df[f"EMA{str(EMA2)}"]) & (df[f"EMA{str(EMA1)}"].shift() <= df[f"EMA{str(EMA2)}"].shift())
    df["Sell"] = (df[f"EMA{str(EMA1)}"] < df[f"EMA{str(EMA2)}"]) & (df[f"EMA{str(EMA1)}"].shift() >= df[f"EMA{str(EMA2)}"].shift())

   
    trade_periods = range(1950,2023)
    data = []
    for year in trade_periods:
        total_expenses = 0
        trade_counts = 0 #to count the number of trades
        cash_balance = 0 
        etfs_holding = 0
        capital_invested = 0
        position_condition = False
        buy_date = None
        df_trade = df[df.Year == year] #between works inclusively 
        for index, row in df_trade.iterrows():
            if not position_condition and row["Buy"]:
                #first purchase
                if cash_balance == 0:  
                    etfs_holding = etf_purchased
                    capital_invested = etf_purchased * row["ETF Price"]
                    if verbose:
                        print("Date:", row['Date'])
                        print("Bought", etfs_holding, "ETFs at a price of: ",row["ETF Price"] )
                        print("Capital invested to this trade:", etfs_holding * row["ETF Price"])
                        print("Cash in hand:", cash_balance)
                        print()

                #remaining purchases
                else:
                    etfs_holding = cash_balance // row["ETF Price"]
                    cash_balance = cash_balance - etfs_holding * row["ETF Price"]
                    if verbose:
                        print("Date:", row["Date"],
                            "\nBought", etfs_holding,"ETF's", "at a price of:", row["ETF Price"], 
                            "\nCapital invested to this trade:", etfs_holding * row["ETF Price"],
                            "\nCash in hand:", cash_balance)
                        print()

                position_condition = True
                buy_date = row['Date']
            
            #sell condition
            elif position_condition and row["Sell"]:
                trade_counts += 1
                cash_balance += etfs_holding * row["ETF Price"]
                days_held = (row['Date'] - buy_date).days
                cash_balance -= etfs_holding * row["ETF Price"] * expense_rate * days_held / 365
                total_expenses += etfs_holding * row["ETF Price"] * expense_rate * days_held / 365
                position_condition = False
                if verbose:

                    print("Date:", row['Date'],
                        "\nSold",etfs_holding, "ETF's at a price of:",row["ETF Price"],
                        "\nCapital gained from trade:", etfs_holding * row["ETF Price"],
                        "\nExpense payment:", etfs_holding * row["ETF Price"] * expense_rate * days_held / 365,
                        "\nNet cash:", cash_balance)
                    print()

                etfs_holding = 0
        
        #the last open condition
        if position_condition:
            sell_date = df_trade.iloc[-1]['Date']
            cash_balance += etfs_holding * df_trade.iloc[-1]["ETF Price"]
            days_held = (sell_date - buy_date).days
            cash_balance -= etfs_holding * df_trade.iloc[-1]["ETF Price"] * expense_rate * days_held / 365
            trade_counts += 1
            total_expenses +=  etfs_holding * df_trade.iloc[-1]["ETF Price"] * expense_rate * days_held / 365
            if verbose:
                print("Date:", row['Date'],
                    "\nSold",etfs_holding, "ETF's at a price of:",df_trade.iloc[-1]["ETF Price"],
                "\nCapital gained from trade:", etfs_holding * df_trade.iloc[-1]["ETF Price"],
                "\nExpense payment:", etfs_holding * df_trade.iloc[-1]["ETF Price"] * expense_rate * days_held / 365,
                "\nNet cash:", cash_balance)
            etfs_holding = 0

        
        if capital_invested == 0:
            continue


        capital_earned = cash_balance - capital_invested
        nominal_return = capital_earned / capital_invested * 100
        data.append((year,trade_counts,capital_invested,cash_balance,total_expenses,capital_earned,nominal_return))
    
        
        
    
    results = pd.DataFrame(data  = data,
                           columns = ["Period","Trade Counts","Capital Invested","Final Capital","Expenses","Capital Gained","(%)Annual_Return_Without_Dividends"
                                        ]).set_index("Period")
    
    return results


def simulate_trade_EMA_gold(df, ounce_purhcased=20, EMA1 = 12, EMA2 =26, verbose = False):
    """
    Computes EMA Crossover Trading over price data
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    etf_purchased : int
        The number of ETFs purchased.
    expense_rate: float
        The expense rate of SPY ETF.
    EMA1: int
        Span of the fast EMA.
    EMA2: int
        Span of the slow EMA.
    verbose: bool
        To show a summary of the trading process.
    
    Returns
    -------
    results: pd.DataFrame
        The results of the simulation

    """

    #dataframe operations
    df = df.copy()
    df["Year"] = pd.to_datetime(df.index).year
    df[f"EMA{str(EMA1)}"] = df['Close'].ewm(span=EMA1, adjust=False).mean()
    df[f"EMA{str(EMA2)}"] = df['Close'].ewm(span=EMA2, adjust=False).mean()

    #buy-sell signals
    df["Buy"] = (df[f"EMA{str(EMA1)}"] > df[f"EMA{str(EMA2)}"]) & (df[f"EMA{str(EMA1)}"].shift() <= df[f"EMA{str(EMA2)}"].shift())
    df["Sell"] = (df[f"EMA{str(EMA1)}"] < df[f"EMA{str(EMA2)}"]) & (df[f"EMA{str(EMA1)}"].shift() >= df[f"EMA{str(EMA2)}"].shift())

   
    trade_periods = range(1970,2023)
    data = []
    for year in trade_periods:
        trade_counts = 0 #to count the number of trades
        cash_balance = 0 
        etfs_holding = 0
        capital_invested = 0
        position_condition = False
        df_trade = df[df.Year == year] 
        for index, row in df_trade.iterrows():
            if not position_condition and row["Buy"]:
                #first purchase
                if cash_balance == 0:  
                    etfs_holding = ounce_purhcased
                    capital_invested = ounce_purhcased * row["Close"]
                    if verbose:
                        print("Date:", row['Date'])
                        print("Bought", ounce_purhcased, "ounces of gold at a price of: ",row["Close"] )
                        print("Capital invested to this trade:", etfs_holding * row["Close"])
                        print("Cash in hand:", cash_balance)
                        print()

                #remaining purchases
                else:
                    etfs_holding = cash_balance // row["Close"]
                    cash_balance = cash_balance - etfs_holding * row["Close"]
                    if verbose:
                        print("Date:", row["Date"],
                            "\nBought", etfs_holding,"ounces of gold", "at a price of:", row["Close"], 
                            "\nCapital invested to this trade:", etfs_holding * row["Close"],
                            "\nCash in hand:", cash_balance)
                        print()

                position_condition = True
            
            #sell condition
            elif position_condition and row["Sell"]:
                trade_counts += 1
                cash_balance += etfs_holding * row["Close"]
                position_condition = False
                if verbose:

                    print("Date:", row['Date'],
                        "\nSold",etfs_holding, "ounces of gold at a price of:",row["Close"],
                        "\nCapital gained from trade:", etfs_holding * row["Close"],
                        "\nNet cash:", cash_balance)
                    print()

                etfs_holding = 0
        
        #the last open condition
        if position_condition:
            cash_balance += etfs_holding * df_trade.iloc[-1]["Close"]
            trade_counts += 1
            if verbose:
                print("Date:", row['Date'],
                    "\nSold",etfs_holding, "ounces of gold at a price of:",df_trade.iloc[-1]["Close"],
                "\nCapital gained from trade:", etfs_holding * df_trade.iloc[-1]["Close"],
                "\nNet cash:", cash_balance)
            etfs_holding = 0

        
        if capital_invested == 0:
            continue


        capital_earned = cash_balance - capital_invested
        nominal_return = capital_earned / capital_invested * 100
        data.append((year,trade_counts,capital_invested,cash_balance,capital_earned,nominal_return))
    
        
        
    
    results = pd.DataFrame(data  = data,
                           columns = ["Period","Trade Counts","Capital Invested","Final Capital","Capital Gained","(%)Annual_Return"
                                        ]).set_index("Period")
    
    return results


def simulate_control_group_gold(df, ounce_purchased = 20):
    """
    Simulates the nominal and real returns of a control group.
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    etf_purchased : int
        The number of ETFs purchased.
    expense_rate: float
        The expense rate of SPY ETF.
    
    Returns
    -------
    results: pd.DataFrame
        The result of the control group simulations
    """
    
    #20 years investment periods
    investment_periods = range(1970, 2023)
    data = []

    for year in investment_periods:
        buy_price = df[(df.Year == year) & (df["Month"] == 1)].Close.mean() 
        sell_price = df[(df.Year == year) & (df["Month"] == 12)].Close.mean() 
        portfolio_value_start = buy_price * ounce_purchased
        portfolio_value_end = sell_price * ounce_purchased
        capital_earned = portfolio_value_end - portfolio_value_start
        nominal_return = capital_earned / portfolio_value_start * 100
        data.append((year, portfolio_value_start, portfolio_value_end, capital_earned, nominal_return))

    results = pd.DataFrame(data = data,
                           columns = ["Period","Capital Invested","Final Capital","Capital Gained", "(%)Annual_Return"]
                           ).set_index("Period")
    
    return results