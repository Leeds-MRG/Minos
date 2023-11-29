""" File for projecting weights for a US cohort into the future.
If we have the 2013 population. Can we project weights forwards into 2018 2023 2028 etc.. to try and maintain representativeness
Mostly reusing Luke's work in generate_repl_pop.py
"""

import pandas as pd
from minos.data_generation.generate_stock_pop import reweight_stock
import numpy as np

def main(years, save):

    # get population
    # get projected weights by lookup.
    file_name = f"data/composite_US/{years[0]}_US_cohort.csv"
    data = pd.read_csv(file_name)
    main_time = data['time']
    data[f"{years[0]}_weight"] = data['weight']

    proj_file = "persistent_data/age-sex-ethnic_projections_2008-2061.csv"
    projections = pd.read_csv(proj_file)
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    for year in years[1:]:
        data['time'] = year
        print('Reweighting by sex, ethnic group, and year...')
        # first group_by sex and year and sum weight for totals, then rename before merge
        new_weights = reweight_stock(data, projections)[['pidp', 'weight']]
        new_weights.columns = ['pidp', 'plus_5_weight']
        data = data.merge(new_weights, on=['pidp'], how='left')
        data['plus_5_weight'] = data["plus_5_weight"].replace(np.nan, 0) # nans if pidp not found in stock pop. default to 0.

    data['time'] = main_time # reset time back to 2013 at the end.

    if save:
        data['plus_5_weight'].to_csv(f"data/extrapolated_weights_data_{years[0]}.csv")
    return data


if __name__ == '__main__':
    start_years = [2011, 2012, 2013]
    intervals = 5
    n_intervals = 1

    for start_year in start_years:
        years = list(range(start_year, start_year + (n_intervals * (intervals+1)), intervals))
        print(years)
        data = main(years, True)
