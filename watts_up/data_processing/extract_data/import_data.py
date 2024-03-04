'''
This file is used to scrape the pricing data and read in the plant level data 
from the raw egrid files
Authors: Jacob Trout and and Praveen Devarajan 
'''

import os
import requests
import json
import pandas as pd
import re
import pathlib



def fetch_electricity_data(url,params):
    """
    Fetches electricity retail sales data from the U.S. Energy Information 
    Administration (EIA) API.

    Returns:
        None: The function writes the fetched data to a JSON file.
    """
    
    def fetch_page(offset):
        params["offset"] = offset
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response
        else:
            return None

    offset = 0
    responses =[]
    while True:
        page_data = fetch_page(offset)
        if page_data:
            responses.append(page_data.json())
            total_records = int(page_data.json()["response"]["total"])
            
            if total_records <= offset + params["length"]:
                break
            else:
                offset += params["length"]
    
    output_dir = (pathlib.Path(__file__).parent.parent.parent / 
                  "data/intermediate_data")

    with open(os.path.join(output_dir, "api_responses.json"), "w") as file:
        json.dump(responses, file)

def import_PLNT_sheet_data():
    """
    This function loads the data in the Excel files from the egrid_data folder
    and returns a dictionary where the keys are file names and the values are
    corresponding Pandas DataFrames.

    Returns:
        A dictionary of Pandas DataFrames.
    """
    folder_path = str(pathlib.Path(__file__).parent.parent.parent /
                       "data/raw_data/egrid_data")

    dfs = {}
    for file in os.listdir(folder_path):
        filename = folder_path + "/" + file
        pattern = r'(?<=20)(\d{2})'
        match = re.findall(pattern, file)
        sheet = "PLNT" + match[0]

        if int(match[0]) < 14:
            if match[0] == "04":
                sheet = "EGRD" + sheet
            df = pd.read_excel(
                filename,
                header=4,
                sheet_name=sheet
            )
        else:
            df = pd.read_excel(
                filename,
                header=1,
                sheet_name=sheet
            )

        df["FILE"] = file

        if 'YEAR' not in df.columns:
            df['YEAR'] = '20' + match[0]

        dfs[file] = df

        json_dataframes = {}
        # Convert each DataFrame to JSON and store in the dictionary
        for key, df in dfs.items():
            json_dataframes[key] = df.to_json()

        output_dir = (pathlib.Path(__file__).parent.parent.parent 
                      / "data/intermediate_data")

        # Write the dictionary to a JSON file
        with open(os.path.join(output_dir, "plant_data.json"), "w") as json_file:
            json_file.write(json.dumps(json_dataframes, indent=4))
