import sqlite3
import pathlib
import pandas as pd
import json
from load_data.schema import schema

OUTPUT_DIR = (pathlib.Path(__file__).parent.parent.parent / "data/final_data")

def makedb():
    """ 
    """

    # save folder path to output directory as string
    folder_path = str(OUTPUT_DIR) + "/"

    # remove database if it exists already
    path = pathlib.Path(OUTPUT_DIR,"plants.db")
    path.unlink()
    # connect to fresh database & create tables
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript(schema())

    #egrid data table
    df = pd.read_csv(folder_path +"cleaned_plant_data.csv")
    df.to_sql('plants', conn, if_exists='replace', index=False)
    print("finished plants table")

    # pricing data table
    with open(folder_path + "cleaned_api_responses.json", "r") as f:
        data = json.load(f)
        for entry in data:
            insert_query = '''
                INSERT INTO elec_table VALUES (?,?,?,?,?,?,?)
            '''
            # Insert data into the table
            c.execute(insert_query, tuple(entry[key] for key in entry.keys()))
    print("finished price table")

    # POP table
    with open(folder_path + "pop_numbers.json", "r") as f:
        data = json.load(f)
        for entry in data:
            insert_query = '''
                INSERT INTO pop_table VALUES (?,?,?,?)
            '''
            # Insert data into the table
            c.execute(insert_query, tuple(entry[key] for key in entry.keys()))
    print("finished pop table")

    # GDP TABLE
    with open(folder_path + "gdp_numbers.json", "r") as f:
        data = json.load(f)
        for entry in data:
            insert_query = '''
                INSERT INTO gdp_table VALUES (?,?,?,?)
            '''
            # Insert data into the table
            c.execute(insert_query, tuple(entry[key] for key in entry.keys()))

    # Commit transaction and close connection
    conn.commit()
    conn.close()
