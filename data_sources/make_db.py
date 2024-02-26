import sqlite3
import pathlib
import os
import pandas as pd
import json

def schema():
    """ Return current version of schema. """
    
    return """
    CREATE TABLE plants (
        id INTEGER PRIMARY KEY,
        year TEXT,
        year_state TEXT,
        state_id TEXT,
        file TEXT,
        pname TEXT,
        orispl REAL,
        oprname TEXT,
        oprcode INTEGER,
        utlsrvnm TEXT,
        nerc TEXT,
        subrgn TEXT,
        srname TEXT, 
        fipsst TEXT,
        fipscnty TEXT, 
        cntyname TEXT, 
        lat REAL, 
        lon REAL,
        plprmfl TEXT, 
        plfuelct TEXT,
        coalflag TEXT,
        capfac TEXT,
        namepcap TEXT,
        plngenan TEXT,
        plco2an TEXT, 
        plgenacl TEXT,
        plgenaol TEXT,
        plgenags TEXT,
        plgenanc TEXT,
        plgenahy TEXT, 
        plgenabm TEXT, 
        plgenawi TEXT,
        plgenaso TEXT,
        plgenagt TEXT, 
        plgenatr TEXT,
        plgenath TEXT,
        plgenacy TEXT,
        plgenacn TEXT,
        sector TEXT, 
        nbfactor TEXT
    );
        CREATE TABLE elec_table (
        stateid TEXT,
        year INTEGER,
        year_state TEXT PRIMARY KEY,
        price_all REAL,
        price_com REAL,
        price_ind REAL,
        price_res REAL
    );
    CREATE TABLE pop_table (
        year INTEGER,
        population INT,
        stateid TEXT,
        year_state TEXT PRIMARY KEY
    );
    CREATE TABLE gdp_table (
        year INTEGER,
        gdp_2022_prices INT,
        stateid TEXT,
        year_state TEXT PRIMARY KEY
    );

    """


def makedb():
    """ 
    """
    df = pd.read_csv("cleaned_plant_data.csv")

    # remove database if it exists already
    path = pathlib.Path("database/plants.db")
    path.unlink()
    
    # connect to fresh database & create tables
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript(schema())

    df.to_sql('plants', conn, if_exists='replace', index=False)

    
    with open("cleaned_api_responses.json", "r") as f:
        data = json.load(f)
    
        for entry in data:
            insert_query = '''
                INSERT INTO elec_table VALUES (?,?,?,?,?,?,?)
            '''
            # Insert data into the table
            c.execute(insert_query, tuple(entry[key] for key in entry.keys()))

    # POP Table

    with open("pop_numbers.json", "r") as f:
        data = json.load(f)
    
        for entry in data:
            insert_query = '''
                INSERT INTO pop_table VALUES (?,?,?,?)
            '''
            # Insert data into the table
            c.execute(insert_query, tuple(entry[key] for key in entry.keys()))

        

    # GDP TABLE
    with open("gdp_numbers.json", "r") as f:
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

def main():
    makedb()

if __name__ == "__main__":
    main()