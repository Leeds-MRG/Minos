#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: robertclay

Functions for refactoring daedalus rate tables. See RateTables.BaseHandler for generation of these tables from scratch.

Compress rate tables to remove location aspect.
Essentially grouping all the race/sex categorys by MSOA and taking the mean.
Needed until can get location data for BHPS.

Compress LAD rate tables into regional rate tables.

"""

import pandas as pd
from US_utils import load_json

LAD_to_region_code = load_json("persistent_data/JSON/", "LAD_to_region_code.json")
LAD_to_region_name = load_json("persistent_data/JSON/", "LAD_to_region_name.json")


def collapse_location(data, file_name):
    """ Pull data frame. Group all rates by the MSOA code and take the mean.
    Save data frame.
    
    
    NOTE: we want to group by both the LAD name and code here. Since
    they are 1 to 1 correspondance however just one is fine and quicker.
    
    Parameters
    --------
    data: pd.DataFrame
     pandas `data` rate table to collapse.
    Returns
    -------
    None.

    """
    # TODO this could be generalised much better.
    # remove unecessary columns
    data = data.drop("LAD.code", axis = 1)
    data = data.drop("LAD.code", axis = 1)

    data = data.groupby(["ETH.group"], as_index= False).mean()
    #data["LAD.code"] = "no_locations"
    #data["LAD.name"] = "no_locations"
    data.to_csv("nolocation_" + file_name, index = True)
    
    return data


def collapse_LAD_to_region(data, file_output):
    """ Pull data frame. Group all rates by the MSOA code and take the mean.
    Save data frame.


    NOTE: we want to group by both the LAD name and code here. Since
    they are 1 to 1 correspondance however just one is fine and quicker.

    Parameters
    --------
    data: pd.DataFrame
     pandas `data` rate table to collapse.
    Returns
    -------
    None.

    """
    # map LAD names and codes to region name and codes.
    data["REGION.code"] = data["LAD.code"].map(LAD_to_region_code)
    data["REGION.name"] = data["LAD.name"].map(LAD_to_region_name)

    # remove LAD columns
    data = data.drop(["LAD.name", "LAD.code"], 1)

    # Group rates by region and ethnicity and take the mean. gives mean rate by region, eth, sex, and age.
    data = data.groupby(["REGION.name", "ETH.group"], as_index=False).mean()
    # rename region and eth columns. done later in BaseHandler instead.
    #columns = list(data.columns)
    #columns[:2] = ["location", "ethnicity"]
    #data.columns = columns
    # save rate tables.
    data.to_csv(file_output, index=True)

    return data

def main(file_source):

    file_name = "Mortality2011_LEEDS1_2.csv"
    data = pd.read_csv(file_source + file_name, index_col=0)
    d1 = collapse_LAD_to_region(data, file_source + "regional_" + file_name)

    file_name = "Fertility2011_LEEDS1_2.csv"
    data = pd.read_csv(file_source + file_name)
    d2 = collapse_LAD_to_region(data, file_source + "regional_" + file_name)
    return d1, d2

if __name__ == "__main__":
    file_source = "persistent_data/"
    d1, d2 = main(file_source)
