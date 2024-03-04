'''
Sets up the Dash application and its layout containing anavigation bar and 
page container for multi-page navigation.

Author: Frank Vasquez
'''

import dash
from dash import Dash, html, page_container, dcc
import dash_bootstrap_components as dbc


app = Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           use_pages=True,
           suppress_callback_exceptions=True)
app.title = 'Watts_Up'

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Analysis", href="/analysis", active="exact", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Trends", href="/prediction", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Predict", href="/predict", style={'font-weight': 'bold'})),
    ],
    brand="CAPP-30122 Project -  E-Grid Data Visualized",
    brand_href="/",
    sticky="top",
    color="darkgreen",
    dark=True,
)

app.layout = html.Div([
	dbc.Container([
	    html.H1(children='Watts Up',
	        style={'textAlign': 'left', 'color': 'darkgreen', 'font-size': '40px', 'font-weight': 'bold'}),

        html.Div(children='',
            style={'textAlign': 'left', 'color': 'black', 'font-size': '20px', 'font-style': 'italic'}),

        html.Div(navbar),
        html.Br(),
        html.P(style={'textAlign': 'right', 'color': 'black', 'font-size': '12px'}),

        page_container, ]) 
])

