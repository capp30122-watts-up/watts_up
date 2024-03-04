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
            marker_color=bar_color
        ))
    
    layout = go.Layout(
        title='Energy Production by Year and Fuel Type',
        xaxis=dict({'title': 'Year'},
            type='category'),
        yaxis={'title': 'Energy Production (MW)'},
        barmode='stack',
        legend=dict(
            orientation="h",
            x=25,
            y=0.5,
            xanchor='left',
            yanchor='middle'
        )
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
                line_width=0.5,
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

def generate_plant_type_map(df_diff, plant_type_color):
    fig = go.Figure()

    specified_types = ['Gas', 'Coal', 'Fossil', 'Wind', 'Nuclear', 'Solar']
    df_filtered = df_diff[df_diff['plant_type'].isin(specified_types)]

    # Map colors or markers to plant types using the defined mapping
    for plant_type in specified_types:
        df_type_specific = df_filtered[df_filtered['plant_type'] == plant_type]
        color = plant_type_color.get(plant_type, 'grey')
        
        fig.add_trace(go.Scattergeo(
            lon=df_type_specific['lon'],
            lat=df_type_specific['lat'],
            text=df_type_specific['pname'] + ': ' + df_type_specific['plant_type'],
            marker=dict(
                size=10,
                color=color,  # Use the specified color for the plant type
                line=dict(width=0.5, color='rgba(0, 0, 0, 0.5)'),
            ),
            name=plant_type
        ))

    fig.update_layout(
        title_text='Plant Types Distribution',
        title_x=0.5,
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(217, 217, 217)',
        ),
        legend_title_text='Plant Type'
    )

    return fig

