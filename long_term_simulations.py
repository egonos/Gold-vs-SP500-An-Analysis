import pandas as pd
import numpy as np
from tqdm import tqdm
from data import *
import mplfinance as mpf
import matplotlib.pyplot as plt

def simulate_twenty_years_of_investment(df, purchase_times=10, sample_size=1, etf_per_purchase=2, expense_ratio=0.00095):
    investment_periods = [(i, i+20) for i in range(1950, 2004)]
    real_returns = []

    for start_year, end_year in tqdm(investment_periods):

        start = df[df['Year'] == start_year]

        for _ in range(sample_size):
            buy_prices = start.sample(purchase_times, replace=False)['Close'].values / 10
            portfolio_value = np.sum(etf_per_purchase * buy_prices)
            portfolio_value_not_invested = portfolio_value
            
            for year in range(start_year + 1, end_year + 1):
             
                annual_growth_constant = df[df['Year'] == year]['Close'].mean() / df[df['Year'] == year - 1]['Close'].mean()
                annual_return_with_divs = annual_growth_constant + divs[year - 1] / 100
                annual_return_with_divs_expenses = annual_return_with_divs - expense_ratio
                annual_return_without_divs_expenses = annual_growth_constant - expense_ratio
                
                portfolio_value *= annual_return_with_divs_expenses
                portfolio_value_not_invested *= annual_return_without_divs_expenses 
                
            
            portfolio_value_adjusted = portfolio_value * cpi[2023] / cpi[end_year]
            portfolio_value_adjusted_not_invested = portfolio_value_not_invested * cpi[2023] / cpi[end_year]
            capital_invested = np.sum(etf_per_purchase * buy_prices)
            capital_invested_adjusted = capital_invested * cpi[2023] / cpi[start_year]
            
            percent_change_nominal = (portfolio_value - capital_invested) * 100 / capital_invested
            percentage_change_not_invested = (portfolio_value_adjusted_not_invested - capital_invested_adjusted) * 100 / capital_invested_adjusted
            percent_change = (portfolio_value_adjusted - capital_invested_adjusted) * 100 / capital_invested_adjusted

            real_returns.append(("("+str(start_year)+", "+ str(end_year)+")", 
                     capital_invested, portfolio_value, portfolio_value-capital_invested,
                     capital_invested_adjusted, portfolio_value_adjusted, percentage_change_not_invested, percent_change,
                     (portfolio_value_adjusted_not_invested - capital_invested_adjusted)))


    simulation_results = pd.DataFrame(real_returns, columns=['Period', 'Capital Invested', 'Portfolio Value', 'Capital Gained', 'Capital Invested Adjusted', 'Portfolio Value Adjusted', '% Change w.o. Dividend', '% Change with Dividend', 'Real Returns'])
    return simulation_results

def simulate_twenty_years_of_investment_gold(df, sample_size=30,purchase_times = 10,ounce_per_purchase = 2):
    investment_periods = [(i, i+20) for i in range(1950, 2004)]
    real_returns = []
    for start_year, end_year in tqdm(investment_periods):
        start = df[df['Year'] == start_year]
        end = df[df["Year"] == end_year]
        
        #for some of the years we only have 4 data points
        if len(start) == 4:
            purchase_times = 1

        for _ in range(sample_size):
            buy_prices = start.sample(purchase_times, replace=False)['Close'].values
            capital_invested = np.sum(buy_prices) * ounce_per_purchase
            portfolio_value = end.Close.mean() * purchase_times * ounce_per_purchase

            portfolio_value_adjusted = portfolio_value * cpi[2023] / cpi[end_year]
            capital_invested_adjusted = capital_invested * cpi[2023] / cpi[start_year]
            percentage_real_returns = (portfolio_value_adjusted - capital_invested_adjusted)/ capital_invested_adjusted * 100

            real_returns.append(("("+str(start_year)+", "+ str(end_year)+")", capital_invested, portfolio_value, portfolio_value - capital_invested, capital_invested_adjusted,
                                 portfolio_value_adjusted, percentage_real_returns))
            

    simulation_results = pd.DataFrame(real_returns, columns=['Period', 'Capital Invested', 'Portfolio Value', 'Capital Gained', 'Capital Invested Adjusted',
                                                             'Portfolio Value Adjusted', '% Change'])
    return simulation_results
