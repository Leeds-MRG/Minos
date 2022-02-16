""" File for missing data correction using last observation carried forward.

Note this is quite slow to do. Lambda functions aren't terrible but this can probably be improved.
"""

import pandas as pd
import numpy as np
import US_utils
import US_missing_description


def locf(data, f_columns = None, b_columns = None, fb_columns = None):
    """ Last observation carrying for correcting missing data.

    Data is often only recorded when someone either enters the study for
    the first time (immutable values e.g. ethnicity) is
    updated (mutable values e.g. education).
    Otherwise attributes are recorded as missing due to non-applicability (-8).
    This function aims to fill in any missing values due to this. E.g. ethnicity
    will be registered all the way through an individual's observations.

    Parameters
    ----------
    data : pd.DataFrame
        The main `data` frame for US to fix leading entries for. This frame must have pidp, time, and the desired list
        of columns.
    columns : list
    type : str
        Type of observation carrying to do. Either forwards 'f' backwards 'b' or forwards then backwards 'fb'.
        Defaults to forward as last observation carried forwards (locf) is the only one you should really do unless
        the attributes are immutable. Even then its tenuous.

    Returns
    -------
    data : pd. DataFrame
        The data frame with missing data correction done by observation carrying.

    """
    print("Starting locf. Grab a coffee..")
    # sort values by pidp and time. Need chronological order for carrying to make sense.
    # Also allows for easy replacing of filled data later.
    data = data.sort_values(by=["pidp", "time"])
    missing_types = ['-1', '-2', '-7', '-8', '-9', -1, -2, -7, -8, -9]

    # Group data into individuals to fill in separately.
    # Acts as a for loop to fill items by each individual. If you dont this it will try and fill the whole dataframe
    # at once.
    pid_groupby = data.groupby(by=["pidp"], sort=False, as_index=False)

    # Fill missing data by individual for given carrying type. Forwards, backwards, or forward then backwards.
    # See pandas ffill and bfill functions for more details.
    if f_columns:
        # Forward fill.
        fill = pid_groupby[f_columns].apply(lambda x: x.replace(missing_types, method="ffill"))
        data[f_columns] = fill
    if b_columns:
        # backward fill. only use this on IMMUTABLE attributes.
        fill = pid_groupby[b_columns].apply(lambda x: x.replace(missing_types, method="bfill"))
        data[b_columns] = fill
    if fb_columns:
        # forwards and backwards fill. again immutables only.
        fill = pid_groupby[fb_columns].apply(lambda x: x.replace(missing_types, method="ffill").replace(missing_types, method="bfill"))
        data[fb_columns] = fill
    data = data.reset_index(drop=True) # groupby messes with the index. make them unique again.
    return data

def main():
    # Load in data.
    # Process data by year and pidp.
    # perform LOCF using lambda forward fill functions.
    years = np.arange(1990, 2017)
    file_names = [f"../../data/deterministic_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    #US_missing_description.missingness_hist(data, "education_state", "age")
    #US_missing_description.missingness_hist(data, "labour_state", "age")
    #US_missing_description.missingness_bars(data, "education_state", "ethnicity")

    before = US_missing_description.missingness_table(data)
    f_columns = ["age", "education_state", "depression", "depression_change",
                 "labour_state", "job_duration_m", "job_duration_y", "job_occupation",
                 "job_industry", "job_sec"] #add more variables here.
    fb_columns = ["sex", "ethnicity", "birth_year"] # or here if they're immutable.
    data = locf(data, f_columns=f_columns, fb_columns=fb_columns)
    after = US_missing_description.missingness_table(data)
    #US_missing_description.missingness_hist(data, "education_state", "age")
    #US_missing_description.missingness_hist(data, "labour_state", "age")
    #US_missing_description.missingness_bars(data, "education_state", "ethnicity")
    US_utils.save_multiple_files(data, years, '../../data/locf_US/', "")
    return data, before, after

if __name__ == "__main__":
    data, before, after = main()