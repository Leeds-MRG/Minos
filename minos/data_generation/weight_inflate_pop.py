"""
27/7/23
Luke Archer

This script is part of the data generation pipeline, and will focus on inflating the population based on their survey
analysis weights. Each record in our dataframe will be duplicated n times, where n = (1000 * sample_weight). I.e. a
record with a sample weight of 1.00 will be duplicated 1000 times, weight of 0.50 will be duplicated 500 times.
"""

import pandas as pd
import numpy as np

import US_utils


def inflate_pop_all_years(data):
    print('Inflating population based on analysis weight...')
    print(f"Dropping {data['weight'].isna().sum()} records due to missing weight.")
    data = data[~data['weight'].isna()]
    # use np.repeat to duplicate copies weight * 1000 times
    data = data.loc[np.repeat(data.index.values, (data['weight'] * 1000))]
    # define a groupID (after grouping by pidp and time) to generate unique pidp's on duplicated records
    data['groupID'] = data.groupby(['pidp', 'time'])['pidp'].rank(method='first')
    # generate unique pidp using groupID
    data['pidp'] = (data['pidp'] * 1000) + data['groupID']

    data.drop(['weight', 'groupID'],
              axis=1,
              inplace=True)
    # last check that no duplicated pidp's remain
    assert (data.duplicated(['pidp', 'time']).sum() == 0)

    return data


def inflate_pop_single_year(data, year):

    data_year = data[data['time'] == year]

    # we need to make sure that all new records are given unique IDs, which is complicated because these pidps will most
    # often span multiple years. There is most likely a clever solution with groupby and transform but I can't get it
    # to work, instead I'm going to try looping through each pidp

    # first duplicate records weight * 100 times
    data_year = data_year.loc[np.repeat(data_year.index.values, (data_year['weight'] * 1000))]
    # now groupby and add a groupID var for modifying the pidp later
    data_year['groupID'] = data_year.groupby('pidp')['pidp'].rank(method='first')
    # finally can modify the pipd by increasing by factor of 1000 + groupID
    data_year['pidp'] = (data_year['pidp'] * 1000) + data_year['groupID']

    # reset index to remove duplicated indices
    data_year.reset_index(drop=True, inplace=True)

    # Finally drop the groupID and weight variables
    data_year.drop(['weight', 'groupID'],
                   axis=1,
                   inplace=True)

    # last check that no duplicated pidp's remain
    assert(data_year.duplicated('pidp').sum() == 0)

    return data_year


def main():
    maxyr = US_utils.get_data_maxyr()

    print('Generating inflated population...')
    years = np.arange(2009, maxyr)
    file_names = [f"data/final_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    data = inflate_pop_all_years(data)
    #data_inf_2014 = inflate_pop_single_year(data, year=2014)
    #data_inf_2020 = inflate_pop_single_year(data, year=2020)

    US_utils.save_multiple_files(data, years, "data/inflated_US/", "")
    #US_utils.save_file(data_inf_2014, 'data/inflated_US/', '', 2014)
    #US_utils.save_file(data_inf_2020, 'data/inflated_US/', '', 2020)


if __name__ == '__main__':
    main()
