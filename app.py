"""
Retirement calculator web app

# Formula for equity after each year:
# eq[y+1] = eq[y] + ri + sa - sp

# eq = equity at end of year
# y = year
# ri = return on investments
# sa = savings from earnings
# sp = spending of equity

# ri = eq[y] * investment annual ROI * (1 - retired tax rate)
# sp = annual spending * (1 + annual inflation rate) ^ (number of years from now)
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    layout="wide",
    page_icon=':older_man:',
    page_title='Retirement calculator'
)

st.title(f'Retirement on investments calculator')

# Inputs in first 2 columns
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 3])
inflation_rate = col1.slider('Inflation rate (%)', 0.0, 10.0, 3.0, .5) / 100
annual_roi = col1.slider('Annual investment ROI (%)', 0.0, 20.0, 6.0, .5) / 100
n_years_save = col2.slider('# years for wage earnings', 0, 50, 10, 1)
annual_savings = col2.slider('Annual savings from wages (x $1,000)', 0, 500, 80, 10)

n_years_retire = col3.slider('# years to be retired', 0, 50, 40, 1)
annual_spending = col3.slider('Annual retired spending (x $1,000)', 0, 100, 30, 1)
starting_equity = col4.slider('Starting equity (x $1,000)', 0, 2000, 100, 10)
tax_rate_retire = col4.slider('Tax rate when retired (%)', 0, 30, 15, 1) / 100


col5.latex("eq[year+1] = eq[year] + ri + sa - sp")
col5.write("_eq_ = equity at end of year")
col5.write("_ri_ = annual return on investments, minus taxes")
col5.write("_sa_ = annual savings from wage earnings")
col5.write("_sp_ = annual spending of equity, inflation-adjusted")
# # ri = eq[y] * investment annual ROI * (1 - retired tax rate)
# # sp = annual spending * (1 + annual inflation rate) ^ (number of years from now)


# Compute equity after each year
years = [0]
equities_by_year = [starting_equity]
investment_earnings_by_year = [0]
savings_by_year = [0]
spending_by_year = [0]
for year_i in range(n_years_save + n_years_retire):
    # Compute amounts for the year
    earnings_from_investments = (equities_by_year[year_i] * annual_roi) * (1 - tax_rate_retire)

    if year_i >= n_years_save:
        spending_after_inflation = annual_spending * (1 + inflation_rate) ** (year_i + 1)
        savings = 0
    else:
        spending_after_inflation = 0
        savings = annual_savings

    # Compute equity for the year
    equity_year_end = equities_by_year[year_i] + earnings_from_investments + savings - spending_after_inflation

    # Log amounts for each year for bar plot
    years.append(year_i + 1)
    equities_by_year.append(equity_year_end)
    investment_earnings_by_year.append(earnings_from_investments)
    savings_by_year.append(savings)
    spending_by_year.append(spending_after_inflation)


# Plot spending and earning
df_plt = pd.concat([
    pd.DataFrame({'year': years, 'category': 'Last year\'s equity', 'value': [0] + equities_by_year[:-1]}),
    pd.DataFrame({'year': years, 'category': 'Investment returns', 'value': investment_earnings_by_year}),
    pd.DataFrame({'year': years, 'category': 'Savings from earnings', 'value': savings_by_year}),
    pd.DataFrame({'year': years, 'category': 'Expenses', 'value': [-x for x in spending_by_year]})
])
df_plt['value'] = df_plt['value'].round(0)
fig = px.bar(
    df_plt,
    x='year', y="value", color='category',
    height=400,
    labels={
        "year": "Years from now",
        "category": "Money category",
        "value": "Amount (x $1,000)"
    }
)
fig.update_xaxes(range=[0, df_plt['year'].max() + 1])
st.plotly_chart(fig, use_container_width=True)

# Only look at inflation-adjusted dollar value
infcol1, infcol2, infcol3 = st.columns([2, 2, 2])
n_years_into_future = infcol1.slider('# years into future', 0, 50, 10, 1)
inflation_rate_v2 = infcol2.slider('Annual inflation rate (%)', 0.0, 10.0, 3.0, .5) / 100
future_dollar_value = (1 + inflation_rate_v2) ** n_years_into_future
infcol3.text(f'$1 today = ${round(future_dollar_value, 2)} in {n_years_into_future} years')
