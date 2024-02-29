import pandas as pd
import sqlite3
import os
import seaborn as sns

conn = sqlite3.connect('data_sources/database/plants.db')
query = """
    SELECT p.year_state, p.year, p.state_id, sum(p.PLCO2AN) as co2, 
    sum(p.PLGENATN) as total_non_renew_gen, sum(p.PLGENATR) as total_renew_gen, 
    o.population, g.gdp_2022_prices as gdp, e.price_all as price
    FROM plants p
    JOIN pop_table o ON p.year_state = o.year_state
    JOIN gdp_table g ON p.year_state = g.year_state 
    JOIN elec_table e ON p.year_state = e.year_state
    GROUP BY p.year_state, p.year;
"""
df = pd.read_sql_query(query, conn)

sorted_df = df.sort_values(by=['year', 'year_state'], ascending=[True, True])

sorted_df["total_gen"] = sorted_df['total_non_renew_gen'] + sorted_df['total_renew_gen']
sorted_df["co2_intensity"] = sorted_df['co2'] / sorted_df['total_gen']
sorted_df["energy_intensity"] = sorted_df['total_gen'] / sorted_df['gdp']
sorted_df["energy_use_per_capita"] = sorted_df['total_gen'] / sorted_df['population']

state_groups = sorted_df.groupby("state_id")

energy_per_cap_scatters = {}
for state, df in state_groups:
    scat = sns.scatterplot(x=df["year"],y=df["energy_use_per_capita"])
    energy_per_cap_scatters[state] = scat
    