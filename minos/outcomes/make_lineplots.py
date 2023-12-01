""" single python function that makes lineplots from a list of arguments.

this file should not be run directly and is called from notebooks. e.g. Rmd notebooks.
"""

# This file is moving lineplot making into one file for the sake of sanity. It doesn't need to be as generaslied as it is now.

# 1. get all source files from some list of interventions.
# 2. aggregate all source files together

import pandas as pd
import re
from glob import glob
from multiprocessing import Pool
import os
from itertools import repeat
import numpy as np
import yaml
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from minos.outcomes.aggregate_subset_functions import dynamic_subset_function, get_required_intervention_variables, get_region_lsoas

pd.options.mode.chained_assignment = None  # default='warn'

def subset_minos_data(data, subset_func_string, mode):
    """ Take treated subset of MINOS output. E.g. only take individuals with children if assessing child benefit policy.

    Parameters
    ----------
    data: pd.DataFrame
    subset_func_string, mode : str
        subset_func_string determines what subset of the population to take. see aggregate_subset_functions.py for
        more details. mode determines whether the scottish population mode should be taken. This might be redundant in future
        if we agree to stick to full UK model.

    Returns
    -------
    subsetted_data : pd.DataFrame
        subsetted_data is the pandas dataframe MINOS output only including those would be intervened upon. e.g. households
        with children when assessing child benefit policy.
    """
    subsetted_data = dynamic_subset_function(data, subset_func_string, mode)
    return subsetted_data

def aggregate_percentage_counts(df, v):
    # for some ordinal variable return a groupby providing the percetage of the population in each variable.
    new_df = pd.DataFrame(df[v].value_counts(normalize=True))
    new_df['prct'] = new_df[new_df.columns[0]]
    new_df[v] = new_df.index
    new_df.reset_index(inplace=True, drop=True)
    return new_df

def aggregate_csv(file, subset_function_string=None, outcome_variable="SF_12", aggregate_method=np.nanmean,
                  mode="default_config", region=None):
    """

    Parameters
    ----------
    file, subset_function_string : string
        What MINOS output file to load and how to subset this file.
    outcome_variable, mode: str
        What variable of MINOS is the outcome and
    aggregate_method : func
    region : string
        What region is being subetted? Defaults to None
    Returns
    -------
    agg_value : float
        Scalar aggregate of a single MINOS output dataset. E.g. the mean SF12 value for all individuals in the desired subset.
    """
    required_columns = get_required_intervention_variables(subset_function_string)
    if region:
        required_columns.append("ZoneID")
    data = pd.read_csv(file, usecols=required_columns, low_memory=True,
                       engine='c')  # low_memory could be buggy but is faster.
    if subset_function_string:
        data = subset_minos_data(data, subset_function_string, mode)
    if region:
        if region == "edinburgh" or region == "scotland":
            region_lsoas = get_region_lsoas(region)["DZ2011_Code"]
        else:
            region_lsoas = get_region_lsoas(region)["lsoa11cd"]

        data = data.loc[data["ZoneID"].isin(region_lsoas), ]
        #print(data.shape)
    agg_value = aggregate_method(data, outcome_variable)
    return agg_value


