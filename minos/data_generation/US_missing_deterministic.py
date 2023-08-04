"""For correcting missing data that is deterministic on other attributes."""


import pandas as pd
import numpy as np
import US_utils
import US_missing_description


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
    columns : list
        Which column to correct data for.
    conditioner, replacer : func
        A conditional function which takes the data and returns a column of booleans.
        These booleans determine which individuals are having data replaced.
        Replacer will determine what these missing values are replaced with.
        This can be a simple deterministic function, or determined by within/cross individual attributes.
    Returns
    -------
    """

    # Calculate people who are unemployed (labour state 2) but registered as missing in SIC codes.
    # Assign these people 0 value SIC/SOC/NSSEC codes. Also set their job duration to 0.
    for column in columns:
        who_missing = data[column].isin(US_utils.missing_types)
        missing_because_condition = who_missing & conditioner(data)
        mbc_index = missing_because_condition.loc[missing_because_condition].index
        data = replacer(data, mbc_index, column)
    return data


def is_unemployed(data):
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

    who = data["labour_state_raw"].isin(["Unemployed", "Family Care", "Student", "Sick/Disabled", "Retired", 'Short-term Working'])
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
    return data


def force_nine(data, index, column):
    """
    Parameters
    ----------
    data
    index
    column
    Returns
    -------
    """
    data.loc[index, column] = "-9.0"
    return data


def force_minus_ten(data, index, column):
    """
    Parameters
    ----------
    data
    index
    column
    Returns
    -------
    """
    data.loc[index, column] = "-10.0"
    return data


def doesnt_smoke(data):
    return data['smoker'] == 2


def inapplicable_job_sector(data):
    return data['job_sector'] == -8


def inapplicable_number_of_children(data):
    return data['nkids_ind_raw'] == -8
    # return data['nkids_ind_raw'] < 0
    # return data['nkids_ind_raw'].isin([-1, -2, -7, -8, -9])


def main(data):
    print("Before removing deterministically missing values.")

    US_missing_description.missingness_table(data)
    # Table of missing values by row/column after correction.
    unemployed_columns = ["job_industry",
                           "job_duration_m",
                           "job_duration_y",
                           "job_sec",
                           "job_occupation"]
    # force unemployed people to have value 0 in unemployed_columns.
    data = det_missing(data, unemployed_columns, is_unemployed, force_zero)
    # Anyone who doesn't smoke force ncigs to 0.
    data = det_missing(data, ['ncigs'], doesnt_smoke, force_zero)
    # anyone who has job_sector == -8 (inapplicable) should be forced to 0
    data = det_missing(data, ['job_sector'], inapplicable_job_sector, force_zero)
    data = det_missing(data, ['nkids_ind_raw'], inapplicable_number_of_children, force_zero)

    # table of missing values by row/column after correction.
    print("After removing deterministically missing values.")
    US_missing_description.missingness_table(data)
    return data


if __name__ == "__main__":
    # Load in data.
    years = np.arange(2009, 2020)
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    data, before, after = main()
