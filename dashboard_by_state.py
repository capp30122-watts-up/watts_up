from sqlalchemy import create_engine
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

#Connect to the database
engine = create_engine('sqlite:///data_sources/database/plants.db')

# Query for energy generation and carbon emission data
query_plants = '''
    SELECT year_state, year, state_id,
    sum(plngenan) as total_energy, sum(plgenatn) as non_renewable_energy, sum(plgenatr) as renewable_energy,
    sum(plco2an) as carbon_emission
    FROM plants 
    GROUP BY year_state, year;
'''
df_plants = pd.read_sql(query_plants, engine)

# Query for energy price data
query_price = '''
    SELECT year, stateid, price_all as price_total, price_com as price_commercial, price_ind as price_industrial, price_res as price_residential
    FROM elec_table
    GROUP BY year_state, year;
'''
df_price = pd.read_sql(query_price, engine)


#Create dashboard
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Energy Generation, Emission and Price Trends by State"),

# Dropdown for state selection    
    dcc.Dropdown(
        id='state-dropdown',
        options=[{'label': state, 'value': state} for state in df_plants['state_id'].unique()],
        value=df_plants['state_id'].unique()[0]
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


@app.callback(
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

    elif selected_trend == 'carbon-trend': 
        filtered_df = df_plants[df_plants['state_id'] == selected_state]
        plot = px.line(filtered_df, x='year', y='carbon_emission', title=f"Carbon Emission Trends in {selected_state}")   
        
    elif selected_trend == 'price-trend':
        filtered_df = df_price[df_price['stateid'] == selected_state]
        long_df = pd.melt(filtered_df, id_vars=['year'], value_vars=['price_total', 'price_commercial', 'price_industrial','price_residential'],
                        var_name='price_type', value_name='price_value')    
        plot = px.line(long_df, x='year', y='price_value', color='price_type', title=f"Energy Price Trends in {selected_state}")
     
    return plot

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)