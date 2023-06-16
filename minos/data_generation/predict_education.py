#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script does prediction of max_education level for all replenishing populations, and those in the stock population
if aged 16-25. This value is then used to decide what level of education an individual achieves, which is a
deterministic process within the pipeline with levels being reached at specific ages.
"""

import pandas as pd
import numpy as np
import argparse
from numpy.random import choice
from rpy2.robjects.packages import importr

import US_utils
from minos.modules import r_utils


def predict_education(data, transition_dir):
    """
    This function predicts the highest level of education that will be attained by simulants in the model.
    There are 2 steps to this process:
        1. First the highest education will be predicted for all 16 year olds in the replenishing population, which
            will then be used in the simulation to decide who and when to change their education.
        2. Predict education for all 16-25 year olds, as they may not have finished education and can still improve.

    IMPORTANT NOTE: The `start_year` variable is hardcoded here, and needs to be updated if we ever change the start
    year of the simulation. This is bad, but any better solution would be quite time consuming and I don't have time
    for it right now. Sorry...

    Parameters
    ----------
    repl
    Returns
    -------
    """
    print("Predicting max education level for replenishing populations...")

    # TODO: Find a way to NOT hardcode this. Probably with some Makefile variable.
    start_year = 2020

    print(f"Start year in predict_education is set to {start_year}.")

    # Doing max_educ prediction here.
    # Using the transition model in transition_dir
    # We will only do prediction for 16-25 YO's in the kick off year, as educ states will change a lot so makes more sense
    # to do a single snapshot

    # get the 16-25 year olds in 2020 (current kick off year)
    dat_youth = data[(data['time'] == start_year) & (data['age'] > 15) & (data['age'] < 26)].reset_index()

    # generate list of columns for prediction output (no educ==4 in Understanding Society)
    cols = ['0', '1', '2', '3', '5', '6', '7']
    rpy2_modules = {"base": importr('base'),
                    "stats": importr('stats'),
                    "nnet": importr("nnet")}

    transition_model = r_utils.load_transitions("education_state/nnet/education_state_2018_2019",
                                                path=transition_dir,
                                                rpy2_modules=rpy2_modules)
    prob_df = r_utils.predict_nnet(transition_model,
                                   rpy2Modules=rpy2_modules,
                                   current=dat_youth,
                                   columns=cols)

    dat_youth['max_educ'] = np.nan
    for i, distribution in enumerate(prob_df.iterrows()):
        dat_youth.loc[i, 'max_educ'] = choice(a=prob_df.columns, size=1, p=distribution[1])[0]

    # Now handle the situation where current educ is higher than max_educ
    # first copy education state onto another var and convert to int
    dat_youth['max_educ'] = dat_youth['max_educ'].astype(int)
    dat_youth['max_educ'][dat_youth['education_state'] > dat_youth['max_educ']] = dat_youth['education_state']

    dat_youth = dat_youth[['pidp', 'time', 'education_state', 'max_educ']]

    # Finally merge dat_youth back onto data
    data = data.merge(dat_youth, on=['pidp', 'time'], how='left')
    # handle duplicated columns
    data['education_state'] = -9
    data['education_state'][data['time'] != start_year] = data['education_state_x']
    data['education_state'][data['time'] == start_year] = data['education_state_y']
    data['max_educ'] = -9
    data['max_educ'][data['time'] != start_year] = data['max_educ_x']
    data['max_educ'][data['time'] == start_year] = data['max_educ_y']

    data.drop(labels=['education_state_x', 'education_state_y', 'max_educ_x', 'max_educ_y'],
              axis=1,
              inplace=True)

    return data


def main(cross_validation):
    maxyr = US_utils.get_data_maxyr()

    source = 'final_US'
    transition_dir = 'data/transitions'
    out_dir = 'stock_US'

    if cross_validation:
        source = 'final_US/cross_validation/simulation'
        transition_dir = 'data/transitions/cross_validation'
        out_dir = 'stock_US/cross_validation/simulation'

    print('Generating stock population...')
    years = np.arange(2009, maxyr)
    file_names = [f"data/{source}/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # Needs a max_educ column despite it not being important for the majority of people
    # Will be used in the future for the 16-25 year olds at the beginning of the simulation
    data['max_educ'] = data['education_state']

    data = predict_education(data, transition_dir)

    US_utils.save_multiple_files(data, years, f"data/{out_dir}/", "")


if __name__ == '__main__':
    # Use argparse to select between normal and cross-validation
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation",
                                     usage='use "%(prog)s --help" for more information')

    parser.add_argument("-c", "--cross_validation", dest='crossval', action='store_true', default=False,
                        help="Select cross-validation mode to produce cross-validation populations.")

    args = parser.parse_args()
    crossval = args.crossval

    main(crossval)
