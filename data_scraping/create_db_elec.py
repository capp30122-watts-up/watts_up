import sqlite3
import json

def schema():
    """ Return current version of schema. """

    return """
    CREATE TABLE elec_table (
        stateid TEXT,
        sectorid TEXT,
        price REAL,
        year INTEGER,
        year_state TEXT PRIMARY KEY,
    );
    """

def run():
    data = []
    with open("cleaned_api_responses.json", "r") as f:
        data = json.load(f)


    conn = sqlite3.connect('project_database.db')

    cursor = conn.cursor()

    cursor.execute(schema())

    for entry in data:
        insert_query = '''
            INSERT INTO elec_table VALUES (?,?,?,?,?)
        '''
        
        # Insert data into the table
        cursor.execute(insert_query, tuple(entry[key] for key in entry.keys()))

    conn.commit()
    conn.close()
