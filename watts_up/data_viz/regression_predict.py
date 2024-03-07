'''
This script will use linear regression to predict when states will
reach a specified percentage of renewable energy.

Author:
    Praveen Chandar Devarajan
'''

import pandas as pd
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import sqlite3

DB_NAME = "plants" #Enter new DB name if changed

def connect_database(db_name):
    """
    Connect to the SQLite database.
    Input:
        Name of the database
    Returns:
        Database connection object.
    """
    conn = sqlite3.connect(f'watts_up/data/final_data/{db_name}.db')
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
    #grouping data by state to run regression
    grouped_data = data.groupby('state_id')
    for state, state_data in grouped_data:
        if state_data["Percentage_Renewable"].iloc[-1] < percent_required:
            # currently the testing data is not utilized, but can be for a 
            # future iteration
            train_data, _ = train_test_split(state_data,\
                                                      test_size=0.2,\
                                                        random_state=100)
            X_train = train_data[['Percentage_Renewable']]
            y_train = train_data['year']
            X_train = sm.add_constant(X_train)
            #Linear regression (year ~ Percentage_Renewable + E)
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
                #This handles the case where the data is not varying enough to 
                #make predictions- so the prediction gives non-sensical years
                statistically_significant = 'Yes' if p_value < 0.05 else 'No'
                predicted_year = 'Not predictable'
                results.append({'state_id': state, 'predicted_year': \
                                predicted_year,
                                'statistically_significant': \
                                statistically_significant})
        else:
            #Case when the state is already there at the given percent
            results.append({'state_id': state, 'predicted_year': \
                            'Already there!',
                            'statistically_significant': \
                            statistically_significant})

    results_df = pd.DataFrame(results)
    results_df.to_csv('watts_up/data/final_data/predictions.csv')
    print("prediction works")

def run_prediction(percent_required):
    """
    Run the renewable energy prediction.

    Args:
        data (pd.DataFrame): Input DataFrame.
        percent_required (float): Desired percentage of renewable energy.
    """
    db_name = DB_NAME
    conn = connect_database(db_name)
    data_prediction = query_totgen(conn)
    prepped_df = prediction_data_prep(data_prediction)
    predict_renewable_energy(prepped_df, percent_required)

