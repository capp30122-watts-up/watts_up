"""
This file contains the definition for the database schema
Authors: Jacob Trout and Praveen Chandar
"""

def schema():
    """ Return current version of schema. """
    
    return """
    CREATE TABLE plants (
        year INTEGER,
        year_state TEXT,
        state_id TEXT,
        pname TEXT,
        orispl INT,
        oprname TEXT,
        oprcode REAL,
        utlsrvnm TEXT,
        utlsrvid INT,
        nerc TEXT,
        subrgn TEXT,
        srname TEXT,
        fipsst INTEGER,
        fipscnty INT,
        cntyname TEXT,
        lat REAL,
        lon REAL,
        plprmfl TEXT,
        plfuelct TEXT,
        plpfgnct TEXT,
        coalflag INT,
        capfac REAL,
        namepcap REAL,
        plngenan REAL,
        plco2an REAL,
        plgenacl REAL,
        plgenaol REAL,
        plgenags REAL,
        plgenanc REAL,
        plgenahy REAL,
        plgenabm REAL,
        plgenawi REAL,
        plgenaso REAL,
        plgenagt REAL,
        plgenaof REAL,
        plgenaop REAL,
        plgenatn REAL,
        plgenatr REAL,
        plgenath REAL,
        plgenacy REAL,
        plgenacn REAL,
        file TEXT,
        sector TEXT,
        nbfactor REAL
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