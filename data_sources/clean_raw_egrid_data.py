
import pandas as pd

COL_NAMES = ['YEAR',
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



def slim_and_append(dict_of_dfs):
    
    """
    This function should load the data in the excel files from egrid_data folder
    and returns a uncleaned Pandas DataFrame

    Returns:
        A dictionary of PandasDataframes
    """

    df_all = pd.DataFrame()
    dictc ={}
    for name, df in dict_of_dfs.items():
        #print(df.columns)
        cols_available = [col for col in COL_NAMES if col in df.columns]
        print(cols_available)
        df2 = df[cols_available].copy()
        df_all = pd.concat([df_all,df2], ignore_index = True)
        #print(df_all.columns)
        
    return df_all



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