"""File for formatting minos output with Chris' spoatially weighted data.

# Merge minos data onto spatially weighted LSOAs.
calculate group mean for each LSOA.
convert mean LSOA data into properties for the ONS LSO GeoJSON.
save geojson to plot in R. (maybe use cartopy instead..)

"""

import pandas as pd
import geojson
from collections import defaultdict
import numpy as np

def main(years, index):

    # only choose common pidps. should be trivial if using same year data.
    # just prevents NAs when merging datasets. will remove some data but produces cleaner plots.
    # may be a way to use more data?

    # chris' spatially weighted data.
    spatial_data = pd.read_csv("/Users/robertclay/data/ADULT_population_GB_2018.csv")
    for year in years:
        # data from some real US/minos output
        if index == "real":
            US_data = pd.read_csv(f"output/test_output/simulation_data/{year}.csv")
        if index == "minos":
            US_data = pd.read_csv(f"data/final_US/{year}_US_Cohort.csv")

        # subset US data. grab common pidps to prevent NA errors.
        spatial_data2 = spatial_data.loc[spatial_data["pidp"].isin(US_data["pidp"]),]
        US_data2 = US_data.loc[US_data["pidp"].isin(spatial_data2["pidp"]),["pidp", "SF_12"]]

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
        json_source = "/Users/robertclay/data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson"
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
        print(f"Merger done for {index} data for year {year}.")
        fname = "/Users/robertclay/data/" + index + f"_LSOA_with_SF12_{year}.geojson"
        with open(fname, 'w') as outfile:
            geojson.dump(map_geojson, outfile)

if __name__ == "__main__":
    years = np.arange(2016, 2017)
    main(years, "real")
    main(years, "minos")
