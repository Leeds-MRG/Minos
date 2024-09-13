"""
HR 09/09/24 To create all-GB or regional synthpop for specified year(s)
Initially for fertility model testing but includes (untested) bootstrapping and priority group functionality
"""

import pandas as pd
import numpy as np
import os
from os.path import dirname as up
import US_utils
import argparse


PERSISTENT_DIR = os.path.join(up(up(up(__file__))), 'persistent_data')
SPATIAL_DIR = os.path.join(PERSISTENT_DIR, 'spatial_data')
DATA_DIR = os.path.join(up(up(up(__file__))), 'data')

SP_FILES = {2019: 'sp_ind_wavek_census2011_est2020_8cons.csv',  # UKDS version for wave k, 2020 (2019 Minos)
            # 2017: '',  # Older version for wave i, 2018 (2019 Minos) by Chris et al.
            # 2019: '',  # Alternative versions from Kashif, early 2023
            # 2020: 'SPIndividuals_Census2011Est2021_USWaveK_UK_population.csv',
            # 2021: '',
            }
LSOA_FILES = {'scotland': 'scotland_data_zones.csv',
              'glasgow': 'glasgow_data_zones.csv',
              'manchester': 'manchester_lsoas.csv',
              'sheffield': 'sheffield_lsoas.csv',
              # 'cardiff': '',  # To do
              # 'west_midlands': '',  # To do
              }
LSOA_WARD_MAPS = {(2011, 2022): 'LSOA11_WD22_LAD22_EW_LU.xlsx',
                  # (2021, 2024): '',
                  }
LSOA_WARD_MAPS_S = {(2011, 2022): "DataZone2011lookup_2022-05-31.csv",
                    # (2021, 2024): ''
                    }
WARD_REGION_MAPS = {2022: 'Ward_to_Local_Authority_District_to_County_to_Region_to_Country_(December_2022)_Lookup_in_United_Kingdom.csv',
                    # 2024: '',
                    }

LSOA_YEAR_DEFAULT = 2011
WARD_YEAR_DEFAULT = 2022

REGION_DEFAULT = 'gb'
PERCENT_DEFAULT = 0.1
YEARS_DEFAULT = (2019,)
VAR_LIST_DEFAULT_FERTILITY = ('pidp',
                              'hidp',
                              'alive',
                              'sex',
                              'age',
                              'birth_year',
                              'region',
                              'ethnicity',
                              'nkids',
                              'nkids_ind',
                              'child_ages',
                              'nresp',
                              'nnewborn',
                              # 'weight',
                              'education_state',
                              'max_educ',
                              'hh_int_m',
                              'hh_int_y',
                              'time',
                              'Date',
                              )


# HR 10/09/24 LSOA to ward mapping, adapted from IE(II)
def get_lsoa_to_ward_map(lsoa_year=LSOA_YEAR_DEFAULT,
                         ward_year=WARD_YEAR_DEFAULT,
                         ):
    lsoa_col = "LSOA" + str(lsoa_year)[-2:] + "CD"
    ward_col = "WD" + str(ward_year)[-2:] + "CD"

    map_file = LSOA_WARD_MAPS[(lsoa_year, ward_year)]
    map_file_fullpath = os.path.join(SPATIAL_DIR, map_file)
    try:
        map_ew_ = pd.read_csv(map_file_fullpath)
    except:
        map_ew_ = pd.read_excel(map_file_fullpath)
    map_ew = dict(zip(map_ew_[lsoa_col], map_ew_[ward_col]))

    lsoa_col_scot = "DZ2011_Code"
    ward_col_scot = "MMWard_Code"
    map_s_fullpath = os.path.join(SPATIAL_DIR, LSOA_WARD_MAPS_S[lsoa_year, ward_year])
    map_s_ = pd.read_csv(map_s_fullpath, encoding='ISO-8859-1')
    map_s = dict(zip(map_s_[lsoa_col_scot], map_s_[ward_col_scot]))

    map_ews = map_ew | map_s
    return map_ews


# HR 10/09/24 Ward to region mapping, adapted from IE(II)
def get_ward_to_region_map(year=WARD_YEAR_DEFAULT,
                           ):
    ward_col = "WD" + str(year)[-2:] + "CD"
    ward_name_col = "WD" + str(year)[-2:] + "NM"
    la_col = "LAD" + str(year)[-2:] + "CD"
    la_name_col = "LAD" + str(year)[-2:] + "NM"
    region_col = "RGN" + str(year)[-2:] + "CD"
    region_name_col = "RGN" + str(year)[-2:] + "NM"
    country_col = "CTRY" + str(year)[-2:] + "CD"
    country_name_col = "CTRY" + str(year)[-2:] + "NM"

    file_full = os.path.join(SPATIAL_DIR, WARD_REGION_MAPS[year])
    raw_ews = pd.read_csv(file_full)

    # Drop NI data
    raw_ews = raw_ews.loc[raw_ews[ward_col].str[0].isin(('E', 'S', 'W'))]

    # Paste country (code and name) to region columns for S and W
    mask = raw_ews[ward_col].str[0].isin(('S', 'W'))
    raw_ews.loc[mask, region_col] = raw_ews.loc[mask, country_col]
    raw_ews.loc[mask, region_name_col] = raw_ews.loc[mask, country_name_col]

    ward_la_map = dict(zip(raw_ews[ward_col], raw_ews[la_col]))
    la_region_map = dict(zip(raw_ews[la_col], raw_ews[region_col]))
    return ward_la_map, la_region_map


