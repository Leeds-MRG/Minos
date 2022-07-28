"""File for mashing many minos runs into one grand mean SF12 distribution over spatial microdata."""

import glob
import pandas as pd
import itertools
import geojson
from collections import defaultdict
import numpy as np
import sys

def get_files(year, *params):

    search_string = 'output/ex1/'
    for item in params:
        search_string += str(item) + '_'
    search_string += f'*{year}.csv'
    print(search_string)
    return glob.glob(search_string)

def main(year, params):
    # chris' spatially weighted data.
    spatial_data = pd.read_csv("persistent_data/ADULT_population_GB_2018.csv")
    p = params[int(sys.argv[1])-1]]
    #p = params[0]
    #for p in params:
    file_names = get_files(year, *p)
    print(file_names)
    first = True
    while file_names:
        file = file_names.pop()
        if first:
            US_data = pd.read_csv(file)
            first = False
        else:
            new_data = pd.read_csv(file)
            US_data = pd.concat([US_data, new_data], ignore_index=True)

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
    print(f"Merger done for {p} params for year {year}.")
    fname = "output/ex1/"
    for text in p:
        fname += str(text) + '_'
    fname += f"{year}.geojson"
    print(f"Saved to {fname}.")

    with open(fname, 'w') as outfile:
        geojson.dump(map_geojson, outfile)

    print("done")

if __name__ == '__main__':
    test = False
    uplift = [0.0, 1000.0, 10000.0]  # assimilation rates
    percentage_uplift = [25.0, 50.0, 75.0] #gaussian observation noise standard deviation

    # Assemble lists into grand list of all combinations.
    # Each experiment will use one item of this list.
    if test:
        parameter_lists = [[1000.0, 75.0]]
    else:
        parameter_lists = [item for item in itertools.product(*[uplift, percentage_uplift])]
    main(2016, parameter_lists)


