"""
Run with: streamlit run retirement_investments.py

# Brainstorm
# Want to define variables
# - number of years going to save
# - year of interest to compute interest
# - spending per year starting that year
# Want to plot bar chart of savings over time
# Want to print some useful stats
# - estimated earnings on investments; in current-day dollars
# - estimated worth in current-day dollars

# Model variables and formula
# future_dollar_value = (1 + inflation_rate) ^ n_years_into_future
# equity_while_earning = starting_equity * (1 + annual_roi) + annual_savings

# TODO
- Write equations in header
- remove text
- make fit on 1 page
- move inflation to bottom
- print formulas
- plot x-axis
- plot y-axis
- plot legend format
- plot tooltip
- plot colors

- re-set defaults
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

st.title(f'Retirement on investments calculator')

# Inputs in first 2 columns
col1, col2, col3 = st.columns([2, 2, 2])
inflation_rate = col1.slider('Inflation rate', 0.0, .1, .03, .005)
annual_roi = col1.slider('Annual ROI', 0.0, .2, .06, .005)
n_years_save = col1.slider('# years to save money', 0, 50, 2, 1)
n_years_coast = col1.slider('# years coasting', 0, 50, 1, 1)

starting_equity = col2.slider('Starting equity (x $1,000)', 0, 2000, 770, 10)
annual_savings = col2.slider('Annual savings (x $1,000)', 0, 500, 200, 10)
annual_spending = col2.slider('Annual spending (x $1,000, today\'s $)', 0, 100, 48, 1)
tax_rate_coast = col2.slider('Tax rate: ', 0.0, 0.3, 0.2, 0.01)

# Compute equity from saving
years, equities_by_year, investment_earnings_by_year, savings_by_year, spending_by_year = [0], [starting_equity], [0], [0], [0]
equity_after_earning = starting_equity
for year_i in range(n_years_save):
    equity_after_earning = equity_after_earning * (1 + annual_roi) + annual_savings
    years.append(year_i + 1)
    equities_by_year.append(equity_after_earning)
    investment_earnings_by_year.append(equity_after_earning * annual_roi)
    savings_by_year.append(annual_savings)
    spending_by_year.append(0)
future_dollar_value_after_saving = (1 + inflation_rate) ** n_years_save
future_dollar_value_after_saving_today_dollars = equity_after_earning / future_dollar_value_after_saving
col3.text(f'Equity after saving = ${equity_after_earning:.0f}K,\n    today\'s dollars: ${future_dollar_value_after_saving_today_dollars:.0f}K')


# Compute investment income after savings
equity_after_coasting = equity_after_earning
for year_i in range(n_years_coast):
    earnings_from_investments = (equity_after_coasting * annual_roi) * (1 - tax_rate_coast)
    spending_after_inflation = annual_spending * (1 + inflation_rate) ** (n_years_save + year_i)
    equity_after_coasting = equity_after_coasting + earnings_from_investments - spending_after_inflation
    
    # Update annual totals
    years.append(year_i + 1 + n_years_save)
    equities_by_year.append(equity_after_coasting)
    investment_earnings_by_year.append(earnings_from_investments)
    savings_by_year.append(0)
    spending_by_year.append(spending_after_inflation)
    
col3.text(f'Earned from investments = ${earnings_from_investments:.0f}K')
col3.text(f'Spending after inflation = ${spending_after_inflation:.0f}K')
col3.text(f'Equity after coasting = ${equity_after_coasting:.0f}K')


# Just look at inflation
n_years_into_future = col3.slider('# years into future', 0, 50, 10, 1)
future_dollar_value = (1 + inflation_rate) ** n_years_into_future
col3.text(f'Future $ value: $1 today = ${round(future_dollar_value, 2)} in {n_years_into_future} years')

# # Plot of Equity every year + earnings and spending
# df = pd.DataFrame({'year': years, 'equity': equities_by_year})
# fig = px.bar(df, x='year', y='equity')

# st.plotly_chart(fig, use_container_width=True)


# Plot with spending and earning
# Plot: x - year, y - $, hue - equity from last year, earned on investments, earned from savings, spent
df_hplot = pd.concat([
    pd.DataFrame({'year': years, 'category': 'last_year_equity', 'value': [0] + equities_by_year[:-1]}),
    pd.DataFrame({'year': years, 'category': 'investment_earnings', 'value': investment_earnings_by_year}),
    pd.DataFrame({'year': years, 'category': 'savings', 'value': savings_by_year}),
    pd.DataFrame({'year': years, 'category': 'spending', 'value': [-x for x in spending_by_year]})
])
fig_hplot = px.bar(df_hplot, x='year', y="value", color='category')
st.plotly_chart(fig_hplot, use_container_width=True)

