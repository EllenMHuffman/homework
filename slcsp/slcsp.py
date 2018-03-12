import pandas as pd

####################
# HELPER FUNCTIONS #
####################


def clean_zipcodes(zips_file):
    """Create dataframe, remove duplicate zipcodes and rate areas from file."""

    df_zip = pd.read_csv(zips_file, dtype={'zipcode': str})
    df_zip.drop_duplicates(['zipcode', 'rate_area'], inplace=True)

    return df_zip


def clean_target_file(target_file):
    """Create dataframe, remove rate column."""

    df_slcsp = pd.read_csv(target_file, dtype={'zipcode': str})
    df_slcsp.drop(['rate'], axis=1, inplace=True)

    return df_slcsp


def find_ambiguous_zipcodes(df_zip_rates):
    """Identify the zipcodes that have multiple rate areas."""

    df_zip_rates['dups'] = df_zip_rates.duplicated('zipcode')
    ambig_zips = df_zip_rates.query('dups == True')['zipcode']

    df_zip_rates.drop_duplicates(['zipcode'], inplace=True)

    return ambig_zips

################################################################################


def create_area_rates(plans_file):
    """Creates a dataframe of each area and its second lowest cost rate."""

    df_plan = pd.read_csv(plans_file)
    df_silver_sorted = df_plan.query('metal_level == "Silver"').sort_values('rate')

    rows = []

    for rate_area, df_by_area in df_silver_sorted.groupby('rate_area'):
        rates_by_area = df_by_area['rate'].unique()
        second_lowest = rates_by_area[1]
        rows.append({'rate_area': rate_area, 'rate': second_lowest})

    return pd.DataFrame(rows)


def assign_areas_to_zipcodes(target_file, zips_file):
    """Assign rate area to each zipcode in target file."""

    df_slcsp = clean_target_file(target_file)
    df_zip = clean_zipcodes(zips_file)

    df_zip_areas = df_slcsp.merge(df_zip[['zipcode', 'rate_area']],
                                  on='zipcode',
                                  how='inner')

    return df_zip_areas


def assign_rates_to_zipcodes(df_zip_areas, df_area_rates):
    """Assign a the second lowest rate to each zipcode in target file."""

    df_zip_rates = df_zip_areas.merge(df_area_rates, on='rate_area', how='left')

    return df_zip_rates


def nullify_ambig_zipcodes(df_zip_rates):
    """Remove rates for any zipcode that has multiple rate areas."""

    ambig_zips = find_ambiguous_zipcodes(df_zip_rates)

    for ambig_zip in ambig_zips:
        index = df_zip_rates.index[df_zip_rates['zipcode'] == ambig_zip]
        df_zip_rates.loc[index, 'rate'] = None

    return df_zip_rates


def write_clean_output(df_zip_rates_nulled, target_file):
    """Remove extra columns from dataframe and output to csv file."""

    slcsp_zipcode_rate = df_zip_rates_nulled.drop(['rate_area', 'dups'], axis=1)

    slcsp_zipcode_rate.to_csv(target_file, header=['zipcode', 'rate'], index=False)

    return slcsp_zipcode_rate

################################################################################


if __name__ == '__main__':
    df_area_rates = create_area_rates('./data/plans.csv')
    df_zip_areas = assign_areas_to_zipcodes(target_file='./data/slcsp.csv',
                                            zips_file='./data/zips.csv')
    df_zip_rates = assign_rates_to_zipcodes(df_zip_areas, df_area_rates)
    df_zip_rates_nulled = nullify_ambig_zipcodes(df_zip_rates)
    write_clean_output(df_zip_rates_nulled, './data/slcsp.csv')
