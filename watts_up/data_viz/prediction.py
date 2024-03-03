
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from pathlib import Path
import matplotlib.pyplot as plt 
import statsmodels.api as sm


db_folder = Path('database')

conn = sqlite3.connect(db_folder / 'plants.db')

query = '''
    SELECT p.year_state, p.year, p.state_id,
    sum(p.PLGENATN) as total_non_renew_gen, sum(p.PLGENATR) as total_renew_gen
    FROM plants p
    GROUP BY p.year_state, p.year;
'''

data = pd.read_sql_query(query, conn)

conn.close()


data = data[data['state_id'] != 'PR']


RenewableGeneration = "total_renew_gen"
NonRenewableGeneration = "total_non_renew_gen"
total_generation_column = "total_generation"
state_column = "state_id"
year_column = "year"

data[total_generation_column] = data[RenewableGeneration] \
    + data[NonRenewableGeneration]


data["PercentageRenewable"] = (data[RenewableGeneration] / \
                               data[total_generation_column]) * 100
data["PercentageNonRenewable"] = (data[NonRenewableGeneration] / \
                                  data[total_generation_column]) * 100

print(data[["year", "state_id", "PercentageRenewable",\
             "PercentageNonRenewable"]])


above60_df = data[data['PercentageRenewable']>60]


above60_df['state_id'].unique()

print("the states which are already above 60 percent",\
      above60_df['state_id'].unique())

grouped_data = data.groupby('state_id')

slopes = {}

def get_slope(state):
    return slopes[state][0]

for state, state_data in grouped_data:
    X = sm.add_constant(state_data[['year']])
    y = state_data['PercentageRenewable']

    model = sm.OLS(y, X).fit()

    slope = model.params['year']
    p_value = model.pvalues['year']
    
    if p_value < 0.05:
        sig = 'Yes'
    else:
        sig = 'No'
    
    slopes[state] = (slope, sig)

top_states = sorted(slopes, key = get_slope, reverse=True)

print("States with the highest improvement in renewable energy:")
for state in top_states[:5]:
    print(f"State {state}: Slope = {slopes[state][0]}, \
          Significance = {slopes[state][1]}")


results = []

grouped_data = data.groupby('state_id')
perc_required = 50 
input_variable = 'PercentageRenewable'
for state, state_data in grouped_data:
    
    if state_data[input_variable].iloc[-1] < perc_required:
        
        train_data, test_data = train_test_split(state_data,\
                                                 test_size=0.2,\
                                                      random_state = 100)
        
        X_train = train_data[[input_variable]]
        y_train = train_data['year']
        X_train = sm.add_constant(X_train)
        
        model = sm.OLS(y_train, X_train).fit()
        
        X_test = sm.add_constant(test_data[[input_variable]])
        y_pred = model.predict(X_test)
        
        p_value = model.pvalues[input_variable]
        predicted_year = round(model.predict([1, input_variable])[0])
        statistically_significant = 'Yes' if p_value < 0.05 else 'No'
        
        current_year = pd.to_datetime('today').year
        if predicted_year >= current_year:
            statistically_significant = 'Yes' if p_value < 0.05 else 'No'
            results.append({'state_id': state, 'predicted_year': int(predicted_year),\
                            'statistically_significant': statistically_significant})
        else:
            statistically_significant = 'Yes' if p_value < 0.05 else 'No'
            predicted_year = 'Not predictable'
            results.append({'state_id': state, 'predicted_year': predicted_year, \
                            'statistically_significant': statistically_significant})
            
    else:
        results.append({'state_id': state, 'predicted_year': 'already reached' ,\
                        'statistically_significant': statistically_significant})


results_df = pd.DataFrame(results)
print(results_df)
results_df.to_csv('place_holder_predictions.csv')
