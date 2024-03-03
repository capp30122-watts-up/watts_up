import numpy as np
import pandas as pd
import dash
import sqlite3
from dash import html, dcc, dash_table, callback
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from pathlib import Path

dash.register_page(__name__)

def df_load(table_name):
    '''
    Load data for dashboard, and create new columns for filtering
    Input:
        table_name
    Output:
        df: dataframe
    '''
    conn = sqlite3.connect('data/final_data/plants.db')
    
    query = f"SELECT * FROM {table_name}"

    df = pd.read_sql_query(query,conn)

    conn.close()

    return df

def retirement_load_and_preprocess_data():
    df = df_load("plants")
    df['other_sources'] = df[['plgenaol', 'plgenagt', 'plgenabm', 'plgenaof','plgenahy','plgenaop']].sum(axis=1)

    df['total_gen_capacity'] = (df['plgenacl'] + df['plgenags'] + df['plgenanc'] + df['plgenawi'] + df['plgenaso']
                            + df['other_sources'])
    
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['total_gen_capacity'] = pd.to_numeric(df['total_gen_capacity'], errors='coerce')
    unique_years = df['year'].unique()
    unique_years.sort()

   
    return df, unique_years

df_from_db, unique_years = retirement_load_and_preprocess_data()

df_grouped_type = df_from_db.groupby('year').agg({
    'plgenacl': 'sum',
    'plgenags': 'sum',
    'plgenanc': 'sum',
    'plgenawi': 'sum', 
    'plgenaso': 'sum',
    'other_sources': 'sum',
    }).reset_index()
total_capacities = {
    fuel_type: df_grouped_type[fuel_type].sum() for fuel_type in ['plgenacl', 'plgenags', 'plgenanc', 'plgenawi', 'plgenaso', 'other_sources']
}
sorted_fuel_types = sorted(total_capacities, key=total_capacities.get)


# creates group bar based on fuel types
def create_grouped_bar_chart(df_grouped_type, sorted_fuel_types):
    # Filter out years where the sum across all fuel types is zero
    df_grouped_type['total_capacity'] = df_grouped_type[sorted_fuel_types].sum(axis=1)
    df_filtered = df_grouped_type[df_grouped_type['total_capacity'] > 0]

    traces = [go.Bar(
        x=df_filtered['year'],
        y=df_filtered[fuel_type],
        name=fuel_type  
    ) for fuel_type in sorted_fuel_types]
    
    layout = go.Layout(
        title='Generating Capacity Retirements by Year and Fuel Type',
        xaxis={'title': 'Year'},
        yaxis={'title': 'Capacity (MW)'},
        barmode='stack',
        legend_title='Fuel Type',
        legend=dict(orientation="h"),
    )
    
    return go.Figure(data=traces, layout=layout)


layout = html.Div([
    html.H1('Analysis Page'),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in unique_years],
        value=unique_years[0]
    ),
    html.Div(
        id='visualizations-container',
        style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}
    ),
    html.Div(id='map-visualization-placeholder', style={'flex': '1'}),
    html.Div(id='bar-chart-placeholder', style={'flex': '1'}),
    # Placeholder for the data table below the visualizations
    html.Div(id='data-table-placeholder')
])


@callback(
    Output('map-visualization-placeholder', 'children'),
    Output('bar-chart-placeholder', 'children'),
    [Input('year-dropdown', 'value')]
)
def update_visualizations(selected_year):
    selected_year = int(selected_year)
    df_previous_and_selected = df_from_db[df_from_db['year'].isin([selected_year - 1, selected_year])]

    df_grouped = df_previous_and_selected.groupby(['pname', 'year'])['total_gen_capacity'].sum().reset_index()



    df_diff = df_grouped.pivot(index='pname', columns='year', values='total_gen_capacity')

    
    df_diff['change'] = df_diff[selected_year] - df_diff.get(selected_year - 1, 0)

    df_locations = df_from_db[['pname', 'lon', 'lat']].drop_duplicates(subset='pname')
    df_diff = df_diff.reset_index().merge(df_locations, on='pname', how='left')

    df_top_changes = df_diff.sort_values(by='change', ascending=False).head(10)

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
        title='Year-over-Year Change in Total Generating Capacity by Plant',
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(217, 217, 217)',
        )
    )

    datatable = dash_table.DataTable(
        columns=[{'name': 'Plant Name', 'id': 'pname'}, {'name': 'Change', 'id': 'change'}],
        data=df_top_changes[['pname', 'change']].to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'minWidth': '100px', 'width': '100px', 'maxWidth': '100px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        page_size=10,  # Ensure only 10 rows are displayed, adjust if needed
        style_data_conditional=[
        {
            'if': {'column_id': 'change', 'filter_query': '{change} > 0'},
            'color': 'green'
        },
        {
            'if': {'column_id': 'change', 'filter_query': '{change} <= 0'},
            'color': 'red'
        }
    ]
),
    
    bar_chart_figure = create_grouped_bar_chart(df_grouped_type,sorted_fuel_types)

    return dcc.Graph(figure=bubble_map), dcc.Graph(figure=bar_chart_figure)
