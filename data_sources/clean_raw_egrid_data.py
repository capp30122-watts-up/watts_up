


    header_df = pd.read_excel(filename, sheet_name="PLNT22", header=0, nrows=0)

    column_list = df.columns.tolist()
    descriptor_list = header_df.columns.tolist()

    # Feilds of interest
    column_list_plantinfo = column_list[0:36]
    column_list_geninfo = column_list[108:]

    header_dictionary = {}
    for i, header in enumerate(column_list):
        header_dictionary[header] = descriptor_list[i]


names = ['PSTATABB', 'PNAME', 'ORISPL', 'PLTYPE', 'OPRNAME', 'OPRCODE', '']
