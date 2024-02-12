"""
Previous version of this is upscaling on households and is problematic because its impossible to calculate new household IDs

Get household IDs
shuffle IDs using hashing mod 10**20 to give 20 digit IDs

for each new households ID
get everyone with the old household ID
assign them the new household ID
put them into the population

Probably some fancy way to do this pandas gruoping/merger.
left (right?) merge on hidp might be the simplest way to do this?

"""

import pandas as pd
from minos.data_generation.US_upscaling import subset_zone_ids, take_synthpop_sample, merge_with_spatial_attributes, \
    get_spatial_attribute_data
import numpy as np
import US_utils
import argparse


def merge_with_synthpop_households(synthpop, msim_data, merge_column="hidp"):
    """ Merge US data on synthetic pop individual data.

    Parameters
    ----------
    synthpop, msim_data : pd.DataFrame
        synthetic spatial population and US msim_data to merge.
    merge_column : str
        Which column to merge upon? usually pidp/hidp
    Returns
    -------
    merged_data : pd.DataFrame
        Merged synthetic US data with spatial component.
    """
    synthpop[f"new_{merge_column}"] = np.arange(synthpop.shape[0])
    synthpop[merge_column] = synthpop[merge_column].astype(int)
    merged_data = synthpop.merge(msim_data, how='left', on=merge_column)
    # merged_data[f"new_{merge_column}"] = merged_data[f'new_{merge_column}']
    return merged_data


def get_data_zones(region):
    """

    Parameters
    ----------
    region: str
        Region to return subset for
    Returns
    -------
    data_zones : list
        Provides a list of data zones to return.
    """

    if region == "glasgow":  # get glasgow data zones, get Understanding Society data.
        data_zones = pd.read_csv("persistent_data/spatial_data/glasgow_data_zones.csv")[
            "lsoa11cd"]  # glasgow data zone IDs.
    elif region == "scotland":
        data_zones = pd.read_csv("persistent_data/spatial_data/scotland_data_zones.csv")["DZ2011_Code"]
        data_zones.columns = ['lsoa11cd']  # standardise column name for zone codes.
    elif region == "manchester":
        data_zones = pd.read_csv("persistent_data/spatial_data/manchester_lsoas.csv")["lsoa11cd"]
    elif region == "sheffield":
        data_zones = pd.read_csv("persistent_data/spatial_data/sheffield_lsoas.csv")["lsoa11cd"]
    elif region == "uk":
        data_zones = None
    else:
        print("Error! Invalid region defined for spatial subsetting.")
        raise ValueError

    return data_zones


def main(region, percentage=100, bootstrapping=False, n=100_000):
    """
    1. Grab individual synthetic spatial population for UK.
    2. Take subset of spatial population in a specific subregion.
        Glasgow City region / GMCA/ Sheffield City Region / Scotland
    3. Merge synthetic population on real Understanding Society data to get populated individual rows with a spatial component.
    4.

    Parameters
    ----------

    percentage : int
        What percent of the synthetic population to use for subsetting
    bootstrapping : bool
        Do bootstrapping on top of synthetic sample to induce uncertainty?
    n : int
        number of boostrapping samples to take.
    """
    # get synthetic data.
    synthpop_file_path = "persistent_data/spatial_data/HH2011PopEst2020UK_population.csv"
    #synthpop_file_path = "persistent_data/spatial_data/HHSPUKL_population.csv"
    #synthpop_file_path = "persistent_data/spatial_data/IndSPUKL_population.csv"
    try:
        synthpop_data = pd.read_csv(synthpop_file_path)  # this is individual population weighted data.
    except FileNotFoundError as e:
        print(e)
        print(f"Synthetic population file not found at {synthpop_file_path}. Please ask MINOS maintainers for access.")
        raise

    data_zones = get_data_zones(region)
    US_data = pd.read_csv("data/final_US/2021_US_cohort.csv")  # only expanding on one year of US data for 2021.
    if type(data_zones) == pd.core.series.Series:
        subsetted_synthpop_data = subset_zone_ids(synthpop_data, data_zones)
    else:
        subsetted_synthpop_data = synthpop_data  # no subsetting for full UK population.

    # if bootstrapping sample from subsetted synthetic data with replacement.
    if bootstrapping:
        subsetted_synthpop_data = subsetted_synthpop_data.sample(n, replace=True)

    # merge synthetic and US data together.
    subsetted_synthpop_data['hidp'] = subsetted_synthpop_data['hhid']
    merged_data = merge_with_synthpop_households(subsetted_synthpop_data, US_data)
    merged_data = merged_data.dropna(axis=0, subset=[
        "time"])  # remove rows that are missing in spatial data and aren't merged properly.
    print(f"{sum(merged_data['time'].value_counts())} rows out of {merged_data.shape[0]} successfully merged.")

    # scramble new hidp and pidp.
    merged_data['hidp'] = merged_data['new_hidp']  # replace old pidp.
    merged_data.drop(['new_hidp', 'hhid'], axis=1, inplace=True)  # removing old hidp columns
    merged_data['pidp'] = merged_data.index  # creating new pidps.

    # take subset of sample if desired. defaults to 100% for now.
    sampled_data = take_synthpop_sample(merged_data, percentage / 100)
    print(f"Taking {percentage}% of sample giving {sampled_data.shape[0]} rows.")

    # merge with spatial_attributes
    # Get SIMD Deciles for Scottish data
    if region in ['scotland', 'glasgow']:
        sampled_data = merge_with_spatial_attributes(sampled_data, get_spatial_attribute_data(), "ZoneID")

    sampled_data['weight'] = 1  # force sample weights to 1. as this data is expanded weights no longer representative
    # but still updating weights helps with weighted aggregates later.

    # US_utils.check_output_dir(f"data/scaled_{region}_US/hh/")  # check save directory exists or create it.
    # US_utils.save_file(sampled_data, f"data/scaled_{region}_US/hh/", '', 2020)
    US_utils.check_output_dir(f"data/scaled_{region}_US/")  # check save directory exists or create it.
    US_utils.save_file(sampled_data, f"data/scaled_{region}_US/", '', 2021)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Raw Data formatting from Understanding Society")
    parser.add_argument("-r", "--region", required=True, type=str,
                        help="""The region to subset for the UK synthetic population.
                              glasgow, scotland, manchester, sheffield, uk only for now.""")
    parser.add_argument("-p", "--percentage", required=False, type=int,
                        help="Percentage of synthetic population to use (e.g. 0-100%).")
    parser.add_argument("-b", "--do_bootstrapping", required=False, type=bool,
                        help="Bootstrapping the synthetic population to incudce uncertainty?")
    parser.add_argument("-s", "--bootstrap_sample_size", required=False, type=int,
                        help="How many bootstrap samples to take. Should only be used with do_bootstrapping above.")

    args = vars(parser.parse_args())
    print(args)
    region = args['region']
    if 'percentage' in args.keys():
        percentage = args['percentage']
    else:
        percentage = 100
    if 'do_bootstrapping' in args.keys():
        do_bootstrapping = args['do_bootstrapping']
    else:
        do_bootstrapping = False
    if "bootstrap_sample_size" in args.keys():
        bootstrap_sample_size = args['bootstrap_sample_size']
    else:
        bootstrap_sample_size = 1

    main(region, percentage, do_bootstrapping, bootstrap_sample_size)
