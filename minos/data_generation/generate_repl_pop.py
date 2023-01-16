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
from numpy.random import choice
import random

import US_utils
from minos.modules import r_utils


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
        # Duplicate this population(TWICE) so we have double the number of 16-year-olds to work with
        new_repl = pd.concat([new_repl, new_repl, new_repl], ignore_index=True)
        # adjust pidp to ensure unique values (have checked this and made sure this will never give us a duplicate)
        new_repl['pidp'] = new_repl['pidp'] + year + 1000000 + new_repl.index

        # now append to original repl
        expanded_repl = pd.concat([expanded_repl, new_repl], axis=0)

    ## Now reweight by sex and year
    print('Reweighting by sex, ethnic group, and year...')
    # first group_by sex and year and sum weight for totals, then rename before merge
    summed_weights = expanded_repl.groupby(['sex', 'time', 'ethnicity'])['weight'].sum().reset_index()
    summed_weights = summed_weights.rename(columns={'weight': 'sum_weight', 'year': 'time'})

    # merge the projection data and summed weights for reweighting
    expanded_repl = expanded_repl.merge(projections, on=['time', 'sex', 'age', 'ethnicity'])
    expanded_repl = expanded_repl.merge(summed_weights, on=['time', 'sex', 'ethnicity'])

    # now reweight new population file
    expanded_repl['weight'] = (expanded_repl['weight'] * expanded_repl['count']) / expanded_repl['sum_weight']

    expanded_repl.drop(labels=['count', 'sum_weight'],
                         inplace=True,
                         axis=1)

    # Final step is to rescale to range(0,1) because larger weights broke some transition models
    expanded_repl['weight'] = (expanded_repl['weight'] - min(expanded_repl['weight'])) / (
                max(expanded_repl['weight']) - min(expanded_repl['weight']))

    return expanded_repl


def predict_education(repl):
    """
    This function predicts the highest level of education that will be attained by simulants in the model.

    There are 2 steps to this process:
        1. First the highest education will be predicted for all 16 year olds in the replenishing population, which
            will then be used in the simulation to decide who and when to change their education.
        2. Predict education for all 16-25 year olds, as they may not have finished education and can still improve.

    Parameters
    ----------
    repl

    Returns
    -------

    """
    print("Predicting max education level for replenishing populations...")

    ## First load in the transition model and produce a probability distribution for max education
    # Then create an empty variable for max_educ, and make a choice from the probability distribution about
    # which level to assign as highest education attainment

    # generate list of columns for prediction output (no educ==4 in Understanding Society)
    cols = ['0', '1', '2', '3', '5', '6', '7']

    transition_model = r_utils.load_transitions(f"data/transitions/education_state/nnet/education_state_2018_2019", "")
    prob_df = r_utils.predict_nnet(transition_model, repl, cols)

    repl['max_educ'] = np.nan
    for i, distribution in enumerate(prob_df.iterrows()):
        repl.loc[i, 'max_educ'] = choice(a=prob_df.columns, size=1, p=distribution[1])[0]

    return repl


def generate_replenishing(projections):
    print('Generating replenishing population...')
    # first collect and load the datafile for 2018
    file_name = "data/complete_US/2018_US_cohort.csv"
    data = pd.read_csv(file_name)

    # expand and reweight the population
    repl = expand_and_reweight_repl(data, projections)

    # finally, predict the highest level of educ
    final_repl = predict_education(repl)

    output_dir = 'data/replenishing/'
    US_utils.check_output_dir(output_dir)
    final_repl.to_csv(output_dir + 'replenishing_pop_2019-2070.csv', index=False)
    print('Replenishing population generated for 2019 - 2070')


def main():
    # read in projected population counts from 2008-2070
    proj_file = "persistent_data/age-sex-ethnic_projections_2008-2061.csv"
    projections = pd.read_csv(proj_file)
    # rename and drop some columns to prepare
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    generate_replenishing(projections)


if __name__ == "__main__":
    main()
