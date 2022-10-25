"""File for formatting minos output with Chris' spoatially weighted data.
"""

import pandas as pd
import geojson
from collections import defaultdict
import numpy as np
import argparse

def main(source, destination, v, tag, method_type):

    """ Aggregate some attribute v to LSOA level and put it in a geojson map.

    - Merge minos data onto spatially weighted LSOAs.
    - Calculate group mean for each LSOA.
    - Convert mean LSOA data into properties for the ONS LSOA GeoJSON.
    - Save to geojson for plotting elsewhere.

    Parameters
    ----------
    source, destination: str
        Where are data being sourced from and what destination is the final geojson being saved to.
    v, tag: str
        Which variable v is being used. Output will create a summary value of v for each LSOA.
    method : str
        What mean is used in pandas groupby. For now just mean and median. Can specify custom functions
         with groupby.apply though
    Returns
    -------
    None
    """

    msim_data = pd.read_csv(source)
    # chris' spatially weighted data.
    spatial_data = pd.read_csv("/Users/robertclay/data/ADULT_population_GB_2018.csv")

    # subset US data. grab common pidps to prevent NA errors.
    spatial_data2 = spatial_data.loc[spatial_data["pidp"].isin(msim_data["pidp"]), ]
    US_data2 = msim_data.loc[msim_data["pidp"].isin(spatial_data2["pidp"]),["pidp", v]]

    # left merge US data into spatial data.
    spatial_data2 = spatial_data2.merge(US_data2, how='left', on='pidp')

    # aggregate spatial data. Group by LSOAs (ZoneID)
    # TODO generalising this groupby to take methods other than just the mean.

    if method_type == "mean":
        group_method = np.mean
        method_kwargs = {}
    if method_type == "median":
        group_method = np.median
        method_kwargs = {}

    spatial_data3 = spatial_data2.groupby("ZoneID")[v].apply(lambda x: group_method(x, **method_kwargs))
    spatial_data3 = pd.DataFrame(spatial_data3)
    spatial_data3["ZoneID"] = spatial_data3.index # put zoneid back into dataframe and reset index.
    spatial_data3 = spatial_data3.reset_index(drop=True)  # resetting index that is changed by groupby.

    # default dict assigns missing values to 0. prevents key errors later for any LSOA missing a value.
    # create a dictionary with keys as LSOAs and values as mean v by LSOA.
    spatial_dict = defaultdict(int, zip(spatial_data3["ZoneID"], spatial_data3[v]))
    print("merger done.")

    save_type = 'csv'
    if save_type == 'geojson':
    # Load in national LSOA geojson map data from ONS.
    #https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2011-boundaries-super-generalised-clipped-bsc-ew-v3/about
        json_source = "persistent_data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson"
        with open(json_source) as f:
            map_geojson = geojson.load(f)

        # loop over geojson features and add in new variable mean property.
        for i, item in enumerate(map_geojson["features"]):
            # grab LSOA of feature and corresponding mean value of v.
            ons_code = item["properties"]["LSOA11CD"]
            variable_code = spatial_dict[ons_code]
            if variable_code == 0: # TODO needs improving with a more general catch all.
                variable_code = None
            # assign the new mean of v to the geojson feature.
            # assign the updated feature back into the geoJSON.
            item['properties'][v] = variable_code
            map_geojson['features'][i] = item

        # save updated geojson for use in map plots.
        print(sum(spatial_dict.values()))
        print(f"GeoJSON attribute added.")
        fname = destination + f"LSOAs_{v}.geojson"
        print(f"Saving to {fname}.")
        with open(fname, 'w') as outfile:
            geojson.dump(map_geojson, outfile)
    if save_type == "csv":
        spatial_data3.to_csv(destination + f"{tag}_LSOAs_{v}.csv", index=False)

if __name__ == "__main__":
    # data from some real US/minos
    # run in terminal e.g.
    # python3 minos/validation.format_spatial_output.py -s output/WS4Intervention/2019.csv -t living_wage -d output/WS4Intervention/ -v hh_income -m mean
    # python3 minos/validation.format_spatial_output.py -s data/final_US/2019.csv -t baseline -d output/WS4Intervention/ -v hh_income -m mean

    parser = argparse.ArgumentParser(description="Raw Data formatting from Understanding Society")
    parser.add_argument("-s", "--source", required=True, type=str,
                        help="The source directory for Understanding Society/Minos data.")
    parser.add_argument("-t", "--tag", required=True, type=str,
                        help="Additional tag for which data is being processed. I.E which intervention baseline/living wage etc.")
    parser.add_argument("-d", "--destination", required=True, type=str,
                        help="Where is the appended geoJSON being saved to.")
    parser.add_argument("-v", "--variable", required=True, type=str,
                        help="What variable from Minos is being appended to the geoJSON (SF_12, hh_income, etc.).")
    parser.add_argument("-m", "--method", required=True, type=str,
                        help="What method is used to aggregate individuals by LSOA.")

    args = vars(parser.parse_args())

    source = args['source']
    tag = args['tag']
    destination = args['destination']
    v = args['variable']
    method = args['method']

    #source = f"output/test_output/simulation_data/2018.csv" # if estimating LSOAs using minos data from some output.
    #source = f"data/final_US/{year}_US_Cohort.csv" # if estimating LSOAs using real data.
    #destination = f"output/test_output/simulation_data/"
    #v = "SF_12"
    main(source, destination, v, tag, method)
