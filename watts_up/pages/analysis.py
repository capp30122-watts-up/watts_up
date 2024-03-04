'''
This script is used to pull and map year-over-year energy production by plant and plant
types.

Author: Frank Vasquez
'''
from watts_up.util.util import PLANT_TYPE_COLOR
from watts_up.data_viz.visuals import bar_chart, bubble_map, generate_plant_type_map
from watts_up.data_viz.data_manager import df_from_db, unique_years
from watts_up.data_viz.helper import aggregate_and_rename_power_generation_data, prepare_data_for_bubble_map
import dash
from dash import html, dcc,callback
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

dash.register_page(__name__, path='/')

# Aggregates and rename power generation data for clearer analysis of plants
df_grouped_type = aggregate_and_rename_power_generation_data(df_from_db)

total_capacities = {
    fuel_type: df_grouped_type[fuel_type].sum() 
    for fuel_type in ['Coal', 'Gas', 'Nuclear', 'Wind', 'Solar', 'Other']
}

sorted_fuel_types = sorted(total_capacities, key=total_capacities.get)
df_grouped_type['total_capacity'] = df_grouped_type[sorted_fuel_types].sum(axis=1)
df_filtered = df_grouped_type[df_grouped_type['total_capacity'] > 0]


# layout of the Dash page, adds dropdowns for visualizations
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
    html.Div(id='bar-chart-placeholder'),
    # Flex container for side-by-side maps
    html.Div([
        html.Div(id='map-visualization-placeholder', style={'flex': '1'}),
        html.Div(id='plant-type-map-placeholder', style={'flex': '1'})
    ], style={'display': 'flex', 'flexDirection': 'row'}),

])

# callback function to update visualizations based on selected year
@callback(
    [Output('map-visualization-placeholder', 'children'),
     Output('bar-chart-placeholder', 'children'),
     Output('plant-type-map-placeholder', 'children')],
   [Input('year-dropdown', 'value')]
)

def update_visualizations(selected_year):
    """Update the visualizations based on the selected year."""
    df_diff = prepare_data_for_bubble_map(df_from_db, selected_year, PLANT_TYPE_COLOR)

    if selected_year is not None:
        # Generate visualizations based on the selected year
        bubble_map_fig = bubble_map(df_diff,PLANT_TYPE_COLOR)
        bar_chart_fig = bar_chart(df_filtered, sorted_fuel_types, PLANT_TYPE_COLOR)
        plant_type_map_fig = generate_plant_type_map(df_from_db,PLANT_TYPE_COLOR)

        # Update and return figures
        bar_chart_fig.update_layout(legend=dict(x=0, y=1.0, bgcolor='rgba(255,255,255,0.5)'))

    return dcc.Graph(figure=bubble_map_fig), dcc.Graph(figure=bar_chart_fig), dcc.Graph(figure=plant_type_map_fig)