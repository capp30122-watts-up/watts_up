'''
This script is used to gather, clean, and load the data into a sqlite database
Author: Jacob Trout
'''

from watts_up.data_processing.extract_data.import_data import fetch_electricity_data, import_PLNT_sheet_data
from watts_up.data_processing.clean_data.clean_data import clean_plant_data, clean_price_data, clean_gdp_data, clean_pop_data
from watts_up.data_processing.load_data.make_db import makedb
from watts_up.util.util import URL, PARAMS
def run_etl():
    """
    This function executes all the functions to complete the full etl process
    and outputs the full SQLite3 database 'plants.db'
    """
    url,params = URL, PARAMS
    # Import Data
    fetch_electricity_data(url,params)
    print("scraping electricity data completed")
    import_PLNT_sheet_data()
    print("ingest plant data completed")

    # Clean Data
    clean_plant_data()
    clean_price_data()
    clean_gdp_data()
    clean_pop_data()
    print("data cleaning completed")

    # Load Database
    makedb()
    print("database created")



