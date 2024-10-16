#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script reweights input populations to MINOS to ensure the starting and replenishment populations are representative
now and into the future.

The two sources of data for reweighting populations are the midyear estimates from 2008 - 2020, and the principal
population projections from 2021 - 2070 (principal projections can be extended to 2120 but I doubt MINOS will ever
want to model that far into the future, ~50 years seems like a reasonable maximum but can be expanded if necessary).

Currently we take the 16 year olds from the final data file for 2018 (start date of the simulations), generate identical
copies of this population for every year of the simulation to 2070, then adjust the analysis weights (`weight` var) by
sex and ethnicity to ensure representative populations into the future.
"""

import pandas as pd
import numpy as np
import argparse

import US_utils


# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning


def reweight_stock(data, projections):
    """

    Parameters
    ----------
    US_2018 : pandas.DataFrame
        Datafile derived from Understanding Society 2018 including all ages
    projections : pandas.DataFrame
        Datafile containing counts by age and sex from 2008 - 2070 (2008-2020 from midyear estimates, 2021 - 2070 from
        principal population projections.
    ethpop : pandas.DataFrame
        Datafile containing counts by ethnic group and age for 2011. Would be good to get these projected into the future.
    Returns
    -------
    expanded_repl : pandas.DataFrame
        Expanded dataset reweighted by sex
    """
    print('Reweighting by age, sex, and ethnic group...')
    # first group_by sex and year and sum weight for totals, then rename before merge
    summed_weights = data.groupby(['sex', 'time', 'age', 'ethnicity'])['weight'].sum().reset_index()
    summed_weights = summed_weights.rename(columns={'weight': 'sum_weight', 'year': 'time'})

    # merge the projection data and summed weights for reweighting
    data = data.merge(projections, on=['time', 'sex', 'age', 'ethnicity'])
    data = data.merge(summed_weights, on=['time', 'sex', 'age', 'ethnicity'])

    reweighted_data = data

    # now reweight new population file
    reweighted_data['weight'] = (reweighted_data['weight'] * reweighted_data['count']) / reweighted_data['sum_weight']
    # drop extra columns
    reweighted_data.drop(labels=['count', 'sum_weight'],
                         inplace=True,
                         axis=1)

    # Final step is to rescale the new weights to range(0,1). The previous large weights broke some of the transition
    # models, specifically the zero-inflated poisson for ncigs
    #TODO: There is another method of rescaling using the numpy.ptp() method that might be faster. Maybe worth looking into (see link below)
    # https://stackoverflow.com/questions/38103467/rescaling-to-0-1-certain-columns-from-pandas-python-dataframe
    reweighted_data['weight'] = (reweighted_data['weight'] - min(reweighted_data['weight'])) / (max(reweighted_data['weight']) - min(reweighted_data['weight']))

    return reweighted_data


def wave_data_copy(data, var, copy_year, paste_year, var_type):
    """
    Unfortunately due to some of the variables we rely on not being available in all waves, we have to take a copy of
    some information and paste it onto another year. Due to the current aim (24/02/23) being to include wave 12 of data
    and use wave 12 (2020 in our timescale) as the kick off point, we need to copy nutrition_quality onto this wave.
    Nutrition_quality is available every second wave, so we will copy wave 11 data onto wave 12. I also don't want to
    lose any of the new respondents in wave 12 that don't have a nutrition_quality value, so I might impute those people
    with the mean of the population.

    Parameters
    ----------
    data : pd.dataframe
        Dataframe of all variables across all years
    var : str
        String variable we want to copy onto another year
    copy_year : int
        Year to copy data from
    paste_year : int
        Year to paste data to

    Returns
    -------
    data_merged : pd.dataframe
        Final dataset with {var} copied from {copy_year} to {paste_year}
    """
    print(f"Copying wave {copy_year} {var} onto wave {paste_year} sample...")

    # get temporary dataframe of pidp, time, and nutrition_quality from 2019
    tmp = data[['pidp', 'time', var]][data['time'] == copy_year]
    # change time to 2018 for tmp
    tmp['time'] = paste_year

    # replace -9 values in paste_year with Nonetype
    data[var][data['time'] == paste_year] = None

    # now merge and combine the two separate nutrition_quality columns (now with suffix') into one col
    data_merged = data.merge(right=tmp,
                             how='left',
                             on=['pidp', 'time'])

    # set up merge labels
    var_x = var + '_x'
    var_y = var + '_y'

    data_merged[var] = -9
    data_merged[var][data_merged['time'] != paste_year] = data_merged[var_x]
    data_merged[var][data_merged['time'] == paste_year] = data_merged[var_y]
    # drop intermediate columns
    data_merged.drop(labels=[var_x, var_y], axis=1, inplace=True)

    # last step is to impute the still missing with the mean value. Without this we would have to drop all the
    # missing values, meaning anybody not in wave 11 would be removed. This is dodgy because we don't know who should be
    # missing, but I don't know what else to do
    # data_merged[var][(data_merged['time'] == paste_year) & (data_merged[var].isna())] = round(data_merged[var][data_merged['time'] == paste_year].mean())
    if var_type == 'continuous':
        data_merged[var][(data_merged['time'] == paste_year) & (data_merged[var].isna())] = \
            data_merged[var][data_merged['time'] == paste_year].median()
    elif var_type == 'ordinal':
        data_merged[var][(data_merged['time'] == paste_year) & (data_merged[var].isna())] = \
            data_merged[var][data_merged['time'] == paste_year].value_counts().index[0]

    return data_merged


def generate_stock(projections, cross_validation):
    maxyr = US_utils.get_data_maxyr()

    print('Generating stock population...')
    years = np.arange(2009, maxyr)
    file_names = [f"data/complete_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # TODO: We reweight the stock population only because reweighting the repl generates very different values to those
    #   we started with (started with mean ~1, ended with mean in the thousands). We could however trust the analysis
    #   weight from the survey and just transform the replenishing population weights to bring the mean back to ~1.
    data = reweight_stock(data, projections)

    # Needs a max_educ column despite it not being important for the majority of people
    # Will be used in the future for the 16-25 year olds at the beginning of the simulation
    data['max_educ'] = data['education_state']

    # # copy 2017 loneliness data onto 2014 for cross-validation runs
    data = wave_data_copy(data,
                          var='loneliness',
                          copy_year=2017,
                          paste_year=2015,
                          var_type='ordinal')
    # # copy wave 11 nutrition_quality onto wave 12
    # data = wave_data_copy(data,
    #                       var='nutrition_quality',
    #                       copy_year=2019,
    #                       paste_year=2020)
    # # copy wave 7 nutrition_quality onto wave 6
    # data = wave_data_copy(data,
    #                       var='nutrition_quality',
    #                       copy_year=2015,
    #                       paste_year=2014)
    data = wave_data_copy(data,
                          var='neighbourhood_safety',
                          copy_year=2020,
                          paste_year=2021,
                          var_type='ordinal')
    data = wave_data_copy(data,
                          var='neighbourhood_safety',
                          copy_year=2014,
                          paste_year=2015,
                          var_type='ordinal')
    data = wave_data_copy(data,
                          var='S7_neighbourhood_safety',
                          copy_year=2020,
                          paste_year=2021,
                          var_type='ordinal')
    data = wave_data_copy(data,
                          var='S7_neighbourhood_safety',
                          copy_year=2014,
                          paste_year=2015,
                          var_type='ordinal')

    # Set loneliness and ncigs as int
    data['loneliness'] = data['loneliness'].astype('int64')
    data['ncigs'] = data['ncigs'].astype('int64')
    data['neighbourhood_safety'] = data['neighbourhood_safety'].astype('int64')
    data['nutrition_quality'] = data['nutrition_quality'].astype('int64')
    #data['housing_quality'] = data['housing_quality'].astype('int64')

    US_utils.save_multiple_files(data, years, "data/final_US/", "")

    # Cross Validation stuff
    # Split pop in half with rng - half to transitions to fit models, half to simulate
    if cross_validation:
        # grab all unique pidps and take half at random
        # TODO: the sample() function can take weights to return equally weighted samples. Problem being that we use
        #   yearly sample weights. Need to either get longitudinal weights or take average of yearly. Or something else.
        all_pidp = pd.Series(data['pidp'].unique())
        #trans_samp = all_pidp.sample(frac=0.5, random_state=1)  # random_state is for seeding and reproducibility

        # Shuffle the pidps randomly and split into 5 chunks
        shuffled = all_pidp.sample(frac=1, random_state=1)
        split = np.array_split(shuffled, 5)

        # Now create separate transition and simulation datasets and save them in subfolders of final_US
        bat1 = data[data['pidp'].isin(split[0])]
        bat2 = data[data['pidp'].isin(split[1])]
        bat3 = data[data['pidp'].isin(split[2])]
        bat4 = data[data['pidp'].isin(split[3])]
        bat5 = data[data['pidp'].isin(split[4])]

        US_utils.save_multiple_files(bat1, years, "data/final_US/cross_validation/batch1/", "")
        US_utils.save_multiple_files(bat2, years, "data/final_US/cross_validation/batch2/", "")
        US_utils.save_multiple_files(bat3, years, "data/final_US/cross_validation/batch3/", "")
        US_utils.save_multiple_files(bat4, years, "data/final_US/cross_validation/batch4/", "")
        US_utils.save_multiple_files(bat5, years, "data/final_US/cross_validation/batch5/", "")


def main():
    # Use argparse to select between normal and cross-validation
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation",
                                     usage='use "%(prog)s --help" for more information')

    parser.add_argument("-c", "--cross_validation", dest='crossval', action='store_true', default=False,
                        help="Select cross-validation mode to produce cross-validation populations.")

    args = parser.parse_args()
    cross_validation = args.crossval

    # read in projected population counts from 2011-2061
    proj_file = "persistent_data/age-sex-ethnic_projections_2008-2061.csv"
    projections = pd.read_csv(proj_file)
    # rename and drop some columns to prepare
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    generate_stock(projections, cross_validation)


if __name__ == "__main__":
    main()
