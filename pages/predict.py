import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc

# Function to create a Dash component for renewable energy predictions

dash.register_page(__name__)

def create_renewable_energy_dash_component():
    data = pd.read_csv('data_viz/place_holder_predictions.csv')

    predictable_data = data[data['predicted_year'] != 'Not predictable'].copy()
    predictable_data['predicted_year'] = pd.to_numeric(predictable_data['predicted_year'], errors='coerce')

    not_predictable_states = data[data['predicted_year'] == 'Not predictable']['state_id'].tolist()

    not_predictable_notice = "Note: Predictions are not available for the following states: " + ", ".join(not_predictable_states) + "."

    fig = px.scatter(predictable_data, x='state_id', y='predicted_year',
                     title='Predicted Year to Reach 60% Renewable Energy by State',
                     labels={'state_id': 'State', 'predicted_year': 'Predicted Year'}
    )
    # Return a Dash layout component
    return html.Div([
        html.H1("Renewable Energy Predictions"),
        dcc.Graph(id='scatter-plot', figure=fig),
        html.P(not_predictable_notice)
    ])

layout = create_renewable_energy_dash_component()