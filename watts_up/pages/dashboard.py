import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import sqlite3


dash.register_page(__name__, path='/')


#Connect to the database
conn = sqlite3.connect('watts_up/data/final_data/plants.db')

# Query for energy generation and carbon emission data
query_plants = '''
    SELECT year, state_id,
    sum(plngenan) as total_energy, sum(plgenatn) as non_renewable_energy, sum(plgenatr) as renewable_energy,
    sum(plco2an) as carbon_emission
    FROM plants 
    GROUP BY year_state
    UNION
    SELECT year, 'US' as state_id,
    sum(plngenan) as total_energy, sum(plgenatn) as non_renewable_energy, sum(plgenatr) as renewable_energy,
    sum(plco2an) as carbon_emission
    FROM plants 
    GROUP BY year;
'''
df_plants = pd.read_sql(query_plants, conn)

# Query for energy price data
query_price = '''
    SELECT year, stateid, price_all as total_average_price, price_com as commercial_price, price_ind as indusrial_price, price_res as residential_price
    FROM elec_table
    GROUP BY year, stateid
    UNION
    SELECT year, 'US' as stateid, price_all as total_average_price, price_com as commercial_price, price_ind as indusrial_price, price_res as residential_price
    FROM elec_table
    GROUP BY year;   
'''
df_price = pd.read_sql(query_price, conn)

layout = html.Div([
    html.H1("Energy Generation, Emission and Price Trends by State"),

# Dropdown for state selection    
    dcc.Dropdown(
        id='state-dropdown',
        options = [{'label': state, 'value': state} for state in df_plants['state_id'].unique()],
        value = 'US'
    ),
    
# Dropdown for trend type selection
    dcc.Dropdown(
            id='trend-type-dropdown',
            options=[
                {'label': 'Energy Generation Trend', 'value': 'energy-trend'},
                {'label': 'Carbon Emission Trend', 'value': 'carbon-trend'},
                {'label': 'Energy Price Trend', 'value': 'price-trend'}
            ],
            value='energy-trend', 
            clearable=False
    ),
    
    # Graph for the selected trend
    dcc.Graph(id='main-plot'),
])

@callback(
    Output('main-plot', 'figure'),
    [Input('state-dropdown', 'value'),
     Input('trend-type-dropdown', 'value')]
)
def update_main_plot(selected_state, selected_trend):
    if selected_trend == 'energy-trend':    
        filtered_df = df_plants[df_plants['state_id'] == selected_state]
        long_df = pd.melt(filtered_df, id_vars=['year'], value_vars=['total_energy', 'non_renewable_energy', 'renewable_energy'],
                        var_name='energy_type', value_name='energy_value')
        plot = px.line(long_df, x='year', y='energy_value', color='energy_type', title=f"Energy Generation Trends in {selected_state}")
        plot.update_yaxes(title_text=' lb/MWh')

    elif selected_trend == 'carbon-trend': 
        filtered_df = df_plants[df_plants['state_id'] == selected_state]
        plot = px.line(filtered_df, x='year', y='carbon_emission', title=f"Carbon Emission Trends in {selected_state}")   
        plot.update_yaxes(title_text='short tons = 2,000 pounds')
        
    elif selected_trend == 'price-trend':
        filtered_df = df_price[df_price['stateid'] == selected_state]
        long_df = pd.melt(filtered_df, id_vars=['year'], value_vars=['total_average_price', 'commercial_price', 'industrial_price','residential_price'],
                        var_name='price_type', value_name='price_value')    
        plot = px.line(long_df, x='year', y='price_value', color='price_type', title=f"Energy Price Trends in {selected_state}")
        plot.update_yaxes(title_text='cents per Kilowatt-hours')
    
    plot.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white'
    )    
        
    return plot
