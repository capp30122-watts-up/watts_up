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


def import_PLNT_sheet_data() -> pd.DataFrame:
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
    folder_path = os.getcwd() + '/egrid_data/'

    df_all = pd.DataFrame()

    for file in os.listdir(folder_path):
        print(file)
        filename = folder_path + file
        pattern = r'(?<=20)(\d{2})'
        match = re.findall(pattern, file)
        sheet = "PLNT"+match[0]

        # format of excel files is different prior to 2014 release
        if int(match[0]) < 14:
            # prior to 2005, sheet names in the workbook were different
            if match[0] == "04":
                sheet = "EGRD"+sheet
            df = pd.read_excel(
            filename,
            header = 4,
            sheet_name=sheet
        )
        else:
            df = pd.read_excel(
                filename,
                header = 1,
                sheet_name=sheet
            )

        df["FILE"] = file

        df_all = pd.concat([df_all,df], ignore_index = True)

    return df_all



    

    

    





