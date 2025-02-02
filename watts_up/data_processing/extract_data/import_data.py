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



def fetch_electricity_data(url, params):
    """
    Fetches electricity retail sales data from the U.S. 
    Energy Information Administration (EIA) API.

    Args:
        url (str): The URL of the EIA API for fetching electricity 
        retail sales data.
        params (dict): The parameters to be included in the API request,
          including offset and length.

    Returns:
        None: The fetched data is saved to a JSON file, and the
          function does not return a value.
    """
    
    output_dir = (pathlib.Path(__file__).parent.parent.parent / 
                  "data/intermediate_data")
    output_file = output_dir / "api_responses.json"

    def fetch_page(offset):
        
        params["offset"] = offset
        response = requests.get(url, params = params)
        if response.status_code == 200:
            return response.json()
        
        # API request failure (non-200 status code)
        print(f"API request failed with status code {response.status_code}.")
        return None

    offset = 0
    responses =[]

    # fetch pages of data until all records are retrieved
    while True:
        page_data = fetch_page(offset)
        if page_data:
            responses.append(page_data)
            total_records = int(page_data["response"]["total"])
            if total_records <= offset + params["length"]:
                break
            else:
                offset += params["length"]
        else:
            print("Exiting due to API request failure.")
            break
    
    with open(output_file, "w") as file:
        json.dump(responses, file)

def import_PLNT_sheet_data():
    """
    This function loads the data in the Excel files from the egrid_data folder
    and returns a json where the keys are filenames and the values are
    corresponding jsons contain the file's data.
    """
    folder_path = str(pathlib.Path(__file__).parent.parent.parent /
                       "data/raw_data/egrid_data")
    output_dir = pathlib.Path(__file__).parent.parent.parent / "data/intermediate_data"
    output_file = output_dir / "plant_data.json"

    # convert all plant data in each excel to pandas files in a dicitonary
    dfs = {}
    for file in os.listdir(folder_path):
        filename = folder_path + "/" + file
        pattern = r'(?<=20)(\d{2})'
        match = re.findall(pattern, file)
        sheet = "PLNT" + match[0]
        # adjust for different file formats before 2014
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

        # Convert each DataFrame to JSON and store in the dictionary
        json_dataframes = {}
        for key, df in dfs.items():
            json_dataframes[key] = df.to_json()
        # Write the dictionary to a JSON file
        with open(output_file, "w") as json_file:
            json_file.write(json.dumps(json_dataframes, indent=4))
