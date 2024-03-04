import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import plotly.express as px
import dash
from dash import html, dcc,callback,Input,Output
from watts_up.data_viz.charts import create_line_chart,create_treemap

#used to label each row to a fuel type
#(Coal vs gas vs solar based on raw data column name)
COLUMNS_CHECK = ['plgenacl', 'plgenags', 'plgenanc', 'plgenawi',
                    'plgenaso', 'plgenaol', 'plgenagt', 'plgenabm',
                    'plgenaof', 'plgenahy', 'plgenaop']
COLUMNS_WANTED = {'plgenacl': "COAL", 'plgenags': "GAS", 'plgenanc': "NUCLEAR",
                    'plgenawi': "WIND", 'plgenaso': "SOLAR"}

#The percentage input for predicting when states will hit x% renewable mix
PREDICT_PERCENT = 60
#fuel types considered for the charts
PLANT_PLOTTING = ['GAS', 'NUCLEAR', 'COAL', 'WIND', 'SOLAR']

dash.register_page(__name__)

def connect_database():
    """
    Connect to the SQLite database.

    Returns:
        sqlite3.Connection: Database connection object.
    """
    conn = sqlite3.connect('watts_up/data/final_data/plants.db')
    return conn

def query_totgen(conn):
    """
    Query total generation data from the database.

    Args:
        conn (sqlite3.Connection): Database connection object.

    Returns:
        pd.DataFrame: DataFrame containing total generation data.
    """
    query = '''
        SELECT p.year_state, p.year, p.state_id, p.plfuelct,
        sum(p.PLGENATN) as total_non_renew_gen, sum(p.PLGENATR) as total_renew_gen
        FROM plants p
        GROUP BY p.year_state, p.year;
    '''
    data = pd.read_sql_query(query, conn)
    return data

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

def clean_label(df):
    """
    Clean labels for plant types based on which of the energy columns has a 
    non zero value. For example, if plgenacl >0 the row will be labelled 'COAL'

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with cleaned plant type labels.
    """

    df['plant_type'] = ''

    for index, row in df.iterrows():
        label = 'OTHER'

        for col in COLUMNS_CHECK:
            if row[col] > 0:
                label = COLUMNS_WANTED.get(col, 'OTHER')
                break

        df.at[index, 'plant_type'] = label

    return df

def prep_line_chart(df):
    """
    Prepare data for a line chart.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing prepared data for the line chart.
    """
 
    df = clean_label(df)

    df['total_generation'] = df["renew_gen"] + df["non_renew"]
    df['total_generation_year'] = df.groupby('year')['total_generation'].transform('sum')

    counts = df.groupby(['year', 'plant_type'])['total_generation'].\
        sum().reset_index(name = 'total_generation_plant_type')
    counts['percentage'] = (counts['total_generation_plant_type'] /\
                             counts.groupby('year')['total_generation_plant_type'].transform('sum')) * 100
    return counts

def prediction_data_prep(data):
    """
    Prepare data for renewable energy prediction.

    Args:
        data (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing prepared data for prediction.
    """

    data["total_generation"] = data["total_renew_gen"] + \
    data["total_non_renew_gen"]

    data["Percentage_Renewable"] = (data["total_renew_gen"] / \
                                   data["total_generation"]) * 100
    data["Percentage_NonRenewable"] = (data["total_non_renew_gen"] / \
                                      data["total_generation"]) * 100
    #removing puerto rico for prediction analysis
    data = data[data['state_id'] != 'PR']

    return data

def predict_renewable_energy(data, percent_required):
    """
    Predict when states will hit %share of renewable energy in
    total energy.

    Args:
        data (pd.DataFrame): Input DataFrame (cleaned and columns added).
        percent_required (float): Desired percentage of renewable energy.

    Returns:
        pd.DataFrame: DataFrame containing prediction results.
    """
    results = []

    grouped_data = data.groupby('state_id')
    for state, state_data in grouped_data:
        if state_data["Percentage_Renewable"].iloc[-1] < percent_required:
            train_data, _ = train_test_split(state_data,\
                                                      test_size=0.2,\
                                                        random_state=100)
            X_train = train_data[['Percentage_Renewable']]
            y_train = train_data['year']
            X_train = sm.add_constant(X_train)
            model = sm.OLS(y_train, X_train).fit()
            p_value = model.pvalues['Percentage_Renewable']
            predicted_year = round(model.predict([1, percent_required])[0])
            statistically_significant = 'Yes' if p_value < 0.05 else 'No'
            current_year = pd.to_datetime('today').year

            if predicted_year >= current_year:
                statistically_significant = 'Yes' if p_value < 0.05 else 'No'
                results.append({'state_id': state, 'predicted_year': \
                                int(predicted_year),
                                'statistically_significant': \
                                statistically_significant})
            else:
                statistically_significant = 'Yes' if p_value < 0.05 else 'No'
                predicted_year = 'Not predictable'
                results.append({'state_id': state, 'predicted_year': \
                                predicted_year,
                                'statistically_significant': \
                                statistically_significant})
        else:
            results.append({'state_id': state, 'predicted_year': \
                            'Already there!',
                            'statistically_significant': \
                            statistically_significant})

    results_df = pd.DataFrame(results)
    results_df.to_csv('watts_up/data/final_data/place_holder_predictions.csv')
    print("everything works")
    return results_df



conn = connect_database()
data_prediction = query_totgen(conn)
data_chart = query_planttypes(conn)
conn.close()

line_chartdf = prep_line_chart(data_chart)
line_chart = create_line_chart(line_chartdf, PLANT_PLOTTING)
predict_df = prediction_data_prep(data_prediction)
predict_renewable_energy(predict_df, PREDICT_PERCENT)

#Layout creation for DASH
layout = html.Div([
    html.H1('Analyzing total energy production by plant category'),
    (dcc.Graph(figure=line_chart)),
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