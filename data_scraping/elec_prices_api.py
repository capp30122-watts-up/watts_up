import requests
import pandas as pd

url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
#api_key = #TODO GLOBAL VARIABLE

params = {
    "api_key": api_key,
    "frequency": "monthly",
    "data[0]": "price",
    "facets[sectorid][]": ["ALL", "COM", "IND", "RES"],
    "facets[stateid][]": [
        "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "ENC",
        "ESC", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY",
        "LA", "MA", "MAT", "MD", "ME", "MI", "MN", "MO", "MS", "MT",
        "MTN", "NC", "ND", "NE", "NEW", "NH", "NJ", "NM", "NV", "NY",
        "OH", "OK", "OR", "PA", "PACC", "PACN", "RI", "SAT", "SC", "SD",
        "TN", "TX", "US", "UT", "VA", "VT", "WA", "WI", "WNC", "WSC",
        "WV", "WY"
    ],
    "start": "2001-01",
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
        return response.json()
    else:
        return None

offset = 0
while True:
    page_data = fetch_page(offset)
    
    if page_data:
        print(page_data)

        try:
            if len(page_data["series"]) < params["length"]:
                break
            else:
                offset += params["length"]
        except:
            break
