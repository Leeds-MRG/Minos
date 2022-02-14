"""Main file for running missing data correction on Understanding Societies in Python. """
import pandas as pd
import numpy as np
import os

import US_missing_description
import US_missing_deterministic as USmd
import US_missing_LOCF
import US_utils


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
    counts = counts.reset_index()
    # Inner merge counts dataframe into main dataframe. Results in one column of nobs added to data.
    data = data.merge(counts, how="inner", on="pidp")
    data["index"] = None
    return data


def main(output_dir):
    # Load in data.
    # Process data by year and pidp.
    years = np.arange(1990, 2019)
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    data = add_nobs_column(data)
    data = US_utils.restrict_chains(data, 2) #grab people with two or more obs.

    # Plots for distribution of missingness before correction. May be better in a separate file/notebook.
    US_missing_description.missingness_hist(data, "education_state", "age")
    US_missing_description.missingness_hist(data, "labour_state", "age")
    US_missing_description.missingness_bars(data, "education_state", "ethnicity")
    before = US_missing_description.missingness_table(data)

    # Correct deterministically missing data due to unemployment.
    columns = ["job_industry",
               "job_duration_m",
               "job_duration_y",
               "job_sec",
               "job_occupation"]
    data = USmd.det_missing(data, columns, USmd.is_employed, USmd.force_zero)
    middle = US_missing_description.missingness_table(data)

    columns = ["sex", "age", "ethnicity", "birth_year", "education_state", "depression_state", "labour_state",
               "job_duration_m", "job_duration_y", "job_occupation", "job_industry", "job_sec"]
    data = US_missing_LOCF.loc(data, columns, "f")

    # TODO MICE goes here to deal with remaining ~100k missing obs.

    after = US_missing_description.missingness_table(data)
    US_missing_description.missingness_hist(data, "education_state", "age")
    US_missing_description.missingness_hist(data, "labour_state", "age")
    US_missing_description.missingness_bars(data, "education_state", "ethnicity")

    data = data.replace([-1, -2, -7, -8, -9, "-1", "-2", "-7", "-8", "-9"], np.nan)
    data = data.dropna()

    US_utils.save_multiple_files(data, years, output_dir, "")

    return data, before, after


if __name__ == "__main__":

    output = 'data/corrected_US/'
    # check if output dir exists and create if not
    if not os.path.isdir(output):
        os.mkdir(output)

    data, before, after = main(output)
