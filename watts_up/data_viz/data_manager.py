'''Loads, preprocesses, and categorizes energy production data from a database, to
ensures that the data is consistently processed and categorized across the project.

Author: Frank Vasquez

'''

from watts_up.data_viz.helper import load_and_preprocess_data, plant_type
from watts_up.util.util import  WANTED_COLUMNS

# Load and preprocess the data once, making it globally accessible
df_from_db, unique_years = load_and_preprocess_data("plants")
df_from_db = plant_type(df_from_db, WANTED_COLUMNS)