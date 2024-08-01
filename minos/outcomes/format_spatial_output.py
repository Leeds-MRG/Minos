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
from minos.outcomes.aggregate_subset_functions import dynamic_subset_function
from multiprocessing import Pool
from itertools import repeat
import sys

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


pd.options.mode.chained_assignment = None  # default='warn'

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
    start_year = 2020
    out_files = []

    while start_year  < int(year):
        out_files.append(glob.glob(source + f"/*{start_year}.csv"))
        start_year += 1

    return out_files


def get_spatial_data():
    """ Get WS3 spatial data for UK

    Returns
    -------
    spatial_data : pd.DataFrame
        Two column data frame with pidps and ZoneIDs (LSOAs).
    """
    try:
        # chris spatially weighted data.
        spatial_data = pd.read_csv("persistent_data/spatial_data/ADULT_population_GB_2018.csv", low_memory=False)
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
    region_file_name_dict = {"manchester": "manchester_lsoas.csv",
                             "scotland": "scotland_data_zones.csv",
                             "sheffield": "sheffield_lsoas.csv",
                             "glasgow": "glasgow_data_zones.csv"}
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
    if "intervention_cost" in data.columns:
        intervention_cost = data.groupby([group_column, 'hidp'], as_index=False)['intervention_cost'].max()
        intervention_cost = intervention_cost.groupby([group_column])['intervention_cost'].sum()
    else:
        intervention_cost = 0

    current_time = data['time'].max()

    data = pd.DataFrame(data.groupby([group_column]).apply(lambda x: method(x[v])))
    data.columns = [v]
    data['intervention_cost'] = intervention_cost
    data['time'] = current_time - 1
    data[group_column] = data.index
    data.reset_index(drop=True, inplace=True)
    return data

def group_by_and_aggregate_longitudinal(data, group_column, v, method):
    grouped_sf12 = data.groupby(by=[group_column, 'time'], as_index=False)["SF_12"].mean()["SF_12"]
    data = data.groupby(by=[group_column, 'run_id', 'time'], as_index=False).agg({'intervention_cost': np.cumsum})
    data['SF_12'] = grouped_sf12
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


def edit_geojson(geojson_data, new_variable_dict, intervention_cost_dict, v):
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
        intervention_cost_code = intervention_cost_dict[LSOA_code]

        if variable_code == 0:  # TODO needs improving with a more general catch all.
            variable_code = None
        # assign the new mean of v to the geojson feature.
        # assign the updated feature back into the geoJSON.
        # TODO should be an easier way to just append this list of features..
        item['properties'][v] = variable_code
        item['properties']['intervention_cost'] = intervention_cost_code
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
    print(f"Saving updated geojson data to {file_name}.")
    with open(file_name, 'w') as outfile:
        geojson.dump(geojson_data, outfile)


def attach_spatial_component(minos_data, spatial_data, v, method=np.nanmean):
    # if the MINOS input is just pure Understanding Society data it needs a spatial component adding.
    # Do this by taking
    common_pidps = spatial_data.loc[spatial_data["pidp"].isin(minos_data["pidp"]), 'pidp']
    minos_data = minos_data.loc[minos_data["pidp"].isin(common_pidps), ["pidp", v]]
    minos_data = spatial_data.loc[spatial_data["pidp"].isin(common_pidps),].merge(minos_data, how='left', on='pidp')
    return minos_data


def load_synthetic_data(minos_file, subset_function, v, method=np.nanmean):
    minos_data = pd.read_csv(minos_file, low_memory=False)

    if subset_function:
        minos_data = dynamic_subset_function(minos_data, subset_function)

    # if dataset empty (e.g. no boosted in start year). do nothing.
    if minos_data.shape[0]:
        subset_columns = ['pidp', "ZoneID", v, 'time', 'hidp']
        if "intervention_cost" in minos_data.columns:
            subset_columns += ["intervention_cost"]
        minos_data = minos_data[subset_columns]
        minos_data = group_by_and_aggregate(minos_data, "ZoneID", v, method)
    return minos_data


def load_data_and_attach_spatial_component(minos_file, spatial_data, subset_function, v, method=np.nanmean):
    minos_data = pd.read_csv(minos_file, low_memory=False)
    if subset_function:
        minos_data = dynamic_subset_function(minos_data, subset_function)
    minos_data = minos_data[['pidp', v, 'time']]
    minos_data = attach_spatial_component(minos_data, spatial_data, v)
    minos_data = group_by_and_aggregate(minos_data, "ZoneID", v, method)
    return minos_data


