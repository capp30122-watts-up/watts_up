import re
import pathlib
from typing import List
import pandas as pd
import os


def import_PLNT_sheet_data() -> pd.DataFrame:
    """
    This function should load the data in the excel files from egrid_data folder
    and returns a dictionary where the keys are file names and the values are
    corresponding Pandas DataFrame

    Returns:
        A dictionary of PandasDataframes
    """
    #folderpath = pathlib.Path(__file__).parent / "egrid_data"
    folder_path = os.getcwd() + '/egrid_data/'

    df_all = pd.DataFrame()

    dfs ={}

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

        if 'YEAR' not in df.columns:
            df['YEAR'] = '20' + match[0]

        dfs[file] = df


    return dfs



    

    

    





