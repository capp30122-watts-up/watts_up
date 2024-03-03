import dash
from dash import html, dcc, page, register_page
import pandas as pd
import plotly.express as px

dash.register_page(__name__)

# Define a function to load and preprocess data, then generate the figure
def load_data_and_create_figure():
    data = pd.read_csv('watts_up/data_viz/place_holder_predictions.csv')

    predictable_data = data[data['predicted_year'] != 'Not predictable'].copy()
    predictable_data['predicted_year'] = pd.to_numeric(predictable_data['predicted_year'], errors='coerce')

    not_predictable_states = data[data['predicted_year'] == 'Not predictable']['state_id'].tolist()

    not_predictable_notice = "Note: Predictions are not available for the following states: " + ", ".join(not_predictable_states) + "."

    fig = px.scatter(predictable_data, x='state_id', y='predicted_year', color='statistically_significant',
                     title='Predicted Year to Reach 60% Renewable Energy by State',
                     labels={'state_id': 'State', 'predicted_year': 'Predicted Year'},
                     color_discrete_map={'Yes': 'blue', 'No': 'red'})
    return fig, not_predictable_notice

# Use the function to create the figure and notice
fig, not_predictable_notice = load_data_and_create_figure()

# Set the page layout
layout = html.Div([
    html.H1("Renewable Energy Predictions"),
    dcc.Graph(id='scatter-plot', figure=fig),
    html.P(not_predictable_notice)
])
