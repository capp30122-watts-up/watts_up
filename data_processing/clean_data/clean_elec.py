import json
import pandas as pd

pd_list = []
data_list = []
with open("api_responses.json", "r") as file:
    responses = json.load(file)

for response in responses:
    data_list += [response['response']['data']]

for sublist in  data_list:
    for dict in sublist:
        pd_list += [dict]
cleaned_df = pd.DataFrame(pd_list)

cleaned_df['period'] = pd.to_datetime(cleaned_df['period'], format='%Y')
cleaned_df['year'] = cleaned_df['period'].dt.year
cleaned_df['year_state'] = cleaned_df['year'].astype(str) + '_' + cleaned_df['stateid'].astype(str)
cleaned_df = cleaned_df.drop(columns = ["price-units", "sectorName", "stateDescription","period"])

cleaned_df['stateid'] = cleaned_df['stateid'].astype(str)  
cleaned_df['sectorid'] = cleaned_df['sectorid'].astype(str)  
cleaned_df['price'] = pd.to_numeric(cleaned_df['price'], errors='coerce')

df_pivoted = cleaned_df.pivot_table(index=['stateid', 'year', 'year_state'],\
                                     columns='sectorid', values='price').\
                                        reset_index()
df_pivoted.rename(columns={'ALL': 'price_all', 'COM': 'price_com', 'IND': \
                           'price_ind', 'RES': 'price_res'}, inplace=True)
df_pivoted.columns.name = None

json_data = df_pivoted.to_json(orient='records')

with open("cleaned_api_responses.json", "w") as file:
    file.write(json_data)