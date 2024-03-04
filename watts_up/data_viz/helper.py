'''
This script contains functions designed to facilitate data processing tasks,
 particularly for handling energy production data by plant types. 

Author: Praveen Chandar Devarajan and Frank Vasquez
'''

import sqlite3
import numpy as np
import pandas as pd

def load_and_preprocess_data(table_name):
    '''
     Parameters:
    - table_name: The name of the table from which to load the data.
    
    Returns:
    - df:  The preprocessed Pandas DataFrame containing the energy production data.
    - unique_years (list): A list of unique years sorted in ascending order, extracted from the data.
    '''
    conn = sqlite3.connect('watts_up/data/final_data/plants.db')
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['other_sources'] = df[['plgenaol', 'plgenagt', 'plgenabm', 'plgenaof', 'plgenahy', 'plgenaop']].sum(axis=1)
    df['total_gen_capacity'] = df['plgenacl'] + df['plgenags'] + df['plgenanc'] + df['plgenawi'] + df['plgenaso'] + df['other_sources']
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['total_gen_capacity'] = pd.to_numeric(df['total_gen_capacity'], errors='coerce')

    unique_years = sorted(df['year'].dropna().unique())

    return df, unique_years

#By Praveen
def plant_type(df, wanted_columns):
    """
    Assigns a plant type to each row in the DataFrame based on the maximum generating capacity.
    
    Parameters:
    - df: Pandas DataFrame containing the data.
    - wanted_columns: A dictionary mapping column names to plant types.
    """

    df['plant_type'] = 'Other'

    for index, row in df.iterrows():
        max_capacity = 0
        max_type = 'Other'
        
        for col, type_name in wanted_columns.items():
            if row[col] > max_capacity:
                max_capacity = row[col]
                max_type = type_name

        df.at[index, 'plant_type'] = max_type
    
    return df


def aggregate_and_rename_power_generation_data(df):
    '''a ggregates yearly power generation data by energy source and renames the columns for clarity.
    Parameters: df -  The Pandas DataFrame containing the energy production data with specific
      columns for each energy source.
    
    Returns:
    - df_grouped_renamed (DataFrame): The aggregated and renamed Pandas DataFrame with yearly sums
      of power generation capacities for each energy source.
    '''
    df_grouped = df.groupby('year').agg({
        'plgenacl': 'sum',
        'plgenags': 'sum',
        'plgenanc': 'sum',
        'plgenawi': 'sum', 
        'plgenaso': 'sum',
        'other_sources': 'sum',
    }).reset_index()

    df_grouped_renamed = df_grouped.rename(columns={
        'plgenacl': 'Coal',
        'plgenags': 'Gas',
        'plgenanc': 'Nuclear',
        'plgenawi': 'Wind',
        'plgenaso': 'Solar',
        'other_sources': 'Other'
    })

    return df_grouped_renamed

#By Frank
def prepare_data_for_bubble_map(df_from_db, selected_year, plant_type_colors):
    '''
        Prepares data for creating a bubble map visualization, showing the change in generating capacity by plant.
        Parameters:

        df_from_db: (df) containing the energy production data, including 
        year, plant name, generation capacity, longitude, latitude, and plant type.

        selected_year (int or str): The year selected for analysis. The function also considers the year 
        prior to the selected year to calculate changes in generating capacity.

        plant_type_colors (dict): A dictionary mapping plant types to specific colors for visualization purposes.
    
        Returns:
        
        df_diff (df): A DataFrame containing the prepared data for each plant, including the change 
        in generating capacity, coordinates for mapping, plant type, bubble size, and color for the visualization.
    '''


    selected_year = int(selected_year)
    df_previous_and_selected = df_from_db[df_from_db['year'].isin([selected_year - 1, selected_year])]

    # Group by plant name and year, then pivot to get a wide-form DataFrame
    df_grouped = df_previous_and_selected.groupby(['pname', 'year'])['total_gen_capacity'].sum().reset_index()
    df_diff = df_grouped.pivot(index='pname', columns='year', values='total_gen_capacity')
    df_diff['change'] = df_diff[selected_year] - df_diff.get(selected_year - 1, 0)

    df_locations = df_from_db[['pname', 'lon', 'lat']].drop_duplicates(subset='pname')
    df_diff = df_diff.reset_index().merge(df_locations, on='pname', how='left')
    df_diff = df_diff.merge(df_from_db[['pname', 'plant_type']].drop_duplicates(), on='pname', how='left')

    # Calculate the size of the bubbles based on the change in generating capacity
    df_diff['change'] = df_diff['change'].fillna(0)
    max_change = max(np.abs(df_diff['change'])) + 1e-9
    df_diff['size'] = np.abs(df_diff['change']) / max_change * 50

    df_diff['color'] = df_diff['plant_type'].map(plant_type_colors)
    df_diff['text'] = df_diff['pname'] + ' (' + df_diff['plant_type'] + '): ' + df_diff['change'].astype(str) + ' MW'

    return df_diff