def load_minos_data(minos_files, subset_function, is_synthetic_pop, v, region='glasgow'):
    # Get spatial data and subset LSOAs for desired region.
    # Pooled as there can be hundreds of datasets here and it gets silly.

    with Pool() as pool:
        if is_synthetic_pop:
            aggregated_spatial_data = pool.starmap(load_synthetic_data,
                                                   zip(minos_files, repeat(subset_function), repeat(v)))
        else:
            spatial_data = get_spatial_data()
            region_lsoas = get_region_lsoas(region)
            spatial_data = subset_lsoas_by_region(spatial_data, region_lsoas)
            # is this the best way to do this? Dont want to load in spatial data 1000 times.
            # Are these hard copies or just refs?
            aggregated_spatial_data = pool.starmap(load_data_and_attach_spatial_component,
                                                   zip(minos_files, repeat(spatial_data), repeat(subset_function), repeat(v)))


    for i, item in enumerate(aggregated_spatial_data):
        item['run_id'] = i

    # loop over minos files for given year. merge with spatial data and aggregate by LSOA.
    total_minos_data = pd.concat(aggregated_spatial_data)

    # total_minos_data = pd.concat([total_minos_data, minos_data])
    return total_minos_data


def main(intervention, year, region, subset_function, is_synthetic_pop, v, method=np.nanmean):
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

    # get subset function from specified subset function string.
    source = get_latest_minos_files(os.path.join("output", mode, intervention))


    print(f"Aggregating MINOS data at {source} for {year} and {region} region.")
    minos_files = get_minos_files(source)
    total_minos_data = pd.DataFrame()
    for yearly_files in minos_files:
        subset_minos_data = load_minos_data(yearly_files, subset_function, is_synthetic_pop, v, region)
        total_minos_data = pd.concat([total_minos_data, subset_minos_data])


    # aggregate repeat minos runs again by LSOA to get grand mean change in SF_12 by lsoa.
    total_minos_data = group_by_and_aggregate_longitudinal(total_minos_data, "ZoneID", v, method)
    total_minos_data = total_minos_data.loc[total_minos_data["time"] == int(year)-1, ]

    print('Done. Saving..')
    # convert
    spatial_dict = defaultdict(int, zip(total_minos_data["ZoneID"], total_minos_data[v]))
    cost_dict = defaultdict(int, zip(total_minos_data["ZoneID"], total_minos_data["intervention_cost"]))
    # Load in national LSOA geojson map data from ONS.
    # https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2011-boundaries-super-generalised-clipped-bsc-ew-v3/about
    json_source = "persistent_data/spatial_data/UK_super_outputs.geojson"
    # json_source = "persistent_data/spatial_data/SG_DataZone_Bdry_2011.json" # scottish data has slightly nicer looking geometries with annoyingly different column names.
    try:
        json_data = load_geojson(json_source)
    except FileNotFoundError as e:
        print(e)
        print(f"\nThe file: {json_source} is missing or not in the correct directory. This file should be tracked by "
              f"the repository and therefore shouldn't be missing, but in this case please contact any of the "
              f"developers of the repository and someone should be able to provide it.\n")
        sys.exit(2)

    if not is_synthetic_pop:
        # Subset the GB data with LSOAs from region of interest
        region_lsoas = get_region_lsoas(region)
        gb_data = get_spatial_data()
        region_data = subset_lsoas_by_region(gb_data, region_lsoas)
        json_data = subset_geojson(json_data, region_data["ZoneID"])
    else:
        json_data = subset_geojson(json_data, total_minos_data["ZoneID"])
    json_data = edit_geojson(json_data, spatial_dict, cost_dict, v)

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
    parser.add_argument("-p", "--synthetic_pop", default="", type=str,
                        help="Is this a synthetic population? If yes it has a spatial component that can be used directly.")
    parser.add_argument("-v", "--aggregation_variable", default="", type=str,
                        help="Which variable should we aggregate and subsequently plot as our key outcome measure.")

    # get args an
    args = vars(parser.parse_args())
    print(args)
    mode = args['mode']
    intervention = args['intervention']
    year = args['year']
    region = args['region']
    subset_function = args['subset_function']
    is_synthetic_pop = args['synthetic_pop']
    v = args['aggregation_variable']
    if is_synthetic_pop == "true":
        is_synthetic_pop = True
    else:
        is_synthetic_pop = False

    main(intervention, year, region, subset_function, is_synthetic_pop, v)
