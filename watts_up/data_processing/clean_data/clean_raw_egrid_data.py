import pandas as pd
from data_processing.extract_data import import_PLNT_sheet_data
import pathlib
import os
import json

COL_NAMES = [
    "YEAR",
    "year_state",
    "state_id",
    "PSTATABB",
    "PNAME",
    "ORISPL",
    "OPRNAME",
    "OPRCODE",
    "UTLSRVNM",
    "UTLSRVID",
    "SECTOR",
    "NERC",
    "SUBRGN",
    "SRNAME",
    "FIPSST",
    "FIPSCNTY",
    "CNTYNAME",
    "LAT",
    "LON",
    "PLPRMFL",
    "PLFUELCT",
    "COALFLAG",
    "CAPFAC",
    "NAMEPCAP",
    "NBFACTOR",
    "PLNGENAN",
    "PLCO2AN",
    "PLGENACL",
    "PLGENAOL",
    "PLGENAGS",
    "PLGENANC",
    "PLGENAHY",
    "PLGENABM",
    "PLGENAWI",
    "PLGENASO",
    "PLGENAGT",
    "PLGENAOF",
    "PLGENAOP",
    "PLGENATN",
    "PLGENATR",
    "PLGENATH",
    "PLGENACY",
    "PLGENACN",
    "FILE",
]


def slim_and_append():
    """
    This function should load the data in the excel files from egrid_data folder
    and returns a uncleaned Pandas DataFrame

    Returns:
        A dictionary of PandasDataframes
    """

    dict_of_dfs = import_PLNT_sheet_data()

    df_all = pd.DataFrame()

    for name, df in dict_of_dfs.items():
        # rename state_id column
        df.rename(columns={"PSTATABB": "state_id"}, inplace=True)
        df["year_state"] = df["YEAR"].astype(str) + "_" + df["state_id"]
        cols_available = [col for col in COL_NAMES if col in df.columns]

        # filter to desired columns that are available in df
        df2 = df[cols_available].copy()
        df_all = pd.concat([df_all, df2], ignore_index=True)

    df_all.columns = df_all.columns.str.lower()

    df_all.to_csv("cleaned_plant_data.csv", index=False)

    json_data = df.to_json(orient="records")

    with open("cleaned_egrid_data.json", "w") as f:
        f.write(json_data)

    output_dir = (pathlib.Path(__file__).parent.parent.parent / "data/final_data")

    with open(os.path.join(output_dir, "cleaned_egrid_data.json"), "w") as file:
        json.dump(json_data, file)


def main():
    slim_and_append()


if __name__ == "__main__":
    main()

