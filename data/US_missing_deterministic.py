"""For correcting missing data that is deterministic on other attributes."""


import pandas as pd
import numpy as np
import US_utils
import US_missing_description
import US_missing_LOCF

def det_missing(data, columns, conditioner, replacer):
    """Correct data that is deterministically missing.

    Requires a data frame, a column to correct, a condition function for correction,
    and a function which decides what to replace missing values with.

    Examples
    --------
    data : US data frame
    columns :  List of columns to update deterministically.
    conditioner : function that returns True if a person is unemployed. False otherwise.
    replacer: function that returns 0 regardless of other individual attributes.

    Parameters
    ----------
    data : pd.DataFrame
        The data to correct data for.
    column : list
        Which column to correct data for.
    conditioner, replacer : func
        A conditional function which takes the data and returns a column of booleans.
        These booleans determine which individuals are having data replaced.
        Replacer will determine what these missing values are replaced with.
        This can be a simple deterministic function, or determined by within/cross individual attributes.
    Returns
    -------
    """
    missing_types = ['-1', '-2', '-7', '-8', '-9', -1, -2, -7, -8, -9]

    # Calculate people who are unemployed (labour state 2) but registered as missing in SIC codes.
    # Assign these people 0 value SIC/SOC/NSSEC codes. Also set their job duration to 0.
    for column in columns:
        who_missing = data[column].isin(missing_types)
        who_condition = conditioner(data)
        missing_because_condition = who_missing & who_condition
        mbc_index = missing_because_condition.loc[missing_because_condition].index
        data[column] = replacer(data, mbc_index, column)
    return data

def is_employed(data):
    """Check who has reason to be unemployed. Students etc. may be employed but if not missing SIC code for example it
        doesn't matter.

    Parameters
    ----------
    data: pd.DataFrame
        Data frame to determine whether individuals are unemployed or not.

    Returns
    -------
    who: pd.Series
        A column of bools determining whether a person is unemployed or not.
    """
    # TODO this condition needs expanding. Needs to be that they have no other job information available as well.
    # Some students can be employed and be missing only one of SIC/SOC codes. These values are truly missing.
    # These people ARE employed and this current condition incorrectly replaces their job with nothing..
    who = data["labour_state"].isin(["Unemployed", "Family Care", "Student", "Sick/Disabled", "Retired"])
    return who

def force_zero(data, index, column):
    """

    Parameters
    ----------
    data
    index
    column

    Returns
    -------

    """
    data.loc[index, column] = 0
    return data[column]


def main():
    # Load in data.
    years = np.arange(1990, 2017)
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    # Summarise data before missingness.
    before = US_missing_description.missingness_table(data)
    US_missing_description.missingness_hist(data, "education_state", "age")
    US_missing_description.missingness_hist(data, "labour_state", "age")
    US_missing_description.missingness_bars(data, "education_state", "ethnicity")

    columns = ["job_industry",
               "job_duration_m",
               "job_duration_y",
               "job_sec",
               "job_occupation"]
    data = det_missing(data, columns, is_employed, force_zero)

    after = US_missing_description.missingness_table(data)
    US_missing_description.missingness_hist(data, "education_state", "age")
    US_missing_description.missingness_hist(data, "labour_state", "age")
    US_missing_description.missingness_bars(data, "education_state", "ethnicity")
    return data, before, after

if __name__ == "__main__":
    data, before, after = main()