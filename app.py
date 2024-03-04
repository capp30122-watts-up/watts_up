import dash
from dash import Dash, html, page_container, dcc
import dash_bootstrap_components as dbc
'''
'''

app = Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           use_pages=True,
           suppress_callback_exceptions=True)
app.title = 'Watts_Up'

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Analysis", href="/analysis", active="exact", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Prediction", href="/prediction", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Predict", href="/predict", style={'font-weight': 'bold'})),
    ],
    brand="Watts Up",
    brand_href="/",
    sticky="top",
    color="#4CAF50",
    dark=True,
)

app.layout = html.Div([
	dbc.Container([
        # Header
	    html.H1(children='Watts Up',
	        style={'textAlign': 'left', 'color': '#4CAF50', 'font-size': '40px', 'font-weight': 'bold'}),

        html.Div(children='"E-Grid data represented"',
            style={'textAlign': 'left', 'color': 'black', 'font-size': '20px', 'font-style': 'italic'}),

        # Navigation bar
        html.Div(navbar),
        html.Br(),
        html.P(style={'textAlign': 'right', 'color': 'black', 'font-size': '12px'}),

        #Pages from the pages will be rendered here
        page_container,

    ]) # End of container
])

if __name__ == '__main__':
    app.run(debug=True)
