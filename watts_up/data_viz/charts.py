"""
Helper scripts for creating treemap and line chart for the trends page.

Author:
Praveen Chandar Devarajan
"""

import plotly.express as px

def create_line_chart(counts, plant_typesplotting):
    """
    Create a line chart. This function doesnt clean or prepare the data. 

    Inputs:
        counts (pd.DataFrame): DataFrame containing data for the line chart.
        The dataframe has sto have % of total energy production per plant type.
        plant_typesplotting (list): List of plant types for plotting.

    Returns:
        Line chart figure.
    """
    fig = px.line(counts, x='year', y='percentage', color='plant_type',
                  markers=True, line_shape='linear',
                  category_orders={'plant_type': plant_typesplotting},
                  color_discrete_sequence=px.colors.qualitative.G10)
    
    # Update layout settings for the chart
    fig.update_layout(title='Dependency on coal plants for total energy production has decreased from 52% to 21% <br>But gas is still very prevalent',
                      xaxis_title='Year',
                      yaxis_title='Percentage (%) of the total energy mix',
                      legend_title='Plant FUEL Type',
                      yaxis=dict(tickformat=""),
                      plot_bgcolor='white',
                      xaxis=dict(
                          showline=True,
                          showgrid=False,
                          showticklabels=True,
                          linecolor='black',
                          linewidth=2,
                          ticks='outside',
                          tickfont=dict(
                              family='Arial',
                              size=12,
                              color='black',
                          )),
                      width=1100,
                      height=600)

    return fig

def create_treemap(raw_df, plant_type, year):
    """
    Create a treemap. This function also performs some basic data grouping.

    Inputs:
        raw_df (pd.DataFrame): Input DataFrame.
        plant_type (str): Plant type for filtering.
        year (int): Year for filtering.

    Returns:
        Treemap figure.
    """
    grouped_data = raw_df.groupby(['year', 'state_id', 'plant_type']).size()\
        .reset_index(name='count')
    
    # Filter data for the specified plant_type and year
    given_typedf = grouped_data[(grouped_data['plant_type'] == plant_type)\
                                 & (grouped_data['year'] == year)]
    fig = px.treemap(given_typedf,
                     path=['state_id'],
                     values='count',
                     title=f'{plant_type} Plants in {year} by State',
                     color='count',
                     color_continuous_scale='Viridis',
                     hover_data=['count','state_id'])
    
    # Calculate and add total count annotation to the chart
    total_count = given_typedf['count'].sum()

    fig.add_annotation(
        x=0.5,
        y=.96,
        text=f'Total: {total_count}',
        showarrow=True,
        font=dict(size=25)
    )
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=100),  
    )

    return fig