

import pandas as pd
import numpy as np
from numpy.random import choice
import argparse
import os
from uuid import uuid4
from rpy2.robjects.packages import importr

import US_utils
from minos.modules import r_utils


def generate_replenishing(projections, scotland_mode, cross_validation, inflated, region):
    print("Generating replenishing...")




def main():
    # Use argparse to select between normal and scotland mode
    parser = argparse.ArgumentParser(description="Generating replenishing populations.",
                                     usage='use "%(prog)s --help" for more information')

    parser.add_argument("-r", "--region", default="",
                        help="Generate replenishing population for specified synthetic scaled data. glasgow or "
                             "scotland for now.")
    parser.add_argument("-s", "--scotland", action='store_true', default=False,
                        help="Select Scotland mode to only produce replenishing using scottish sample.")
    parser.add_argument("-c", "--cross_validation", dest='crossval', action='store_true', default=False,
                        help="Select cross-validation mode to produce cross-validation replenishing population.")
    parser.add_argument("-i", "--inflated", dest='inflated', action='store_true', default=False,
                        help="Select inflated mode to produce inflated cross-validation populations from inflated"
                             "data.")

    args = parser.parse_args()
    scotland_mode = args.scotland
    cross_validation = args.crossval
    inflated = args.inflated
    region = args.region

    # read in projected population counts from 2008-2070
    proj_file = "persistent_data/age-sex-ethnic_projections_2008-2061.csv"
    projections = pd.read_csv(proj_file)
    # rename and drop some columns to prepare
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    generate_replenishing(projections, scotland_mode, cross_validation, inflated, region)


if __name__ == "__main__":
    print("Running the show!")
    main()