def aggregate_variables_by_year(source, tag, years, subset_func_string, v="SF_12", ref="Baseline", method=np.nanmean,
                                mode="default_config", region=None):
    """ Get multiple MINOS files, subset and aggregate over some variable and aggregate method.

    Parameters
    ----------
    source: str
        What directory is being aggregated. E.g. output/baseline/
    mode: bool
        Is this aggregation being done on the scottish pop?
    years, v : list
        What range of years are being used. What set of variables are being aggregated.
    tag: str
        The written english name of the intervention being processed in source.
         Used in the 'tag' column to plot lineplot legend.
         E.g. source `livingWageIntervention` is the file path but `Living Wage Intervention` should go in the legend.
    method: func :
        What method is used to aggregate outcome variable data. Usually np.nanmean but nanmedian etc. can be used
    region string:
        Is a specific subregion of the data being used. e.g. glasgow region for scottish data.
    Returns
    -------
    aggregated_data: pd.DataFrame
        Data frame with columns year, tag and v. Year is year of observation, tag is MINOS batch run and intervention
        it has come from, v is aggregated variable. Usually SF12.
    """

    aggregated_data = pd.DataFrame()
    aggregated_means = []
    for year in years:
        files = glob(os.path.join(source, f"*{year}.csv"))  # grab all files at source with suffix year.csv.
        # files = files[:10]
        # 2018 is special case - not simulated yet and therefore doesn't have any of the tags for subset functions
        # Therefore we are just going to get everyone alive for now
        # TODO: Set this value from the config file so it only happens for the year before simulation (currently 2020) and isn't hardcoded
        with Pool() as pool:
            if year > 2020 or tag == ref:
                aggregated_means = pool.starmap(aggregate_csv,
                                                zip(files, repeat(subset_func_string), repeat(v), repeat(method),
                                                    repeat(mode), repeat(region)))
        if aggregated_means == []:  # if no datasets found for given year supply a dummy row.
            print(
                f"warning no datasets found for intervention {tag} and year {year}. This will result in a blank datapoint in the final lineplot.")
            aggregated_means = [None]

        if method == weighted_nanmean or method == child_uplift_cost_sum:
            single_year_aggregates = pd.DataFrame(aggregated_means, columns = [v])
            single_year_aggregates['year'] = year
            single_year_aggregates['tag'] = tag
            aggregated_data = pd.concat([aggregated_data, single_year_aggregates])
        elif v in ['housing_quality', 'neighbourhood_safety', 'loneliness']:
            for i, single_year_aggregate in enumerate(aggregated_means):
                single_year_aggregate['time'] = year
                single_year_aggregate['tag'] = tag
                single_year_aggregate['id'] = i
                aggregated_data = pd.concat([aggregated_data, single_year_aggregate])

    aggregated_data.reset_index(drop=True, inplace=True)
    return aggregated_data


def relative_scaling(df, v, ref):
    """ Scale aggregate data based on some reference source.

    For each year
        Find the mean of the reference column for each year xbar.
        Find the mean of the reference group x_bar.
        Divide all values within the year regardless of tag by xbar.
    E.g. reference = 'baseline' makes baseline values all 1.
    Any other policy change is relative to this.
    E.g. an uplift policy would likely produce values greater than 1 to signify increase in SF12 on average.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe df containing 3 columns year, tag, v. Long frame of aggregates by year and source.
    years: np.arange
        List of year
    v: str
        Variable to aggregate.
    ref: str
        Reference source to scale against.

    Returns
    -------
    df: pd.DataFrame
        Dataframe df containing 3 columns year, tag, v. Long frame of aggregates by year and source.
    """
    # if no reference column don't scale anything..
    if ref is not None:
        years = sorted(list(set(df['year'])))
        for i, year in enumerate(years):
            # get data for each year. get reference level sf12 for each year. divide all sf12 values be reference value.
            # sf12 for ref level will be 1. for other levels values >1 implies increase relative to baseline.
            # <1 implies reduction.

            year_df = df.loc[df['year'] == year,].copy()
            x_bar = np.nanmean(year_df.loc[year_df['tag'] == ref, v])
            year_df[v] /= x_bar
            if i == 0: # for first year only consider reference variable. e.g. baseline.
                year_df = year_df.loc[year_df['tag'] == ref, ]
            df.loc[df['year'] == year, v] = year_df[v]
    else:
        print("No reference ref defined. No relative scaling used. May make hard to read plots..")
    return df


