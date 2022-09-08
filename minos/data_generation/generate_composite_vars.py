#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file generates composite variables for use in the SIPHER project investigating pathways to change in mental health.

Currently does not handle missing data for composites. This is done in R using the mice package. May be worth moving
these functions entirely into R. Some variables are imputed then combined and vice versa which makes this tricky.
"""
import pandas as pd
import numpy as np

import US_utils
import US_missing_description as USmd

# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning


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
    data["housing_complete"] = (data.loc[:, sum_list] >= 0).all(1)
    # sum up all non-negative values in sum_list vars
    data["housing_sum"] = data[sum_list].gt(0).sum(axis=1)

    # conditionally assign housing_quality var based on housing_sum
    # first set conditions and values for 3 level var
    # TODO virtually noone in the bottom tier. need to experiment with critical/luxury items.
    # Switch to 2 or more for now.
    #conditions = [
    #    (data["housing_sum"] == 0),
    #    (data["housing_sum"] > 0) & (data["housing_sum"] < 6),
    #    (data["housing_sum"] == 6),
    #]
    conditions = [
        (data["housing_sum"] <= 2),
        (data["housing_sum"] > 2) & (data["housing_sum"] < 6),
        (data["housing_sum"] == 6),
    ]
    values = [1, 2, 3]
    # Now apply conditions with numpy.select(), solution found here: https://datagy.io/pandas-conditional-column/
    data["housing_quality"] = np.select(conditions, values)

    # drop cols we don't need
    data.drop(labels=['housing_sum', 'housing_complete', 'fridge_freezer', 'washing_machine', 'tumble_dryer',
                      'dishwasher', 'microwave', 'heating'],
              axis=1,
              inplace=True)

    return data


def generate_hh_income(data):
    """ Generate household income based on the following formulas:

    hh_income_intermediate = ((net hh income) - (rent + mortgage + council tax)) / hh_size
    hh_income = hh_income_intermediate adjusted for inflation using CPI

    Parameters
    ----------
    data : Pd.DataFrame
        A DataFrame containing corrected data
    Returns
    -------
    data : Pd.DataFrame
        The same DataFrame now containing a calculated household income variable
    """
    # first calculate outgoings (set to 0 if missing (i.e. if negative))
    data["hh_rent"][data["hh_rent"] < 0] = 0
    data["hh_mortgage"][data["hh_mortgage"] < 0] = 0
    data["council_tax"][data["council_tax"] < 0] = 0
    data["outgoings"] = -9
    data["outgoings"] = data["hh_rent"] + data["hh_mortgage"] + data["council_tax"]

    # Now calculate hh income before adjusting for inflation
    data["hh_income"] = -9
    data["hh_income"] = (data["hh_netinc"] - data["outgoings"]) / data["oecd_equiv"]

    # Adjust hh income for inflation
    data = US_utils.inflation_adjustment(data, "hh_income")

    # now drop the intermediates
    data.drop(labels=['hh_rent', 'hh_mortgage', 'council_tax', 'outgoings', 'hh_netinc', 'oecd_equiv'],
              axis=1,
              inplace=True)

    return data


def generate_composite_neighbourhood_safety(data):
    """ Generate a composite neighbourhood safety value from 7 crime frequency variables found in Understanding Society.

    'crburg' neighbourhood burglaries
    'crcar' neighbourhood car crime
    'crdrnk' neighbourhood drunks
    'crmugg' neighbourhood muggings
    'crrace' neighbourhood racial abuse
    'crteen' neighbourhood teenager issues
    'crvand' neighbourhood vandalism issues

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

    sum_list = ['burglaries', 'car_crime', 'drunks', 'muggings', 'racial_abuse','teenagers', 'vandalism']
    # sum up all non-negative values in sum_list vars
    data["safety_sum"] = data[sum_list].gt(0).sum(axis=1)

    # conditionally assign housing_quality var based on housing_sum
    # first set conditions and values for 3 level var
    conditions = [
        (data["safety_sum"] == 0),
        (data["safety_sum"] > 0) & (data["safety_sum"] < 7),
        (data["safety_sum"] == 7),
    ]
    values = [1, 2, 3]
    # Now apply conditions with numpy.select(), solution found here: https://datagy.io/pandas-conditional-column/
    data["neighbourhood_safety"] = np.select(conditions, values)

    # drop cols we don't need
    data.drop(labels=['safety_sum'] + sum_list,
              axis=1,
              inplace=True)

    return data

def generate_labour_composite(data):
    """ Combine part/full time employment (emp_type) with labour state (labour_state)

    Parameters
    ----------
    data : pandas.DataFrame
        Before employment composite processing.
    Returns
    -------
    data : pandas.DataFrame
        Data with final labour_state and emp_type removed.
    """

    # grab anyone whop is Employed.

    who_employed = data.loc[data["labour_state"]=="Employed"]
    # there are around 14k missing values per year in emp_type.
    # Most of these can probably be removed with LOCF imputation.
    # Just ignoring anyone with missing emp_type value for now. Assume they're FT employed.

    # Grab anyone with emp_type 2 (part time employed) and reassign their labour state.
    who_parttime_employed = who_employed.loc[data["emp_type"] == 2].index
    data.loc[who_parttime_employed, "labour_state"] = "PT Employed"
    # Other and gov training are tiny classes (<50 per year) so just bin them into employed.
    data["labour_state"] = data["labour_state"].replace(["Government Training", "Other"], "Employed")
    # remove no longer needed variables.
    data.drop(labels=['emp_type'],
              axis=1,
              inplace=True)
    return data

