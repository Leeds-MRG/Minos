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


def predict_education(data, transition_dir, predict_yr):
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

    # Set min and max ages for prediction. Max age to transition into an education level is 30, so stop predicting as 29
    age_min = 16
    age_max = 29

    print(f"Start year in predict_education is set to {predict_yr}.")

    #dat_predict = data[data['time'] == predict_yr]
    dat_predict = data.sort_values(['pidp', 'time']).groupby('pidp').tail(1)
    #dat_predict = data.loc[data.groupby('pidp')['max_educ'].idxmax()]

    # get the last record for each individual
    #dat_predict = data.sort_values(['pidp', 'time']).groupby(['pidp']).last()
    # also get the pidp's of all predicted individuals so we know who to replace at the end
    predicted_pidps = dat_predict['pidp']

    # Doing max_educ prediction here.
    # Using the transition model in transition_dir
    # We will only do prediction for 16-30 YO's in the kick off year, as educ states can only change within these ages

    # get the 16-25 year olds in 2020 (current kick off year)
    dat_youth = dat_predict[(dat_predict['age'] >= age_min) & (dat_predict['age'] <= age_max)].reset_index()

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

    # dat_youth = dat_youth[['pidp', 'time', 'education_state', 'max_educ']]
    dat_youth = dat_youth[['pidp', 'education_state', 'max_educ']]

    # Finally merge dat_youth back onto data
    # data = data.merge(dat_youth, on=['pidp', 'time'], how='left', suffixes=('_data', '_youth'))
    dat_predict = dat_predict.merge(dat_youth, on=['pidp'], how='left', suffixes=('_data', '_youth'))
    # handle duplicated columns
    dat_predict['education_state'] = -9
    dat_predict['education_state'][dat_predict['age'] > age_max] = dat_predict['education_state_data']
    dat_predict['education_state'][dat_predict['age'] <= age_max] = dat_predict['education_state_youth']
    dat_predict['max_educ'] = -9
    dat_predict['max_educ'][dat_predict['age'] > age_max] = dat_predict['max_educ_data']
    dat_predict['max_educ'][dat_predict['age'] <= age_max] = dat_predict['max_educ_youth']

    dat_predict.drop(labels=['education_state_data', 'education_state_youth', 'max_educ_data', 'max_educ_youth'],
              axis=1,
              inplace=True)

    # set people back to FT education if max_educ > education_state (i.e. haven't yet reached highest qualification)
    dat_predict['S7_labour_state'][dat_predict['max_educ'] > dat_predict['education_state']] = 'FT Education'

    # final step is to attach dat_predict back to data (replace the max_educ column essentially) and backward fill
    # within pidp groups
    dat_predict = dat_predict[['pidp', 'time', 'max_educ']]
    data = data.merge(dat_predict, on=['pidp', 'time'], how='left')
    # Now replace all
    data['max_educ'] = np.nan
    #data['max_educ'][[data['pidp'] not in predicted_pidps]] = data['max_educ_x']
    #data['max_educ'][[data['pidp'] in predicted_pidps]] = data['max_educ_y']

    data['max_educ'][~data['pidp'].isin(predicted_pidps)] = data['max_educ_x']
    data['max_educ'][data['pidp'].isin(predicted_pidps)] = data['max_educ_y']




    #data['max_educ'][data['time'] != predict_yr] = data['max_educ_x']
    #data['max_educ'][data['time'] == predict_yr] = data['max_educ_y']
    #data[data.sort_values(['pidp', 'time']).groupby('pidp').tail(1)] = data['max_educ_y']
    #data.loc[data.groupby('pidp').max_educ.idxmax()] = data['max_educ_y']

    # now groupby and bfill max_educ
    #data['max_educ'] = data[['pidp', 'max_educ']].groupby(by=["pidp"], sort=False, as_index=False).bfill()
    data.sort_values('time', inplace=True)
    data['max_educ'] = data.groupby(by=['pidp'], sort=False)['max_educ'].bfill()

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

    # first collect and load the datafile for 2020
    # file_name = f"data/{source}/2020_US_cohort.csv"
    # data = pd.read_csv(file_name)

    # Needs a max_educ column despite it not being important for the majority of people
    # Will be used in the future for the 16-25 year olds at the beginning of the simulation
    data['max_educ'] = data['education_state']

    data = predict_education(data, transition_dir, predict_yr=maxyr-1)

    US_utils.save_multiple_files(data, years, f"data/{out_dir}/", "")

    #US_utils.check_output_dir(out_dir)
    #data.to_csv(f'data/{out_dir}/2020_US_cohort.csv', index=False)


if __name__ == '__main__':
    # Use argparse to select between normal and cross-validation
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation",
                                     usage='use "%(prog)s --help" for more information')

    parser.add_argument("-c", "--cross_validation", dest='crossval', action='store_true', default=False,
                        help="Select cross-validation mode to produce cross-validation populations.")

    args = parser.parse_args()
    crossval = args.crossval

    main(crossval)
