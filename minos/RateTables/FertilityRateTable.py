import pandas as pd

from minos.RateTables.BaseHandler import BaseHandler
from minos.data_generation.convert_rate_data import cache_fertility_by_region
import os
from os.path import dirname as up
from os.path import exists
from os import remove
import numpy as np
from minos.utils import extend_series, get_nearest
from minos.data_generation import generate_composite_vars


RATETABLE_PATH_DEFAULT = os.path.join(up(up(up(__file__))), "persistent_data")
# RATETABLE_FILE_DEFAULT = "fertility_rate_table_1.csv"
# RATETABLE_DEFAULT = os.path.join(RATETABLE_PATH_DEFAULT, RATETABLE_FILE_DEFAULT)

PARITY_DEFAULT = True
PARITY_PATH_DEFAULT = RATETABLE_PATH_DEFAULT
PARITY_FILE_DEFAULT = "fertilityratesbyparity1934to2020englandandwales.xlsx"
PARITY_DEFAULT = os.path.join(PARITY_PATH_DEFAULT, PARITY_FILE_DEFAULT)

NEWETHPOP_FOLDER_DEFAULT = os.path.join(RATETABLE_PATH_DEFAULT, "Fertility")

PARITY_MAX_DEFAULT = generate_composite_vars.PARITY_MAX_DEFAULT
AGE_RANGE_DEFAULT = [10, 49]
YEAR_RANGE_DEFAULT = [2011, 2021]

PARITY_SHEET = "Table"
PARITY_HEADER = 6
PARITY_END = 2294

THRESHOLD_DEFAULT = 1000
APPLY_MAX_PARITY_DEFAULT = True

# Generate all column headers
pop_headers = ["p" + str(i + 1) for i in range(5)]
births_headers = ["b" + str(i + 1) for i in range(5)]
fert_headers = ["f" + str(i + 1) for i in range(5)]
# common_headers = ['year', 'age', 'nkids']

# Valid ages in ONS data before extension
AGE1, AGE2 = 15, 44


def parse_parity_ons(parity_file=PARITY_DEFAULT,
                     sheet=PARITY_SHEET,
                     header_index=PARITY_HEADER,
                     end_index=PARITY_END):
    """
    To parse parity file, extract useful parts and reformat

    Parameters
    ----------
    parity_file : str
        File from which parity-disaggregated fertility data are to be retrieved
    sheet : str
        Sheet of Excel file from which data is to be taken
    header_index : int
        Index of header row
    end_index : int
        Last row of data

    Returns
    -------
    df_parity_raw : Pandas DataFrame
        DataFrame of births, population and fertility rate by parity,
        age of mother and year of birth, 1934-2020

    """
    # Read in file and reformat
    df_parity_raw = pd.read_excel(parity_file,
                                  sheet_name=sheet,
                                  header=header_index-1,
                                  nrows=end_index-header_index)

    # Exclude some unnamed and unneeded columns and rename the rest
    df_parity_raw = df_parity_raw.loc[:, ~df_parity_raw.columns.str.contains('^Unnamed')].drop(["Year of birth of mother"], axis=1)
    col_headers = ['year', 'age', 'pop_total'] + pop_headers + births_headers + ['births_total'] + fert_headers
    df_parity_raw.columns.values[:] = col_headers
    df_parity_raw['fert_total'] = df_parity_raw['births_total']/df_parity_raw['pop_total']

    return df_parity_raw


