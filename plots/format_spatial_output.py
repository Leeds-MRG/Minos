"""File for formatting minos output with Chris' spoatially weighted data.

# Merge minos data onto spatially weighted LSOAs.
calculate group mean for each LSOA.
convert mean LSOA data into properties for the ONS LSO GeoJSON.
save geojson to plot in R. (maybe use cartopy instead..)

"""

import pandas as pd
import geojson
from collections import defaultdict

def main():
    # data from some minos output
    minos_data = pd.read_csv("output/test_output/simulation_data/5.csv")
    # chris' spatially weighted data.
    spatial_data = pd.read_csv("/Users/robertclay/data/ADULT_population_GB_2018.csv")

    lsoa_geojson = 0

    # only choose common pidps. should be trivial if using same year data.
    spatial_data2 = spatial_data.loc[spatial_data["pidp"].isin(minos_data["pidp"]),]
    minos_data2 = minos_data.loc[minos_data["pidp"].isin(spatial_data2["pidp"]),["pidp", "SF_12"]]

    # take smaller subset of data for testing..
    #spatial_data2 = spatial_data2.head(20000000)
    spatial_data2 = spatial_data2.merge(minos_data2, how='left', on='pidp')

    spatial_data3 = spatial_data2.groupby("ZoneID").mean()
    spatial_data3["ZoneID"] = spatial_data3.index
    spatial_data3.reset_index(drop=True)

    # default dict assigns missing values to 0. prevents key errors later.
    spatial_dict = defaultdict(int, zip(spatial_data3["ZoneID"], spatial_data3["SF_12"]))
    print("merger done.")

    # load in geojson map data.
    json_source = "/Users/robertclay/data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson"
    with open(json_source) as f:
        map_geojson = geojson.load(f)

    # loop over geojson items and add in new SF12 mean property.
    for i, item in enumerate(map_geojson["features"]):
        ons_code = item["properties"]["LSOA11CD"]
        SF12_code = spatial_dict[ons_code]
        if SF12_code == 0:
            SF12_code = None
        item['properties']["SF_12"] = SF12_code
        map_geojson['features'][i] = item

    fname = "/Users/robertclay/data/LSOA_with_SF12.geojson"
    with open(fname, 'w') as outfile:
        geojson.dump(map_geojson, outfile)

if __name__ == "__main__":
    main()
