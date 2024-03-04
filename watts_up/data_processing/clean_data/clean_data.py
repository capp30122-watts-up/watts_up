import pandas as pd
import pathlib
import os
import json
import regex as re
from io import StringIO
from watts_up.util.util import COL_NAMES,STATE_MAPPING_DATA


def clean_plant_data():
    """
    This function should load the data in the excel files from egrid_data folder
    and returns a uncleaned Pandas DataFrame

    Returns:
        A dictionary of PandasDataframes
    """
    # Read the JSON file
    output_dir = pathlib.Path(__file__).parent.parent.parent / "data/intermediate_data"
    json_file_path = output_dir / "plant_data.json"

    with open(json_file_path, "r") as json_file:
        json_dataframes = json.load(json_file)

    # Convert JSON data back to DataFrames
    dict_of_dfs = {}
    for key, json_string in json_dataframes.items():
        dict_of_dfs[key] = pd.read_json(StringIO(json_string))

    # Now dfs is your dictionary of DataFrames
    df_all = pd.DataFrame()

    for name, df in dict_of_dfs.items():
        # rename state_id column
        df.rename(columns={"PSTATABB": "state_id"}, inplace=True)
        df["year_state"] = df["YEAR"].astype(str) + "_" + df["state_id"]
        cols_available = [col for col in COL_NAMES if col in df.columns]

        # filter to desired columns that are available in df
        df2 = df[cols_available].copy()
        df_all = pd.concat([df_all, df2], ignore_index=True)

    df_all.columns = df_all.columns.str.lower()
    
    json_data = df_all.to_json(orient="records")

    output_dir = (pathlib.Path(__file__).parent.parent.parent / "data/final_data")

    with open(os.path.join(output_dir, "cleaned_egrid_data.json"), "w") as f:
        f.write(json_data)


def clean_price_data():

    pd_list = []
    data_list = []
    json_file_path = (pathlib.Path(__file__).parent.parent.parent / "data/intermediate_data/api_responses.json")
    with open(json_file_path, "r") as file:
        responses = json.load(file)

    for response in responses:
        data_list += [response['response']['data']]

    for sublist in  data_list:
        for dict in sublist:
            pd_list += [dict]
    cleaned_df = pd.DataFrame(pd_list)
    
    for index, row in cleaned_df.iterrows():
        cleaned_df.at[index, 'period'] = pd.to_datetime(row['period'], format='%Y')
        cleaned_df.at[index, 'year'] = cleaned_df.at[index, 'period'].year
        cleaned_df.at[index, 'year_state'] = f"{cleaned_df.at[index, 'year']}_{row['stateid']}"
        row.stateid = str(row.stateid)
        row.sectorid = str(row.sectorid)
    cleaned_df = cleaned_df.drop(columns = ["price-units", "sectorName", "stateDescription","period"])

    # cleaned_df['stateid'] = cleaned_df['stateid'].astype(str)  
    # cleaned_df['sectorid'] = cleaned_df['sectorid'].astype(str)  
    cleaned_df['price'] = pd.to_numeric(cleaned_df['price'], errors='coerce')

    df_pivoted = cleaned_df.pivot_table(index=['stateid', 'year', 'year_state'],\
                                        columns='sectorid', values='price').\
                                            reset_index()
    df_pivoted.rename(columns={'ALL': 'price_all', 'COM': 'price_com', 'IND': \
                            'price_ind', 'RES': 'price_res'}, inplace=True)
    df_pivoted.columns.name = None

    #Writing the cleaned data to a json file
    json_data = df_pivoted.to_json(orient='records')
    output_dir = (pathlib.Path(__file__).parent.parent.parent / "data/final_data")
    with open(os.path.join(output_dir, "cleaned_api_responses.json"), "w") as file:
        file.write(json_data)



DATA_DIR = (pathlib.Path(__file__).parent.parent.parent / "data/raw_data/gdp_pop")
DATA_DIR_OUTPUT = (pathlib.Path(__file__).parent.parent.parent / "data/final_data")



STATE_MAPPING = pd.DataFrame(STATE_MAPPING_DATA)

def clean_gdp_data():
    raw_gdp_path = pathlib.Path(DATA_DIR) / 'gdp.csv'
    raw_gdp = pd.read_csv(raw_gdp_path)

    melted_df = pd.melt(raw_gdp, id_vars=['Years'], var_name='State', value_name='gdp_2022_prices')
    merged_df = pd.merge(melted_df, STATE_MAPPING, left_on='State', right_on='state', how='left') \
                .drop(columns=['state', 'State']) \
                .rename(columns={"Years": 'year'}) 
    merged_df['year_state'] = merged_df['year'].astype(str) + '_' + merged_df['stateid'].astype(str)

    # Make the json file
    json_data = merged_df.to_json(orient='records')
    with open(pathlib.Path(DATA_DIR_OUTPUT) / 'gdp_numbers.json', 'w') as json_file:
        json_file.write(json_data)

def clean_pop_data():
    pop_2019_path = pathlib.Path(DATA_DIR) / 'p1.csv'
    pop_2022_path = pathlib.Path(DATA_DIR) / 'p2.csv'

    pop_2019 = pd.read_csv(pop_2019_path)
    pop_2022 = pd.read_csv(pop_2022_path)

    # Cleaning pop_2019
    pop_2019 = pop_2019.drop(columns=['4/1/2010 Census population!!Population',\
                                       '4/1/2010 population estimates base!!Population'])
    col_names = pop_2019.columns.tolist()
    year_cols = [col_names[0]]
    for column in col_names[1:]:
        year_cols.append(re.findall(r'(\d{4})', str(column))[0])
    pop_2019.columns = year_cols
    pop_2019 = pop_2019.rename(columns={"Geographic Area Name (Grouping)": 'state'})

    # Cleaning pop_2022
    pop_2022['State'] = pop_2022['State'].str.lstrip('.')
    pop_2022 = pop_2022.rename(columns={"State": 'state'})

    merged_df = pd.merge(pop_2019, pop_2022, left_on='state', right_on='state', how='left')
    merged_df = merged_df[merged_df['state'] != 'Puerto Rico']
    pop_final = pd.melt(merged_df, id_vars=['state'], var_name='year', value_name='population')
    merged_df1 = pd.merge(pop_final, STATE_MAPPING, left_on='state', right_on='state', how='left')
    merged_df1['year_state'] = merged_df1['year'].astype(str) + '_' + merged_df1['stateid'].astype(str)
    merged_df1 = merged_df1.drop(columns=['state'])
    merged_df1['year'] = merged_df1['year'].astype(int)
    merged_df1['population'] = merged_df1['population'].str.replace(',', '').astype(int)
    
    #Make the json file
    json_data = merged_df1.to_json(orient='records')
    with open(os.path.join(DATA_DIR_OUTPUT,"pop_numbers.json"), 'w') as json_file:
        json_file.write(json_data)