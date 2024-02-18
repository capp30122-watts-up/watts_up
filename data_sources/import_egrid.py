import re
import pathlib
from typing import List
import pandas as pd
import os


def list_files_in_folder():
    #folderpath = pathlib.Path(__file__).parent / "egrid_data"
    folder_path = os.getcwd() + '/egrid_data/post_2014'
    files_list = os.listdir(folder_path)
    return files_list

files_in_folder = list_files_in_folder()

def filter_plnt_sheets(sheet_name):
    return sheet_name.startswith('PLNT')

names = ['PSTATABB', 'PNAME', 'ORISPL', 'PLTYPE', 'OPRNAME', 'OPRCODE', '']

def clean_ppp_data() -> pd.DataFrame:
    """
    This function should load the data from data/il-ppp.csv
    and return a list of CleanedData tuples.

    * For PPP data you should use the ID, BorrowerName, BorrowerCity, and BorrowerZip
    * All data should be converted to lowercase & stripped of leading and trailing whitespace.
    * All zip codes should be 5 digits long.

    Returns:
        A list of CleanedData tuples
    """
    #folderpath = pathlib.Path(__file__).parent / "egrid_data"
    folder_path = os.getcwd() + '/egrid_data/post_2014/'
    files_in_folder = list_files_in_folder()
    print(files_in_folder)

    df_all = pd.DataFrame()

    for file in files_in_folder:
        print(file)
        filename = folder_path + file

        pattern = r'(?<=20)(\d{2})'
        match = re.findall(pattern, file)
        sheet = "PLNT"+match[0]

        df = pd.read_excel(
            filename,
            header = 1,
            sheet_name=sheet
        )

        df_all = pd.concat([df_all,df], ignore_index = True)

    return df_all





    header_df = pd.read_excel(filename, sheet_name="PLNT22", header=0, nrows=0)

    column_list = df.columns.tolist()
    descriptor_list = header_df.columns.tolist()

    # Feilds of interest
    column_list_plantinfo = column_list[0:36]
    column_list_geninfo = column_list[108:]

    header_dictionary = {}
    for i, header in enumerate(column_list):
        header_dictionary[header] = descriptor_list[i]



    

    

    





