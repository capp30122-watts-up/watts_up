# visit http://127.0.0.1:8050/ in your web browser.

import pandas as pd
import numpy as np
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go



df = pd.read_csv('/Users/frankvasquez/capp30122/project/watts_up/data_viz/egrid_dummy_data.csv')
df1 = df.loc[:, ['YEAR','PLGENACL']]
df1['PLGENACL'] = df1['PLGENACL'].fillna(0)
df_result = df1.groupby(['YEAR'],as_index = False)['PLGENACL'].sum()

app = Dash(__name__)


app.layout = html.Div([
    html.Div(children='Cool data stuff'),

    dcc.Dropdown(df_result['YEAR'], id='drop'),
    html.Div(id='output'),
    dcc.Graph(figure=px.line(df_result, x='YEAR', y='PLGENACL'))
])

if __name__ == '__main__':
    app.run(debug=True)


