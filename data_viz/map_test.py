import numpy as np
import pandas as pd
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

#connects to sqlite3 database
database_path = Path(__file__).parent.parent / 'data_sources' / 'database' / 'plants.db'

connect = sqlite3.connect(database_path)
# converts to pd from sql query
df_from_db = pd.read_sql_query("SELECT * FROM plants", connect)
connect.close()
df_grouped = df_from_db.groupby('state_id')
df_summed = df_grouped['plgenacl'].sum().reset_index()

unique_years = df_from_db['year'].unique()
unique_years.sort()

app = Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in unique_years],
        value=unique_years[0] # can change value to any year (its set to 2004)
    ),
    html.Div(id='visualizations-placeholder'),
    html.Div(id='top-10-table-placeholder')  
])

#output
@app.callback(
    Output('visualizations-placeholder', 'children'),
    [Input('year-dropdown', 'value')]
)

def update_visualizations(selected_year):
    filtered_df = df_from_db[df_from_db['year'] == selected_year]

    df_grouped = filtered_df.groupby('state_id')
    df_summed = df_grouped['plgenacl'].sum().reset_index()

    # Creates the data visualizations based on the filtered groups.     
    choropleth = go.Choropleth(
        locations=df_summed['state_id'],
        z=df_summed['plgenacl'].astype(int),
        locationmode='USA-states',
        colorscale='Blues',
        colorbar_title='Electricity Generation per State (COAL)'
    )

    fig_choropleth = go.Figure(data=[choropleth])
    fig_choropleth.update_layout(
        title_text=f'{selected_year} State Annual Net Generation (MWh)',
        geo_scope='usa'
    )

    #makes table
    top_10_df = filtered_df.groupby('state_id', as_index=False)['plgenacl'].sum().nlargest(10, 'plgenacl')
    
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in top_10_df.columns],
        data=top_10_df.to_dict('records'),
        page_size=10,  #rows/size
        style_table={'height': '300px', 'overflowY': 'auto'}
    )
    #map of plants by year- can decrease and increase
    scattergeo = go.Scattergeo(
        lon=filtered_df['lon'],
        lat=filtered_df['lat'],
        mode='markers',
        marker=dict(
            size=5,
            color='red',
            line_color='black',
            line_width=0.5,
        ),
        text=filtered_df['state_id']
    )

    fig_scattergeo = go.Figure(data=[scattergeo])
    fig_scattergeo.update_layout(
        title_text=f'{selected_year} Plant Locations',
        geo_scope='usa',
    )
   
    #wraps it in HTML component
    components = [dcc.Graph(figure=fig_choropleth), table, dcc.Graph(figure=fig_scattergeo)]
    return components


#run it baby
if __name__ == '__main__':
    app.run_server(debug=True)
