import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import plotly.express as px
from pathlib import Path
import dash
from dash import html, dcc, callback, Output,Input
import plotly.graph_objects as go
import numpy as np


dash.register_page(__name__)

# Connect to the database
def connect_to_database():
    conn = sqlite3.connect('data/final_data/plants.db')
    return conn

# Query total generation data
def query_total_generation(conn):
    query = '''
        SELECT p.year_state, p.year, p.state_id, p.plfuelct,
        sum(p.PLGENATN) as total_non_renew_gen, sum(p.PLGENATR) as total_renew_gen
        FROM plants p
        GROUP BY p.year_state, p.year;
    '''
    data = pd.read_sql_query(query, conn)
    return data

# Query plant types data
def query_plant_types(conn):
    query = '''
        SELECT p.year_state, p.year, p.state_id,plgenacl, plgenags, plgenanc, plgenawi, \
                            plgenaso, plgenaol, plgenagt, plgenabm,\
                                plgenaof, plgenahy, plgenaop,\
                                      p.PLFUELCT,p.PLGENATN as renew_gen,\
                                        p.PLGENATR as non_renew
        FROM plants p;
    '''
    data2 = pd.read_sql_query(query, conn)
    return data2

def clean_label(df):

    columns_to_check = ['plgenacl', 'plgenags', 'plgenanc', 'plgenawi', \
                            'plgenaso', 'plgenaol', 'plgenagt', 'plgenabm',\
                                'plgenaof', 'plgenahy', 'plgenaop']
    wanted_columns = {'plgenacl': "COAL", 'plgenags': "GAS", 'plgenanc': \
                    "NUCLEAR", 'plgenawi': "WIND", 'plgenaso': "SOLAR"}

    df['plant_type'] = ''

    for index, row in df.iterrows():
        label = 'others'
        
        for col in columns_to_check:
            if row[col] > 0:
                label = wanted_columns.get(col, 'OTHER')
                break

        df.at[index, 'plant_type'] = label

    return df

def prep_line_chart(data2):
    RenewableGeneration = "renew_gen"
    NonRenewableGeneration = "non_renew"
    data2 = clean_label(data2)

    data2['total_generation'] = data2[RenewableGeneration] + \
        data2[NonRenewableGeneration]
    data2['total_generation_year'] = data2.groupby('year')\
        ['total_generation'].transform('sum')

    counts = data2.groupby(['year', 'plant_type'])['total_generation'].\
    sum().reset_index(name='total_generation_plant_type')
    counts['percentage'] = (counts['total_generation_plant_type'] / \
                            counts.groupby('year')['total_generation_plant_type'].\
                                transform('sum')) * 100
    return counts

def create_line_chart(counts, plant_typesplotting):
    fig = px.line(counts, x='year', y='percentage', color='plant_type',\
                   markers=True, line_shape='linear',
                category_orders={'plant_type': plant_typesplotting},
                color_discrete_sequence=px.colors.qualitative.G10)

    fig.update_layout(title='Percentage of Total Plants for Each Plant Type Over the Years',
                    xaxis_title='Year',
                    yaxis_title='Percentage of Total Plants',
                    legend_title='Plant Type',
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
    grouped_data = raw_df.groupby(['year', 'state_id', 'plant_type']).\
        size().reset_index(name='count')
    given_typedf = grouped_data[(grouped_data['plant_type'] == plant_type) \
                                & (grouped_data['year'] == year)]
    fig = px.treemap(given_typedf,
                     path=['state_id'],
                     values='count',
                     title=f'{plant_type} Plants in {year} by State',
                     color='count',
                     color_continuous_scale='Viridis',
                     hover_data=['count'])

    total_count = given_typedf['count'].sum()

    fig.add_annotation(
        x=0.5,
        y=.92,
        text=f'Total: {total_count}',
        showarrow=True,
        font=dict(size=25)
    )

    return fig

def prediction_data_prep(data):
    RenewableGeneration = "total_renew_gen"
    NonRenewableGeneration = "total_non_renew_gen"
    total_generation_column = "total_generation"

    data[total_generation_column] = data[RenewableGeneration] + \
        data[NonRenewableGeneration]

    data["PercentageRenewable"] = (data[RenewableGeneration] / \
                                   data[total_generation_column]) * 100
    data["PercentageNonRenewable"] = (data[NonRenewableGeneration] / \
                                      data[total_generation_column]) * 100
    data = data[data['state_id'] != 'PR']

    return data

def predict_renewable_energy(data, percent_required):
    results = []

    grouped_data = data.groupby('state_id')
    for state, state_data in grouped_data:
        if state_data["PercentageRenewable"].iloc[-1] < percent_required:
            train_data, test_data = train_test_split(state_data,\
                                                     test_size=0.2, random_state=100)
            X_train = train_data[['PercentageRenewable']]
            y_train = train_data['year']
            X_train = sm.add_constant(X_train)
            model = sm.OLS(y_train, X_train).fit()
            p_value = model.pvalues['PercentageRenewable']
            predicted_year = round(model.predict([1, percent_required])[0])
            statistically_significant = 'Yes' if p_value < 0.05 else 'No'
            current_year = pd.to_datetime('today').year

            if predicted_year >= current_year:
                statistically_significant = 'Yes' if p_value < 0.05 else 'No'
                results.append({'state_id': state, 'predicted_year': int(predicted_year),
                                'statistically_significant': statistically_significant})
            else:
                statistically_significant = 'Yes' if p_value < 0.05 else 'No'
                predicted_year = 'Not predictable'
                results.append({'state_id': state, 'predicted_year': predicted_year,
                                'statistically_significant': statistically_significant})
        else:
            results.append({'state_id': state, 'predicted_year': 'Already there!',
                            'statistically_significant': statistically_significant})

    results_df = pd.DataFrame(results)
    results_df.to_csv('place_holder_predictions.csv')
    print("everything works")
    return results_df

def layout():
    conn = connect_to_database()
    data = query_total_generation(conn)
    data2 = query_plant_types(conn)
    conn.close()
    plant_typesplotting = ['GAS', 'NUCLEAR', 'COAL', 'WIND', 'SOLAR']
    
    counts = prep_line_chart(data2)
    line_chart = create_line_chart(counts, plant_typesplotting)

    treemaps = []

    unique_plant_types = ['COAL', 'SOLAR', 'GAS']  

    for year in [2004, 2014, 2022]:
        treemap_dropdown = dcc.Dropdown(
            id=f'treemap-dropdown-{year}',
            options=[{'label': plant_type, 'value': plant_type} for \
                     plant_type in unique_plant_types],
            value=unique_plant_types[0]
        )

        treemap_graph = dcc.Graph(id=f'treemap-{year}')

        treemaps.append(html.Div([
            treemap_dropdown,
            treemap_graph
        ]))


    @callback(
        [Output(f'treemap-{year}', 'figure') for year in [2004, 2014, 2022]],
        [Input(f'treemap-dropdown-{year}', 'value') for year in [2004, 2014, 2022]]
    )
    
    def update_treemaps(*selected_plant_types):
        figures = []

        for year, plant_type in zip([2004, 2014, 2022], selected_plant_types):
            treemap = create_treemap(data2, plant_type, year)
            figures.append(treemap)

        return figures


    percentage = 60
    predict_df = prediction_data_prep(data)
    results_df = predict_renewable_energy(predict_df, percentage)
    layout = html.Div([html.H1('Prediction Page'),
                     html.Div(dcc.Graph(figure=line_chart)),
                     *treemaps,
                     html.Pre(results_df.to_string())])
    return layout
####################
