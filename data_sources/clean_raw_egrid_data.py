import re
import pathlib
from typing import List
import pandas as pd
import os
import import_egrid as ie

COL_NAMES = ['YEAR',
 'year_state',
 'state_id',
 'PSTATABB',
 'PNAME',
 'ORISPL',
 'OPRNAME',
 'OPRCODE',
 'UTLSRVNM',
 'UTLSRVID',
 'SECTOR',
 'NERC',
 'SUBRGN',
 'SRNAME',
 'FIPSST',
 'FIPSCNTY',
 'CNTYNAME',
 'LAT',
 'LON',
 'PLPRMFL',
 'PLFUELCT',
 'COALFLAG',
 'CAPFAC',
 'NAMEPCAP',
 'NBFACTOR',
 'PLNGENAN',
 'PLCO2AN',
 'PLGENACL',
 'PLGENAOL',
 'PLGENAGS',
 'PLGENANC',
 'PLGENAHY',
 'PLGENABM',
 'PLGENAWI',
 'PLGENASO',
 'PLGENAGT',
 'PLGENAOF',
 'PLGENAOP',
 'PLGENATN',
 'PLGENATR',
 'PLGENATH',
 'PLGENACY',
 'PLGENACN',
 'FILE']



def slim_and_append():
    
    """
    This function should load the data in the excel files from egrid_data folder
    and returns a uncleaned Pandas DataFrame

    Returns:
        A dictionary of PandasDataframes
    """

    dict_of_dfs = ie.import_PLNT_sheet_data()

    df_all = pd.DataFrame()

    for name, df in dict_of_dfs.items():
        # rename state_id column
        df.rename(columns={'PSTATABB': 'state_id'}, inplace=True)
        df['year_state'] = df['YEAR'].astype(str) + "_" + df['state_id']
        cols_available = [col for col in COL_NAMES if col in df.columns]

        # filter to desired columns that are available in df 
        df2 = df[cols_available].copy()
        df_all = pd.concat([df_all, df2], ignore_index = True)

    df_all.columns = df_all.columns.str.lower()

    df_all.to_csv("cleaned_plant_data.csv", index=False)



    json_data = df.to_json(orient='records')

    with open('cleaned_egrid_data.json', 'w') as f:
        f.write(json_data)
        
    return df_all

def main():
    slim_and_append()


if __name__ == "__main__":
    main()


    



    """
    header_df = pd.read_excel(filename, sheet_name="PLNT22", header=0, nrows=0)

    column_list = df.columns.tolist()
    descriptor_list = header_df.columns.tolist()

    # Feilds of interest
    column_list_plantinfo = column_list[0:36]
    column_list_geninfo = column_list[108:]

    header_dictionary = {}
    for i, header in enumerate(column_list):
        header_dictionary[header] = descriptor_list[i]


    names = ['PSTATABB','PNAME','ORISPL','PLTYPE','OPRNAME','OPRCODE', '']
    """