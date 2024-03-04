'''
This script is used to gather, clean, and load the data into a sqlite database
Author: Jacob Trout
'''

from watts_up.data_processing.extract_data.import_data import fetch_electricity_data, import_PLNT_sheet_data
from watts_up.data_processing.clean_data.clean_data import clean_plant_data, clean_price_data, clean_gdp_data, clean_pop_data
from watts_up.data_processing.load_data.make_db import makedb

def run_etl():
    # Import Data
    fetch_electricity_data()
    import_PLNT_sheet_data()

    # Clean Data
    clean_plant_data()
    clean_price_data()
    clean_gdp_data()
    clean_pop_data()

    # Load Database
    makedb()



