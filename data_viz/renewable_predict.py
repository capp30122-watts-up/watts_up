import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc



file_path = 'place_holder_predictions.csv'
data = pd.read_csv(file_path)

predictable_data = data[data['predicted_year'] != 'Not predictable'].copy()
predictable_data['predicted_year'] = pd.to_numeric(predictable_data['predicted_year'], errors='coerce')

not_predictable_states = data[data['predicted_year'] == 'Not predictable']['state_id'].tolist()

not_predictable_notice = "Note: Predictions are not available for the following states: " + ", ".join(not_predictable_states) + "."

fig = px.scatter(predictable_data, x='state_id', y='predicted_year', color='statistically_significant',
                 title='Predicted Year to Reach 60% Renewable Energy by State',
                 labels={'state_id': 'State', 'predicted_year': 'Predicted Year'},
                 color_discrete_map={'Yes': 'blue', 'No': 'red'})

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Renewable Energy Predictions"),
    dcc.Graph(id='scatter-plot', figure=fig),
    html.P(not_predictable_notice)
])

if __name__ == '__main__':
    app.run_server(debug=True)
