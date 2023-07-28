"""
27/7/23
Luke Archer

This script is part of the data generation pipeline, and will focus on inflating the population based on their survey
analysis weights. Each record in our dataframe will be duplicated n times, where n = (100 * sample_weight). I.e. a
record with a sample weight of 1.00 will be duplicated 100 times, weight of 2.50 will be duplicated 250 times.
"""

import pandas as pd
import numpy as np

import US_utils


def inflate_population(data):
    print('Inflating population based on analysis weight...')
    print(f"Dropping {data['weight'].isna().sum()} records due to missing weight.")
    data = data[~data['weight'].isna()]
    data = data.loc[np.repeat(data.index.values, (data['weight'] * 100))]
    data['pidp'] = data.groupby(['pidp', 'time'])

    # we need to make sure that all new records are given unique IDs, which is complicated because these pidps will most
    # often span multiple years. That means we need to probably do 2 groupings, first by pidp alone


    data.drop('weight',
              axis=1,
              inplace=True)
    return data


def main():
    maxyr = US_utils.get_data_maxyr()

    print('Generating inflated population...')
    years = np.arange(2009, maxyr)
    file_names = [f"data/final_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    data = inflate_population(data)

    US_utils.save_multiple_files(data, years, "data/inflated_US/", "")


if __name__ == '__main__':
    main()
