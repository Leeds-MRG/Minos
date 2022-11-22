"""File for formatting minos output with Chris' spoatially weighted data.
"""

import pandas as pd
import geojson
from collections import defaultdict
import numpy as np
import argparse
import glob
import os

def eightyTwenty(income):

    split = pd.qcut(income, q=5, labels=[1, 2, 3, 4, 5])
    who_bottom_twenty = split == 1
    who_top_eighty = split > 1
    eightyTwentyRatio = sum(income[who_bottom_twenty])/sum(income[who_top_eighty])
    return eightyTwentyRatio


def group_minos_by_pidp(source, year, v, method):
    """ Load files from multiple minos runs and aggregate SF12 by mean.
    Parameters
    ----------
    source

    Returns
    -------

    """
    files = glob.glob(source + f"/*{year}.csv")
    df = pd.DataFrame()
    for file in files:
        df = pd.concat([df, pd.read_csv(file, low_memory=True)])
    df = df.groupby(['pidp']).apply(lambda x: method(x[v]))
    df = pd.DataFrame(df)
    df.columns = [v]
    df['pidp'] = df.index
    df.reset_index(drop=True, inplace=True)
    return df

def main(source, year, destination, v = "SF_12", method = np.nanmean, save_type='geojson'):

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
    print(f"Aggregating MINOS data at {source} for {year}.")
    msim_data = group_minos_by_pidp(source, year, v, method)
    print('Done. Merging with spatial data..')
    # chris spatially weighted data.
    spatial_data = pd.read_csv("persistent_data/ADULT_population_GB_2018.csv")
    #spatial_data = pd.read_csv("persistent_data/ADULT_population_GB_2018_with_LADS.csv")

    # subset msim data. grab common pidps to prevent NA errors.

    common_pidps = spatial_data.loc[spatial_data["pidp"].isin(msim_data["pidp"]),'pidp']
    msim_data = msim_data.loc[msim_data["pidp"].isin(common_pidps),["pidp", v]]

    spatial_data = spatial_data.loc[spatial_data["pidp"].isin(common_pidps),].merge(msim_data, how='left', on='pidp')

    # aggregate spatial data. Group by LSOAs (ZoneID)
    # TODO generalising this groupby to take methods other than just the mean.

    # TODO just aggregates over LSOA for now. maybe specify different resolutions if they are added to chris' data.
    #group_on = "LADcd" # which spatial resolution to group by. LAD or LSOA
    group_on = "ZoneID"
    # group over spatial resolution and aggregate using method (usually nanmean) to get aggregate values by spatial area.
    # E.g. get mean sf12 by lsoa.
    spatial_data = spatial_data.groupby(group_on).apply(lambda x: method(x[v]))
    spatial_data = pd.DataFrame(spatial_data)
    spatial_data.columns = [v]
    spatial_data[group_on] = spatial_data.index # put zoneid back into dataframe and reset index. rename to LSOAcd.
    spatial_data.reset_index(inplace=True, drop=True)  # resetting index that is changed by groupby.


    # default dict assigns missing values to 0. prevents key errors later for any LSOA missing a value.
    # create a dictionary with keys as LSOAs and values as mean v by LSOA.

    print('Done. Saving..')
    # just csvs. used for WS4.
    if save_type == "csv":
        spatial_data.to_csv(os.path.join(destination, f"{method.__name__}_{group_on}_{v}.csv", index=False))
    elif save_type == 'geojson':
        # convert
        spatial_dict = defaultdict(int, zip(spatial_data["ZoneID"], spatial_data[v]))
        # Load in national LSOA geojson map data from ONS.
        #https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2011-boundaries-super-generalised-clipped-bsc-ew-v3/about
        json_source = "persistent_data/UK_super_outputs.geojson"
        with open(json_source) as f:
            map_geojson = geojson.load(f)

        # loop over geojson features and add in new variable mean property.
        for i, item in enumerate(map_geojson["features"]):
            # grab LSOA of feature and corresponding mean value of v.
            ons_code = item["properties"]["ZoneID"]
            variable_code = spatial_dict[ons_code]
            if variable_code == 0: # TODO needs improving with a more general catch all.
                variable_code = None
            # assign the new mean of v to the geojson feature.
            # assign the updated feature back into the geoJSON.
            item['properties'][v] = variable_code
            map_geojson['features'][i] = item

        # save updated geojson for use in map plots.
        print(f"GeoJSON {v} attribute added.")
        fname = os.path.join(destination, f"{method.__name__}_{v}_{year}.geojson")
        print(f"Saving to {fname}.")
        with open(fname, 'w') as outfile:
            geojson.dump(map_geojson, outfile)

if __name__ == "__main__":
    # data from some real US/minos
    # run in terminal e.g.
    # python3 minos/validation.format_spatial_output.py -s output/WS4Intervention/2019.csv -t living_wage -d output/WS4Intervention/ -v hh_income -m mean
    # python3 minos/validation.format_spatial_output.py -s data/final_US/2019.csv -t baseline -d output/WS4Intervention/ -v hh_income -m mean

    parser = argparse.ArgumentParser(description="Raw Data formatting from Understanding Society")
    parser.add_argument("-s", "--source", required=True, type=str,
                        help="The source directory for Understanding Society/Minos data.")
    parser.add_argument("-y", "--year", required=True, type=str,
                        help="Year of minos data to plot. e.g. 2014.")
    parser.add_argument("-d", "--destination", required=True, type=str,
                        help="Where is the appended geoJSON being saved to.")
    parser.add_argument("-v", "--variable", required=False, type=str,
                        help="What variable from Minos is being appended to the geoJSON (SF_12, hh_income, etc.).")
    parser.add_argument("-m", "--method", required=False, type=str,
                        help="What method is used to aggregate individuals by LSOA.")
    parser.add_argument("-f", "--format", required=True, type=str,
                        help="What file format is used. csv or geojson.")

    args = vars(parser.parse_args())

    source = args['source']
    year = args['year']
    destination = args['destination']
    v = args['variable']
    method_type = args['method']
    save_type = args['format']

    if method_type == "nanmean":
        method = np.nanmean
    else:
        #TODO no better way to do this to my knowledge without eval() which shouldn't be used.
        raise ValueError("Unknown aggregate function specified. Please add specifc function required at 'aggregate_minos_output.py")


    #source = f"output/test_output/simulation_data/2018.csv" # if estimating LSOAs using minos data from some output.
    #source = f"data/final_US/{year}_US_Cohort.csv" # if estimating LSOAs using real data.
    #destination = f"output/test_output/simulation_data/"
    #v = "SF_12"
    main(source, year, destination, v, method, save_type)
