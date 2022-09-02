"""File for aggregating many minos runs into one grand mean SF12 distribution over spatial microdata."""

import glob
import pandas as pd
import itertools
import geojson
from collections import defaultdict
import numpy as np
import sys

def get_files(source, year, params, param_names):
    """

    Parameters
    ----------
    source: str
        Where are experiment data stored . Usually in /output for minos.
    year: int
        What year is it?
    params: list
        List of experiment parameter names. used to construct glob search string. e.g. using run_id will return all
        files with the form source/run_id_*.csv. I.E. every experiment with a run_id in source for the given year.

    Returns
    -------
    files : list
        List of file names to pull csvs from.
    """

    search_string = source
    for p, n in zip(params, param_names):
        search_string += n + "_" + str(p) + '_'
    search_string += f'*{year}.csv'
    print(search_string)
    files = glob.glob(search_string)
    return files

def main(source, spatial_source, year, params, param_names):
    """ Main file for aggregating minos experiments into geojson data.

    source: str
        Where are experiment data stored . Usually in /output for minos.
    year: int
        What year is it?
    params: list
        List of experiment parameter names. used to construct glob search string. e.g. using run_id will return all
        files with the form source/run_id_*.csv. I.E. every experiment with a run_id in source for the given year.

    Returns
    -------
    None
    """
    # chris' spatially weighted data.
    spatial_data = pd.read_csv(spatial_source)

    file_names = get_files(source, year, params, param_names)
    print(file_names)
    US_data = pd.DataFrame()
    for file in file_names:
        US_data = pd.concat([US_data, pd.read_csv(file)], ignore_index=True)

    print(US_data.shape)
    # subset US data. grab common pidps to prevent NA errors.
    spatial_data2 = spatial_data.loc[spatial_data["pidp"].isin(US_data["pidp"]),]
    US_data2 = US_data.loc[US_data["pidp"].isin(spatial_data2["pidp"]),["pidp", "SF_12"]]
    US_data2 = US_data2.groupby("pidp", as_index=False).mean()

    # left merge US data into spatial data.
    spatial_data2 = spatial_data2.merge(US_data2, how='left', on='pidp')

    # aggregate spatial data. Group by LSOAs (ZoneID)

    spatial_data3 = spatial_data2.groupby("ZoneID").mean()
    spatial_data3["ZoneID"] = spatial_data3.index # put zoneid back into dataframe and reset index.
    spatial_data3.reset_index(drop=True)

    # default dict assigns missing values to 0. prevents key errors later for any LSOA missing a value.
    spatial_dict = defaultdict(int, zip(spatial_data3["ZoneID"], spatial_data3["SF_12"]))
    print("merger done.")

    # load in geojson map data from ONS.
    #https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2011-boundaries-super-generalised-clipped-bsc-ew-v3/about
    json_source = "persistent_data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson"
    #json_source = "/Users/robertclay/data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson"
    with open(json_source) as f:
        map_geojson = geojson.load(f)

    # loop over geojson features and add in new SF12 mean property.
    for i, item in enumerate(map_geojson["features"]):
        ons_code = item["properties"]["LSOA11CD"]
        SF12_code = spatial_dict[ons_code]
        if SF12_code == 0:
            SF12_code = None
        item['properties']["SF_12"] = SF12_code
        map_geojson['features'][i] = item

    # save updated geojson for use in map plots.
    print(sum(spatial_dict.values()))
    print(f"Merger done for {params} params for year {year}.")
    fname = source
    for p, n in zip(params, param_names):
        fname += n + '_' + str(p) + '_'
    fname += f"{year}.geojson"

    with open(fname, 'w') as outfile:
        geojson.dump(map_geojson, outfile)
    print(f"Saved to {fname}.")

if __name__ == '__main__':
    test = False
    #uplift = [0.0, 1000.0, 10000.0]  # assimilation rates
    #percentage_uplift = [25.0, 50.0, 75.0] #gaussian observation noise standard deviation

    # Assemble lists into grand list of all combinations.
    # Each experiment will use one item of this list.
    #if test:
    #    parameter_lists = [[1000.0, 75.0]]
    #else:
    #    parameter_lists = [item for item in itertools.product(*[uplift, percentage_uplift])]
    parameters = [0, 10]
    parameter_names = ['uplift', 'prop']
    main('output/ex1/', "persistent_data/ADULT_population_GB_2018.csv", 2016, parameters, parameter_names)


