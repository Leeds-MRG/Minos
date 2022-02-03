#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 10:42:32 2021

@author: robertclay
"""

import numpy as np
from collections import Counter

from US_missing_data_correction import load_data

def individual_trajectories(data, attribute, trajectories_ids):
    """ Grab trajectories for each person for a given attribute.
    
    E.G. grabbing the qualification attribute trajcetories will produce a list
    of the education paths for each person. These may looks like:
    ["GCSE GCSE GCSE",
     "GCSE GCSE A-Level",
     "A-Level Degree Higher Degree",
     ...]
    I.E. the trajectories of three people who get no further education, 
    A-levels, and a Masters degree respectively.
    
    Parameters
    ----------
    data : pandas.DataFrame
        The subsetted `data` of people with at least k entires.
    attribute : string
        The desired `attribute` to grab the trajctories of.
    trajectories_ids : list
        `trajectories_ids` The personal IDs (pids) of anyone with at least
        k entries. Useful for subsetting with loc.
    Returns
    -------
    transitions : list
        A list of `transitions` for each individual over time 
        for the given attribute.

    """
    # Group over ids (and time).
    # Lambda functions grabs the values of attribute over time for each person.
    # Then cast to list instead of pd series.
    
    pid_groupby = data.groupby(by=["pidp"], sort=False, 
                                     as_index = False)
    trajectories = pid_groupby[attribute].apply(lambda x: list(x.values))
    trajectories = list(trajectories)
    return trajectories

def print_freq_table(transitions):
    """ Output a frequency table giving the most common trajectories.
    

    Parameters
    ----------
    transitions : list
        A list of `transitions` for each individual over time 
        for the given attribute.

    Returns
    -------
    freq_table : collection.Counter
        `freq_table` A frequency table indicating which 

    """
    freq_table = Counter(transitions)
    #print(freq_table)
    return freq_table

def is_string_in(main_string, sub_strings):
    """Is a substring in another string?
    
    Parameters
    ----------
    main_string : str
        `main_string` the string to search. 
    sub_strings : list
        `sub_strings` A list of strings to search for in the main string.

    Returns
    -------
    is_match : bool
        `is_match` Are any of the the sub strings in the main string.
    """
    is_match = False

    for sub_string in sub_strings:
        
        s = len(sub_string)
            
        for i in range(len(main_string[:-s])):
            # search for the first letter only initially for speed.
            if main_string[i] == sub_string[0]:
                # If the first letter is found check if the whole string is there.
                # Can probably do this faster by searching for 2nd then 3rd letters...
                if main_string[i : i + s] == sub_string:
                    
                    is_match = True
                    break
                
    return is_match     

def single_transitions(trajectories):
    """split up qualification trajectories into length two transitions.
    
    
    """
    transitions = []
    for traj in trajectories:
        
        n = len(traj)
        
        for i in range(n-1):
            
            transition = str(traj[i:i+2])
            transitions.append(transition)            
    return transitions

def unique_transitions(trajectories):
    """ Record transitions only when a new value occurs
    

    Returns
    -------
    None.

    """
    transitions = []
    for traj in trajectories:
        transition = []
        previous_item = None
        for i in range(len(traj)):
            
            item = traj[i]
            if item != previous_item:
                transition.append(item)
            previous_item = item
            
        transitions.append(str(transition))
    return transitions

if __name__ == "__main__":

    wave_numbers = np.arange(1991, 2017)    
    data = load_data(wave_numbers)
    data = data.dropna(0)
    ids = list(np.unique(data["pidp"]))
    trajectories = individual_trajectories(data, "education_state", ids)
    transitions = unique_transitions(trajectories)
    # print frequency table
    freq_table = dict(print_freq_table(transitions))
       