"""
This file is used to clean and format the plant, pricing, gdp, and population 
data to prepare for database creation
Authors: Jacob Trout and Praveen Devarajan 
"""

import pandas as pd
import pathlib
import os
import json
import regex as re
from io import StringIO
from watts_up.util.util import COL_NAMES, STATE_MAPPING_DATA


DATA_DIR_OUTPUT = pathlib.Path(__file__).parent.parent.parent / "data/final_data"
DATA_DIR_INPUT = pathlib.Path(__file__).parent.parent.parent / "data/raw_data/gdp_pop"
STATE_MAPPING = pd.DataFrame(STATE_MAPPING_DATA)

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
    Reads the JSON file containing API responses, extracts relevant data, and
    creates a pandas DataFrame. Then writes the output to a new JSON.
    """
    data_list = []
    pd_list = []

    json_file_path = (
        pathlib.Path(__file__).parent.parent.parent
        / "data/intermediate_data/api_responses.json"
    )
    
    with open(json_file_path, "r") as file:
        responses = json.load(file)

    for response in responses:
        data_list += [response["response"]["data"]]
    # Create a DataFrame
    for sublist in data_list:
        for dict in sublist:
            pd_list += [dict]
    cleaned_df = pd.DataFrame(pd_list)

    # Performing data cleaning- creating year, year_state unique id 
    cleaned_df['period'] = pd.to_datetime(cleaned_df['period'], format="%Y")
    cleaned_df['year'] = cleaned_df['period'].dt.year
    cleaned_df['stateid'] = cleaned_df['stateid'].astype(str)
    cleaned_df['year_state'] = cleaned_df['year'].astype(str)\
          + '_' + cleaned_df['stateid']
    cleaned_df['sectorid'] = cleaned_df['sectorid'].astype(str)

    cleaned_df = cleaned_df.drop(
        columns=["price-units", "sectorName", "stateDescription", "period"])
    cleaned_df["price"] = pd.to_numeric(cleaned_df["price"], errors="coerce")

    #Pivoting df to have unique year_states with multiple price columns
    df_pivoted = cleaned_df.pivot_table\
        (index=["stateid", "year", "year_state"], \
         columns="sectorid", values="price").reset_index()
    
    df_pivoted.rename(columns = \
                      {"ALL": "price_all", "COM": "price_com",\
                        "IND": "price_ind", "RES": "price_res"}, inplace=True)

    df_pivoted.columns.name = None

    # Writing the cleaned data to a json file
    json_data = df_pivoted.to_json(orient="records")

    with open(os.path.join(DATA_DIR_OUTPUT, \
                           "cleaned_api_responses.json"), "w") as file:
        file.write(json_data)


def clean_gdp_data():
    """
    Cleans raw GDP data from a CSV file and writes the cleaned data to a
    JSON file.
    """

    raw_gdp_path = pathlib.Path(DATA_DIR_INPUT) / "gdp.csv"
    raw_gdp = pd.read_csv(raw_gdp_path)

    # Melt DF to convert different columns of state into row values
    melted_df = pd.melt(raw_gdp, id_vars=["Years"], var_name="State",\
              value_name="gdp_2022_prices")
    
    # Map the state ids to state names
    merged_df = (pd.merge(melted_df, STATE_MAPPING,\
                           left_on="State", right_on="state", how="left")
        .drop(columns=["state", "State"])
        .rename(columns={"Years": "year"}))
    
    # Create the year_state unique column for the database
    merged_df["year_state"] = (
        merged_df["year"].astype(str) + "_" + merged_df["stateid"].astype(str))

    # Make the json file
    json_data = merged_df.to_json(orient="records")
    with open(pathlib.Path(DATA_DIR_OUTPUT) / "gdp_numbers.json", "w") as \
                                                                    json_file:
        json_file.write(json_data)


def clean_pop_data():
    """
    Cleans raw population data from CSV files and writes the cleaned data to a
    JSON file.
    """
    pop_2019_path = pathlib.Path(DATA_DIR_INPUT) / "p1.csv"
    pop_2022_path = pathlib.Path(DATA_DIR_INPUT) / "p2.csv"

    #Contaings 2010-2019 population data
    pop_2019 = pd.read_csv(pop_2019_path)
    # Contains 2020-2023 population data
    pop_2022 = pd.read_csv(pop_2022_path)

    def clean_2019(pop_2019):
        """
        Performing all the cleaning activities required for the pop_2019 csv
        """
        # Dropping two columns of 2010 data retaining only one (of 3)
        pop_2019 = pop_2019.drop(columns=["4/1/2010 Census population!!Population",\
                "4/1/2010 population estimates base!!Population"])
        
        #Cleaning up the col-names of the csv and renaming the dfcolumns
        col_names = pop_2019.columns.tolist()
        year_cols = [col_names[0]]
        for column in col_names[1:]:
            # Extracting the four-digit year from the column name using regex
            year_cols.append(re.findall(r"(\d{4})", str(column))[0])
        pop_2019.columns = year_cols
        clean_2019 = pop_2019.rename(columns=\
                                {"Geographic Area Name (Grouping)": "state"})
        return clean_2019
    
    cleaned_2019 = clean_2019(pop_2019)
    # Cleaning pop_2022
    pop_2022["State"] = pop_2022["State"].str.lstrip(".")
    cleaned_2022 = pop_2022.rename(columns={"State": "state"})

    #merging the two population files
    merged_df = pd.merge(cleaned_2019, cleaned_2022, left_on="state",\
                          right_on="state", how="left")
    
    merged_df = merged_df[merged_df["state"] != "Puerto Rico"]
    merged_df = pd.melt(merged_df, id_vars=["state"], var_name="year",\
                         value_name="population")

    #Performing state_state id matching, creating unique column for db
    mapped_df = pd.merge(merged_df, STATE_MAPPING, left_on="state", \
                          right_on="state", how="left")
    mapped_df["year_state"] = \
        mapped_df["year"].astype(str) + "_" + mapped_df["stateid"].astype(str)
    mapped_df = mapped_df.drop(columns=["state"])
    mapped_df["year"] = mapped_df["year"].astype(int)

    #removing 'comma' and storing population as an int
    mapped_df["population"] = mapped_df["population"].\
        str.replace(",", "").astype(int)

    # Make the json file
    json_data = mapped_df.to_json(orient="records")
    with open(os.path.join(DATA_DIR_OUTPUT, "pop_numbers.json"), "w") as\
                                                                     json_file:
        json_file.write(json_data)
