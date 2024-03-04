'''
    Creates an animated Dash component visualizing the predicted year by which 
    each state is expected to reach 60% renewable energy.

    Author: Frank Vasquez
'''
import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc

dash.register_page(__name__)

def create_animated_renewable_energy_dash_component():
    '''
    This function loads a dataset from a CSV file containing states and their 
    respective predicted years for achieving 60% renewable energy.

     Returns:
        A Dash HTML containing the animated bar chart
    '''
    data = pd.read_csv('watts_up/data_viz/place_holder_predictions.csv')

    data['predicted_year'] = pd.to_numeric(data['predicted_year'], errors='coerce', downcast='integer')

    not_predictable_states = data[data['predicted_year'].isna()]['state_id'].unique()
    not_predictable_notice = "Note: Predictions are not available for the following states: " + ", ".join(not_predictable_states) + "."

    predictable_data = data.dropna(subset=['predicted_year'])

    # determines minimum and maximum years in the dataset for the animation range
    min_year = data['predicted_year'].min()
    max_year = data['predicted_year'].max()
    min_year = int(min_year)
    max_year = int(max_year)

    frames_data = pd.DataFrame()

    # creates a df  for each year in the range, marking progress towards the goal    
    for year in range(min_year, max_year + 1):
        year_data = predictable_data.copy()
        year_data['display_year'] = year_data['predicted_year'].apply(lambda x: x if x <= year else None)
        year_data['year'] = year
        # Aggregate the data for all frames
        frames_data = pd.concat([frames_data, year_data])
        

    fig = px.bar(frames_data, x='state_id', y='display_year', animation_frame='year',
                 title='Progress Towards 60% Renewable Energy by State',
                 labels={'state_id': 'State', 'display_year': 'Predicted Year'},
                 range_y=[min_year, max_year])

    fig.update_layout(xaxis_title="State",
                      yaxis_title="Predicted Year",
                      plot_bgcolor="white",
                      transition={'duration': 50}, 
                      xaxis=dict(showline=True, showgrid=False, linecolor='black'),
                      yaxis=dict(showgrid=True, gridcolor='lightgrey'),
                      )

    return html.Div([
        html.H1("Renewable Energy Prediction Progress"),
        dcc.Graph(id='animated-bar-chart', figure=fig),
        html.P(not_predictable_notice) 
    ])
# Assign the component to the layout variable for viz
layout = create_animated_renewable_energy_dash_component()