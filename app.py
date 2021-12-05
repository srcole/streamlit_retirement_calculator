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
from datetime import date

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
n_years_save = col2.slider('# years for wage earnings', 0, 50, 15, 1)
annual_savings = col2.slider('Annual savings from wages (x $1,000)', 0, 500, 50, 10)

n_years_retire = col3.slider('# years to be retired', 0, 50, 25, 1)
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
dollar_value_vs_today_by_year = [1]
savings_by_year = [0]
spending_by_year = [0]
for year_i in range(n_years_save + n_years_retire):
    # Compute amounts for the year
    earnings_from_investments = (equities_by_year[year_i] * annual_roi) * (1 - tax_rate_retire)
    dollar_value_vs_today = (1 + inflation_rate) ** (year_i + 1)

    if year_i >= n_years_save:
        spending_after_inflation = annual_spending * dollar_value_vs_today
        savings = 0
    else:
        spending_after_inflation = 0
        savings = annual_savings

    # Compute equity for the year
    equity_year_end = equities_by_year[year_i] + earnings_from_investments + savings - spending_after_inflation

    # Log amounts for each year for bar plot
    years.append(year_i + 1)
    equities_by_year.append(equity_year_end)
    dollar_value_vs_today_by_year.append(dollar_value_vs_today)
    investment_earnings_by_year.append(earnings_from_investments)
    savings_by_year.append(savings)
    spending_by_year.append(spending_after_inflation)


# Create placeholder for chart
chart = st.empty()

# Only look at inflation-adjusted dollar value. And define chart y axis
pltdollarcol, pltyearcol, infcol1, infcol2, infcol3 = st.columns([2, 2, 3, 3, 3])
n_years_into_future = infcol1.slider('# years into future', 0, 50, 10, 1)
inflation_rate_v2 = infcol2.slider('Annual inflation rate (%)', 0.0, 10.0, 3.0, .5) / 100
future_dollar_value = (1 + inflation_rate_v2) ** n_years_into_future
infcol3.text(f'$1 today = ${round(future_dollar_value, 2)} in {n_years_into_future} years')

# Define chart y-axis
plt_dollars_choice = pltdollarcol.radio('Dollar units', ['Unadjusted', 'Inflation-adjusted'], index=0)
plt_years_choice = pltyearcol.radio('Time units', ['Years', '# years'], index=1)
todays_year = date.today().year

# Plot spending and earning
df_plt = pd.concat([
    pd.DataFrame({'year': years, 'dollar_value': dollar_value_vs_today_by_year, 
        'category': 'Last year\'s equity', 'value': [0] + equities_by_year[:-1]}),
    pd.DataFrame({'year': years, 'dollar_value': dollar_value_vs_today_by_year, 
        'category': 'Investment returns', 'value': investment_earnings_by_year}),
    pd.DataFrame({'year': years, 'dollar_value': dollar_value_vs_today_by_year, 
        'category': 'Savings from earnings', 'value': savings_by_year}),
    pd.DataFrame({'year': years, 'dollar_value': dollar_value_vs_today_by_year, 
        'category': 'Expenses', 'value': [-x for x in spending_by_year]})
])

# Determine units based on UI selection
this_year = date.today().year
if plt_dollars_choice == 'Unadjusted':
    df_plt['value'] = df_plt['value'].round(0)
    y_axis_label = 'Amount (x $1,000)'
else:
    df_plt['value'] = (df_plt['value'] / df_plt['dollar_value']).round(0)
    y_axis_label = f'Amount (x $1,000),<br>inflation-adjusted {this_year}-dollars'

if plt_years_choice == 'Years':
    df_plt['year'] = df_plt['year'] + this_year
    x_axis_label = "Year"
    xaxis_limits = [this_year, df_plt['year'].max() + 1]
else:
    x_axis_label = "Years from now"
    xaxis_limits = [0, df_plt['year'].max() + 1]

# Create plot
fig = px.bar(
    df_plt,
    x='year', y="value", color='category',
    height=400,
    color_discrete_sequence=["gray", "green", "blue", "red"],
    labels={
        "year": x_axis_label,
        "category": "Money category",
        "value": y_axis_label
    }
)
fig.update_xaxes(range=xaxis_limits)
# fig.update_layout(hovermode='x')
fig.update_traces(hovertemplate="<br>".join([
        "$%{y}K"
    ]))
fig.update_layout(hovermode="x unified")
chart.plotly_chart(fig, use_container_width=True)
