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

def fetch_electricity_data():
    """
    Fetches electricity retail sales data from the U.S. Energy Information 
    Administration (EIA) API.
    """
    url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
    api_key = os.environ.get("API_KEY")
    output_dir = (pathlib.Path(__file__).parent.parent.parent / 
                  "data/intermediate_data")
    output_file = output_dir / "api_responses.json"

    params = {
        "api_key": api_key,
        "frequency": "annual",
        "data[0]": "price",
        "facets[sectorid][]": ["ALL", "COM", "IND", "RES"],
        "facets[stateid][]": [
            "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE",
            "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY",
            "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT",
            "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY",
            "OH", "OK", "OR", "PA", "RI", "SAT", "SC", "SD",
            "TN", "TX", "UT", "VA", "VT", "WA", "WI",
            "WV", "WY"
        ],
        "start": "2004-01",
        "end": "2023-11",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "sort[1][column]": "stateid",
        "sort[1][direction]": "asc",
        "length": 5000
    }

    def fetch_page(offset):
        params["offset"] = offset
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None

    offset = 0
    responses =[]
    while True:
        page_data = fetch_page(offset)
        if page_data:
            responses.append(page_data)
            total_records = int(page_data["response"]["total"])
            if total_records <= offset + params["length"]:
                break
            else:
                offset += params["length"]
    
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
