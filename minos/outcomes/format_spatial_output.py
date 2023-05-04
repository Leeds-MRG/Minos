"""File for formatting minos output with Chris' spoatially weighted data.
"""

import pandas as pd
import geojson
from collections import defaultdict
import numpy as np
import argparse
import glob
import os
from datetime import datetime
from aggregate_subset_functions import dynamic_subset_function

"""
Get spatial data.
Find subset of spatial data within desired lsoas (e.g. manchester)
for each minos run
    get minos data and take specific desired subset. 
    merge minos and spatial data
    group by lsoa and take SF12 nanmean
stack columns of lsoa and mean sf12 from all minos runs together
aggregate again by lsoa and mean.
get a set of lsoas and grand mean sf12
save to geojson. 

This reformat has a number of advantages

"""

# def eightyTwenty(income):
#
#     split = pd.qcut(income, q=5, labels=[1, 2, 3, 4, 5])
#     who_bottom_twenty = split == 1
#     who_top_eighty = split > 1
#     eightyTwentyRatio = sum(income[who_bottom_twenty])/sum(income[who_top_eighty])
#     return eightyTwentyRatio

def get_latest_minos_files(source):
    """Get the latest data for a given source (config and intervention type) chronologically."""
    runtime = os.listdir(os.path.abspath(source))
    if len(runtime) > 1:  # Select most recent run
        runtime = max(runtime, key=lambda d: datetime.strptime(d, "%Y_%m_%d_%H_%M_%S"))
    elif len(runtime) == 1:  # os.listdir returns a list, we only have 1 element
        runtime = runtime[0]
    else:
        raise RuntimeError("The output directory supplied contains no subdirectories, and therefore no data to "
                           "aggregate. Please check the output directory.")
    return os.path.join(source, runtime)

def get_minos_files(source):
    return glob.glob(source + f"/*{year}.csv")

def get_spatial_data():
    """ Get WS3 spatial data for UK

    Returns
    -------
    spatial_data : pd.DataFrame
        Two column data frame with pidps and ZoneIDs (LSOAs).
    """
    try:
        # chris spatially weighted data.
        spatial_data = pd.read_csv("persistent_data/spatial_data/ADULT_population_GB_2018.csv")
    except FileNotFoundError as e:
        print(e)
        print("\nREADME::\n"
              "The spatially disaggregated version of Understanding Society is required to spatially disaggregate and "
              "produce maps from the output populations. Due to it's size, this file is not tracked along in the "
              "github repository, and must be acquired separately. Please email l.archer@leeds.ac.uk or gyrc@leeds.ac.uk "
              "for more information if required.\n")
        raise
    return spatial_data

def get_region_lsoas(region):

    region_file_name_dict = {"manchester" : "manchester_lsoas.csv",
                             "scotland": "scotland_data_zones.csv",
                             "sheffield" : "sheffield_lsoas.csv",
                             "glasgow" : "glasgow_data_zones.csv"}
    lsoas_file_path = "persistent_data/spatial_data/" + region_file_name_dict[region]
    return pd.read_csv(lsoas_file_path)

def group_by_and_aggregate(data, group_column, v, method):
    """ Aggregate values by

    Parameters
    ----------
    data : pd.DataFrame
    group_column, v : str
        Column to aggregate over (e.g. lsoa/pidp) and variable v to apply aggregate function to (e.g. SF12).
    method : func
        Function to aggregate variable v over. Usually np.nanmean. Can be any function that takes a vector and return scalar.
    Returns
    -------
    data : pd.DataFrame
        Data gruoped by group_column and aggregated over variable v using function method.
    """
    data = pd.DataFrame(data.groupby([group_column]).apply(lambda x: method(x[v])))
    data.columns = [v]
    data[group_column] = data.index
    data.reset_index(drop=True, inplace=True)
    return data

def subset_lsoas_by_region(spatial_data, region_data):
    """ Find lsoas within a certain region e.g. scotland, manchester.

    Parameters
    ----------
    spatial_data : pd.DataFrame
        Spatially representative data for the UK. Has two columns for US pidp and LSOA variables.
    region_data : pd.DataFrame
        Subset of LSOAs from specified region

    Returns
    -------
    spatial_data : pd.DataFrame
        spatial_data only with LSOAs from specified region data.
    """
    return spatial_data[spatial_data['ZoneID'].isin(region_data["lsoa11cd"])]


def edit_geojson(geojson_data, new_variable_dict, v):
    """ Add new property to some geojson multipolygon data such as mean SF12 value

    Multipolygon is essentially a list of dictionaries. Each polygon has a 'features' subdictionary that is being appended.

    Parameters
    ----------
    geojson_data : geojson.MultiPolygon
        Geojson data to append.
    new_variable_dict : dict
        Dictionary mapping keys from each polygon in the geojson data to values of the property being appended v.
        For example, geojson data may consist of LSOAs and SF12 values are being appended. In this case we would have
        a dictionary with LSOA keys each with some SF12 mean value.
    v : str
        Name of the new property being added e.g `SF_12`
    Returns
    -------
    geojson_data : geojson.MultiPolygon
        geojson data with new property v added to features.
    """
    # This could be more generalised but not worth it.
    # Loop over geojson polygons (features). Get list of propo
    for i, item in enumerate(geojson_data["features"]):
        # Get the LSOA code for this polygon.
        LSOA_code = item["properties"]["ZoneID"]
        variable_code = new_variable_dict[LSOA_code]
        if variable_code == 0:  # TODO needs improving with a more general catch all.
            variable_code = None
        # assign the new mean of v to the geojson feature.
        # assign the updated feature back into the geoJSON.
        # TODO should be an easier way to just append this list of features..
        item['properties'][v] = variable_code
        geojson_data['features'][i] = item
    return geojson_data


