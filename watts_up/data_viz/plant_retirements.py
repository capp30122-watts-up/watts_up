import numpy as np
import pandas as pd
from dash import html, dcc, dash_table, page
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from pathlib import Path
from watts_up.data_viz.helper import df_load


def retirement_load_and_preprocess_data():
    df = df_load("plants")
    df['total_gen_capacity'] = df['plgenacl'] + df['plgenaol'] + df['plgenags'] + df['plgenaof']
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['total_gen_capacity'] = pd.to_numeric(df['total_gen_capacity'], errors='coerce')
    print("DataFrame shape:", df.shape)  # Print the shape of the DataFrame
    unique_years = df['year'].unique()
    print("Unique years:", unique_years)
    unique_years.sort()

    return df, unique_years