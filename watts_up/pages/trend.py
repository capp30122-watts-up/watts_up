'''
This script analyzes year-over-year energy production by plant types,creates a
treemap of fuel type based data for a selected year.

Author:
Praveen Chandar Devarajan
'''
import sqlite3
import pandas as pd
import dash
from dash import html, dcc,callback,Input,Output
from watts_up.data_viz.charts import create_line_chart,create_treemap
from watts_up.data_viz.helper import plant_type


#used to label each row to a fuel type
#(Coal vs gas vs solar based on raw data column name)
COLUMNS_CHECK = ['plgenacl', 'plgenags', 'plgenanc', 'plgenawi',
                    'plgenaso', 'plgenaol', 'plgenagt', 'plgenabm',
                    'plgenaof', 'plgenahy', 'plgenaop']
COLUMNS_WANTED = {'plgenacl': "COAL", 'plgenags': "GAS", 'plgenanc': "NUCLEAR",
                    'plgenawi': "WIND", 'plgenaso': "SOLAR"}


#fuel types considered for the charts
PLANT_PLOTTING = ['GAS', 'NUCLEAR', 'COAL', 'WIND', 'SOLAR']

#enter the new database name here if changed.
DB_NAME = "plants"

dash.register_page(__name__)

def connect_database(db_name):
    """
    Connect to the SQLite database.
    Input:
        Name of the database
    Returns:
        sqlite3.Connection: Database connection object.
    """
    conn = sqlite3.connect(f'watts_up/data/final_data/{db_name}.db')
    return conn

def query_planttypes(conn):
    """
    Query plant types data from the database.

    Args:
        conn (sqlite3.Connection): Database connection object.

    Returns:
        pd.DataFrame: DataFrame containing plant types data.
    """
    columns_check_str = ', '.join(COLUMNS_CHECK)
    
    query = f'''
        SELECT p.year_state, p.year, p.state_id, {columns_check_str},
               p.PLFUELCT, p.PLGENATN as renew_gen, p.PLGENATR as non_renew
        FROM plants p;
    '''
    df = pd.read_sql_query(query, conn)
    return df


def prep_line_chart(df):
    """
    Prepare data for a line chart.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing prepared data for the line chart.
    """
    #Use helper function to label the plant into plant_types
    df = plant_type(df,COLUMNS_WANTED)

    df['total_generation'] = df["renew_gen"] + df["non_renew"]
    counts = df.groupby(['year', 'plant_type'])['total_generation'].\
        sum().reset_index(name = 'total_generation_plant_type')
    counts['percentage'] = (counts['total_generation_plant_type'] /\
                             counts.groupby('year')['total_generation_plant_type'].\
                                transform('sum')) * 100
    return counts


db_name = DB_NAME 
conn = connect_database(db_name)
data_chart = query_planttypes(conn)
conn.close()

line_chartdf = prep_line_chart(data_chart)
line_chart = create_line_chart(line_chartdf, PLANT_PLOTTING)


#Layout creation for DASH
layout = html.Div([
    html.H1('Analyzing total energy production by plant category'),
    (dcc.Graph(figure=line_chart)),
    #Drop down for the tree-map, the options are years and plant_types
    dcc.Dropdown(id='type-dropdown',
                 options=[{'label': plant_type, 'value': plant_type}\
                           for plant_type in PLANT_PLOTTING],
                 value='COAL'),
    dcc.Dropdown(id='year-dropdown',
                 options=[{'label': '2004', 'value': 2004}, {'label': '2014',\
                                                              'value': 2014},
                          {'label': '2022', 'value': 2022}],
                 value=2004),
    dcc.Graph(id='treemap-graph')  
])
#dropdown for the treemap - year and fuel type
@callback(
    Output('treemap-graph', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('type-dropdown', 'value')]
)
def update_treemap(selected_year, selected_type):
    return create_treemap(data_chart, selected_type, selected_year)