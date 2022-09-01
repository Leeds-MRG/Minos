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
sex to ensure
"""

import pandas as pd
import numpy as np

import US_utils


# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning


def expand_and_reweight_repl(US_2018, projections):
    """ Expand and reweight replenishing populations (16 year olds) from 2019 - 2070

    Parameters
    ----------
    US_2018 : pandas.DataFrame
        Datafile derived from Understanding Society 2018 including all ages
    projections : pandas.DataFrame
        Datafile containing counts by age and sex from 2008 - 2070 (2008-2020 from midyear estimates, 2021 - 2070 from
        principal population projections.
    Returns
    -------
    expanded_repl : pandas.DataFrame
        Expanded dataset (copy of original 16 year olds for each year from 2018 - 2070) reweighted by sex
    """

    # just select the 16 year olds in 2018 to be copied and reweighted
    repl_2018 = US_2018[(US_2018['age'] == 16)]
    expanded_repl = pd.DataFrame()
    # first copy original dataset for every year from 2018 (current) - 2070
    for year in range(2018, 2071, 1):
        # first get copy of 2018 16 year olds
        new_repl = repl_2018
        # change time (for entry year)
        new_repl['time'] = year
        # change birth year
        new_repl['birth_year'] = new_repl['birth_year'] + (year - 2017)
        # change interview year
        new_repl['hh_int_y'] = new_repl['hh_int_y'].astype(int) + (year - 2017)
        # now update Date variable (just use US_utils function
        new_repl = US_utils.generate_interview_date_var(new_repl)
        # adjust pidp to ensure unique values (have checked this and made sure this will never give us a duplicate)
        new_repl['pidp'] = new_repl['pidp'] + year + 1000000

        # now append to original repl
        expanded_repl = pd.concat([expanded_repl, new_repl], axis=0)

    # first group_by sex and year and sum weight for totals, then rename before merge
    summed_weights = expanded_repl.groupby(['sex', 'time'])['weight'].sum().reset_index()
    summed_weights = summed_weights.rename(columns={'weight': 'sum_weight', 'year': 'time'})

    # merge the projection data and summed weights for reweighting
    expanded_repl = expanded_repl.merge(projections, on=['time', 'sex', 'age'])
    expanded_repl = expanded_repl.merge(summed_weights, on=['time', 'sex'])

    # now reweight new population file
    expanded_repl['weight'] = (expanded_repl['weight'] * expanded_repl['count']) / expanded_repl['sum_weight']

    return expanded_repl


def generate_replenishing(projections):
    # first collect and load the datafile for 2018
    file_name = "data/complete_US/2018_US_cohort.csv"
    data = pd.read_csv(file_name)

    repl = expand_and_reweight_repl(data, projections)

    output_dir = 'data/replenishing/'
    US_utils.check_output_dir(output_dir)
    repl.to_csv(output_dir + 'replenishing_pop_2019-2070.csv')


def reweight_stock(data, projections):
    """

    Parameters
    ----------
    US_2018 : pandas.DataFrame
        Datafile derived from Understanding Society 2018 including all ages
    projections : pandas.DataFrame
        Datafile containing counts by age and sex from 2008 - 2070 (2008-2020 from midyear estimates, 2021 - 2070 from
        principal population projections.
    Returns
    -------
    expanded_repl : pandas.DataFrame
        Expanded dataset (copy of original 16 year olds for each year from 2018 - 2070) reweighted by sex
    """
    # first group_by sex and year and sum weight for totals, then rename before merge
    summed_weights = data.groupby(['sex', 'time', 'age'])['weight'].sum().reset_index()
    summed_weights = summed_weights.rename(columns={'weight': 'sum_weight', 'year': 'time'})

    # merge the projection data and summed weights for reweighting
    data = data.merge(projections, on=['time', 'sex', 'age'])
    data = data.merge(summed_weights, on=['time', 'sex', 'age'])

    reweighted_data = data

    # now reweight new population file
    reweighted_data['weight'] = (reweighted_data['weight'] * reweighted_data['count']) / reweighted_data['sum_weight']

    return reweighted_data


def generate_stock(projections):
    years = np.arange(2009, 2020)
    file_names = [f"data/complete_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    data = reweight_stock(data, projections)

    US_utils.save_multiple_files(data, years, "data/final_US/", "")

def main():
    # read in projected population counts from 2008-2070
    proj_file = "persistent_data/pop_projections_2008-2070.csv"
    projections = pd.read_csv(proj_file)
    # rename and drop some columns to prepare
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    generate_replenishing(projections)

    generate_stock(projections)



if __name__ == "__main__":
    main()