def find_latest_source_file_path(file_path):
    """ A file path can have multiple runs of data that are sorted by time Y_m_d_H_M_S. Find the lastest one.

    Parameters
    ----------
    all_file_paths : list
        All directories in the all_file_paths directory. Should all have names as timestamps with form Y_m_d_H_M_S.
    Returns
    -------
    latest_file_path: str
        Returns the latest path in all_file_paths chronologically.
    """
    # replaced latest file search with regex because it keeps finding aggregate data and
    # .DSStore files and im slowly losing my mind.
    # sort file list and pull latest files until a regex date match is found.
    all_file_paths = sorted(os.listdir(file_path))
    # NOTE THIS IS AN EXACT MATCH. ANY FILE WITH STUFF EITHER SIDE OF A DATE WILL NOT BE FOUND.
    date_pattern = re.compile(r'^(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})$')
    if len(all_file_paths) > 1:
        # if more than 1, select most recent datetime
        while all_file_paths:
            file  = all_file_paths.pop()
            if date_pattern.match(file):
                latest_file_path = file
                break
        if not all_file_paths:
            raise RuntimeError("The output directory supplied contains no subdirectories, and therefore no data to "
                               "aggregate. Please check the output directory.")
        #latest_file_path = max(all_file_paths, key=lambda d: datetime.strptime(d, "%Y_%m_%d_%H_%M_%S"))
    elif len(all_file_paths) == 1:
        latest_file_path = all_file_paths[0]  # os.listdir returns a list, we only have 1 element
    else:
        raise RuntimeError("The output directory supplied contains no subdirectories, and therefore no data to "
                           "aggregate. Please check the output directory.")
    return os.path.join(file_path, latest_file_path)


def aggregate_lineplot(df, destination, prefix, v, method):
    """ Plot lineplot over sources and years for aggregated v.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with mean SF12 values over time by intervention.
    destination : str
        Where is the plot being saved to.
    Returns
    -------
    None
    """
    # seaborn line plot does this easily. change colours, line styles, and marker styles for easier readibility.
    df[v] -= 1  #  set centre at 0.

    # set year to int for formatting purposes
    df['year'] = pd.to_datetime(df['year'], format='%Y')

    # now rename some vars for plot labelling and formatting
    # Capital letter for 'year'
    # 'tag' renamed to 'Legend'
    df.rename(columns={"year": "Year",
                       "tag": "Legend"},
              inplace=True)
    df.reset_index(drop=True, inplace=True)

    f = plt.figure()
    sns.lineplot(data=df, x='Year', y=v, hue='Legend', style='Legend', markers=True, palette='Set2')
    if prefix:
        file_name = f"{prefix}_{v}_aggs_by_year.pdf"
    else:
        file_name = f"{v}_aggs_by_year.pdf"
    file_name = os.path.join(destination, file_name)

    # Sort out axis labels
    if v == 'SF_12':
        v = 'SF12 MCS'
    plt.ylabel(f"{v} nanmean")
    plt.tight_layout()

    dir_name = os.path.dirname(file_name)
    if not os.path.isdir(dir_name):
        print("Plots folder not found; creating...")
        os.mkdir(dir_name)
    plt.savefig(file_name)
    print(f"Lineplot saved to {file_name}")


def find_MINOS_years_range(file_path):
    """ Calculate the number of years in MINOS output data.

    Parameters
    ----------
    file_path: MINOS runs to calculate the number of years of data to aggregate for.

    Returns
    -------
    years: np.arange
        List of years to aggregate data for
    """
    # MINOS data has a yaml config that contains number of years model runs for. Find that and return it.
    with open(f"{file_path}/config_file.yml", "r") as stream:
        config = yaml.safe_load(stream)
    start_year = config['time']['start']['year']
    end_year = config['time']['end']['year']
    years = np.arange(start_year, end_year)
    return years


def weighted_nanmean(df, v, weights = "weight", scale=1):
    #df = df.loc[df['weight'] > 0]

    #df.loc[df.index, weights] = 1/df[weights]
    return np.nansum(df[v] * df[weights]) / sum(df[weights]) * scale
    #return np.nanmean()

def child_uplift_cost_sum(df, v, weights='weight'):
    # get unique households
    # get boost amount per household
    df = df.loc[df['weight'] > 0]
    group = df.groupby(['hidp'])
    weights = 1/group[weights].sum()
    return np.nansum(weights * group[v].min())/np.nansum(weights)

