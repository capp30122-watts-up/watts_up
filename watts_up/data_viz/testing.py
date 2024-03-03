# # import pandas as pd
# from dash import Dash, dcc, html, Input, Output
# import plotly.express as px 
# import plotly.graph_objects as go


#  add data source here 


# app = Dash(__name__)


#  df = pd.xxxxx add the data source here
# # df = df.groupby(['Year' 'Month', 'State', 'Sector_Id', ' Price' ])[['']].mean()
# # df.reset_index(inplace=True)

# # uses dash to create interactive dashboard

# app.layout = html.Div([
#     html.H1("Retail sales of Electricity", style={'text-align': 'center'}),
#     dcc.Dropdown(id="select_year",
#                  options=[
#                      {"label": "2015", "value": 2001},
#                      {"label": "2016", "value": 2002},
#                      {"label": "2017", "value": 2003}
#                      {"label": "2015", "value": 2004},
#                      {"label": "2016", "value": 2005},
#                      {"label": "2017", "value": 2006}
#                      {"label": "2015", "value": 2007},
#                      {"label": "2016", "value": 2008},
#                      {"label": "2017", "value": 2009},
#                      {"label": "2018", "value": 2010}],
                     
#                  multi=False,
#                  value=2015,
#                  style={'width': "40%"}
#                  ),

#     html.Div(id='output_container', children=[]),
#     html.Br(),
#     dcc.Graph(id='egrid_map', figure={})

# ])

# # Connect the Plotly graphs with Dash Components
# @app.callback(
#     [Output(component_id='output_container', component_property='children'),
#      Output(component_id='my_bee_map', component_property='figure')],
#     [Input(component_id='select_year', component_property='value')]
# )
# def update_graph(option_slctd):
#     print(option_slctd)
#     print(type(option_slctd))

#     container = "The year chosen by user was: {}".format(option_slctd)

#     dff = df.copy()
#     dff = dff[dff["Year"] == option_slctd]
#     dff = dff[dff["Affected by"] == "Varroa_mites"]

#     # Plotly Express
#     fig = px.choropleth(
#         data_frame=dff,
#         locationmode='USA-states',
#         locations='state_code',
#         scope="usa",
#         color='Pct of Colonies Impacted',
#         hover_data=['State', 'Pct of Colonies Impacted'],
#         color_continuous_scale=px.colors.sequential.YlOrRd,
#         labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
#         template='plotly_dark'
#     )

#     # Plotly Graph Objects (GO)
#     # fig = go.Figure(
#     #     data=[go.Choropleth(
#     #         locationmode='USA-states',
#     #         locations=dff['state_code'],
#     #         z=dff["Pct of Colonies Impacted"].astype(float),
#     #         colorscale='Reds',
#     #     )]
#     # )
#     #
#     # fig.update_layout(
#     #     title_text="Bees Affected by Mites in the USA",
#     #     title_xanchor="center",
#     #     title_font=dict(size=24),
#     #     title_x=0.5,
#     #     geo=dict(scope='usa'),
#     # )

#     return container, fig
