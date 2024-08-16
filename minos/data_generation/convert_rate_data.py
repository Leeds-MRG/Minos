#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: robertclay

Functions for refactoring daedalus rate tables. See RateTables.BaseHandler for generation of these tables from scratch.

Compress rate tables to remove location aspect.
Essentially grouping all the race/sex categories by MSOA and taking the mean.
Needed until can get location data for BHPS.

Compress LAD rate tables into regional rate tables.

"""

import pandas as pd
from minos.data_generation.US_utils import load_json
import os
from os.path import dirname as up
from minos.utils import get_nearest


LAD_to_region_code = load_json(os.path.join(up(up(up(__file__))), "persistent_data/JSON/"), "LAD_to_region_code.json")
LAD_to_region_name = load_json(os.path.join(up(up(up(__file__))), "persistent_data/JSON/"), "LAD_to_region_name.json")

PERSISTENT_DATA_DIR = os.path.join(up(up(up(__file__))), "persistent_data/")
FERT_DIR_DEFAULT = os.path.join(PERSISTENT_DATA_DIR, "Fertility")
FERT_STUBS = ["Fertility", "_LEEDS1_2.csv"]
MORT_DIR_DEFAULT = os.path.join(PERSISTENT_DATA_DIR, "Mortality")
MORT_STUBS = ["Mortality", "_LEEDS1_2.csv"]

YEAR_RANGE_DEFAULT = None
VARS_TO_GROUP_DEFAULT = ["REGION.name", "ETH.group"]
CACHE_DEFAULT = True
BY_REGION_DEFAULT = True  # If false, do not collapse into regions, and leave by local authority (LA)


def collapse_location(data, file_name):
    """ Pull data frame. Group all rates by the MSOA code and take the mean.
    Save data frame.
    
    
    NOTE: we want to group by both the LAD name and code here. Since
    they are 1 to 1 correspondence however just one is fine and quicker.
    
    Parameters
    --------
    data: pd.DataFrame
     pandas `data` rate table to collapse.
    Returns
    -------
    None.

    """
    # TODO this could be generalised much better.
    # remove unecessary columns
    data = data.drop("LAD.code", axis = 1)
    data = data.drop("LAD.code", axis = 1)

    data = data.groupby(["ETH.group"], as_index= False).mean()
    #data["LAD.code"] = "no_locations"
    #data["LAD.name"] = "no_locations"
    data.to_csv("nolocation_" + file_name, index = True)
    
    return data


def collapse_LAD_to_region(data, file_output, cache=CACHE_DEFAULT, vars_to_group=VARS_TO_GROUP_DEFAULT):
    """ Pull data frame. Group all rates by the MSOA code and take the mean.
    Save data frame.


    NOTE: we want to group by both the LAD name and code here. Since
    they are 1 to 1 correspondence however just one is fine and quicker.

    Parameters
    --------
    data: pd.DataFrame
     pandas `data` rate table to collapse.
    Returns
    -------
    None.

    """
    # map LAD names and codes to region name and codes.
    data["REGION.code"] = data["LAD.code"].map(LAD_to_region_code)
    data["REGION.name"] = data["LAD.name"].map(LAD_to_region_name)

    # remove LAD columns
    # data = data.drop(["LAD.name", "LAD.code"], 1)
    data = data.drop(columns=["LAD.name", "LAD.code"])

    # Group rates by region and ethnicity and take the mean. gives mean rate by region, eth, sex, and age.
    data = data.groupby(vars_to_group, as_index=False).mean()
    # rename region and eth columns. done later in BaseHandler instead.
    #columns = list(data.columns)
    #columns[:2] = ["location", "ethnicity"]
    #data.columns = columns
    # save rate tables.
    if cache:
        print("Caching intermediate rate table to:", file_output)
        data.to_csv(file_output, index=True)

    return data


def main(file_source):

    file_name = "Mortality2011_LEEDS1_2.csv"
    data = pd.read_csv(file_source + file_name, index_col=0)
    d1 = collapse_LAD_to_region(data, file_source + "regional_" + file_name)

    file_name = "Fertility2011_LEEDS1_2.csv"
    data = pd.read_csv(file_source + file_name, index_col=0)  # Specifying index column removes extraneous column of unnecessary data
    d2 = collapse_LAD_to_region(data, file_source + "regional_" + file_name)
    return d1, d2


# HR 17/04/23 To get all years of NewEthPop fertility and mortality data (as format identical for both)
def compile_years(stubs,
                  input_dir,
                  year_range=YEAR_RANGE_DEFAULT,
                  by_region=BY_REGION_DEFAULT):

    # Get all files present
    input_files = [file for file in os.listdir(input_dir) if stubs[0] in file and stubs[1] in file]
    input_files.sort()
    # print("Input files:", input_files)

    # Get dict of all years present and corresponding input files
    year_dict = {int(file.removeprefix(stubs[0]).removesuffix(stubs[1])): os.path.join(input_dir, file) for file in input_files}
    years_present = sorted(list(year_dict.keys()))

    bad_value = 2061
    if bad_value in years_present:
        years_present = [y for y in years_present if y != bad_value]
    # print("Years present:", list(years_present))

    if not year_range:
        # If year range to grab not specified, just get all present in folder
        year_range = [min(years_present), max(years_present)]
    # elif year_range[0] > year_range[1]:
    #     # Flip if passed in wrong order
    #     year_range[0], year_range[1] = year_range[1], year_range[0]

    # Get nearest range of available years
    year_range[0] = get_nearest(years_present, year_range[0])
    year_range[1] = get_nearest(years_present, year_range[1])
    print("Year range:", year_range)
    years = list(range(year_range[0], year_range[1] + 1))
    print("Years:", years)

    df_dict = {year: pd.DataFrame(pd.read_csv(file, index_col=0)).set_index('LAD.name') for year, file in year_dict.items() if year in years}

    # df_final = pd.concat(df_dict.values(), keys=df_dict.keys())
    df_final = pd.concat(df_dict.values(), keys=df_dict.keys(), names=['year']).reset_index()

    # Collapse per-LA data to per_region
    if by_region:
        vars_to_group = VARS_TO_GROUP_DEFAULT
        vars_to_group.append('year')  # Add year to variables to retain (i.e. not take mean)
        df_final = collapse_LAD_to_region(df_final, file_output=None, vars_to_group=vars_to_group, cache=False)

    return df_final, year_range


# HR 19/04/23 Caching here so can be called from elsewhere
def cache_fertility_by_region(stubs=FERT_STUBS,
                              input_dir=FERT_DIR_DEFAULT,
                              year_range=YEAR_RANGE_DEFAULT,
                              by_region=True,
                              output_prefix="regional_fertility_",
                              output_folder=PERSISTENT_DATA_DIR):

    # Grab all NewEthPop data and cache
    try:
        print("Trying to parse and cache intermediate fertility data to folder:", output_folder, "...")
        df, year_range_out = compile_years(stubs=stubs,
                                           input_dir=input_dir,
                                           year_range=year_range,
                                           by_region=by_region)

    except FileNotFoundError as e:
        print("Could not find NewEthPop data")
        print("If you do not have the NewEthPop fertility data, download it from the following link and copy the folder to persistent_data/:")
        print("https: // reshare.ukdataservice.ac.uk / 852508 /")
        print("\n", e, "\n")
        return None

    # Cache to CSV
    # out_filename = output_prefix + str(year_range_out[0]) + "_" + str(year_range_out[1]) + ".csv"
    out_filename = output_prefix + 'newethpop.csv'
    out_fullpath = os.path.join(output_folder, out_filename)
    print("Caching intermediate fertility data for year range", year_range_out, "to:", out_fullpath, "...")
    print("Year range may differ from those specified according to the degree of overlap with NewEthPop data")

    if not os.path.exists(output_folder):
        print("Output folder not present, creating...")
        os.makedirs(output_folder)
    df.to_csv(out_fullpath, index=True)
    print("Done")
    return out_fullpath


# HR 19/04/23 Caching here so can be called from elsewhere
def cache_mortality_by_region(stubs=MORT_STUBS,
                              input_dir=MORT_DIR_DEFAULT,
                              year_range=YEAR_RANGE_DEFAULT,
                              by_region=True,
                              output_prefix="regional_mortality_",
                              output_folder=PERSISTENT_DATA_DIR):

    # Grab all NewEthPop data and cache
    try:
        print("Trying to parse and cache intermediate mortality data to folder:", output_folder, "...")
        df, year_range_out = compile_years(stubs=stubs,
                                           input_dir=input_dir,
                                           year_range=year_range,
                                           by_region=by_region)

    except FileNotFoundError as e:
        print("Could not find NewEthPop data")
        print("If you do not have the NewEthPop mortality data, download it from the following link and copy the folder to persistent_data/:")
        print("https: // reshare.ukdataservice.ac.uk / 852508 /")
        print("\n", e, "\n")
        return None

    # Cache to CSV
    # out_filename = output_prefix + str(year_range_out[0]) + "_" + str(year_range_out[1]) + ".csv"
    out_filename = output_prefix + 'newethpop.csv'
    out_fullpath = os.path.join(output_folder, out_filename)
    print("Caching intermediate mortality data for year range", year_range_out, "to:", out_fullpath, "...")
    print("Year range may differ from those specified according to the degree of overlap with NewEthPop data")

    if not os.path.exists(output_folder):
        print("Output folder not present, creating...")
        os.makedirs(output_folder)
    df.to_csv(out_fullpath, index=True)
    print("Done")
    return out_fullpath


def transform_rate_table(df, year_start, year_end, age_start, age_end, unique_sex=None):

    """Function that transforms an input rate dataframe into a format readable for Vivarium
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


if __name__ == "__main__":
    # file_source = PERSISTENT_DATA_DIR
    # d1, d2 = main(file_source)

    ## HR 15/08/24 Testing to mimic rate table construction by mortality and fertility rate table classes
    ## after moving transform_rate_table to here
    cache_fertility_by_region()
    cache_mortality_by_region()
