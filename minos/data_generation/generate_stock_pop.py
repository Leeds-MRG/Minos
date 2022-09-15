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

import US_utils


# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning


def reweight_stock(data, projections, ethpop):
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
        Expanded dataset (copy of original 16 year olds for each year from 2018 - 2070) reweighted by sex
    """
    print('Reweighting by age and sex...')
    # first group_by sex and year and sum weight for totals, then rename before merge
    summed_weights = data.groupby(['sex', 'time', 'age'])['weight'].sum().reset_index()
    summed_weights = summed_weights.rename(columns={'weight': 'sum_weight', 'year': 'time'})

    # merge the projection data and summed weights for reweighting
    data = data.merge(projections, on=['time', 'sex', 'age'])
    data = data.merge(summed_weights, on=['time', 'sex', 'age'])

    reweighted_data = data

    # now reweight new population file
    reweighted_data['weight'] = (reweighted_data['weight'] * reweighted_data['count']) / reweighted_data['sum_weight']
    # drop extra columns
    reweighted_data.drop(labels = ['count', 'sum_weight'],
                         inplace=True,
                         axis=1)

    print('Reweighting by ethnicity...')
    # first group_by sex and ethnicity and sum weight for totals, then rename before merge
    summed_weights = data.groupby(['sex', 'ethnicity', 'age'])['weight'].sum().reset_index()
    summed_weights = summed_weights.rename(columns={'weight': 'sum_weight'})

    # merge the projection data and summed weights for reweighting
    reweighted_data = reweighted_data.merge(ethpop, on=['sex', 'ethnicity', 'age'])
    reweighted_data = reweighted_data.merge(summed_weights, on=['sex', 'ethnicity', 'age'])

    # now reweight new population file
    reweighted_data['weight'] = (reweighted_data['weight'] * reweighted_data['count']) / reweighted_data['sum_weight']
    # drop extra columns
    reweighted_data.drop(labels=['count', 'sum_weight'],
                         inplace=True,
                         axis=1)

    return reweighted_data


def generate_stock(projections, ethpop):
    print('Generating stock population...')
    years = np.arange(2009, 2020)
    file_names = [f"data/complete_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # TODO: We reweight the stock population only because reweighting the repl generates very different values to those
    #   we started with (started with mean ~1, ended with mean in the thousands). We could however trust the analysis
    #   weight from the survey and just transform the replenishing population weights to bring the mean back to ~1.
    data = reweight_stock(data, projections, ethpop)

    # Needs a max_educ column despite it not being important for the majority of people
    # Will be used in the future for the 16-25 year olds at the beginning of the simulation
    data['max_educ'] = data['education_state']

    US_utils.save_multiple_files(data, years, "data/final_US/", "")


def main():
    # read in projected population counts from 2008-2070
    proj_file = "persistent_data/pop_projections_2008-2070.csv"
    projections = pd.read_csv(proj_file)
    # rename and drop some columns to prepare
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    # read in ethpop for 2011
    ethpop_file = 'persistent_data/ethpop_2011.csv'
    ethpop = pd.read_csv(ethpop_file)
    ethpop = ethpop.drop(labels='Unnamed: 0', axis=1)


    #generate_replenishing(projections)

    generate_stock(projections, ethpop)



if __name__ == "__main__":
    main()