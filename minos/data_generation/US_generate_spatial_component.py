"""This file generates a synthetic spatial component for Understanding Society data to be used in Minos."""


import pandas as pd
import numpy as np
import argparse

import US_utils

def main(years):
    # Take source from command line args (or most likely from Makefile variable)
    parser = argparse.ArgumentParser(description="Adding spatial data from Chris' spatially disaggregated lookup dataset.")
    parser.add_argument("-s", "--source_dir", required=True, type=str,
                        help="The source directory for the spatially disaggregated lookup.")
    args = parser.parse_args()

    # Get source from args
    source = args.source_dir

    # Chris' spatial data
    # only load this in once its very big. 53m rows.
    chris_data = pd.read_csv(source + "ADULT_population_GB_2018.csv")

    for year in years:
        sheffield_lsoas = pd.read_csv("persistent_data/sheffield_lsoas.csv")
        # data from some real US/minos output
        US_data = pd.read_csv(f"data/final_US/{year}_US_cohort.csv")
        # subset US data. grab common pidps to prevent NA errors.
        spatial_data = chris_data.loc[chris_data["ZoneID"].isin(sheffield_lsoas['x']),]
        spatial_data = spatial_data.loc[spatial_data["pidp"].isin(US_data["pidp"]),]
        # left merge US data into spatial data.
        spatial_data = spatial_data.merge(US_data, how='left', on='pidp')
        print(f"Saving spatial data for year: {year}.")
        US_utils.save_file(spatial_data, "spatial_US", "", year)
        #spatial_data.to_csv(f"data/spatial_US/{year}_US_cohort.csv")

if __name__ == '__main__':
    main(np.arange(2009, 2019, 1))