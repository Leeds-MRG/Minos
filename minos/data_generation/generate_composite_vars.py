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

    # drop cols we don't need
    data.drop(labels=['housing_sum', 'housing_complete'], axis=1, inplace=True)

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
    # apply basrate (hourly_rate) if present and non-negative
    #data["hourly_wage"] = data["hourly_rate"][data["hourly_rate"] >= 0]
    # Now calculate for salaried employees
    #data["hourly_wage"][(data["gross_paypm"] > 0) & (data["job_hours"] > 0)] = data["gross_paypm"] / (data["job_hours"] * 4)
    # Now calculate for self-employed (make sure s/emp pay not missing and hours worked over 0)
    #data["hourly_wage"][(~data["gross_pay_se"].isin([-8, -7])) & (data["job_hours_se"] > 0)] = data["gross_pay_se"] / (data["job_hours_se"] * 4)

    # Try a different one where we combine gross pay and business income as well as job and business hours
    # first calculate a monthly income from the business
    data["jb_inc_monthly"] = -9
    data["jb_inc_monthly"][(data["jb_inc"] >= 0) & (data["jb_inc_per"] == 1)] = data["jb_inc"] * 4
    data["jb_inc_monthly"][(data["jb_inc"] >= 0) & (data["jb_inc_per"] == 2)] = data["jb_inc"]
    # Add up the incomes
    data["total_income"] = 0
    data["total_income"][data["jb_inc_monthly"] >= 0] += data["jb_inc_monthly"]
    data["total_income"][data["gross_paypm"] >= 0] += data["gross_paypm"]
    data["total_income"][data["gross_pay_se"] >= 0] += data["gross_pay_se"]
    data["total_income"][(data["jb_inc_monthly"] < 0) & (data["gross_paypm"] < 0) & (data["gross_pay_se"] < 0)] = -9
    #data["total_income"][(data["jb_inc_monthly"] >= 0) or (data["gross_paypm"] >= 0) or (data["gross_pay_se"] >= 0)] = data["jb_inc_monthly"] + data["gross_paypm"]
    # Add up the working hours
    data["total_hours"] = 0
    data["total_hours"][data["job_hours"] > 0] += data["job_hours"]
    data["total_hours"][data["job_hours_se"] > 0] += data["job_hours_se"]
    data["total_hours"][(data["job_hours"] < 0) & (data["job_hours_se"] < 0)] = -9
    # now calculate hourly wage again
    data["hourly_wage"] = 0
    data["hourly_wage"][(data["total_income"] >= 0) & (data["total_hours"] >= 0)] = data["total_income"] / (data["total_hours"] * 4)
    data["hourly_wage"][(data["total_income"] < 0) | (data["total_hours"] < 0)] = -9

    # add in missing codes for known missings
    data["hourly_wage"][data["labour_state"] == "Unemployed"] = -1
    data["hourly_wage"][data["labour_state"] == "Retired"] = -2
    data["hourly_wage"][data["labour_state"] == "Sick/Disabled"] = -3
    data["hourly_wage"][data["labour_state"] == "Student"] = -4
    data["hourly_wage"][data["labour_state"].isin(["Government Training",
                                                   "Maternity Leave",
                                                   "Family Care",
                                                   "Other"])] = -5
    # now replace all still nan with -9
    data["hourly_wage"].fillna(-9, inplace=True)

    return data


def generate_hh_income(data):
    """

    Parameters
    ----------
    data : Pd.DataFrame
        A DataFrame containing corrected data
    Returns
    -------
    data : Pd.DataFrame
        The same DataFrame now containing a calculated household income variable
    """
    ## Calculation of household income:
    # hh_intermediate = ((net hh income) - (rent + mortgage + council tax)) * hh_size
    # hh_income = hh_intermediate adjusted for inflation using CPI

    # first calculate outgoings (set to 0 if missing (i.e. if negative))
    data["hh_rent"][data["hh_rent"] < 0] = 0
    data["hh_mortgage"][data["hh_mortgage"] < 0] = 0
    #data["hh_ctax"][data["hh_ctax"] < 0] = 0  # add this in when possible
    data["outgoings"] = -9
    data["outgoings"] = data["hh_rent"] + data["hh_mortgage"] # + data["hh_ctax"]


    # Now calculate hh income before adjusting for inflation
    data["hh_income"] = -9
    data["hh_income"] = (data["hh_netinc"] - data["outgoings"]) * data["oecd_equiv"]

    # Adjust hh income for inflation
    data = US_utils.inflation_adjustment(data, "hh_income")

    return data



def main():
    # first collect and load the datafiles for every year
    years = np.arange(1990, 2019)
    file_names = [f"data/corrected_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # generate composite variables
    #data = calculate_hourly_wage(data)                  # hourly_wage
    data = generate_composite_housing_quality(data)     # housing_quality
    data = generate_hh_income(data)                     # hh_income

    US_utils.save_multiple_files(data, years, "data/composite_US/", "")


if __name__ == "__main__":
    main()
