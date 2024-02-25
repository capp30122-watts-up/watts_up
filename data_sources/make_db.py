import sqlite3
import pathlib
import os
import pandas

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

    """


def makedb(df):
    """ (re)create database from a normalized_parks.json from PA #2 """
    # remove database if it exists already
    path = pathlib.Path("database/plants.db")
    path.unlink()
    
    # connect to fresh database & create tables
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript(schema())

    df.to_sql('plants', conn, if_exists='replace', index=False)


    # Commit transaction and close connection
    conn.commit()
    conn.close()
    