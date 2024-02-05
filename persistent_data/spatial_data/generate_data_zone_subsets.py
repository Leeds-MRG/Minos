import pandas as pd


def main():

    # load in full UK wide lookup.
    # get this data here https://geoportal.statistics.gov.uk/datasets/0d11d17118ec44fcbe890fed53df4a9d_0/explore
    lookup_file_name = "persistent_data/spatial_data/Output_Area_to_LSOA_to_MSOA_to_Local_Authority_District_(December_2017)_Lookup_with_Area_Classifications_in_Great_Britain.csv"
    lsoa_lookup = pd.read_csv(lookup_file_name)

    # subsetting data from desired regions.
    sheffield_subset = lsoa_lookup.loc[lsoa_lookup['LAD17NM'] == "Sheffield",]
    manchester_subset = lsoa_lookup.loc[lsoa_lookup['LAD17NM'] == "Manchester", ]
    glasgow_subset = lsoa_lookup.loc[lsoa_lookup['LAD17NM'] == "Glasgow City", ]
    scotland_subset = lsoa_lookup.loc[lsoa_lookup['CTRY11NM'] == "Scotland", ]

    # only taking required column
    sheffield_lsoas = sheffield_subset['LSOA11CD']
    manchester_lsoas = manchester_subset['LSOA11CD']
    glasgow_data_zones = glasgow_subset['LSOA11CD']
    scotland_data_zones = scotland_subset['LSOA11CD']

    #saving
    sheffield_lsoas.to_csv("persistent_data/spatial_data/sheffield_lsoas.csv")
    manchester_lsoas.to_csv("persistent_data/spatial_data/manchester_lsoas.csv")
    glasgow_data_zones.to_csv("persistent_data/spatial_data/glasgow_data_zones.csv")
    scotland_data_zones.to_csv("persistent_data/spatial_data/scotland_data_zones.csv")

if __name__ == '__main__':
    main()