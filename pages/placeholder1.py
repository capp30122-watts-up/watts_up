import dash
from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd

dash.register_page(__name__)



# Example data (replace this with your actual dataframe)
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

# Define the layout of the app
app.layout = html.Div([
    dcc.Graph(id='stacked-area-chart'),
])

@app.callback(
    Output('stacked-area-chart', 'figure'),
    Input('stacked-area-chart', 'id')  # This input is not used, it's just to trigger the callback
)
def update_graph(_):
    # Create the figure
    fig = go.Figure()

    # Adding each trace
    for column in df.columns[1:]:
        fig.add_trace(go.Scatter(
            x=df['Year'],
            y=df[column].cumsum(),  # Assuming you want to stack the values
            hoverinfo='x+y',
            mode='lines',
            stackgroup='one',  # Define stack group
            name=column
        ))

    # Update layout
    fig.update_layout(
        title='Energy Source Shares in United States Electricity Generation, 1920-2021',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Percentage', tickformat='%'),
        showlegend=True,
    )

    return fig