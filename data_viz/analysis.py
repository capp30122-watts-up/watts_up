import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from ..data_viz.plant_retirements import retirement_load_and_preprocess_data

dash.register_page(__name__)

df_from_db, unique_years = retirement_load_and_preprocess_data()

layout = html.Div([
    html.H1('Analysis Page'),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in unique_years],
        value=unique_years[0]  
    ),
    html.Div(id='visualizations-placeholder'),
])

@app.callback(
    Output('visualizations-placeholder', 'children'),
    [Input('year-dropdown', 'value')]
)
def update_visualizations(selected_year):
    selected_year = int(selected_year)
    df_previous_and_selected = df_from_db[df_from_db['year'].isin([selected_year - 1, selected_year])]

    df_grouped = df_previous_and_selected.groupby(['pname', 'year'])['total_gen_capacity'].sum().reset_index()
    df_diff = df_grouped.pivot(index='pname', columns='year', values='total_gen_capacity')
    df_diff['change'] = df_diff[selected_year] - df_diff.get(selected_year - 1, 0)

    df_locations = df_from_db[['pname', 'lon', 'lat']].drop_duplicates(subset='pname')
    df_diff = df_diff.reset_index().merge(df_locations, on='pname', how='left')

    bubble_map = go.Figure()
    df_diff['change'] = df_diff['change'].fillna(0)
    max_change = max(np.abs(df_diff['change'])) + 1e-9
    sizes = np.abs(df_diff['change']) / max_change * 50
    df_diff['lon'] = df_diff['lon'].fillna(0)

    bubble_map.add_trace(go.Scattergeo(
        lon=df_diff['lon'],
        lat=df_diff['lat'],
        text=df_diff['pname'] + ': ' + df_diff['change'].astype(str) + ' MW',
        marker=dict(
            size=sizes,
            color=np.sign(df_diff['change']),
            colorscale=['red', 'blue'],
            sizemode='area',
            line_width=0.5,
            opacity=0.7
        ),
        name='Year-over-Year Change'
    ))

    bubble_map.update_layout(
        title='Year-over-Year Change in Total Generating Capacity by Plant',
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(217, 217, 217)',
        )
    )

    df_diff_for_table = df_diff[['pname', 'change']].copy()
    df_diff_for_table['change'] = df_diff_for_table['change'].round(2)

    components = [
        dcc.Graph(figure=bubble_map),
        html.H4('Year-over-Year Change in Generating Capacity by Plant', style={'marginTop': '30px'}),
        dcc.DataTable(
            data=df_diff_for_table.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df_diff_for_table.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'minWidth': '100px', 'width': '100px', 'maxWidth': '100px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
            page_size=10
        )
    ]
    return components