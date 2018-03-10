import pandas as pd


# Find Second Lowest Cost Silver Plan by Rate Area

df_plan = pd.read_csv('./plans.csv')

df_plan.query('metal_level == "Silver"').sort_values(['rate_area', 'rate']
                                                     )[['rate', 'rate_area']]


rate_areas = df_plan['rate_area'].unique()

columns = ['rate_area', 'rate']
df_area_rates = pd.DataFrame(columns=columns)

i = 0
for area in rate_areas:
    rates_by_area = df_plan.query('rate_area == @area').sort_values('rate')['rate'].unique()
    second_lowest = rates_by_area[1]
    data = ({'rate_area': area, 'rate': second_lowest})
    df_area_rates.loc[i] = pd.Series(data)
    i += 1


# Assign Rates to Zipcodes

df_slcsp = pd.read_csv('./slcsp.csv', dtype={'zipcode': str})

df_zip = pd.read_csv('./zips.csv', dtype={'zipcode': str})
df_zip.drop_duplicates(['zipcode', 'rate_area'], inplace=True)

df_zip_areas = df_slcsp.merge(df_zip[['zipcode', 'rate_area']], on='zipcode', how='inner')


df_zip_areas['dups'] = df_zip_areas.duplicated('zipcode')
df_zip_areas.drop(['rate'], axis=1, inplace=True)

df_zip_rates = df_zip_areas.merge(df_area_rates, on='rate_area', how='left')


# Find Ambiguous Zipcodes

ambig_zips = df_zip_rates.query('dups == True')['zipcode']

df_zip_rates.drop_duplicates(['zipcode'], inplace=True)

for ambig_zip in ambig_zips:
    index = df_zip_rates.index[df_zip_rates['zipcode'] == ambig_zip]
    df_zip_rates.loc[index, 'rate'] = None


# Clean and Output Data

df_zip_rates.drop(['rate_area', 'dups'], axis=1, inplace=True)
df_zip_rates.to_csv('./testing.csv', header=['zipcode', 'rate'], index=False)
