import numpy as np
import pandas as pd
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go


df = pd.read_csv('/Users/frankvasquez/capp30122/project/watts_up/data_viz/egrid2022_data.csv')

df1 = df.loc[:, ['YEAR', 'PLGENACL', 'PSTATABB', 'LAT', 'LON']]
df1['PLGENACL'] = df1['PLGENACL'].str.replace(',', '').astype(float)
df1['PLGENACL'] = pd.to_numeric(df1['PLGENACL'], errors='coerce')
df1['PLGENACL'] = df1['PLGENACL'].fillna(0)
df_grouped = df1.groupby('PSTATABB')
df_summed = df_grouped['PLGENACL'].sum().reset_index()


choropleth = go.Choropleth(
    locations=df_summed['PSTATABB'],  
    z=df_summed['PLGENACL'].astype(int),  
    locationmode='USA-states',
    colorscale='Blues',
    colorbar_title='Electricity Generation per State (COAL)'
)

fig_choropleth = go.Figure(data=[choropleth])

fig_choropleth.update_layout(
    title_text='2022 State Annual Net Generation (MWh)',
    geo_scope='usa'
)


scattergeo = go.Scattergeo(
    lon=df1['LON'], 
    lat=df1['LAT'], 
    mode='markers',
    marker=dict(
        size=5,
        color='red',
        line_color='black',
        line_width=0.5,
    ),
    text=df1['PSTATABB']
)

fig_scattergeo = go.Figure(data=[scattergeo])

fig_scattergeo.update_layout(
    title_text='Plant Locations',
    geo_scope='usa',  
)
fig_scattergeo.show()
fig_choropleth.show()



