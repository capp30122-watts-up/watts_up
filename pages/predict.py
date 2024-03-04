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

    fig = px.bar(predictable_data, x='state_id', y='predicted_year',
                 title='Predicted Year to Reach 60% Renewable Energy by State',
                 labels={'state_id': 'State', 'predicted_year': 'Predicted Year'})

    # Adjust the layout for better readability
    fig.update_layout(xaxis_title="State",
                      yaxis_title="Predicted Year",
                      plot_bgcolor="white",
                      xaxis=dict(showline=True, showgrid=False, linecolor='black'),
                      yaxis=dict(showgrid=True, gridcolor='lightgrey'),
                      )
    fig.update_xaxes(tickangle=45)

    # Set the range of the y-axis from 2024 to the maximum predicted year in the data + 1
    max_year = predictable_data['predicted_year'].max()
    fig.update_yaxes(range=[2024, max_year + 1])  # Adjust y-axis range

    # Return a Dash layout component
    return html.Div([
        html.H1("Renewable Energy Predictions"),
        dcc.Graph(id='bar-chart', figure=fig),
        html.P(not_predictable_notice)
    ])


layout = create_renewable_energy_dash_component()