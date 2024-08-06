"""Main file for running missing data correction on Understanding Societies in Python. """
import pandas as pd
import numpy as np
import os

import US_missing_description
import US_missing_deterministic as USmd
import US_missing_LOCF
import US_missing_data_correction as USmdc
import US_utils
import US_complete_case as UScc

def add_nobs_column(data):
    """ Add column for number of observations (nobs) per individual to data frame

    Parameters
    ----------
    data : pd.DataFrame
        Data frame to add number of observations column to.

    Returns
    -------
    data : pd.DataFrame
        Frame with column added.
    """
    # build counts data frame. two columns for number of observations and indiviudal ids.
    counts = pd.DataFrame(data["pidp"].value_counts())
    counts.columns = ["nobs"]
    counts["pidp"] = counts.index
    counts = counts.reset_index(drop=True)
    # Inner merge counts dataframe into main dataframe. Results in one column of nobs added to data.
    data = data.merge(counts, how="inner", on="pidp")
    return data


def main(output_dir):
    maxyr = US_utils.get_data_maxyr()
    # Load in data.
    # Process data by year and pidp.
    years = np.arange(1991, maxyr)  # need the full range of US data for locf imputation.
    save_years = np.arange(2009, maxyr)  # only saving UKHLS data after 2009.

    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    #data = add_nobs_column(data)
    # data = US_utils.restrict_chains(data, 2)  # grab people with two or more obs.  # HR 444

    # missingness table simply counts number of missing data entries in entire data frame.
    print("Raw data before correction")

    # Last observation carried forwards (LOCF) interpolation of variables only recorded when changed.
    data_locf = US_missing_LOCF.main(data)
    data = data_locf.where(-data_locf.isnull(), data) # this is the more complex version.

    # Correct deterministically missing data due to unemployment. see US_missing_deterministic.py
    data = USmd.main(data)

    # Cut back to just save data. don't want to complete case rows that aren't used.
    print("Removing data before 2009 as it is not used in MINOS.")
    data = data.loc[data["time"].isin(save_years)]

    # TODO Any further deterministic missingness correction goes here? this is entirely deterministic correction for now.
    # TODO MICE goes here to deal with remaining missing obs. current just using complete case. from US_complete_case.py
    # TODO a further deterministic stage may be needed to better handle missing values in composites.

    # data = data.loc[data['region'] != "Northern Ireland", ]
    US_utils.save_multiple_files(data, save_years, output_dir, "")


if __name__ == "__main__":
    output_dir = 'data/corrected_US/'
    main(output_dir)
