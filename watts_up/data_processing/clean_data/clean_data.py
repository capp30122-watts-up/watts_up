'''
This file is used to clean and format the plant, pricing, gdp, and population 
data to prepare for database creation
Authors: Jacob Trout and Praveen Devarajan 
'''
import pandas as pd
import pathlib
import os
import json
import regex as re
from io import StringIO
from watts_up.util.util import COL_NAMES, STATE_MAPPING_DATA

DATA_DIR_OUTPUT = (pathlib.Path(__file__).parent.parent.parent / "data/final_data")

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
    with open(os.path.join(DATA_DIR_OUTPUT, "cleaned_egrid_data.json"), "w") as f:
        f.write(json_data)


def clean_price_data():
    """
    Cleans raw price data obtained from API responses stored in a JSON file.
    Reads the JSON file containing API responses, extracts relevant data, and creates a pandas DataFrame.
    Cleans the DataFrame by:
    1. Converting the 'period' column to datetime format and extracting the year.
    2. Creating a new column 'year_state' by combining 'year' and 'stateid' columns.
    3. Dropping unnecessary columns: 'price-units', 'sectorName', 'stateDescription', 'period'.
    4. Converting 'stateid' and 'sectorid' columns to strings.
    5. Converting 'price' column to numeric format.
    6. Pivoting the DataFrame to have 'stateid', 'year', 'year_state' as index and 'sectorid' as columns.
    7. Renaming sectorid columns for better readability: 'ALL' to 'price_all', 'COM' to 'price_com',
       'IND' to 'price_ind', 'RES' to 'price_res'.
    8. Writing the cleaned DataFrame to a new JSON file.
    """
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
    with open(os.path.join(DATA_DIR_OUTPUT, "cleaned_api_responses.json"), "w") as file:
        file.write(json_data)

DATA_DIR = (pathlib.Path(__file__).parent.parent.parent / "data/raw_data/gdp_pop")
STATE_MAPPING = pd.DataFrame(STATE_MAPPING_DATA)

def clean_gdp_data():
    """
    Cleans raw GDP data from a CSV file and writes the cleaned data to a JSON file.
    Reads the raw GDP data from a CSV file, melts it to long format, merges with state mapping,
    drops unnecessary columns, renames columns, and creates a new column 'year_state' by combining
    'year' and 'stateid'. Finally, writes the cleaned DataFrame to a JSON file.
    """
    raw_gdp_path = os.path.join(DATA_DIR, 'gdp.csv')
    raw_gdp = pd.read_csv(raw_gdp_path)

    melted_df = pd.melt(raw_gdp, id_vars=['Years'], var_name='State', value_name='gdp_2022_prices')
    merged_df = pd.merge(melted_df, STATE_MAPPING, left_on='State', right_on='state', how='left')
    merged_df = merged_df.drop(columns=['state','State'])
    merged_df = merged_df.rename(columns={"Years": 'year'})
    merged_df['year_state'] = merged_df['year'].astype(str) + '_' + merged_df['stateid'].astype(str)

    # Make the json file
    json_data = merged_df.to_json(orient='records')
    with open(os.path.join(DATA_DIR_OUTPUT, 'gdp_numbers.json'), 'w') as json_file:
        json_file.write(json_data)

def clean_pop_data():
    """
    Cleans raw population data for the years 2019 and 2022 from CSV files and writes the cleaned data to a JSON file.
    Reads the raw population data from two CSV files, cleans each separately, merges them,
    melts to long format, merges with state mapping, drops unnecessary columns, renames columns,
    creates a new column 'year_state' by combining 'year' and 'stateid', and writes the cleaned DataFrame to a JSON file.
    """
    pop_2019_path = os.path.join(DATA_DIR, 'p1.csv')
    pop_2022_path = os.path.join(DATA_DIR, 'p2.csv')

    pop_2019 = pd.read_csv(pop_2019_path)
    pop_2022 = pd.read_csv(pop_2022_path)

    # Cleaning pop_2019
    pop_2019 = pop_2019.drop(columns=['4/1/2010 Census population!!Population', '4/1/2010 population estimates base!!Population'])
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