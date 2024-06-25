""" File for correcting missing longitudinal data in US dataset.

"""

import pandas as pd
import numpy as np
import US_utils


def fix_leading_entries(data):
    """ Remove missing values for attributes due to leading data issues.
    
    Data is often only recorded when someone either enters the study for 
    immutable values (ethnicity) or when a mutable value (education) is 
    updated. Otherwise attributes can simply not be recorded as missing.
    This function aims to fill in any attributes that have leading values
    but are otherwise missing.

    Parameters
    ----------
    data : pd.DataFrame
        The main `data` frame for US to fix leading entries for.

    Returns
    -------
    data:

    """
    ids = list(set(data["pidp"]))
    fb_columns = ["ethnicity",
                  "education_state", 
                  "depression_state", 
                  "labour_state_raw",
                  "sex"]
    data = data.sort_values(by=["pidp", "time"])
    # divide data into individuals to alter seperately.
    # this is by far the most computionally heavy thing here so maybe do this
    # earlier if other functoins need it.
    
    # Loop over each agent (via pid and groupby) and front/back fill missing values
    # accordingly.
    
    pid_groupby = data.groupby(by=["pidp"], sort=False, 
                                     as_index = False)
    # fill forwards then backwards 
    fb_fill = pid_groupby[fb_columns].apply(lambda x: x.ffill().bfill())
    data[fb_columns] = fb_fill[fb_columns]
    #data.dropna(subset=["ethnicity", "education_state"], inplace=True)
    
    # back then forward filling is very risky here but not much better
    # only doing this after all other job status e.g. student are filled 
    # to 0 (no job) so the back fill doesnt falsely fill these.
    # TODO research better ways to fill emissing employment data.
    bf_columns = ["job_industry", "job_sec", "job_occupation"]
    bf_fill = pid_groupby[bf_columns].apply(lambda x: x.bfill().ffill())
    data[bf_columns] = bf_fill[bf_columns]
    
    #f_columns = ["labour_state"]
    #f_fill = pid_groupby[f_columns].apply(lambda x: x.ffill())
    #data[f_columns] = f_fill[f_columns]
    
    data = data.dropna(0)
    
    return data

        
def main(save):
    # Load data.
    wave_numbers = np.arange(2008, 2019)
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in wave_numbers]
    #wave_numbers = np.arange(2007, 2009)
    k = 3 # minimum number of data entries per individual.
    data = US_utils.load_multiple_data(file_names)
    data = data.reset_index(drop=True)
    data = data.drop(data.loc[data["labour_state"]=="Other"].index)

    # Restrict ages.
    # data = US_utils.restrict_variable(data, 0, 100)  # HR 444
    # Restrict to complete chains.
    # data = US_utils.restrict_chains(data, k)  # HR 444
    data = fix_leading_entries(data)
    if save:
        US_utils.save_multiple_files(data, wave_numbers, "data/corrected_US/", "")
    return data


if __name__ == "__main__":
    save = True
    data = main(save)
    
    

    