#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 14:12:06 2021

@author: robertclay

This file is for parsing the understanding societies data over all waves into 
a persistent data frame containing immutable person attributes for all
agents over all times and variable frames containing values that do change
over each wave.

This file is necessary due to the formatting of BHPS. If a person enters
a given wave most of their attributes are not carries on to the next wave. 
For example their ethnicity is registered when they enter but then recorded as 
N/A (-8) for remaining waves. Even variable attributes such as their age may 
be recorded as N/A when they can change. In some cases this may be due to
no follow up. Someone with a disease may not be asked about it again. 
If this not a chronic disease it is difficult to say if they have maintained 
their state and interpolation is required.

For now, this file is just reorganising the 4 main attributes extracted for 
vivarium age, ethnicity, id number, and sex to keep the population high.
"""

import glob
from string import ascii_lowercase
import pandas as pd

def all_wave_directories(source, suffix):
    """ Get all file names for bhps waves
    

    Parameters
    ----------
    source : str
        `source` where are directories.

    Returns
    -------
    directories : list
        List of `directories` to extract from.

    """
    
    directories = sorted(glob.glob(source + suffix + "*"))
    return directories

def extract_data_files(directories):
    
    
    return datasets

if __name__ == "__main__":
    source = "/Users/robertclay/Documents/6614stata_471A424C959CCFC9AE423A866B5794B9_V1/UKDA-6614-stata/stata/stata11_se/"
    bhps_dirs = all_wave_directories(source, "bhps_")
    uklhs_dirs = all_wave_directories(source, "ukhls_w")
    
    uklhs_cross = pd.read_stata(uklhs_dirs[-1] + "/xwavedat.dta")
    uklhs_cross = uklhs_cross[["pid", "ethn_dv", "sex"]]
    