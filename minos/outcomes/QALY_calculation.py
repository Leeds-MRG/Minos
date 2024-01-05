"""
author: Luke Archer
date: 30/10/23

This script will calculate the QALYs for each year for a specific intervention (or baseline). First this will just be
at the whole population level, but will be expanded soon to allow for calculations within specified groups.
"""

import argparse
import pandas as pd
import numpy as np
import os
import yaml
from multiprocessing import Pool
from itertools import repeat
import glob as glob
from aggregate_subset_functions import dynamic_subset_function

import minos.utils as utils


def aggregate_csv(filename, intervention):
    """

    Parameters
    ----------
    filename : basestring
        Name of the file to be aggregated for a specific year.
    intervention : basestring
        Name of intervention, to specify whether to record certain values as 0 (in case of baseline) or calculate them
        from data.

    Returns
    -------
     : vector
        Vector of information about that specific run for that specific year. This is to be aggregated in the
        Multiprocessing pool to generate a dataframe with each row corresponding to a specific run in a specific
        intervention.
    """
    df = pd.read_csv(filename, low_memory=False)
    #if subset_func_string:
        #df = dynamic_subset_function(df, subset_func_string, mode)
    #print(f"For substring chain {subset_func_string} there are {df.shape[0]} eligible individuals in the dataset.")

    # get the run_id from the filename and attach to the dataset (if batch run)
    filename_nopath = filename.split(sep='/')[-1]
    if filename_nopath.count('_') == 0:
        # If no underscore in filename, this is not a batch run and run_id can be set to 1
        run_id = 1  # 0 would be more pythonic but the batch runs start at 1 so I'm copying that
    else:
        # If underscores present, take run_id from filename
        run_id = filename_nopath.split(sep='_')[0].lstrip('0')

    # record size of not dead population in year
    # record size of dead population in year
    # from both of these pieces of information we can calculate incidence of mortality
    total_pop_size = len(df)
    alive_pop = df['alive'].value_counts()['alive']
    dead_pop = df['alive'].value_counts()['dead']

    # to investigate the mortality rate we can look at the ratio of dead to alive and compare across years
    alive_ratio = (alive_pop / total_pop_size) * 100

    # drop zero weight samples
    df = df[df['weight'] > 0]
    # adjust SF_12 values by sampling weight
    df['SF_12_MCS'] = (df['SF_12_MCS'] * ((1 / df['weight']) / df['weight'].sum()))
    df['SF_12_PCS'] = (df['SF_12_PCS'] * ((1 / df['weight']) / df['weight'].sum()))
    # also adjust boost_amount
    df['boost_amount'] = (df['boost_amount'] * ((1 / df['weight']) / df['weight'].sum()))

    # record boost information for intervention runs, set to 0 for baseline
    if intervention == 'baseline':
        pop_boosted = 0
        total_boost = 0
    else:
        pop_boosted = df['income_boosted'].sum()
        total_boost = df['boost_amount'].sum()

    return [run_id, alive_pop, dead_pop, total_pop_size, pop_boosted, total_boost, alive_ratio, np.nanmean(df['SF_12_MCS']), np.nanmean(df['SF_12_PCS'])]


def calculate_qaly(df):
    """
    QALY calculation comes from Lawrence and Fleishman (2004) - https://pubmed.ncbi.nlm.nih.gov/15090102/

    In table 4 of the above paper, regression model coefficients were presented which allow the mapping of MCS and PCS
    scores onto EQ-5D, from which we can calculate utility scores.

    From the utility scores we can calculate QALYs by multiplying the utility score by the population size (alive).

    Parameters
    ----------
    df

    Returns
    -------

    """

    # Run without any subpopulations to worry about

    # First calculate utility score using values table 4 from Lawrence and Fleishman (2004)
    df['utility'] = -1.6984 + \
        (df['SF_12_PCS'] * 0.07927) + \
        (df['SF_12_MCS'] * 0.02859) + \
        ((df['SF_12_PCS'] * df['SF_12_MCS']) * -0.000126) + \
        ((df['SF_12_PCS'] * df['SF_12_PCS']) * -0.00141) + \
        ((df['SF_12_MCS'] * df['SF_12_MCS']) * -0.00014) + \
        ((df['SF_12_PCS'] * df['SF_12_PCS'] * df['SF_12_PCS']) * 0.0000107)

    # adjust for sample weight
    df['utility'] = df['utility'] * (df['weight'] / df['weight'].sum())

    # Now calculate QALYs by multiplying utility score by pop_size
    df['QALYs'] = df['utility'] * df['alive_pop']

    return df


def main(mode, intervention):

    # set file directory
    file_dir = os.path.join('output/', mode, intervention)
    runtime_list = os.listdir(os.path.abspath(file_dir))
    runtime = utils.get_latest_subdirectory(runtime_list)

    batch_source = os.path.join(file_dir, runtime)
    #  batch_source = os.path.join(source, directory)
    # get years from MINOS batch run config yaml.
    with open(f"{batch_source}/config_file.yml", "r") as stream:
        config = yaml.safe_load(stream)
        start_year = config['time']['start']['year']
        end_year = config['time']['end']['year']
        years = np.arange(start_year, end_year)

    combined_output = pd.DataFrame()
    # use multiprocessing to read in files and aggregating
    for year in years+1:
        files = glob.glob(os.path.join(batch_source, f"*{year}.csv"))  # grab all files at source with suffix year.csv.

        # aggregate the files using multiprocessing
        with Pool() as pool:
            aggregated_means = pool.starmap(aggregate_csv, zip(files, repeat(intervention)))

        new_df = pd.DataFrame(aggregated_means)
        new_df.columns = ['run_id', 'alive_pop', 'dead_pop', 'total_pop_size', 'pop_boosted', 'total_boost', 'alive_ratio', 'SF_12_MCS', 'SF_12_PCS']
        new_df['year'] = year
        new_df['intervention'] = intervention
        combined_output = pd.concat([combined_output, new_df])
        print(f'Finished aggregating data for year {year}...')

    print('Finished aggregating data...')

    qaly_df = calculate_qaly(combined_output)

    # finally, save qaly df into output directory
    # reorder columns first and sort by run_id and year
    # reorder first
    cols_to_front = ['run_id', 'year']
    qaly_df = qaly_df[cols_to_front + [col for col in qaly_df.columns if col not in cols_to_front]]
    # now sort
    qaly_df = qaly_df.sort_values(['run_id', 'year'], ascending=True)
    out_name = os.path.join(batch_source, 'qalys.csv')
    qaly_df.to_csv(out_name, index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Arguments for calculation QALYs over different experiments or "
                                                 "sub-populations.")

    parser.add_argument("-m", "--mode", required=True,
                        help="Which experiment are we calculating for? Options currently are default_config, SIPHER7,"
                             "and SIPHER7_glasgow.")
    parser.add_argument("-i", "--intervention", required=False, default="baseline",
                        help="Is this a baseline or intervention run? Which intervention if intervention?")

    args = parser.parse_args()

    mode = args.mode
    intervention = args.intervention

    main(mode, intervention)
