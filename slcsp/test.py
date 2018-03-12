import pandas as pd
import unittest
from slcsp import (find_ambiguous_zipcodes, create_area_rates,
                   assign_areas_to_zipcodes, assign_rates_to_zipcodes,
                   nullify_ambig_zipcodes, write_clean_output)


class TestSlcspFunctions(unittest.TestCase):

    def test_find_ambiguous_zipcodes(self):
        rows = [{'zipcode': '79168', 'rate_area': 2, 'rate': 184.97},
                {'zipcode': '54923', 'rate_area': 15, 'rate': 196.64},
                {'zipcode': '54923', 'rate_area': 11, 'rate': 235.65}]
        df_zip_rates = pd.DataFrame(rows)

        result = find_ambiguous_zipcodes(df_zip_rates)
        self.assertEqual(result[2], '54923')

    def test_create_area_rates(self):
        result = create_area_rates('./test_data/plans.csv')
        self.assertEqual(result['rate'][0], 166.13)
        self.assertEqual(result['rate_area'][0], 1)
        self.assertEqual(result['rate'][66], 304.21)
        self.assertEqual(result['rate_area'][66], 67)

    def test_assign_areas_to_zipcodes(self):
        result = assign_areas_to_zipcodes('./test_data/slcsp.csv', './test_data/zips.csv')
        self.assertEqual(result['zipcode'][0], '64148')
        self.assertEqual(result['rate_area'][0], 3)
        self.assertEqual(result['zipcode'][63], '31551')
        self.assertEqual(result['rate_area'][63], 6)

    def test_assign_rates_to_zipcodes(self):
        df_zip_areas = pd.DataFrame([
            {'zipcode': '64148', 'rate_area': 3},
            {'zipcode': '31551', 'rate_area': 6}
            ])
        df_area_rates = pd.DataFrame([
            {'rate_area': 3, 'rate': 195.66},
            {'rate_area': 6, 'rate': 1165.50}
            ])
        result = assign_rates_to_zipcodes(df_zip_areas, df_area_rates)

        self.assertEqual(result['zipcode'][0], '64148')
        self.assertEqual(result['rate_area'][0], 3)
        self.assertEqual(result['rate'][0], 195.66)
        self.assertEqual(result['zipcode'][1], '31551')
        self.assertEqual(result['rate_area'][1], 6)
        self.assertEqual(result['rate'][1], 1165.50)

    def test_nullify_ambig_zipcodes(self):
        import math

        df_zip_rates = pd.DataFrame([
            {'zipcode': '64148', 'rate_area': 3, 'rate': 195.66},
            {'zipcode': '31551', 'rate_area': 6, 'rate': 1165.50},
            {'zipcode': '54923', 'rate_area': 15, 'rate': 196.64},
            {'zipcode': '54923', 'rate_area': 11, 'rate': 235.65}
            ])
        result = nullify_ambig_zipcodes(df_zip_rates)

        self.assertTrue(math.isnan(result['rate'][2]))
        self.assertEqual(result['rate_area'][2], 15)
        self.assertEqual(len(result), 3)

    def test_write_clean_output(self):
        rows = [{'rate': 195.66, 'rate_area': 3, 'zipcode': '64148', 'dups': False},
                {'rate': 1165.50, 'rate_area': 6, 'zipcode': '31551', 'dups': False},
                {'rate': float('nan'), 'rate_area': 15, 'zipcode': '54923', 'dups': False}
                ]
        df_zip_rates_nulled = pd.DataFrame(rows)

        result = write_clean_output(df_zip_rates_nulled, './test_data/slcsp_output.csv')

        self.assertEqual(result['rate'][0], 195.66)
        self.assertEqual(result['zipcode'][0], '64148')
        with self.assertRaises(KeyError):
            result['dups']


class TestIntegration(unittest.TestCase):

    def test_function_integration(self):
        df_area_rates = create_area_rates('./test_data/plans.csv')
        df_zip_areas = assign_areas_to_zipcodes(target_file='./test_data/slcsp.csv',
                                                zips_file='./test_data/zips.csv')
        df_zip_rates = assign_rates_to_zipcodes(df_zip_areas, df_area_rates)
        df_zip_rates_nulled = nullify_ambig_zipcodes(df_zip_rates)
        write_clean_output(df_zip_rates_nulled, './test_data/slcsp_output.csv')

        self.assertEqual(df_zip_rates_nulled[df_zip_rates_nulled.zipcode == '77052'].rate.iloc[0], 235.92)


if __name__ == '__main__':
    unittest.main()