# HR 10/09/24 Add spatial attributes (ward, LA, region) in one go
def add_spatial_attributes(pop,
                           lsoa_year=LSOA_YEAR_DEFAULT,
                           ward_year=WARD_YEAR_DEFAULT,
                           ):
    ward_map = get_lsoa_to_ward_map(lsoa_year, ward_year)
    ward_la_map, la_region_map = get_ward_to_region_map(ward_year)

    lsoa_col = "LSOA" + str(lsoa_year)[-2:] + "CD"
    ward_col = "WD" + str(ward_year)[-2:] + "CD"
    la_col = "LA" + str(ward_year)[-2:] + "CD"
    region_col = "RGN" + str(ward_year)[-2:] + "CD"

    pop[ward_col] = pop[lsoa_col].map(ward_map)
    pop[la_col] = pop[ward_col].map(ward_la_map)
    pop[region_col] = pop[la_col].map(la_region_map)
    return pop


def merge_with_synthpop(synthpop,
                        us_data,
                        merge_column="pidp",
                        ):
    """ Merge US data on synthetic pop individual data.

    Parameters
    ----------
    synthpop, us_data : pd.DataFrame
        synthetic spatial population and US data to merge
        merge_column : str
    Returns
    -------
    merged_data : pd.DataFrame
        Merged synthetic US data with spatial component
    """
    # synthpop[f"new_{merge_column}"] = np.arange(synthpop.shape[0])
    synthpop[merge_column] = synthpop[merge_column].astype(int)
    merged_data = synthpop.merge(us_data, how='left', on=merge_column)
    return merged_data


def get_lsoas(region,
              lsoa_year=LSOA_YEAR_DEFAULT,
              ):
    """

    Parameters
    ----------
    region : str
        Region to return subset for
    lsoa_year : int
        Year to use for LSOA definitions
    Returns
    -------
    data_zones : list
        Data zones in specified region
    """

    if region in LSOA_FILES:
        lsoa_file = LSOA_FILES[region]
        lsoa_fullpath = os.path.join(SPATIAL_DIR, lsoa_file)
        lsoas = pd.read_csv(lsoa_fullpath)['LSOA11CD']
    elif region == 'gb':
        lsoas = list(get_lsoa_to_ward_map(lsoa_year=lsoa_year).keys())
    else:
        print("Error! Invalid region defined for spatial subsetting")
        raise ValueError

    return lsoas


def take_sample(data,
                percent=PERCENT_DEFAULT,
                ):
    """

    Parameters
    ----------
    data : Pandas DataFrame
        Population from which sample will be taken
    percent : float
        Percentage of population to be sampled

    Returns
    -------

    """
    # Shuffle data to randomise
    sample_data = data.sample(frac=1)

    if percent != 100:
        sample_data = sample_data.sample(frac=percent/100)
        print(f"Taking {percent}% of sample giving {sample_data.shape[0]} individuals")

    # Force sample weights to 1 as US weights (if retained) are not longer representative
    sample_data['weight'] = 1
    return sample_data