def subset_geojson(geojson_data, subset):
    """Take subset of features from a geojson"""
    new_features = []
    subset = set(subset.values)
    keep = [i for i, feature in enumerate(geojson_data['features']) if feature['properties']["ZoneID"] in subset]
    geojson_data['features'] = [geojson_data['features'][i] for i in keep]
    return geojson_data

def load_geojson(source_file_name):
    """ Load a geojson file.

    Parameters
    ----------
    source_file_name : str
        Where to load geojson data from

    Returns
    -------
    geojson_data : geojson.MultiPolygon
        Geojson data for some region of the UK to modify.
    """
    with open(source_file_name) as f:
        geojson_data = geojson.load(f)
    return geojson_data


def save_geojson(geojson_data, file_name):
    """ Save geojson data to file_name.

    Parameters
    ----------
    geojson_data : geojson.MultiPolygon
        Geojson data with aggregated SF12 attribute attached for mapping.
    file_name : str
        What to save geojson data as.

    Returns
    -------
    None
    """
    print(f"Saving to SF12 updated geojson data to {file_name}.")
    with open(file_name, 'w') as outfile:
        geojson.dump(geojson_data, outfile)


def main(source, year, region, subset_function, v = "SF_12", method = np.nanmean):

    """ Aggregate some attribute v to LSOA level and put it in a geojson map.

    - Merge minos data onto spatially weighted LSOAs.
    - Calculate group mean for each LSOA.
    - Convert mean LSOA data into properties for the ONS LSOA GeoJSON.
    - Save to geojson for plotting elsewhere.

    Parameters
    ----------
    source, destination: str
        Where are data being sourced from and what destination is the final geojson being saved to.
    v: str
        Which variable v is being used. Output will create a summary value of v for each LSOA.
    method : func
        What aggregator is used in pandas groupby. For now just mean and median. Can specify custom functions
         with groupby.apply though
    save_type: str
        What type of file is the output saved to? csv or geojson.
    Returns
    -------
    None
    """
    print(f"Aggregating MINOS data at {source} for {year} and {region} region.")

    # Get spatial data and subset LSOAs for desired region.
    spatial_data = get_spatial_data()
    region_lsoas = get_region_lsoas(region)
    spatial_data = subset_lsoas_by_region(spatial_data, region_lsoas)

    #loop over minos files for given year. merge with spatial data and aggregate by LSOA.
    total_minos_data = pd.DataFrame()
    minos_files = get_minos_files(source)
    for file in minos_files:
        minos_data = pd.read_csv(file)
        if subset_function:
            minos_data = dynamic_subset_function(minos_data, subset_function)
        minos_data = minos_data[['pidp', v]]

        common_pidps = spatial_data.loc[spatial_data["pidp"].isin(minos_data["pidp"]),'pidp']
        minos_data = minos_data.loc[minos_data["pidp"].isin(common_pidps),["pidp", v]]
        minos_data = spatial_data.loc[spatial_data["pidp"].isin(common_pidps),].merge(minos_data, how='left', on='pidp')
        minos_data = group_by_and_aggregate(minos_data, "ZoneID", v, method)
        total_minos_data = pd.concat([total_minos_data, minos_data])

    # aggregate repeat minos runs again by LSOA to get grand mean change in SF_12 by lsoa.
    total_minos_data = group_by_and_aggregate(total_minos_data, "ZoneID", v, method)

    print('Done. Saving..')
    # convert
    spatial_dict = defaultdict(int, zip(total_minos_data["ZoneID"], total_minos_data[v]))
    # Load in national LSOA geojson map data from ONS.
    #https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2011-boundaries-super-generalised-clipped-bsc-ew-v3/about
    json_source = "persistent_data/spatial_data/UK_super_outputs.geojson"
    #json_source = "persistent_data/spatial_data/SG_DataZone_Bdry_2011.json" # scottish data has slightly nicer looking geometries with annoyingly different column names.
    json_data = load_geojson(json_source)
    json_data = subset_geojson(json_data, spatial_data["ZoneID"])
    json_data = edit_geojson(json_data, spatial_dict, "SF_12")

    # save updated geojson for use in map plots.
    print(f"GeoJSON {v} attribute added.")
    fname = os.path.join(source, f"{region}_{method.__name__}_{v}_{year}.geojson")
    save_geojson(json_data, fname)
    print("Done!")

if __name__ == "__main__":
    # parse inputs from bash script. not meant to be run directly.
    parser = argparse.ArgumentParser(description="Raw Data formatting from Understanding Society")
    parser.add_argument("-m", "--mode", required=True, type=str,
                        help="The mode of MINOS. Usually the config file (e.g. default_config/scotland_mode).")
    parser.add_argument("-i", "--intervention", required=True, type=str,
                        help="Extension in output data for each intervention. E.g." +
                             " baseline/livingWaveIntervention/povertyLineChildUplift")
    parser.add_argument("-y", "--year", required=True, type=str,
                        help="Year of minos data to plot. e.g. 2014.")
    parser.add_argument("-r", "--region", required=True, type=str,
                        help="What region of geojson data is being generated.")
    parser.add_argument("-s", "--subset_function", default="", type=str,
                        help="What subset function is used for data frame. Usually none or who_boosted/intervened on.")

    # get args an
    args = vars(parser.parse_args())
    print(args)
    mode = args['mode']
    intervention = args['intervention']
    year = args['year']
    region = args['region']
    subset_function = args['subset_function']

    # get subset function from specified subset function string.
    source = get_latest_minos_files(os.path.join("output", mode, intervention))

    main(source, year, region, subset_function)
