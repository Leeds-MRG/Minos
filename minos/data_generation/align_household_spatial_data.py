"""Given household upscaled data from US_household_upscaling.py realign certain spatial values to match LSOA
aggregates."""

import pandas as pd
from US_utils import check_output_dir, save_file


def main(US_data, region):
    """ Main function for updating spatial variables on scaled synthetic data for MINOS.

    Parameters
    ----------
    region : str
        Which spatial region of Great Britain is being updated.

    Returns
    -------
    None - Saves data at the end to csvs.
    """

    # load US data, spatial data, and urban/rural classifier data.
    #US_data = pd.read_csv(f"data/scaled_{region}_US/2020_US_cohort.csv")  # only expanding on one year of US data for 2021.
    spatial_data = pd.read_csv("persistent_data/spatial_data/Output_Area_to_LSOA_to_MSOA_to_Local_Authority_District_(December_2017)_Lookup_with_Area_Classifications_in_Great_Britain.csv")
    EW_urban_rural_data = pd.read_csv("persistent_data/spatial_data/rural_urban_by_lsoa.csv")
    S_urban_rural_data = pd.read_csv("persistent_data/spatial_data/rural_urban_by_data_zone.csv")

    #Combine urban/rural classifiers data for england/wales and scotland.
    # Get required columns and make consistent names.
    EW_urban_rural_data = EW_urban_rural_data[['Lower Super Output Area 2011 Code', "Rural Urban Classification 2011 (2 fold)"]]
    EW_urban_rural_data.columns = ['ZoneID', "urban"]
    S_urban_rural_data =  S_urban_rural_data[['FeatureCode', "Value"]]
    S_urban_rural_data.columns = ['ZoneID', "urban"]

    # concat two data frames to get UK LSOA to urban/rural classifier map.
    urban_rural_data = pd.concat([EW_urban_rural_data, S_urban_rural_data])
    urban_rural_zone_dict = dict(urban_rural_data.values)
    urban_rural_int_dict = {"Urban": 1, "Rural": 2, 1: 1, 2: 2}

    # assign urban 1/2 values based on zoneid.
    US_data['urban'] = US_data['ZoneID'].map(urban_rural_zone_dict)
    US_data['urban'] = US_data['urban'].map(urban_rural_int_dict)

    # assign region based on zoneid.
    lsoa_region_dict = dict(spatial_data[["LSOA11CD", "RGN11NM"]].values)
    US_data['region'] = US_data['ZoneID'].map(lsoa_region_dict)

    # save data.
    #check_output_dir(f"data/scaled_{region}_aligned_US/")  # check save directory exists or create it.
    #save_file(US_data, f"data/scaled_{region}_aligned_US/", '', 2020)
    return US_data


if __name__ == '__main__':
    region = 'manchester'
    main(region)