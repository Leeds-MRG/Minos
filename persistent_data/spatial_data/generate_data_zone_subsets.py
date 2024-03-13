import pandas as pd
import os
from os.path import dirname as up
from minos.utils import get_lsoa_la_map


def main():

    spatial_path = up(__file__)
    # load in full UK wide lookup.
    # get this data here https://geoportal.statistics.gov.uk/datasets/0d11d17118ec44fcbe890fed53df4a9d_0/explore
    # lookup_file_name = os.path.join(spatial_path, "Output_Area_to_LSOA_to_MSOA_to_Local_Authority_District_(December_2017)_Lookup_with_Area_Classifications_in_Great_Britain.csv")
    # lsoa_lookup = pd.read_csv(lookup_file_name)
    # la_name = 'LAD17NM'
    # country_name = 'CTRY11NM'
    # lsoa_code = 'LSOA11CD'

    ''' HR 06/02/24 Standardising lookups, re. 389 '''
    lsoa_lookup = get_lsoa_la_map()
    la_name = 'LAD22NM'
    country_name = 'CTRY11NM'
    lsoa_code = 'LSOA11CD'

    manchester_LA_names = ["Bolton",
                           "Bury",
                           "Manchester",
                           "Oldham",
                           "Rochdale",
                           "Salford",
                           "Stockport",
                           "Tameside",
                           "Trafford",
                           "Wigan"]
    # subsetting data from desired regions.
    sheffield_subset = lsoa_lookup.loc[lsoa_lookup[la_name] == "Sheffield", ]
    manchester_subset = lsoa_lookup.loc[lsoa_lookup[la_name].isin(manchester_LA_names), ]
    glasgow_subset = lsoa_lookup.loc[lsoa_lookup[la_name] == "Glasgow City", ]
    scotland_subset = lsoa_lookup.loc[lsoa_lookup[country_name] == "Scotland", ]

    # only taking required column
    sheffield_lsoas = sheffield_subset[lsoa_code]
    manchester_lsoas = manchester_subset[lsoa_code]
    glasgow_data_zones = glasgow_subset[lsoa_code]
    scotland_data_zones = scotland_subset[lsoa_code]

    #saving
    sheffield_lsoas.to_csv(os.path.join(spatial_path, "sheffield_lsoas.csv"))
    manchester_lsoas.to_csv(os.path.join(spatial_path, "manchester_lsoas.csv"))
    glasgow_data_zones.to_csv(os.path.join(spatial_path, "glasgow_data_zones.csv"))
    scotland_data_zones.to_csv(os.path.join(spatial_path, "scotland_data_zones.csv"))

    # do the same for LADs.
    sheffield_lsoas = sheffield_subset[la_name]
    manchester_lsoas = manchester_subset[la_name]
    glasgow_data_zones = glasgow_subset[la_name]
    scotland_data_zones = scotland_subset[la_name]

    #saving
    sheffield_lsoas.to_csv(os.path.join(spatial_path, "sheffield_LAs.csv"))
    manchester_lsoas.to_csv(os.path.join(spatial_path, "manchester_LAs.csv"))
    glasgow_data_zones.to_csv(os.path.join(spatial_path, "glasgow_LAs.csv"))
    scotland_data_zones.to_csv(os.path.join(spatial_path, "scotland_LAs.csv"))




if __name__ == '__main__':
    main()
