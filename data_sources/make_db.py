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
        file TEXT,
        pname TEXT,
        lat REAL,
        lon REAL,
        pstatabb TEXT
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
        
    # need id_ for generate_times & easy access to foreign key
    for id, row in df.iterrows():
    
        # insert one row at a time (for clarity & since this isn't speed-critical)
        c.execute(
            "INSERT INTO plants (id, year, file, pname, lat, lon, pstatabb) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                id,
                row["YEAR"],
                row["FILE"],
                row["PNAME"],
                row["LAT"],
                row["LON"],
                row["PSTATABB"],
            ),
        )
    c.execute("COMMIT")
    c.close()