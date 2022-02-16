#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 13:30:03 2021

@author: robertclay
file for generating some fake anxiety tables
"""

import pandas as pd
import numpy as np
import datetime

def load_bhps_file(file):
    """ Given a file directory load a BHPS wave as a pandas dataframe

    Parameters
    --------
    file : str
        path of the`file` to read

    Returns
    ------
    data : pandas.DataFrame
        Output `data` read from the csv at file.
    """

    data = pd.read_stata(file, convert_categoricals = False)
    return data

def subset_bhps_data(data):
    """Reformat BHPS data for use in daedalus framework. Take desired columns
    and remove any rows with NaN entries. Per BHPS data dictionaries
    this is intiger values -1 through -9 respectively. See them for more
    details.

    Parameters
    ----------
    data : pd.DataFrame
        `data` to take subset of

    Returns
    -------
    data : pd.DataFrame
        `data` subsetted.

    """
    # Columns to pull from data. Ethnicity, age, and gender.
    #columns = ["pid", "ba_sex" ,"ba_doby", "ba_race", "ba_plb4d"]
    columns = ["pidp", "a_sex" ,"a_birthy", "a_racel",]
               #"c_racelo_code", "c_racelot_code", "c_racelwt"] # needs locations not in this data.
    # take subset
    data = data[columns]
    # count how many NaN entries are in each row. If 0 return True
    index = np.sum(data.isin([-1, -2, -3, -4, -5, -6, -7, -8, -9]), axis = 1) == 0
    # take only rows with 0 missing entries 
    data = data[index]
    data.columns = ["pid", "sex", "age", "ETH.group",]# "location"]
    #data["pid"] = data.index
    return data

def format_gender_bhps(data):
    """ nothing needs to be done here. Its the same as in daedalus
    
    1 - male
    2 - female
    

    Parameters
    ----------
    data : pd.DataFrame
        `data` to process genders of.

    Returns
    -------
    data : pd.DataFrame
        `data` with processed genders.

    """
    gender_dict = {1: "M", 2: "F"}
    data = data.replace({"sex": gender_dict})
    return data

def format_age_bhps(data, current_time):
    """Convert year they were born into age in years.
    
    Since the monthborn is omitted just randomise it.

    Parameters
    ----------
    data : pd.DataFrame
        `data` to modify 
    
    current_time : datetime.datetime
        The current time to calculate the ages against.
        
    Returns
    -------
    data : TYPE
        DESCRIPTION.

    """
    
    # grab data, calculate age vs current_time, and convert into years
    ages = data["age"]
    ages = [datetime.datetime.strptime(str(age), "%Y") for age in ages]
    ages = [(current_time - age) for age in ages]
    ages = [age.total_seconds()/(60*60*24*365.25) for age in ages]
    
    # this should give the ages assuming everyone is born on 01/01 of their birth year.
    # now add some random birthdays.
    # I.E subtract a proportion of time between their current age (if younger than 1) 
    # and a whole year (if older than 1) to randomise their birthday.
    
    for i, age in enumerate(ages):
        if age < 1 :
            ages[i] -= np.random.uniform(0 , age)
        else:
            ages[i] -= np.random.uniform(0, 1)
        #ages[i] = int(ages[i])
    data["age"] = ages
    
    return data

def format_location_bhps(data):
    """ no location data yet. just use placehlder columns for MSOA and location
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.

    Returns
    -------
    data : TYPE
        DESCRIPTION.

    """
    data["MSOA"] = "no_location"
    data["location"] = "no_location"
    return data    

def format_ethnicity_bhps(data):
    """ convert intiger ethnicities of BHPS to three letter string tags.
    

    Parameters
    ----------
    data : pd.DataFrame
        `data` to format ethnicities of.

    Returns
    -------
    data : pd.DataFrame
        `data` with ethnicities formatted to three character format for daedalus.
    """
    
    int_to_str_ethnic_dict = {1: "WBI", #white british
                              # Misc white aggregated into white other WHO
                              2 : "WHO", # Irish 
                              3 : "WHO", # travller
                              4 : "WHO", # other
                              # Mixed races aggregated into MIX
                              5 : "MIX", # white black caribbean
                              6 : "MIX", # white black african
                              7 : "MIX", # white asian
                              8 : "MIX", # other
                              # asians
                              9 : "IND", # indian
                              10 : "PAK", # pakistani
                              11 : "BAN", # bangladeshi
                              12 : "CHI", # chinese
                              17 : "OAS", # arab put into other asian as not (yet?) in daedalus
                              13 : "OAS", # other asian
                              # black
                              14 : "BLC", # black carribean
                              15: "BLA", # black african
                              16 : "OBL", # other black
                              #other
                              97: "OTH", # other with BHPS' other id 97
                              }
    
    # replace items in ethnicity column
    # items with the given intiger keys of the dict above are replace with the three character 
    # ethnicity codes.
    data["ETH.group"] = data["ETH.group"].map(int_to_str_ethnic_dict)
    
    return data   

def save_rate_table(data, tier):
    data.to_csv(f"bhps_depression_tier{tier}_table.csv")

def main():

    file_source = "/Users/robertclay/Documents/6614stata_471A424C959CCFC9AE423A866B5794B9_V1/UKDA-6614-stata/stata/stata11_se/"
    file_name = "bphsw1/ba_indresp.dta"
    file_name = "ukhls_w1/a_indresp.dta"
    file_path = file_source + file_name
    current_time = datetime.datetime.strptime("00:00 01/01/2011", "%H:%M %d/%m/%Y")
    
    data = load_bhps_file(file_path)
    data = subset_bhps_data(data)
    data = format_gender_bhps(data)
    data = format_age_bhps(data, current_time)
    data = format_ethnicity_bhps(data)
    
    unique_ethnicity = set(data["ETH.group"])
    unique_sex = ["M", "F"]
    
    iterables = [unique_ethnicity]
    index = pd.MultiIndex.from_product(iterables, names = ["ETH.group"])
    rate_frame = pd.DataFrame(index = index)
    
    for sex in unique_sex:
        for age in np.arange(-1, 101):
            
            if age == -1:
                age_band = "B.0"
            elif age == 100:
                age_band = "100.101p"
            else: 
                age_band = str(age) + "." + str(age + 1)
            
            column_name = sex + age_band
            rate_frame[column_name] = [0.1] * len(rate_frame.index)
    
    save_rate_table(rate_frame, 0)
    save_rate_table(rate_frame, 1)
    save_rate_table(rate_frame, 2)


if __name__ == "__main__":
    main()