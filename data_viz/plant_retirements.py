import numpy as np
import pandas as pd
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
import sqlite3
import plotly.graph_objects as go
from pathlib import Path

# Connects to sqlite3 database
database_path = Path(__file__).parent.parent / 'data_sources' / 'database' / 'plants.db'

connect = sqlite3.connect(database_path)
# Converts to pd from sql query
df_from_db = pd.read_sql_query("SELECT * FROM plants", connect)
connect.close()

df_from_db['year'] = pd.to_numeric(df_from_db['year'], errors='coerce')
df_from_db['plgenacl'] = pd.to_numeric(df_from_db['plgenacl'], errors='coerce')

app = Dash(__name__)

unique_years = df_from_db['year'].unique()
unique_years.sort()

app.layout = html.Div([
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in unique_years],
        value=unique_years[0]  
    ),
    html.Div(id='visualizations-placeholder'),
])

@app.callback(
    Output('visualizations-placeholder', 'children'),
    [Input('year-dropdown', 'value')]
)
def update_visualizations(selected_year):
    selected_year = int(selected_year)
    df_previous_and_selected = df_from_db[df_from_db['year'].isin([selected_year - 1, selected_year])]

    # this is to Group by plant name and year, then sum the generation capacity
    df_grouped = df_previous_and_selected.groupby(['pname', 'year'])['plgenacl'].sum().reset_index()

    df_diff = df_grouped.pivot(index='pname', columns='year', values='plgenacl')

    # Calculate the difference in generation capacity for each plant between the two years
    df_diff['change'] = df_diff[selected_year] - df_diff.get(selected_year - 1, 0)

    df_locations = df_from_db[['pname', 'lon', 'lat']].drop_duplicates(subset='pname')
    df_diff = df_diff.reset_index().merge(df_locations, on='pname', how='left')


    # Create the bubble map
    bubble_map = go.Figure()

    df_diff['change'] = df_diff['change'].fillna(0)

    max_change = max(np.abs(df_diff['change'])) + 1e-9  
    sizes = np.abs(df_diff['change']) / max_change * 50 

    df_diff['lon'] = df_diff['lon'].fillna(0)  

    bubble_map.add_trace(go.Scattergeo(
    lon=df_diff['lon'],  
    lat=df_diff['lat'],
    text=df_diff['pname'] + ': ' + df_diff['change'].astype(str) + ' MW',
    marker=dict(
        size=sizes,
        color=np.sign(df_diff['change']),
        colorscale=['red', 'blue'],
        sizemode='area',
        line_width=0.5,
        opacity=0.7
    ),
    name='Year-over-Year Change'
))


    bubble_map.update_layout(
        title=f'Year-over-Year Change in Generating Capacity by Plant',
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(217, 217, 217)',
        )
    )

    # Wrap it in HTML component
    components = [dcc.Graph(figure=bubble_map)]
    return components

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
