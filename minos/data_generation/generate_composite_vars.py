#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file generates composite variables for use in the SIPHER project investigating pathways to change in mental health
"""
import pandas as pd
import numpy as np
import US_utils


def generate_composite_housing_quality(data):
    """
    Generate a composite housing quality variable from 6 variables found in Understanding Society (technically 7 as
    the heating variable is generated from a different variables in both BHPS and UKHLS that essentially measures
    the same thing).

    Information on the variables involved:
    - fridge_freezer    (cduse5)
    - washing_machine   (cduse6)
    - tumble_dryer      (cduse7)
    - dishwasher        (cduse8)
    - microwave         (cduse9)
    - heating           (BHPS - hsprbk & UKHLS - hheat)

    The composite variable (called housing_quality) will have 3 levels:
    - Yes to all    == 1
    - Yes to some   == 2
    - No to all     == 3

    Parameters
    ----------
    data : Pd.DataFrame
        A DataFrame containing corrected data from all years of Understanding Society (1990-2019)
    Returns
    -------
    data : Pd.DataFrame
        The same DataFrame now containing a composite housing quality variable
    """
    # first make list of the columns we're interested in
    sum_list = ['fridge_freezer', 'washing_machine', 'tumble_dryer', 'dishwasher', 'microwave', 'heating']
    # TODO: Improve this boolean definition. Can't for the life of me find a way to do this properly using the list
    # now create a boolean var that equals True only if all the values for each of these vars are non-negative (i.e. not missing)
    data["housing_complete"] = (data.loc[:, sum_list] >= 0).all(1)
    # sum up all non-negative values in sum_list vars
    data["housing_sum"] = data[sum_list].gt(0).sum(axis=1)

    # conditionally assign housing_quality var based on housing_sum
    # first set conditions and values for 3 level var
    conditions = [
        (data["housing_sum"] == 0),
        (data["housing_sum"] > 0) & (data["housing_sum"] < 6),
        (data["housing_sum"] == 6),
    ]
    values = [1, 2, 3]
    # Now apply conditions with numpy.select(), solution found here: https://datagy.io/pandas-conditional-column/
    data["housing_quality"] = np.select(conditions, values)

    return data


def calculate_hourly_wage(data):
    """

    Parameters
    ----------
    data : Pd.DataFrame
        A DataFrame containing corrected data from all years of Understanding Society (1990-2019)
    Returns
    -------
    data : Pd.DataFrame
        The same DataFrame now containing a calculated hourly wage variable
    """
    # apply basrate if present and non-negative (first make float)
    data["hourly_wage"] = data["hourly_rate"][data["hourly_rate"] >= 0]
    # Now calculate for salaried employees
    data["hourly_wage"][(data["gross_paypm"] > 0) & (data["job_hours"] > 0)] = data["gross_paypm"] / (data["job_hours"] * 4)

    # add in missing codes for known missings
    #data["hourly_wage"] = -9
    data["hourly_wage"][data["labour_state"] == "Unemployed"] = -1
    data["hourly_wage"][data["labour_state"] == "Retired"] = -2
    data["hourly_wage"][data["labour_state"] == "Self-employed"] = -3
    data["hourly_wage"][data["labour_state"] == "Sick/Disabled"] = -4
    data["hourly_wage"][data["labour_state"] == "Student"] = -5
    data["hourly_wage"][data["labour_state"].isin(["Government Training",
                                                   "Maternity Leave",
                                                   "Family Care",
                                                   "Other"])] = -6
    # now replace all still nan with -9
    data["hourly_wage"].fillna(-9, inplace=True)

    return data


def main():
    # first collect and load the datafiles for every year
    years = np.arange(1990, 2019)
    file_names = [f"data/corrected_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # generate composite variables
    data = calculate_hourly_wage(data)                  # hourly_wage
    data = generate_composite_housing_quality(data)     # housing_quality

    US_utils.save_multiple_files(data, years, "data/composite_US/", "")


if __name__ == "__main__":
    main()
