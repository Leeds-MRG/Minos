#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: robertclay

Compress rate tables to remove location aspect.
Essentially grouping all the race/sex categorys by MSOA and taking the mean.
Needed until can get location data for BHPS.
"""

import pandas as pd

def collapse_index_rate_table(data, file_name):
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
    data = data.drop("LAD.code", axis = 1)
    data = data.drop("LAD.name", axis = 1)

    data = data.groupby(["ETH.group"], as_index= False).mean()
    #data["LAD.code"] = "no_locations"
    #data["LAD.name"] = "no_locations"
    data.to_csv("nolocation_" + file_name, index = True)
    
    return data
    
if __name__ == "__main__":    
    file_name = "Mortality2011_LEEDS1_2.csv"
    data = pd.read_csv(file_name, index_col = 0)
    d1 = collapse_index_rate_table(data, file_name)
    
    file_name2 = "Fertility2011_LEEDS1_2.csv"
    data = pd.read_csv(file_name)
    d2 = collapse_index_rate_table(data, file_name2)