def main(directories, tags, subset_function_strings, prefix, mode='default_config', ref="Baseline", v="SF_12",
         method='nanmean', region=None):
    """ Main method for converting multiple sources of MINOS data into a lineplot.


    Parameters
    ----------
    directories
    tags
    subset_function_strings
    v
    method
    mode
    region

    Returns
    -------

    """

    # Without using eval this is the best way I can think of to import from string to function.
    if method == "nanmean" or method == "weighted_nanmean":
        method = weighted_nanmean
    elif method == "percentages":
        method = aggregate_percentage_counts
    elif method == "child_uplift_cost_sum":
        method = child_uplift_cost_sum
    else:
        raise ValueError(
            "Unknown aggregate function specified. Please add specifc function required at 'aggregate_minos_output.py")

    directories = directories.split(",")
    tags = tags.split(",")
    subset_function_strings = subset_function_strings.split(',')

    aggregate_long_stack = pd.DataFrame()
    for directory, tag, subset_function_string in zip(directories, tags, subset_function_strings):
        file_path = os.path.abspath(os.path.join('output/', mode, directory))
        # TODO needs regex here rather than every file. Keeps catching .DS_Store and my will to live.
        latest_file_path = find_latest_source_file_path(file_path)
        years = find_MINOS_years_range(latest_file_path)

        print(f"Aggregating for source {latest_file_path}, tag {tag} using {method.__name__} over {v}")
        new_aggregate_data = aggregate_variables_by_year(latest_file_path, tag, years,
                                                         subset_function_string, v=v, ref=ref,
                                                         method=method, region=region)
        aggregate_long_stack = pd.concat([aggregate_long_stack, new_aggregate_data])

    if v == "SF_12":
        scaled_data = relative_scaling(aggregate_long_stack, v, ref)
        print("relative scaling done. plotting.. ")
        aggregate_lineplot(scaled_data, "plots", prefix, v, method)
    elif v == "boost_amount":
        aggregate_lineplot(aggregate_long_stack, "plots", prefix, v, method)
    elif method == aggregate_percentage_counts:
        print(f"Data compiled for variable {v} using method {method.__name__}.")
        file_path = latest_file_path + f"/{v}_aggregation_using_{method.__name__}.csv"
        aggregate_long_stack.to_csv(file_path)
        print(f"Saved to {file_path}.")

if __name__ == '__main__':
    print("MAIN HERE IS JUST FOR DEBUGGING. RUN MAIN IN A NOTEBOOK INSTEAD. ")

    #define test parameters and run.
    directories = "baseline,25RelativePoverty,50RelativePoverty"
    tags = "Baseline,25 Relative Poverty,50 Relative Poverty"
    subset_function_strings = "who_below_living_wage_and_kids,who_boosted,who_boosted"
    prefix = "baseline_25_50_relative_poverty"
    mode = 'default_config'
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    # mode = "glasgow_scaled"
    # directories = "baseline,EPCG,EBSS"
    # tags = "Baseline,Energy Price Cap Guarantee,Energy Bill Support Scheme"
    # subset_function_strings = "who_uses_energy,who_boosted,who_boosted"
    # prefix = "epcg_ebss_baseline"

    # directories = "baseline,baseline,baseline,baseline,baseline,baseline,baseline,baseline,baseline,baseline,baseline,baseline"
    # tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    # subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    # prefix="simd_deciles"
    # mode = "glasgow_scaled"
    # ref='National Average'

    # directories = "baseline,livingWageIntervention"
    # tags = "Baseline,Living Wage Intervention"
    # subset_function_strings = "who_below_living_wage,who_boosted"
    # prefix = "baseline_living_wage"
    # mode = 'default_config'
    # ref = "Baseline"
    # v = "housing_quality"
    # method = 'percentages'


    # directories = "25RelativePoverty,25UniversalCredit"
    # tags = "£25 Relative Poverty,£25 Universal Credit"
    # subset_function_strings = "who_boosted,who_boosted"
    # prefix = "25rp_25uc_cost_lineplot"
    # mode = 'default_config'
    # ref = "25RelativePoverty"
    # v = "boost_amount"
    # method = 'child_uplift_cost_sum'

    main(directories, tags, subset_function_strings, prefix, mode, ref, v, method)


# TODO find a way to aggregate boxplots/ridgelines together