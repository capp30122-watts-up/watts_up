'''
This script creates a Dash component visualizing 
the predicted year each state will reach 60% renewable energy.

Author: Praveen Chandar + Frank Vasquez

'''
import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc

dash.register_page(__name__)

def create_renewable_energy_dash_component():
    '''
    Returns:
        A Dash HTML Div component containing the visualization and a note on states without predictions.
    
    '''
    data = pd.read_csv('watts_up/data_viz/place_holder_predictions.csv')

    predictable_data = data[data['predicted_year'] != 'Not predictable'].copy()
    predictable_data['predicted_year'] = pd.to_numeric(predictable_data['predicted_year'], errors='coerce')

    not_predictable_states = data[data['predicted_year'] == 'Not predictable']['state_id'].tolist()
    not_predictable_notice = "Note: Predictions are not available for the following states: " + ", ".join(not_predictable_states) + "."

    fig = px.bar(predictable_data, x='state_id', y='predicted_year',
                 title='Predicted Year to Reach 60% Renewable Energy by State',
                 labels={'state_id': 'State', 'predicted_year': 'Predicted Year'})

   
    fig.update_layout(xaxis_title="State",
                      yaxis_title="Predicted Year",
                      plot_bgcolor="white",
                      xaxis=dict(showline=True, showgrid=False, linecolor='black'),
                      yaxis=dict(showgrid=True, gridcolor='lightgrey'),
                      )
    fig.update_xaxes(tickangle=45)

    ## Adjust y-axis range
    max_year = predictable_data['predicted_year'].max()
    fig.update_yaxes(range=[2024, max_year + 1])

    return html.Div([
        html.H1("Renewable Energy Predictions"),
        dcc.Graph(id='bar-chart', figure=fig),
        html.P(not_predictable_notice)
    ])


layout = create_renewable_energy_dash_component()