def extend_parity_ons(df_parity,
                      n,
                      age_range=AGE_RANGE_DEFAULT,
                      year_range=YEAR_RANGE_DEFAULT):
    """
    To extend parity data to wider range of ages and greater parity

    Parameters
    ----------
    df_parity : Pandas DataFrame
        Parity data before extension
    age_range : list of int
        Min and max ages
    year_range : list of int
        Min and max years to retrieve
    n : int
        Maximum number of children and therefore length of data series
        for each value of age and year

    Returns
    -------
    pop_concat : Pandas DataFrame
        DataFrame containing population data
        over specified range of ages and parities
    births_concat : Pandas DataFrame
        DataFrame containing births data
        over specified range of ages and parities

    """
    # Split by year to make extending easier
    year_dict = {yr: df_parity.loc[df_parity['year'] == yr].set_index('age').drop('year', axis=1) for yr in df_parity['year'].unique() if yr in range(*year_range)}

    # Iterate over years for readability
    pop_dict = {}
    births_dict = {}
    # fert_dict = {}

    cols = [col for col in year_dict[min(year_dict.keys())].columns if col in pop_headers]
    to_extend_by = n - len(pop_headers) + 2
    # print(to_extend_by)

    for year, year_data in year_dict.items():

        # 1. Extend population to lower and upper age range by taking mean of nearest values
        cols = [col for col in year_data.columns if col in pop_headers]
        newpop = {}

        for col in cols:
            data = list(year_data[col])

            # Extend population with mean of nearest five ages, a > 44
            data.extend([np.mean(data[-5:])] * 4)
            newpop[col] = data

            # Extend population with mean of nearest five ages, a < 15
            data = data[::-1]

            if data[-1] < sum(data)/THRESHOLD_DEFAULT:
                # if data[-1] < 0:
                value = 0
            else:
                value = np.mean(data[-5:])
            data.extend([value] * 4)
            data = data[::-1]

            newpop[col] = data

        # 2. Extend population to higher parity values using geometric series
        df_pop = pd.DataFrame(newpop)

        newlines = {}
        for i, row in df_pop.iterrows():
            data = list(row)
            # if data[-1] <= 5:
            if data[-1] <= sum(data)/THRESHOLD_DEFAULT:
                newline = data
                newline.extend([0.0] * (to_extend_by - 1))
            else:
                newline = extend_series(data, to_extend_by, r0=0.5)
            newlines[i] = newline

        df_pop = pd.DataFrame(newlines).T
        pop_dict[year] = df_pop


        # 3. Extend births to lower and upper age ranges using geometric series
        cols = [col for col in year_data.columns if col in births_headers]

        # Extend births with geometric series, a > 44y
        newbir = {col: extend_series(list(year_data[col]), 5, r0=0.1) for col in cols}

        # Extend births with geometric series, a < 15y
        newbir = {col: extend_series(series, 5, r0=0.01, reverse=True) for col, series in newbir.items()}  # Same as above, but reverse before and after


        # 4. Extend births to higher parity values using geometric series
        df_bir = pd.DataFrame(newbir)

        newlines = {}
        for i, row in df_bir.iterrows():
            data = list(row)
            # if data[-1] <= 1:
            if data[-1] <= sum(data)/THRESHOLD_DEFAULT:
                newline = data
                newline.extend([0.0] * (to_extend_by - 1))
            else:
                newline = extend_series(data, to_extend_by, r0=0.5)
            newlines[i] = newline

        df_bir = pd.DataFrame(newlines).T
        births_dict[year] = pd.DataFrame(df_bir)


    # Convert into dataframes and tidy up
    births_concat = pd.concat(births_dict).reset_index(level=[0,1])
    births_concat.columns.values[0:2] = ['year', 'age']
    births_concat['age'] += age_range[0]
    # births_concat.columns.values[-n:] = range(n)

    pop_concat = pd.concat(pop_dict).reset_index(level=[0,1])
    pop_concat.columns.values[0:2] = ['year', 'age']
    pop_concat['age'] += age_range[0]
    # pop_concat.columns.values[-n:] = range(n)

    pop_concat = pop_concat.set_index(['year', 'age'])
    births_concat = births_concat.set_index(['year', 'age'])

    fert_concat = births_concat.divide(pop_concat)
    fert_concat = fert_concat.replace([np.inf, -np.inf, np.NaN], 0.0)  # Reset all blow-ups to zero (as caused by zero population values)
    fert_concat = fert_concat.mask(fert_concat > 1, 1)  # Reset f > 1 to f = 1, as this is a probability so must be 0 < f < 1
    fert_concat = fert_concat.mask(fert_concat < 0, 0)  # Reset f < 0 to f = 0, as this is a probability so must be 0 < f < 1

    # # HR 13/06/23 Add total fertility df for use later
    # # Note these data are NOT extended to higher parities!
    # # fert_total_concat = df_parity[['age', 'year', 'fert_total']].set_index(['year', 'age'])
    # fert_total_concat = df_parity[['age', 'year', 'fert_total']][df_parity['year'].between(*year_range)].set_index(['year', 'age'])
    #
    # # Also create total fertility based on parity-extended data for comparison
    # fert_total_ext_concat = births_concat.sum(axis=1)/pop_concat.sum(axis=1)

    # return year_dict, pop_concat, births_concat, fert_concat, fert_total_concat, fert_total_ext_concat
    return pop_concat, births_concat


