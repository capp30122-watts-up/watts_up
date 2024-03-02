from sqlalchemy import create_engine
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

engine = create_engine('sqlite:///data_sources/database/plants.db')

query = '''
    SELECT year_state, year, state_id,
    sum(plngenan) as total_energy, sum(plgenatn) as non_renewable_energy, sum(plgenatr) as renewable_energy
    FROM plants 
    GROUP BY year_state, year;
'''

df = pd.read_sql(query, engine)

# Create a Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Energy Trends by State"),
    dcc.Dropdown(
        id='state-dropdown',
        options=[{'label': state, 'value': state} for state in df['state_id'].unique()],
        value=df['state_id'].unique()[0]
    ),
    dcc.Graph(id='trend-plot')
])

@app.callback(
    Output('trend-plot', 'figure'),
    Input('state-dropdown', 'value')
)

    
def update_plot(selected_state):
    filtered_df = df[df['state_id'] == selected_state]
    long_df = pd.melt(filtered_df, id_vars=['year'], value_vars=['total_energy', 'non_renewable_energy', 'renewable_energy'],
                      var_name='energy_type', value_name='energy_value')
    plot = px.line(long_df, x='year', y='energy_value', color='energy_type', title=f"Energy Trends in {selected_state}")
    return plot

if __name__ == '__main__':
    app.run_server(debug=True)