def main(region=REGION_DEFAULT,
         bootstrapping=False,
         priority_sub=False,
         multisamp=False,
         years=list(YEARS_DEFAULT),
         var_list=list(VAR_LIST_DEFAULT_FERTILITY),
         percentage=PERCENT_DEFAULT,
         n=100_000,
         ):
    """
    1. Grab individual synthetic population for GB
    2. Take regional subset of synthetic population, as specified
        e.g. Glasgow City region / GMCA / Sheffield City Region / Scotland
    3. Merge synthetic population on Understanding Society data to get individuals with spatial component

    Parameters
    ----------
    region : str
        Region of GB to be subsetted
    bootstrapping : bool
        Whether to bootstrap on top of synthetic sample to induce uncertainty
    priority_sub : bool
        Whether to select for priority groups
    multisamp : bool
        Whether to create multiple samples
    years : tuple
        Years for which synthetic population will be calculated
    var_list : tuple
        Understanding Society variables to be used to populate synthetic population; restrict to reduce memory
    percentage : float
        Percentage of population to be sampled
    n : int
        Number of bootstrapping samples to take.
    """
    var_list = list(var_list)
    for year in years:

        # Get raw (i.e. unpopulated) synthetic population
        synthpop_file_path = os.path.join(SPATIAL_DIR, SP_FILES[year])
        try:
            sp = pd.read_csv(synthpop_file_path)
        except FileNotFoundError as e:
            print(e)
            print("Synthetic population file not found at {} for {}. Please ask MINOS maintainers for access".format(synthpop_file_path, year))
            raise

        # Get LSOAs in region to be subsetted, then filter
        lsoa_col = "LSOA" + str(LSOA_YEAR_DEFAULT)[-2:] + "CD"
        lsoas = get_lsoas(region)
        # sp.rename(columns={'ZoneID': lsoa_col}, inplace=True)  # Rename column that is present in some version of synthpop
        # sp = sp.loc[sp['LSOA11CD'].isin(lsoas)]
        sp = sp.loc[sp['ZoneID'].isin(lsoas)]

        ''' HR 11/09/24 Bootstrapping not tested '''
        # # If bootstrapping sample from subsetted synthetic data with replacement (i.e. allow multiple instances)
        # if bootstrapping:
        #     sp = sp.sample(frac=1)  # Shuffle to randomise
        #     sp = sp.sample(n, replace=True)

        ''' HR 11/09/24 Priority group subsetting not tested '''
        # # Generate a dataset of individuals in priority subgroups
        # # 1. NEED TO MERGE ON PRIORITY COLUMNS HERE FIRST...
        # if priority_sub:
        #     priority_columns = [col for col in sp.columns if col.startswith('priority_')]
        #     mask = sp[priority_columns].any(axis=1)
        #     sp = sp[mask]
        # # 2. ...THEN DROP EXTRANEOUS COLUMNS HERE AS NECESSARY

        # Get US data, filtering for required variables only
        us_fullpath = os.path.join(DATA_DIR, 'imputed_final_US', str(year) + '_US_cohort.csv')
        us_data = pd.read_csv(us_fullpath)[var_list]

        ''' HR 11/09/24 Multisampling not tested '''
        # Generate n sample populations
        if multisamp:
            n_samples = 10
            for i in range(n_samples):
                # Get sample of synthpop and merge with US data
                multi = take_sample(sp, percentage)
                merged_multi = merge_with_synthpop(multi, us_data)

                # Scramble pidp
                merged_multi['pidp'] = merged_multi.reset_index().index

                file_multi = os.path.join(DATA_DIR, f'scaled_{region}_US_{i+1}/')
                US_utils.save_file(merged_multi, file_multi, '', year)

        # Get sample of synthpop and merge with US data
        samp = take_sample(sp, percentage)
        merged = merge_with_synthpop(samp, us_data)

        # Compute proportion of synthpop individuals present in US data, i.e. degree of overlap - should be 100%!
        ids_sp = set(sp['pidp'].unique())
        ids_us = set(us_data['pidp'].unique())
        n_overlap = len(ids_sp & ids_us)  # Get set intersection of pidps
        n_total = len(ids_sp)
        prop = 100*n_overlap/n_total
        print('Degree of overlap b/t synthpop and US data: {}/{} ({}%)'.format(n_overlap, n_total, prop))

        # Scramble pidp
        merged['pidp'] = merged.reset_index().index

        if priority_sub:
            # file_dest = os.path.join(DATA_DIR, f'{region}_priority_sub/')
            print('Priority sub true')
            pass  # HR 11/09/24 Bypassing priority group functionality as not tested
        else:
            print('Priority sub false')
            file_dest = os.path.join(DATA_DIR, f'scaled_{region}_US/')
        US_utils.save_file(merged, file_dest, '', year)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Individual-level synthetic population creation'
                                                 'using Understanding Society')
    parser.add_argument("-r", "--region", required=True, type=str, default=REGION_DEFAULT,
                        help="The region to subset for the GB synthetic population")
    parser.add_argument("-b", "--do_bootstrapping", required=False, action='store_false',
                        help="Bootstrapping the synthetic population to include uncertainty?")
    parser.add_argument('-pr', '--priority_subgroups', required=False, default=False,
                        help="Create a synthetic population of only the people in a priority subgroup")
    parser.add_argument('-m', '--multisample', required=False, action='store_true',
                        help='Generate 10 distinct samples to evaluate sample uncertainty; should only be used if the'
                             'percentage of the sample is less than 100% (otherwise you would just duplicate that '
                             'sample')
    parser.add_argument("-v", "--var_list", required=False, type=list, default=VAR_LIST_DEFAULT_FERTILITY,
                        help='List of US variables to merge with synthetic population')
    parser.add_argument("-y", "--years", required=False, type=list, default=YEARS_DEFAULT,
                        help='Years for which populated synthetic population is to be created')
    parser.add_argument("-p", "--percentage", required=False, type=float, default=PERCENT_DEFAULT,
                        help="Percentage of synthetic population to use (e.g. 0-100%)")
    parser.add_argument("-s", "--bootstrap_sample_size", required=False, type=int, default=1,
                        help="How many bootstrap samples to take; should only be used with do_bootstrapping above")

    args = vars(parser.parse_args())
    print(args)

    region = args['region']
    do_bootstrapping = args['do_bootstrapping']
    priority_subgroups = args['priority_subgroups']
    multisample = args['multisample']
    years = args['years']
    var_list = args['var_list']
    percentage = args['percentage']
    bootstrap_sample_size = args['bootstrap_sample_size']

    main(region=region,
         bootstrapping=do_bootstrapping,
         priority_sub=priority_subgroups,
         multisamp=multisample,
         years=years,
         var_list=var_list,
         percentage=percentage,
         n=bootstrap_sample_size,
         )
