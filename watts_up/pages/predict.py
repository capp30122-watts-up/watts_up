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


    not_predictable_states = data[data['predicted_year'] == 'Not predictable']['state_id'].tolist()
    not_predictable_notice = "Note: Some states have already reached the level \
        and predictions are not available for the following states: " + ", ".join(not_predictable_states) + "."

    fig = px.choropleth(predictable_data, 
                        locations='state_id', 
                        locationmode='USA-states', 
                        color='predicted_year',
                        color_continuous_scale='Reds',
                        #color_continuous_midpoint=20,
                        title='Predicted Year to Reach 60% Renewable Energy by State',
                        labels={'predicted_year': 'Predicted Year'})

    # Adjust the layout for better readability
    fig.update_layout(geo=dict(scope='usa', showlakes=True, lakecolor='rgb(255, 255, 255)'),
                      xaxis_title="State",
                      yaxis_title="Predicted Year",
                      plot_bgcolor="white",
                      transition={'duration': 50}, 
                      xaxis=dict(showline=True, showgrid=False, linecolor='black'),
                      yaxis=dict(showgrid=True, gridcolor='lightgrey'),
                      )

    fig.update_xaxes(tickangle=45)

    # Set the range of the color scale to cover the predicted years
    fig.update_coloraxes(colorbar=dict(title='Predicted Year'))


    return html.Div([
        html.H1("Renewable Energy Predictions Map"),
        dcc.Graph(id='choropleth-map', figure=fig),
        html.P(not_predictable_notice)
    ])


layout = create_renewable_energy_dash_component()