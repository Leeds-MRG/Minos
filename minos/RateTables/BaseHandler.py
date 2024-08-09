import pandas as pd
import numpy as np
from os.path import exists
from os import remove
from minos.utils import get_nearest

class BaseHandler:
    def __init__(self, configuration):
        self.configuration = configuration
        self.filename = None
        self.rate_table_dir = 'persistent_data/'
        self.rate_table_path = None
        self.rate_table = None

    def set_rate_table(self):
        if not exists(self.rate_table_path):
            self._build()
            self.cache()
        else:
            print('Fetching rate table from cache {}'.format(self.rate_table_path))
            self.rate_table = pd.read_csv(self.rate_table_path, index_col=[0])

    def set_matrix_tables(self):
        self._build()

    def cache(self, overwrite=False):
        if not exists(self.rate_table_path) or overwrite:
            print('Caching rate table...')
            self.rate_table.to_csv(self.rate_table_path, index=False)
            print('Cached to {}'.format(self.rate_table_path))
        else:
            print('File already exists at {}'.format(self.rate_table_path))

    def clear_cache(self):
        if exists(self.rate_table_path):
            print('Removing {}'.format(self.rate_table_path))
            remove(self.rate_table_path)
        else:
            print('No file at {} found, did not remove'.format(self.rate_table_path))

    def _build(self):
        pass

    @staticmethod
    def transform_rate_table(df, year_start, year_end, age_start, age_end, unique_sex=None):

        """Function that transform an input rate dataframe into a format readable for vivarium
            public health.

            Parameters:
            df (dataframe): Input dataframe with rates produced by LEEDS
            year_start (int): Year for the interpolation to start
            year_end (int): Year for the interpolation to finish
            age_start (int): Minimum age observed in the rate table
            age_end (int): Maximum age observed in the rate table
            unique_sex (list of ints): Sex of individuals to be considered

            Returns:
            df (dataframe): A dataframe with the right vph format.
            """

        # get the unique values observed on the rate data
        if unique_sex is None:
            unique_sex = [1, 2]
        unique_locations = df['REGION.name'].unique()
        unique_ethnicity = df['ETH.group'].unique()

        # HR 20/04/23 Get all years from year_start and year_end
        unique_years = df['year'].unique()
        print("\n## Running transform_rate_table, checking years... ##")
        years = list(range(year_start, year_end))
        print("\n## years before checking:", years)

        year_start = get_nearest(list(unique_years), year_start)
        year_end = get_nearest(list(unique_years), year_end)
        years = list(range(year_start, year_end))
        print("\n## years after checking:", years)

        # loop over the observed values to fill the new dataframe
        list_dic = []
        for location in unique_locations:

            sub_loc_df = df.loc[df['REGION.name'] == location]

            for eth in unique_ethnicity:

                sub_loc_eth_df = sub_loc_df.loc[sub_loc_df['ETH.group'] == eth]

                for sex in unique_sex:

                    # columns are separated for male and female rates
                    if sex == 1:
                        column_suffix = 'M'
                        sex = "Male"  # TODO robs a moron. Either force numerics in rate tables or strings.

                    else:
                        column_suffix = 'F'
                        sex = "Female"

                    for age in range(age_start, age_end):

                        # cater for particular cases (age less than 1 and more than 100).
                        if age == -1:
                            column = column_suffix + 'B.0'
                        elif age == 100:
                            column = column_suffix + '100.101p'
                        else:
                            # columns parsed to the right name (eg 'M.50.51' for a male between 50 and 51 yo)
                            column = column_suffix + str(age) + '.' + str(age + 1)

                        # HR 21/04/23 Old block not including year
                        # if sub_loc_eth_df[column].shape[0] == 1:
                        #     value = sub_loc_eth_df[column].values[0]
                        # else:
                        #     value = 0
                        #     print('Problem, more or less than one value in this category')
                        #
                        # # create the rate row.
                        # dict = {'region': location, 'ethnicity': eth, 'age_start': age, 'age_end': age + 1, 'sex': sex,
                        #         'year_start': year_start, 'year_end': year_end, 'mean_value': value}
                        # list_dic.append(dict)

                        # HR 21/04/23 New block to include year
                        for year in years:

                            # Get sub-dataframe for year
                            sub_loc_eth_year_df = sub_loc_eth_df.loc[sub_loc_eth_df['year'] == year]

                            if sub_loc_eth_year_df[column].shape[0] == 1:
                                value = sub_loc_eth_year_df[column].values[0]
                            else:
                                value = 0
                                print('Problem, more or less than one value in this category')

                            # create the rate row.
                            _dict = {'region': location, 'ethnicity': eth, 'age_start': age, 'age_end': age + 1, 'sex': sex,
                                     'year_start': year, 'year_end': year + 1, 'mean_value': value}
                            list_dic.append(_dict)

        return pd.DataFrame(list_dic)

    @staticmethod
    def compute_migration_rates(df_migration_numbers, df_population_total, year_start, year_end, age_start, age_end,
                                unique_sex=[1, 2], normalize=True):
        """Function that computes the migration (this can be immigration or emigration) rates based on an input dataframe containing the total values of
         migration seen and an input dataframe containing the total population values. The rate is the ratio between both and is returned as a rate
          table in a format readable for vivarium public health.

          Parameters:
          df_migration_numbers (dataframe): Input dataframe with total emigration values produced by LEEDS
          df_population_total (dataframe): Input dataframe with total population values produced by LEEDS

          year_start (int): Year for the interpolation to start
          year_end (int): Year for the interpolation to finish
          age_start (int): Minimum age observed in the rate table
          age_end (int): Maximum age observed in the rate table
          unique_sex (list of ints): Sex of individuals to be considered
          normalize (True/False): divide by the number of population

          Returns:
          df (dataframe): A dataframe with the right vph format.
          """

        # get the unique values observed on the rate data
        unique_locations = df_migration_numbers['LAD.code'].unique()
        unique_ethnicity = df_migration_numbers['ETH.group'].unique()

        # loop over the observed values to fill the new dataframe
        list_dic = []
        for location in unique_locations:

            sub_loc_df = df_migration_numbers.loc[df_migration_numbers['LAD.code'] == location]
            sub_loc_df_total = df_population_total.loc[df_population_total['LAD'] == location]

            for eth in unique_ethnicity:

                sub_loc_eth_df = sub_loc_df.loc[sub_loc_df['ETH.group'] == eth]
                sub_loc_eth_df_total = sub_loc_df_total.loc[
                    (sub_loc_df_total['ETH'] == eth + "_UK") | (sub_loc_df_total['ETH'] == eth + "_NonUK")]

                for sex in unique_sex:

                    # columns are separated for male and female rates
                    if sex == 1:
                        column_suffix = 'M'
                    else:
                        column_suffix = 'F'

                    for age in range(age_start, age_end):

                        # cater for particular cases (age less than 1 and more than 100).
                        if age == -1:
                            column = column_suffix + 'B.0'
                            column_total = 'B'
                        elif age == 100:
                            column = column_suffix + '100.101p'
                        else:
                            # columns parsed to the right name (eg 'M.50.51' for a male between 50 and 51 yo)
                            column = column_suffix + str(age) + '.' + str(age + 1)
                            column_total = column_suffix + str(age)

                        if sub_loc_eth_df[column].shape[0] == 1 and sub_loc_eth_df_total[column_total].sum() != 0:
                            if normalize:
                                value = sub_loc_eth_df[column].values[0] / sub_loc_eth_df_total[column_total].sum()
                            else:
                                value = sub_loc_eth_df[column].values[0]
                        else:
                            value = 0

                        # create the rate row.
                        dict = {'location': location, 'ethnicity': eth, 'age_start': age, 'age_end': age + 1, 'sex': sex,
                                'year_start': year_start, 'year_end': year_end, 'mean_value': value}
                        list_dic.append(dict)

        return pd.DataFrame(list_dic)
