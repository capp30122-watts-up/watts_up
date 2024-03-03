import requests
import json
import os

url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
api_key = os.environ.get("API_KEY")


#params format and the values example provided in the website
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


with open("api_responses.json", "w") as file:
    json.dump(responses, file)