def apply_parity_to_newethpop(births_ons,
                              pop_ons,
                              nep,
                              apply_max_parity=APPLY_MAX_PARITY_DEFAULT,
                              ):
    """
    To add parity as variable to NewEthPop fertility data

    Parameters
    ----------
    births_ons : Pandas DataFrame
        DataFrame of number of births by age and year, from ONS 1934-2020 dataset
    pop_ons : Pandas DataFrame
        DataFrame of female population by age and year, from ONS 1934-2020 dataset
    nep : Pandas DataFrame
        DataFrame of fertility by age, year and ethnicity, from NewEthPop (nep)

    Returns
    -------
    fert_out : Pandas DataFrame
        Fertility with parity in NewEthPop (nep) format

    """
    # nep = pd.read_csv(newethpop_file, index_col=0)
    births = births_ons
    pop = pop_ons


    # Create new version of NewEthPop extended by parity
    # Logic is:
    # 1. Grab fertility column ("mean_value") from NewEthPop-based per-region rate table as a list
    # 2. Iterate over list; for each entry f(a,y,e,r) grab corresponding value from ONS rate table for f(a,y,p)
    # 3. Expand single fertility value into f(p) for parity by matching total fertility values
    # 4. Apply filters to ensure 0 < f(p) < 1 ("truncate")
    ons_years = sorted(list(births_ons.index.unique(0)))
    n = len(births_ons.columns)
    fert_list = []
    for row,data in nep.iterrows():

        year = data['year_start']
        # print('year', year)
        age = data['age_start']
        f_nep = data['mean_value']
        # print(year, age, f_nep)

        # Get nearest ONS year and expand fertility value by parity
        # print("NewEthPop year sought", year)
        if not year in ons_years:
            year = get_nearest(ons_years, year)
        # print("ONS year found", year)

        b_ons = births.loc[(year,age)]
        p_ons = pop.loc[(year,age)]
        # print("Found year/age {}/{} in ONS data:".format(year, age))
        f_ons = sum(b_ons)/sum(p_ons)

        factor = f_nep/f_ons
        f_corr = factor*b_ons/p_ons
        f_trunc = [el if el <= 1.0 else 1.0 for el in f_corr]

        # HR 30/06/23 Set last value to zero to enforce max. value
        if apply_max_parity:
            f_trunc[-1] = 0

        if AGE1 <= age <= AGE2:
            f_simple = f_trunc
        else:
            f_simple = [0]*len(f_trunc)

        f_block = pd.concat([data]*n, axis=1).T  # Duplicate and stack n rows
        # print(f_trunc)
        f_block['nkids_ind'] = range(n)
        f_block['fertility'] = f_simple

        # TESTING: Some optional columns
        # data['f_ons'] = f_ons
        # data['factor'] = factor
        f_block.drop("mean_value", axis=1, inplace=True)  # Remove "mean_value" to ensure not being used in pipeline

        fert_list.append(f_block)

    fert_out = pd.concat(fert_list)
    # outfile = "fert_out.csv"
    # print("Dumping to", outfile)
    # fert_out.to_csv(outfile, index=False)

    # return nep, births, pop, fert_list, fert_out
    return fert_out


class FertilityRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.scaling_method = self.configuration["scale_rates"]["method"]
        self.filename = f'fertility_rate_table_{self.configuration["scale_rates"][self.scaling_method]["fertility"]}'

        # HR 13/05/24 Adding option for excluding parity for #369
        if 'parity' in self.configuration:
            self.parity = self.configuration['parity']
        else:
            self.parity = PARITY_DEFAULT
        if not self.parity:
            self.filename += '_noparity'

        self.filename += '.csv'
        self.rate_table_path = self.rate_table_dir + self.filename
        print("Path to rate table: {}".format(self.rate_table_path))

        self.source_file = self.configuration.path_to_fertility_file
        if "parity_max" in self.configuration:
            self.parity_max = self.configuration["parity_max"]
        else:
            self.parity_max = PARITY_MAX_DEFAULT
        # print("Max. parity:", self.parity_max)
        self._parity_added = False

    def _build(self):
        # HR 21/04/23 Try and load from source file, otherwise create from primary data
        try:
            print("Trying to load from source file...")
            df = pd.read_csv(self.source_file)
            # self._parity_added = True
            print("Found rate table file at", self.source_file)
        except FileNotFoundError as e:
            print("Couldn't load from source file")
            print("\n", e, "\n")
            print("Creating source file from primary NewEthPop data...")
            dump_path = cache_fertility_by_region()
            if dump_path:
                print("Dumped source file to:", dump_path)
                self.source_file = dump_path
                df = pd.read_csv(self.source_file)
            else:
                print("Couldn't dump source file")

        yr_start = self.configuration['time']['start']['year']
        yr_end = self.configuration['time']['end']['year']
        print('Computing fertility rate table for years in range [', yr_start, ',', yr_end, ']...')

        self.rate_table = self.transform_rate_table(df,
                                                    yr_start,
                                                    yr_end,
                                                    10, 50, [2])

        # HR 21/06/23 Expanding fertility rate table by parity
        # print("Expanding NewEthPop fertility data with parity data from ONS 1934-2020")
        if self.parity:
            self.rate_table = self.add_parity()

        if self.configuration["scale_rates"][self.scaling_method]["fertility"] != 1:
            print(f'Scaling the fertility rates by a factor of {self.configuration["scale_rates"][self.scaling_method]["fertility"]}')
            # self.rate_table["mean_value"] *= float(self.configuration["scale_rates"][self.scaling_method]["fertility"])
            self.rate_table["fertility"] *= float(self.configuration["scale_rates"][self.scaling_method]["fertility"])

    def add_parity(self):
        # Avoid running more than once as will break rate table
        if self._parity_added:
            print("Already added parity, returning existing rate table")
            return self.rate_table

        rt = self.rate_table

        df_parity = parse_parity_ons()
        pop_concat, births_concat = extend_parity_ons(df_parity,
                                                      self.parity_max)
        print("Extending NewEthPop data with parity")
        print("This may take several minutes, depending on the number of years covered...")
        rt_parity = apply_parity_to_newethpop(births_ons=births_concat,
                                              pop_ons=pop_concat,
                                              nep=self.rate_table)
        print("Done")
        self._parity_added = True

        return rt_parity

