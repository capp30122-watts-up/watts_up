import plotly.graph_objects as go
import pandas as pd
import numpy as np

def bar_chart(df_filtered, sorted_fuel_types, plant_type_colors):
    traces = []
    for fuel_type in sorted_fuel_types:
        bar_color = plant_type_colors.get(fuel_type, '#D3D3D3')
        
        traces.append(go.Bar(
            x=df_filtered['year'],
            y=df_filtered[fuel_type],
            name=fuel_type,
            marker = dict(
                color=bar_color,
                line=dict(color='rgba(0, 0, 0, 0.5)', width=1)  # Add border here
            )
        ))
    
    layout = go.Layout(
        title='Energy Production by Year and Fuel Type (2004 - 2022)',
        xaxis=dict({'title': 'Year'},
            type='category'),
        yaxis={'title': 'Energy Production (MW)'},
        barmode='stack',
        legend=dict(
            orientation="h",
            x=25,
            y=10,
            xanchor='left',
            yanchor='bottom',
        ),
        annotations=[dict(
        x=.4,
        y=-.2,
        xref='paper',
        yref='paper',
        text='Overview: YoY limited fluctuation of total energy production(MW), and increase in renewable energy production',
        font=dict(
            size=14,
            color="black"
        ),
        align='center'
    )] 
)
    
    return go.Figure(data=traces, layout=layout)


def bubble_map(df_diff,plant_type_colors):
    bubble_map = go.Figure()
    
    # Iterate over each unique plant type to ensure it gets added to the legend
    for plant_type in df_diff['plant_type'].unique():
        df_subset = df_diff[df_diff['plant_type'] == plant_type]
        bubble_map.add_trace(go.Scattergeo(
            lon=df_subset['lon'],
            lat=df_subset['lat'],
            text=df_subset['text'],
            marker=dict(
                size=df_subset['size'],
                color=plant_type_colors[plant_type],
                sizemode='area',
                line=dict(width=.2, color='black'),
                opacity=0.7
    ),
            name=plant_type  
        ))
    
    bubble_map.update_layout(
        title_text='Year-over-Year Change in Total Generating Capacity by Plant',
        geo=dict(scope='usa', projection_type='albers usa', showland=True, landcolor='rgb(217, 217, 217)'),
        legend_title_text='Plant Type',
        legend=dict(orientation='h', itemsizing='constant', traceorder='normal', x=0.5, xanchor='center', y=-0.1, yanchor='top')
    )

    return bubble_map


def generate_plant_type_map(df_from_db, plant_type_color):
    years = sorted(df_from_db['year'].unique())
    fig = go.Figure()

    marker_size = 5

    for year in years:
        df_year = df_from_db[df_from_db['year'] == year]

        for plant_type in df_year['plant_type'].unique():
            df_type_specific = df_year[df_year['plant_type'] == plant_type]
            color = plant_type_color.get(plant_type, 'grey')

            fig.add_trace(go.Scattergeo(
                lon=df_type_specific['lon'],
                lat=df_type_specific['lat'],
                text=df_type_specific.apply(lambda row: f"{row['pname']} ({row['plant_type']})", axis=1),
                marker=dict(
                    size=marker_size,
                    color=color,
                    line=dict(width=0.5, color='rgba(0, 0, 0, 0.5)')
                ),
                name=plant_type,  
                visible=(year == years[0])
            ))
    #slider
    steps = []
    for i, year in enumerate(years):
        step = dict(
            method="update",
            args=[{"visible": [(year == y) for y in years for _ in df_year['plant_type'].unique()]}],
            label=str(year)
        )
        steps.append(step)

    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Year: "},
        steps=steps,
    )]

    fig.update_layout(
        sliders=sliders,
        title_text='Plant Locations by Type',
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(217, 217, 217)',
            countrycolor="RebeccaPurple",
        ),
        legend_title_text='Plant Type',
        legend=dict(traceorder='normal')
    )
    fig.for_each_trace(
        lambda trace: trace.update(showlegend=(trace.name in df_from_db['plant_type'].unique()))
    )

    return fig
