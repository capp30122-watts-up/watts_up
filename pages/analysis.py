import numpy as np
import pandas as pd
import dash
import sqlite3
from dash import html, dcc, dash_table, callback, callback_context
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from pathlib import Path
import plotly.express as px

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



# Mapping of columns to their corresponding energy source types
wanted_columns = {
    'plgenacl': "COAL",
    'plgenags': "GAS",
    'plgenanc': "NUCLEAR",
    'plgenawi': "WIND",
    'plgenaso': "SOLAR",
    'plgenaol': "OIL",
    'plgenagt': "GEOTHERMAL",
    'plgenabm': "BIOMASS",
    'plgenaof': "FOSSIL",
    'plgenahy': "HYDRO",
    'plgenaop': "OTHER"
}

# Initialize the plant_type column
df_from_db['plant_type'] = ''

for index, row in df_from_db.iterrows():
    # Find the column among the specified ones that has the maximum value for this row
    max_value_column = max(wanted_columns.keys(), key=lambda col: row[col] if col in row else 0)
    
    # Use the column name to get the corresponding plant type from the wanted_columns dictionary
    # Default to 'OTHER' if the column name is not in the dictionary (should not happen with the current setup)
    df_from_db.at[index, 'plant_type'] = wanted_columns.get(max_value_column, 'OTHER')


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

def generate_plant_type_map(df_diff):
    fig = go.Figure()

    # Get unique plant types
    plant_types = df_diff['plant_type'].unique()

    # Map colors or markers to plant types if desired
    colors = px.colors.qualitative.Set1  # Example color palette

    for i, plant_type in enumerate(plant_types):
        df_filtered = df_diff[df_diff['plant_type'] == plant_type]
        fig.add_trace(go.Scattergeo(
            lon=df_filtered['lon'],
            lat=df_filtered['lat'],
            text=df_filtered['pname'] + ': ' + df_filtered['plant_type'],
            marker=dict(
                size=10,
                color=colors[i % len(colors)],  # Cycle through colors
                line=dict(width=0.5, color='rgba(0, 0, 0, 0.5)'),
            ),
            name=plant_type
        ))

    fig.update_layout(
        title_text='Plant Types Distribution',
        title_x=0.5,
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(217, 217, 217)',
        ),
        legend_title_text='Plant Type'
    )

    return fig


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
    # Flex container for side-by-side maps
    html.Div([
        html.Div(id='map-visualization-placeholder', style={'flex': '1'}),
        html.Div(id='plant-type-map-placeholder', style={'flex': '1'})
    ], style={'display': 'flex', 'flexDirection': 'row'}),  # This line sets up the flex container
    # Placeholder for the data table below the visualizations
    html.Div(id='data-table-placeholder'),
    html.Div(id='bar-chart-placeholder')

])

@callback(
    [Output('map-visualization-placeholder', 'children'),
     Output('bar-chart-placeholder', 'children'),
     Output('data-table-placeholder', 'children'),
     Output('plant-type-map-placeholder', 'children')],  # Add this line
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
    df_diff = df_diff.merge(df_from_db[['pname', 'plant_type']].drop_duplicates(), on='pname', how='left')
    df_top_changes = df_diff.sort_values(by='change', ascending=False).head(10)



    #start creation of buble map
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
            colorscale=['#FF5733', '#2ECC71'],  # Red to Green scale
            sizemode='area',
            line_width=0.5,
            opacity=0.7
        ),
        name='Year-over-Year Change'
    ))

    bubble_map.update_layout(
        title_text='Year-over-Year Change in Total Generating Capacity by Plant',
        title_x=0.5,
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(217, 217, 217)',
        ),
        legend_title_text='Change in Capacity'
    )

    bar_chart_figure = create_grouped_bar_chart(df_grouped_type, sorted_fuel_types)
    bar_chart_figure.update_layout(legend=dict(x=0, y=1.0, bgcolor='rgba(255,255,255,0.5)'))
    plant_type_map = generate_plant_type_map(df_diff)


    
    # Define the DataTable to display top changes
    table = dash_table.DataTable(
        id='top-changes-table',
        columns=[
            {"name": "Plant Name", "id": "pname"},
            {"name": "Change in MW", "id": "change"},
            {"name": "Plant Type", "id": "plant_type"}  # Add this line
        ],
        data=df_top_changes.to_dict('records'),

        style_as_list_view=True,
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            {
                'if': {'column_id': 'change', 'filter_query': '{change} > 0'},
                'color': 'green',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'change', 'filter_query': '{change} <= 0'},
                'color': 'red',
                'fontWeight': 'bold'
            }
        ]
    )

    return dcc.Graph(figure=bubble_map), dcc.Graph(figure=bar_chart_figure), table, dcc.Graph(figure=plant_type_map)