def generate_energy_composite(data):
    """Merge energy consumption for gas and or electric into one column.

    Energy bills are sum of gas and electricity bills together.
    Some people pay bills seperately and some pay them together. This results in three variables.
    This function compresses them into one gas and or electricity bill expenditure.

    1. gather those who pay both together and ignore them
    2. gather those who pay sole gas bill. If duel value is -8 set it to this. create gas added flag value.
    3. gather those who pay sole electricity bill. if duel value is -8 or has true gas added flag add this.
    4. oil consumption ??
    5. add new composite to data frame and remove anything else.

    Parameters
    ----------

    data : pd.DataFrame
        US data with  'xpelecy' yearly electricty expenditure, 'xpgasy' yearly gas expenditure
        and 'xpduely' duel bill expenditure.
    Returns
    -------
    data : pd.DataFrame
        US data with 'electricity_bill' composite column.
    """

    # indicators for who is missing yearly gas and electrictiy bills but has some other energy bill.
    # gas electric oil and other only.
    who_just_gas = (data['yearly_gas_electric'].isin(US_utils.missing_types)) & ~(data['yearly_gas'].isin(US_utils.missing_types))
    who_just_elec = (data['yearly_gas_electric'].isin(US_utils.missing_types)) & ~(data['yearly_electric'].isin(US_utils.missing_types))
    who_just_oily = (data['yearly_gas_electric'].isin(US_utils.missing_types)) & ~(data['yearly_oil'].isin(US_utils.missing_types))
    who_just_other = (data['yearly_gas_electric'].isin(US_utils.missing_types)) & ~(data['yearly_other_fuel'].isin(US_utils.missing_types))

    imputation_index = who_just_gas
    # update everyone who is missing a gas and electric bill with their gas bill.
    data.loc[who_just_gas, 'yearly_gas_electric'] = data.loc[who_just_gas, 'yearly_gas']

    # TODO combined imputation rather than just adding to everyone who has missing in each category?
    # helps to preserve missing values.
    # e.g. everyone who has gas but not duel just has missing values replaced.
    # however for electric some people will have already imputed gas values, some actually missing and some duel values.
    # need a way to work out who is being set a new value from missing and who is adding to a non-zero value.
    # probably loc functions conditioning on positive bills.
    # for now just naively adding things together. will be add differences between -9 and -1 but shouldnt matter too much.

    # work out who has been imputed already.
    #imputation_index *= who_just_elec
    # work out who in who_just_elec has not been imputed yet.
    # who_just_elec *= ~imputation_index
    #data.loc[who_just_elec, 'yearly_gas_electric'] = data.loc[who_just_elec, 'yearly_electric']
    #data.loc[imputation_index, 'yearly_gas_electric'] += data.loc[imputation_index, 'yearly_electric']
    data.loc[who_just_elec, 'yearly_gas_electric'] = data.loc[who_just_elec, 'yearly_electric']

    #imputation_index *= who_just_oily
    #who_just_oily *= ~imputation_index
    #data.loc[who_just_oily, 'yearly_gas_electric'] = data.loc[who_just_oily, 'yearly_oil']
    #data.loc[imputation_index, 'yearly_gas_electric'] += data.loc[imputation_index, 'yearly_oil']
    data.loc[who_just_oily, 'yearly_gas_electric'] = data.loc[who_just_oily, 'yearly_gas']

    #imputation_index *= who_just_other
    #who_just_other *= ~imputation_index
    #data.loc[who_just_other, 'yearly_gas_electric'] = data.loc[who_just_other, 'yearly_other_fuel']
    #data.loc[imputation_index, 'yearly_gas_electric'] += data.loc[imputation_index, 'yearly_other_fuel']
    data.loc[who_just_other, 'yearly_gas_electric'] = data.loc[who_just_other, 'yearly_other_fuel']

    print(sum(data['yearly_gas_electric'] == -8))
    data.drop(labels=['yearly_gas', 'yearly_electric', 'yearly_oil', 'yearly_other_fuel'],
              axis=1,
              inplace=True)

    return data
def main():
    # first collect and load the datafiles for every year
    years = np.arange(2009, 2020)
    file_names = [f"data/corrected_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # generate composite variables
    data = generate_composite_housing_quality(data)       # housing_quality.
    data = generate_hh_income(data)                       # hh_income.
    data = generate_composite_neighbourhood_safety(data)  # safety.
    data = generate_labour_composite(data)                # labour state.
    data = generate_energy_composite(data)                # energy consumption.

    US_utils.save_multiple_files(data, years, "data/composite_US/", "")


if __name__ == "__main__":
    main()
