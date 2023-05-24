# combine US data with SIPHER household synthetic pop to build a full scale over some spatial area.

# for now, this is just looking at glasgow area and does the following
# get full UK spatia data
# take those individuals in glasgow data zones
# merge them with MINOS data to get  individuals for all of glasgow
# take some random percentage as a subset. May not be necessary for a medium size city.
import pandas as pd
import numpy as np
import US_utils

def subset_zone_ids(data, subset):
    """ Return some subset of the UK national set of ZoneIDs e.g. glasgow/manchester only.

    Parameters
    ----------
    data : Synthetic data with two columns for pidp and ZoneID (LSOA)
    subset: pd.Series
        Which ZoneIDs to keep

    Returns
    -------
    """
    subsetted_data = data.loc[data["ZoneID"].isin(subset)]
    return subsetted_data

def merge_with_synthpop_individuals(synthpop, msim_data, merge_column="pidp"):
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

def take_synthpop_sample(merged_data, percent, seed=8):
    """ Take smaller subset of full scale synthetic population

    Parameters
    ----------
    merged_data: pd.DataFrame
        Full scale population data.
    percent, seed : float

    Returns
    -------
    sample_data : pd.DataFrame
        A percent sample of merged_data chosen with random seed.
    """
    n = int(merged_data.shape[0] * percent)
    sample_data = merged_data.sample(n=n, replace=False, random_state=seed)
    return sample_data

def main():
    """
    1. Grab individual synthetic spatial population for UK.
    2. Take subset of spatial population in a specific subregion.
        Glasgow City region / GMCA/ Sheffield City Region / Scotland
    3. Merge synthetic population on real Understanding Society data to get populated individual rows with a spatial component.
    4.
    """
    #synthpop_file_name = "../HH2011PopEst2020S_population.csv"
    synthpop_data = pd.read_csv("../data/Ind2011PopEst2020S_population.csv") # this is individual population weighted data.
    #synthpop_data = pd.read_csv("../data/HH2011PopEst2020S_population.csv") # this is household weighted data. not working atm. need to investigate.
    glasgow_data_zones = pd.read_csv("persistent_data/spatial_data/glasgow_data_zones.csv")["lsoa11cd"] # glasgow data zone IDs.
    US_data = pd.read_csv("data/final_US/2020_US_cohort.csv") # only expanding on one year of US data for 2020.

    # merge spatial and US data.
    # TODO should generalise this to any subset of lsoas but no point for now.
    subsetted_synthpop_data = subset_zone_ids(synthpop_data, glasgow_data_zones)
    merged_data = merge_with_synthpop_individuals(subsetted_synthpop_data, US_data)
    merged_data = merged_data.dropna(axis=0, subset=["time"]) # remove rows that are missing in spatial data and aren't merged properly.
    print(f"{sum(merged_data['time'].value_counts())} rows out of {merged_data.shape[0]} successfully merged.")

    # take sample of merged data.
    percent = 1.0 # = 0.1
    sampled_data = take_synthpop_sample(merged_data, percent)
    print(f"Taking {100*percent}% of sample giving {sampled_data.shape[0]} rows.")

    US_utils.check_output_dir("data/scaled_US/") # check save directory exists or create it.
    US_utils.save_file(sampled_data, "data/scaled_glasgow_US/", '', 2020)


if __name__ == '__main__':
    main()