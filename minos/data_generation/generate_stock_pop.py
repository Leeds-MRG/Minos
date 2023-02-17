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


def generate_stock(projections):
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

    # Set loneliness and ncigs as int
    data['loneliness'] = data['loneliness'].astype('int64')
    data['ncigs'] = data['ncigs'].astype('int64')
    data['neighbourhood_safety'] = data['neighbourhood_safety'].astype('int64')
    data['nutrition_quality'] = data['nutrition_quality'].astype('int64')
    data['housing_quality'] = data['housing_quality'].astype('int64')

    US_utils.save_multiple_files(data, years, "data/final_US/", "")


def main():
    # read in projected population counts from 2011-2061
    proj_file = "persistent_data/age-sex-ethnic_projections_2008-2061.csv"
    projections = pd.read_csv(proj_file)
    # rename and drop some columns to prepare
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    generate_stock(projections)


if __name__ == "__main__":
    main()
