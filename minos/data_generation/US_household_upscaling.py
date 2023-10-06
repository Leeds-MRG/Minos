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
from minos.data_generation.US_upscaling import subset_zone_ids, take_synthpop_sample, merge_with_spatial_attributes, get_spatial_attribute_data, get_knn_cluster_data
import numpy as np
import US_utils


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
    #merged_data[f"new_{merge_column}"] = merged_data[f'new_{merge_column}']
    return merged_data

def main():
    """
    1. Grab individual synthetic spatial population for UK.
    2. Take subset of spatial population in a specific subregion.
        Glasgow City region / GMCA/ Sheffield City Region / Scotland
    3. Merge synthetic population on real Understanding Society data to get populated individual rows with a spatial component.
    4.
    """
    synthpop_file_path = "../data/HH2011PopEst2020S_population.csv"
    try:
        synthpop_data = pd.read_csv(synthpop_file_path) # this is individual population weighted data.
    except FileNotFoundError as e:
        print(e)
        print(f"Synthetic population file not found at {synthpop_file_path}. Please ask MINOS maintainers for access.")
        raise

    #synthpop_data = pd.read_csv("../data/HH2011PopEst2020S_population.csv") # this is household weighted data. not working atm. need to investigate.
    glasgow_data_zones = pd.read_csv("persistent_data/spatial_data/glasgow_data_zones.csv")["lsoa11cd"] # glasgow data zone IDs.
    US_data = pd.read_csv("data/final_US/2020_US_cohort.csv") # only expanding on one year of US data for 2020.
    subsetted_synthpop_data = subset_zone_ids(synthpop_data, glasgow_data_zones)
    subsetted_synthpop_data['hidp'] = subsetted_synthpop_data['hhid']
    merged_data = merge_with_synthpop_households(subsetted_synthpop_data, US_data)

    merged_data['hidp'] = merged_data['new_hidp'] # replace old pidp.

    percent = 1.0 # = 0.1
    sampled_data = take_synthpop_sample(merged_data, percent)
    print(f"Taking {100*percent}% of sample giving {sampled_data.shape[0]} rows.")

    # merge with spatial_attributes
    # get simd_deciles
    sampled_data = merge_with_spatial_attributes(sampled_data, get_spatial_attribute_data(), "ZoneID")
    # get_zone_ids
    sampled_data = merge_with_spatial_attributes(sampled_data, get_knn_cluster_data(), "ZoneID")

    sampled_data['weight'] = 1 # force sample weights to 1.

    US_utils.check_output_dir("data/scaled_glasgow_US/") # check save directory exists or create it.
    US_utils.save_file(sampled_data, "data/scaled_glasgow_US/", 'household_', 2020)


if __name__ == '__main__':
    main()