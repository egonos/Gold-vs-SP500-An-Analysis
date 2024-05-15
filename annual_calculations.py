import pandas as pd
import numpy as np
from tqdm import tqdm
from data import *
import mplfinance as mpf
import matplotlib.pyplot as plt

def compute_annual_returns_stocks(df):
    """
    Computes annual returns of stocks
    Parameters
    ----------
    df: pd.DataFrame
        The DataFrame containing the data
    
    Returns
    -------
    results: pd.DataFrame
        A DataFrame containing annual returns of SP500

    """
    investment_periods = range(1951, 2024)
    annual_returns = []
    for year in tqdm(investment_periods):
        current_year_data = df[df['Year'] == year]
        previous_year_data = df[df['Year'] == year - 1]

        current_year_mean = current_year_data['Close'].mean()
        previous_year_mean = previous_year_data['Close'].mean()
        dividend_return = divs[year-1] * previous_year_mean / 100
        inflation_constant = cpi[year] / cpi[year-1]

        adjusted_previous_mean = previous_year_mean * inflation_constant
        adjusted_dividend_return = dividend_return * inflation_constant
        adjusted_annual_return_without_dividends = (current_year_mean - adjusted_previous_mean) / adjusted_previous_mean * 100
        adjusted_annual_return_with_dividends = (current_year_mean + adjusted_dividend_return - adjusted_previous_mean) / adjusted_previous_mean * 100
        annual_returns.append(((year-1, year), adjusted_annual_return_without_dividends, adjusted_annual_return_with_dividends))

    results = pd.DataFrame(annual_returns, columns=["Period", "(%)Adjusted_Annual_Return_Without_Dividends", "(%)Adjusted_Annual_Return_With_Dividends"])
    results = results.set_index("Period")
    return results

def compute_annual_returns_stocks_individually(df):
    """
    Computes annual returns of stocks one by one for each month then combines the values
    Parameters
    ----------
    df: pd.DataFrame
        A dataframe containing stock prices

    Returns
    -------
    individual_return_df: pd.DataFrame
        A dataframe containing the annual returns stocks monthly average
    """

    investment_periods = range(1951, 2024)
    annual_returns = []
    for year in tqdm(investment_periods):
        individual_returns = []
        for month in range(1,13):
            current_year_data = df[(df['Year'] == year) & (df['Month'] == month)]
            previous_year_data = df[(df['Year'] == year-1) & (df['Month'] == month)]

            current_year_mean = current_year_data['Close'].mean()
            previous_year_mean = previous_year_data['Close'].mean()
            dividend_return = divs[year-1] * previous_year_mean / 100 
            inflation_constant = cpi[year] / cpi[year-1]

            adjusted_previous_mean = previous_year_mean * inflation_constant
            adjusted_dividend_return = dividend_return * inflation_constant
            adjusted_annual_return = (current_year_mean + adjusted_dividend_return - adjusted_previous_mean) / adjusted_previous_mean * 100

            individual_returns.append(adjusted_annual_return)

        mean_returns = np.mean(individual_returns)
        annual_returns.append(((year,year-1), mean_returns))

    
    individual_return_df = pd.DataFrame(data = annual_returns,
                                        columns = ['Period','(%)Adjusted_Real_Returns'],
                                        ).set_index('Period')
    
    return individual_return_df

def compute_annual_returns_stocks_individually_display(df):
    """
    Computes annual returns of stocks one by one for each month
    Parameters
    ----------
    df: pd.DataFrame
        A dataframe containing stock prices

    Returns
    -------
    individual_return_display_df: pd.DataFrame
        A dataframe containing the annual returns stocks
    """

    investment_periods = range(1951, 2024)
    annual_returns = []
    for year in tqdm(investment_periods):
        individual_returns = []
        for month in range(1,13):
            current_year_data = df[(df['Year'] == year) & (df['Month'] == month)]
            previous_year_data = df[(df['Year'] == year-1) & (df['Month'] == month)]

            current_year_mean = current_year_data['Close'].mean()
            previous_year_mean = previous_year_data['Close'].mean()
            dividend_return = divs[year-1] * previous_year_mean / 100 
            inflation_constant = cpi[year] / cpi[year-1]

            adjusted_previous_mean = previous_year_mean * inflation_constant
            adjusted_dividend_return = dividend_return * inflation_constant
            adjusted_annual_return = (current_year_mean + adjusted_dividend_return - adjusted_previous_mean) / adjusted_previous_mean * 100

            individual_returns.append(((year-1,year),month,adjusted_annual_return))

        annual_returns.extend(individual_returns)
    
    individual_return_display_df = pd.DataFrame(data = annual_returns,
                                                columns = ["Period", "Month", "(%)Adjusted_Real_Returns"]).set_index("Period")
    
    return individual_return_display_df



def compute_annual_returns_commodity(df,start = 1951,end = 2024):
    """
    Computes the annual returns of commodity
    Parameters
    ----------
    df: pd.DataFrame
        A dataframe containing commodity prices
    
    Returns
    -------
    results: pd.DataFrame
        A dataframe containing the annual returns of a commodity
    """
    df = df.copy()
    df["Year"] = pd.to_datetime(df["Date"]).dt.year
    investment_periods = range(start, end)
    annual_returns = []
    for year in tqdm(investment_periods):
        current_year_data = df[df['Year'] == year]
        previous_year_data = df[df['Year'] == year - 1]

        current_year_mean = current_year_data['Close'].mean()
        previous_year_mean = previous_year_data['Close'].mean()
        inflation_constant = cpi[year] / cpi[year-1]

        adjusted_previous_mean = previous_year_mean * inflation_constant
        adjusted_annual_return = (current_year_mean - adjusted_previous_mean) / adjusted_previous_mean * 100
        annual_returns.append(((year-1, year), adjusted_annual_return))

    results = pd.DataFrame(annual_returns, columns=["Period", "(%)Adjusted_Annual_Return"])
    results = results.set_index("Period")
    return results

def compute_annual_returns_gold_individually(df):
    """
    Computes annual returns of gold for each month then combines the results
    Parameters
    ----------
    df: pd.DataFrame
        A dataframe containing gold prices
    
    Returns
    -------
    individual_return_df: pd.DataFrame
        A dataframe containing the annual returns of gold
        
    """
    annual_returns = []
    for year in tqdm(range(1951,2024)):
        individual_returns = []
        for month in range(1,13):
            current_year_data = df[(df['Year'] == year) & (df['Month'] == month)]
            previous_year_data = df[(df['Year'] == year-1) & (df['Month'] == month)]

            if len(current_year_data) == 0 or len(previous_year_data) == 0:
                    continue

            current_year_mean = current_year_data['Close'].mean()
            previous_year_mean = previous_year_data['Close'].mean()
            inflation_constant = cpi[year] / cpi[year-1]

            adjusted_previous_mean = previous_year_mean * inflation_constant
            adjusted_annual_return = (current_year_mean - adjusted_previous_mean) / adjusted_previous_mean * 100

            individual_returns.append(adjusted_annual_return)


        mean_returns = np.mean(individual_returns)
        annual_returns.append(((year-1,year), mean_returns))

    
    individual_return_df = pd.DataFrame(data = annual_returns,
                                        columns = ['Period','(%)Adjusted_Real_Returns'],
                                        ).set_index('Period')
    
    return individual_return_df
