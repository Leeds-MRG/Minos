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
import argparse
import os
from rpy2.robjects.packages import importr

import US_utils
from minos.modules import r_utils


# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None  # default='warn' #supress SettingWithCopyWarning


def expand_repl(US_2018):
    """ 
    Expand and reweight replenishing populations (16-year-olds) from 2019 - 2070
    
    Parameters
    ----------
    US_2018 : pandas.DataFrame
        Datafile derived from Understanding Society 2018 including all ages
    projections : pandas.DataFrame
        Datafile containing counts by age and sex from 2008 to 2070 (2008-2020 from midyear estimates, 2021 - 2070 from
        principal population projections).
    Returns
    -------
    expanded_repl : pandas.DataFrame
        Expanded dataset (copy of original 16-year-olds for each year from 2018 to 2070) reweighted by sex
    """

    # just select the 16 and 17-year-olds in 2018 to be copied and reweighted (replace age as 16)
    repl_2018 = US_2018[(US_2018['age'].isin([16, 17]))]
    repl_2018['age'] = 16
    # We can't have 16-year-olds with higher educ than level 2 (these are all from 17 yos) so replace these with 2
    repl_2018['education_state'][repl_2018['education_state'] > 2] = 2

    expanded_repl = pd.DataFrame()
    # first copy original dataset for every year from 2018 (current) - 2070
    for year in range(2018, 2071, 1):
        # first get copy of 2018 16 (and 17) -year-olds
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
        new_repl['pidp'] = new_repl['pidp'] + year + 1000000 + new_repl.index

        #print(f"There are {len(new_repl)} people in the replenishing population in year {year}.")

        ## Previously tried duplicating the 16 year olds but this is hard in Scotland mode as there are only 3 people
        # Duplicate this population(TWICE) so we have double the number of 16-year-olds to work with
        # Instead now we take both 16 and 17-year-olds, and call them all 16-year-olds
        # new_repl = pd.concat([new_repl, new_repl, new_repl], ignore_index=True)

        # now append to original repl
        expanded_repl = pd.concat([expanded_repl, new_repl], axis=0)

    return expanded_repl


def reweight_repl(expanded_repl, projections):
    """
    
    Parameters
    ----------
    expanded_repl
    projections
    
    Returns
    -------
    
    """
    ## Now reweight by sex and year
    print('Reweighting by sex, ethnic group, and year...')

    ## SCOTLAND MODE FORCED A CHANGE IN ETHNICITY
    # People categorised as white vs non-white instead of all ethnic groups due to small numbers
    # Re-categorise the projections and sum across ethnic groups
    #projections['ethnicity'][~projections['ethnicity'].isin(['WBI', 'WHO'])] = 'Non-White'
    #projections['ethnicity'][projections['ethnicity'].isin(['WBI', 'WHO'])] = 'White'
    #projections = projections.groupby(['sex', 'age', 'time', 'ethnicity'])['count'].sum().reset_index()

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

    return(expanded_repl)


def predict_education(repl, transition_dir):
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
    rpy2_modules = {"base": importr('base'),
                    "stats": importr('stats'),
                    "nnet": importr("nnet"),
                    "ordinal": importr('ordinal'),
                    "zeroinfl": importr("pscl"),
                    "geepack": importr("geepack"),
                    }
    transition_model = r_utils.load_transitions("education_state/nnet/education_state_2018_2019", rpy2_modules, path=transition_dir)
    prob_df = r_utils.predict_nnet(transition_model, rpy2_modules, repl, cols)

    repl['max_educ'] = np.nan
    for i, distribution in enumerate(prob_df.iterrows()):
        repl.loc[i, 'max_educ'] = choice(a=prob_df.columns, size=1, p=distribution[1])[0]

    return repl


def generate_replenishing(projections, scotland_mode, cross_validation):

    output_dir = 'data/replenishing'
    data_source = 'final_US'
    transition_dir = 'data/transitions'

    if scotland_mode:
        data_source = 'scotland_US'
        output_dir = 'data/replenishing/scotland'
        transition_dir = 'data/transitions/scotland'
    if cross_validation:
        data_source = 'final_US/cross_validation/batch1'
        output_dir = 'data/replenishing/cross_validation'
        transition_dir = 'data/transitions/cross_validation/version1'

    # first collect and load the datafile for 2018
    file_name = f"data/{data_source}/2020_US_cohort.csv"
    data = pd.read_csv(file_name)

    # expand and reweight the population
    expanded_repl = expand_repl(data)

    reweighted_repl = reweight_repl(expanded_repl, projections)

    # finally, predict the highest level of educ
    final_repl = predict_education(reweighted_repl, transition_dir)

    US_utils.check_output_dir(output_dir)
    final_repl.to_csv(f'{output_dir}/replenishing_pop_2019-2070.csv', index=False)
    print('Replenishing population generated for 2019 - 2070')


def main():

    # Use argparse to select between normal and scotland mode
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation",
                                     usage='use "%(prog)s --help" for more information')

    parser.add_argument("-s", "--scotland", action='store_true', default=False,
                        help="Select Scotland mode to only produce replenishing using scottish sample.")
    parser.add_argument("-c", "--cross_validation", dest='crossval', action='store_true', default=False,
                        help="Select cross-validation mode to produce cross-validation replenishing population.")

    args = parser.parse_args()
    scotland_mode = args.scotland
    cross_validation = args.crossval


    # read in projected population counts from 2008-2070
    proj_file = "persistent_data/age-sex-ethnic_projections_2008-2061.csv"
    projections = pd.read_csv(proj_file)
    # rename and drop some columns to prepare
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    generate_replenishing(projections, scotland_mode, cross_validation)


if __name__ == "__main__":
    main()
