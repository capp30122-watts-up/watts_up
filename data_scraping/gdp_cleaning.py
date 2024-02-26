import os
import pandas as pd
import regex as re

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_sources/gdp_pop')

STATE_MAPPING_DATA = {
    'state': ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'American Samoa', 'California', 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Guam', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas',
                         'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Northern Mariana Islands',
                         'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Trust Territories', 'Utah', 'Vermont', 'Virgin Islands', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'],
    'stateid': ['AL', 'AK', 'AZ', 'AR', 'AS', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS',
                            'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP',
                            'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'TT', 'UT', 'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY'],
}

STATE_MAPPING = pd.DataFrame(STATE_MAPPING_DATA)

def gdp_data():
    raw_gdp_path = os.path.join(DATA_DIR, 'gdp.csv')
    raw_gdp = pd.read_csv(raw_gdp_path)

    melted_df = pd.melt(raw_gdp, id_vars=['Years'], var_name='State', value_name='gdp_2022_prices')
    merged_df = pd.merge(melted_df, STATE_MAPPING, left_on='State', right_on='state', how='left')
    merged_df = merged_df.drop(columns=['state','State'])
    merged_df = merged_df.rename(columns={"Years": 'year'})
    merged_df['year_state'] = merged_df['year'].astype(str) + '_' + merged_df['stateid'].astype(str)

    # Make the json file
    json_data = merged_df.to_json(orient='records')
    with open(os.path.join(DATA_DIR, 'gdp_numbers.json'), 'w') as json_file:
        json_file.write(json_data)

def pop_data():
    pop_2019_path = os.path.join(DATA_DIR, 'p1.csv')
    pop_2022_path = os.path.join(DATA_DIR, 'p2.csv')

    pop_2019 = pd.read_csv(pop_2019_path)
    pop_2022 = pd.read_csv(pop_2022_path)

    # Cleaning pop_2019
    pop_2019 = pop_2019.drop(columns=['4/1/2010 Census population!!Population', '4/1/2010 population estimates base!!Population'])
    col_names = pop_2019.columns.tolist()
    year_cols = [col_names[0]]
    for column in col_names[1:]:
        year_cols.append(re.findall(r'(\d{4})', str(column))[0])
    pop_2019.columns = year_cols
    pop_2019 = pop_2019.rename(columns={"Geographic Area Name (Grouping)": 'state'})

    # Cleaning pop_2022
    pop_2022['State'] = pop_2022['State'].str.lstrip('.')
    pop_2022 = pop_2022.rename(columns={"State": 'state'})

    merged_df = pd.merge(pop_2019, pop_2022, left_on='state', right_on='state', how='left')
    merged_df = merged_df[merged_df['state'] != 'Puerto Rico']
    pop_final = pd.melt(merged_df, id_vars=['state'], var_name='year', value_name='population')
    merged_df1 = pd.merge(pop_final, STATE_MAPPING, left_on='state', right_on='state', how='left')
    merged_df1['year_state'] = merged_df1['year'].astype(str) + '_' + merged_df1['stateid'].astype(str)
    merged_df1 = merged_df1.drop(columns=['state'])
    merged_df1['year'] = merged_df

    #Make the json file
    json_data = merged_df1.to_json(orient='records')
    with open(os.path.join(DATA_DIR,"pop_numbers.json"), 'w') as json_file:
        json_file.write(json_data)

def main():
    gdp_data()
    pop_data()

if __name__ == "__main__":
    main()