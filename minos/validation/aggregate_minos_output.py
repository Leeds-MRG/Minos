import pandas as pd
import glob as glob
import numpy as np
import argparse
import os
import yaml
from datetime import datetime
from multiprocessing import Pool
from itertools import repeat
from aggregate_subset_functions import dynamic_subset_function


def aggregate_csv(filename, v, agg_method, subset_func_string, mode):
    'converts a filename to a pandas dataframe'
    df = pd.read_csv(filename, low_memory=False)
    if subset_func_string:
       df = dynamic_subset_function(df, subset_func_string, mode)
    return agg_method(df[v])


def aggregate_variables_by_year(source, mode, years, tag, v, method, subset_func_string):
    """ Get aggregate values for value v using method function. Do this over the specified source and years.
    A MINOS batch run under a certain intervention will produce 1000 files over 10 years and 100 iterations.
    These files will all be in the source directory.
    For each year this function grabs all files. If the model runs from 2010-2020 there would be 100 files for 2010.
    For each file within a year the method function is used over variable v.
    The default is taking the mean over SF12 using np.nanmean.
    For each file this will produce a scalar value.
    This scalar value is used along with a year and tag tag as a row in the output dataframe df.
    These tags determine which year and which source the dataframe row belongs to.
    If the source is a £25 uplift intervention the tag tag will correspond to this.
    This is used later by sns.lineplot.
    This is repeated over all years to produce an output dataframe with 1000 rows.
    Each row is an aggregated v value for each iteration and year pair.

    Parameters
    ----------
    source: str
        What directory is being aggregated. E.g. output/baseline/
    mode: bool
        Is this aggregation being done on the scottish pop?
    years, v : list
        What range of years are being used. What set of variables are being aggregated.
    tag: str
        Which data source are being processed. adds a tag column to the df with this tag.
    method: func
    Returns
    -------
    df: pd.DataFrame
        Data frame with columns year, tag and v. Year is year of observation, tag is MINOS batch run and intervention
        it has come from, v is aggregated variable. Usually SF12.
    """

    df = pd.DataFrame()
    for year in years:
        files = glob.glob(os.path.join(source, f"*{year}.csv"))  # grab all files at source with suffix year.csv.

        # 2018 is special case - not simulated yet and therefore doesn't have any of the tags for subset functions
        # Therefore we are just going to get everyone alive for now
        if year == years[0]:
            subset_func_string = 'who_alive'
        with Pool() as pool:
            aggregated_means = pool.starmap(aggregate_csv,
                                            zip(files, repeat(v), repeat(method), repeat(subset_func_string), repeat(mode)))

        new_df = pd.DataFrame(aggregated_means)
        new_df.columns = [v]
        new_df['year'] = year
        new_df['tag'] = tag
        df = pd.concat([df, new_df])
    return df


def main(source, mode, years, tags, v, method, subset_function_string):
    """
    Parameters
    ----------
    source: list
        MINOS batch run to process.
    years: list
        Range of years to plot.
    tag: list
        Corresponding name of the MINOS batch source. Usually what intervention was used. Baseline Uplift, etc..
    v: str
        What variable to aggregate on. Defaults to SF_12
    method: func
        What function to aggregate over. Default np.nanmean.
    destination: str
        Where to save final plots. Defaults to original source.
    subset_function_string : str
        What chain of subset functions are aggregated on?
    Returns
    -------
    df: pd.DataFrame
        Dataframe df containing 3 columns year, tag, v. Long frame of aggregates by year and source.
    """
    print(f"Aggregating for source {source}, tag {tags} using {method.__name__} over {v}")
    destination = os.path.join(source, f"aggregated_{v}_by_{method.__name__}.csv")
    df = aggregate_variables_by_year(source, mode, years, tag, v, method, subset_function_string)
    df.to_csv(destination, index=False)
    print(f"Saved file to {destination}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Aggregate output data from a MINOS batch run directory.")
    parser.add_argument("-m", "--mode", required=True, type=str,
                        help="The output directory for Minos data. Usually output/*")
    parser.add_argument("-d", "--directories", required=True, type=str,
                        help="Subdirectories within source that are aggregated. Usually experiment names baseline childUplift etc.")
    parser.add_argument("-t", "--tags", required=True, type=str,
                        help="Corresponding name tags for which data is being processed. I.E which intervention Baseline/£20 Uplift etc. Used as label in later plots.")
    parser.add_argument("-v", "--variable", required=False, type=str, default='SF_12',
                        help="What variable from Minos is being aggregated. Defaults to SF12.")
    parser.add_argument("-a", "--aggregate_method", required=False, type=str, default="nanmean",
                        help="What method is used to aggregate population. Defaults to np.nanmean.")
    parser.add_argument("-f", "--subset_function", required=False, type=str, default=None,
                        help="What subset of the population is used in analysis. E.g. only look at the treated subset of the population")

    args = vars(parser.parse_args())
    mode = args['mode']
    directories = args['directories']
    tags = args['tags']
    v = args['variable']
    method = args['aggregate_method']
    subset_functions = args['subset_function']

    if method == "nanmean":
        method = np.nanmean
    else:
        #TODO no better way to do this to my knowledge without eval() which shouldn't be used.
        raise ValueError("Unknown aggregate function specified. Please add specifc function required at 'aggregate_minos_output.py")
        #TODO replace this if...else... with a try...except block around the main function below.


    directories = directories.split(",")
    tags = tags.split(",")
    subset_functions = subset_functions.split(',')

    for directory, tag, subset_function_string in zip(directories, tags, subset_functions):

        # Handle the datetime folder inside the output. Select most recent run
        runtime = os.listdir(os.path.abspath(os.path.join('output/', mode, directory)))
        #TODO: Replace this block (or encapsulate) in a try except block for proper error handling
        if len(runtime) > 1:
            # if more than 1, select most recent datetime
            runtime = max(runtime, key=lambda d: datetime.strptime(d, "%Y_%m_%d_%H_%M_%S"))
        elif len(runtime) == 1:
            runtime = runtime[0]  # os.listdir returns a list, we only have 1 element
        else:
            raise RuntimeError("The output directory supplied contains no subdirectories, and therefore no data to "
                               "aggregate. Please check the output directory.")

        batch_source = os.path.join('output/', mode, directory, runtime)
        #  batch_source = os.path.join(source, directory)
        # get years from MINOS batch run config yaml.
        with open(f"{batch_source}/config_file.yml", "r") as stream:
            config = yaml.safe_load(stream)
            start_year = config['time']['start']['year']
            end_year = config['time']['end']['year']
            years = np.arange(start_year, end_year)
        #print(batch_source, years)
        df = main(batch_source, mode, years, tag, v, method, subset_function_string)
