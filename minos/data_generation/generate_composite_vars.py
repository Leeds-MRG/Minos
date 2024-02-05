#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file generates composite variables for use in the SIPHER project investigating pathways to change in mental health.

Currently does not handle missing data for composites. This is done in R using the mice package. May be worth moving
these functions entirely into R. Some variables are imputed then combined and vice versa which makes this tricky.
"""

import pandas as pd
import numpy as np
import sys

from minos.data_generation import US_utils
# import US_missing_description as USmd

# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None  # default='warn' #supress SettingWithCopyWarning

PARITY_MAX_DEFAULT = 10

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

    *** CHANGE 13/12/21 ***
    The previous method of generating a housing_quality composite results in a heavily skewed variable. There are very
    few people in the 'No to all' category, which makes sense as having none of the list above would be a very low
    quality household. Instead, based on some input from SIPHER colleagues, we will make a slight change to the
    composite. We will define a 'core set' of the above variables, and categorise people based on their access to the
    core set and the additional variables.

    Core set:
    - fridge_freezer
    - washing_machine
    - adequate_heating

    The new composite will be:
    Missing 1+ core     == 1
    All core some bonus == 2
    All core all bonus  == 3

    Parameters
    ----------
    data : Pd.DataFrame
        A DataFrame containing corrected data from all years of Understanding Society (1990-2019)
    Returns
    -------
    data : Pd.DataFrame
        The same DataFrame now containing a composite housing quality variable
    """
    print('Generating composite for housing_quality...')

    # list both core and bonus vars
    core_list = ['fridge_freezer', 'washing_machine', 'heating']
    bonus_list = ['tumble_dryer', 'dishwasher', 'microwave']
    # data["housing_core_complete"] = (data.loc[:, core_list] >= 0).all(1)
    # data["housing_bonus_complete"] = (data.loc[:, bonus_list] >= 0).all(1)

    # sum up all non-negative values in both lists of vars
    data["housing_core_sum"] = data[core_list].gt(0).sum(axis=1)
    data["housing_bonus_sum"] = data[bonus_list].gt(0).sum(axis=1)

    # conditionally assign housing_quality var based on the housing sum values
    # first set conditions and values for 3 level var
    conditions = [
        (data["housing_core_sum"] >= 0) & (data["housing_core_sum"] < 3),  # less than full core
        (data["housing_core_sum"] == 3) & (data["housing_bonus_sum"] >= 0) & (data["housing_bonus_sum"] < 3),
        # all core some bonus
        (data["housing_core_sum"] == 3) & (data["housing_bonus_sum"] == 3),  # all core all bonus
    ]
    values = ['Low', 'Medium', 'High']

    # Now apply conditions with numpy.select(), solution found here: https://datagy.io/pandas-conditional-column/
    data["housing_quality"] = np.select(conditions, values)
    # Set to -9 if missing (currently when housing_quality == 0)
    data['housing_quality'][data['housing_quality'] == 0] = -9

    print('Generating composite for SIPHER 7 housing_quality...')
    ## ALSO generate SIPHER 7 version of this variable (simple sum of factors)
    data['S7_housing_quality'] = -9
    data['S7_housing_quality'][(data['housing_core_sum'] + data['housing_bonus_sum']) == 6] = 'Yes to all'
    data['S7_housing_quality'][(data['housing_core_sum'] + data['housing_bonus_sum']).isin(range(1, 6))] = 'Yes to some'
    data['S7_housing_quality'][(data['housing_core_sum'] + data['housing_bonus_sum']) == 0] = 'No to all'

    # drop cols we don't need
    data.drop(labels=['housing_core_sum', 'housing_bonus_sum', 'fridge_freezer', 'washing_machine',
                      'tumble_dryer', 'dishwasher', 'microwave',],# 'heating'],
              axis=1,
              inplace=True)

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
    print('Calculating hourly wage...')

    # apply basrate (hourly_rate) if present and non-negative
    data["hourly_wage"] = data["hourly_rate"][data["hourly_rate"] >= 0]
    # Now calculate for salaried employees (monthly wage applied to weekly hours worked, so multiply hours by 4.2)
    # (4.2 because thats the average number of weeks in a month)
    data["hourly_wage"][(data["gross_paypm"] > 0) & (data["job_hours"] > 0)] = data["gross_paypm"] / (
                data["job_hours"] * 4.2)
    # Now calculate for self-employed (make sure s/emp pay not missing and hours worked over 0)
    # data["hourly_wage"][(~data["gross_pay_se"].isin([-8, -7])) & (data["job_hours_se"] > 0)] = data["gross_pay_se"] / (data["job_hours_se"] * 4)

    """
    KEEPING THIS BECAUSE IT MIGHT BE USEFUL ONE DAY!!!
    The code below in line comments is another attempt at calculating hourly wage, but trying to take into account and 
    be a bit clever with self employed people and small business owners. It uses variables for the hours normally
    worked in a week for self employed people, as well as average income taken from job/business and the pay period.
    The results of this were a decent chunk of self employed people and small business owners that were below the 
    living wage (and often the minimum wage) where they were obviously being propped up with income from different 
    sources (like business dividends), but it wasn't exactly obvious where to find how much they were taking in addition
    to what we knew. I'm leaving it in though because we might be able to do that with a bit more time and some more 
    variables from US that I didn't find.
    """
    # # Try a different one where we combine gross pay and business income as well as job and business hours
    # # first calculate a monthly income from the business
    # data["jb_inc_monthly"] = -9
    # data["jb_inc_monthly"][(data["jb_inc"] >= 0) & (data["jb_inc_per"] == 1)] = data["jb_inc"] * 4
    # data["jb_inc_monthly"][(data["jb_inc"] >= 0) & (data["jb_inc_per"] == 2)] = data["jb_inc"]
    # # Add up the incomes
    # data["total_income"] = 0
    # data["total_income"][data["jb_inc_monthly"] >= 0] += data["jb_inc_monthly"]
    # data["total_income"][data["gross_paypm"] >= 0] += data["gross_paypm"]
    # data["total_income"][data["gross_pay_se"] >= 0] += data["gross_pay_se"]
    # data["total_income"][(data["jb_inc_monthly"] < 0) & (data["gross_paypm"] < 0) & (data["gross_pay_se"] < 0)] = -9
    # #data["total_income"][(data["jb_inc_monthly"] >= 0) or (data["gross_paypm"] >= 0) or (data["gross_pay_se"] >= 0)] = data["jb_inc_monthly"] + data["gross_paypm"]
    # # Add up the working hours
    # data["total_hours"] = 0
    # data["total_hours"][data["job_hours"] > 0] += data["job_hours"]
    # data["total_hours"][data["job_hours_se"] > 0] += data["job_hours_se"]
    # data["total_hours"][(data["job_hours"] < 0) & (data["job_hours_se"] < 0)] = -9
    # # now calculate hourly wage again
    # data["hourly_wage"] = 0
    # data["hourly_wage"][(data["total_income"] >= 0) & (data["total_hours"] >= 0)] = data["total_income"] / (data["total_hours"] * 4)
    # data["hourly_wage"][(data["total_income"] < 0) | (data["total_hours"] < 0)] = -9

    # add in missing codes for known missings
    # CHANGE 03/10/23 - replacing all these with 0 instead of missing codes
    data["hourly_wage"][data["labour_state_raw"] == "Unemployed"] = 0
    data["hourly_wage"][data["labour_state_raw"] == "Retired"] = 0
    data["hourly_wage"][data["labour_state_raw"] == "Sick/Disabled"] = 0
    data["hourly_wage"][data["labour_state_raw"] == "Student"] = 0
    data["hourly_wage"][data["labour_state_raw"].isin(["Government Training",
                                                       "Maternity Leave",
                                                       "Family Care",
                                                       "Other"])] = 0

    # handle minimum wage values
    # all values from here: https://www.gov.uk/national-minimum-wage-rates
    # less than 18
    data['hourly_wage'][
        (data['hourly_wage'] > 0) & (data['hourly_wage'] < 5.28) & (data['age'] < 18)] = 5.28
    # 18 - 20
    data['hourly_wage'][
        (data['hourly_wage'] > 0) & (data['hourly_wage'] < 7.49) & (data['age'] >= 18) & (data['age'] <= 20)] = 7.49
    # 21 - 22
    data['hourly_wage'][
        (data['hourly_wage'] > 0) & (data['hourly_wage'] < 10.18) & (data['age'] >= 21) & (data['age'] <= 22)] = 10.18
    # 23 & over
    data['hourly_wage'][
        (data['hourly_wage'] > 0) & (data['hourly_wage'] < 10.18) & (data['age'] >= 23)] = 10.42

    # now replace all still nan with -9
    data["hourly_wage"].fillna(-9, inplace=True)

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
    print('Generating household income...')

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


def generate_SIPHER_7_neighbourhood_safety(data):
    """

    Parameters
    ----------
    data

    Returns
    -------

    """
    print('Generating composite for SIPHER 7 neighbourhood_safety...')

    # create an empty var to fill up
    data['S7_safety'] = '-9'
    # if all non-missing variables == 4, this is the best group (hardly ever have safety issues)
    data.S7_safety[(data['burglaries'].isin([4, -10, -9, -2, -3])) &
                   (data['car_crime'].isin([4, -10, -9, -2, -3])) &
                   (data['drunks'].isin([4, -10, -9, -2, -3])) &
                   (data['muggings'].isin([4, -10, -9, -2, -3])) &
                   (data['teenagers'].isin([4, -10, -9, -2, -3])) &
                   (data['vandalism'].isin([4, -10, -9, -2, -3]))] = 'Hardly ever'

    # if all non-missing vars == 1, this is the worst group (often have safety issues)
    data.S7_safety[(data['burglaries'].isin([1, -10, -9, -2, -3])) &
                   (data['car_crime'].isin([1, -10, -9, -2, -3])) &
                   (data['drunks'].isin([1, -10, -9, -2, -3])) &
                   (data['muggings'].isin([1, -10, -9, -2, -3])) &
                   (data['teenagers'].isin([1, -10, -9, -2, -3])) &
                   (data['vandalism'].isin([1, -10, -9, -2, -3]))] = 'Often'

    # if its neither of the extreme groups, it must be in the middle (missings dealt with next)
    data.S7_safety[(data['S7_safety'] != 'Hardly ever') &
                   (data['S7_safety'] != 'Often')] = 'Some of the time'


    # If all missing then set back to -9
    data.S7_safety[(data['burglaries'] < 0) &
                   (data['car_crime'] < 0) &
                   (data['drunks'] < 0) &
                   (data['muggings'] < 0) &
                   (data['teenagers'] < 0) &
                   (data['vandalism'] < 0)] = '-9'

    data['S7_neighbourhood_safety'] = data['S7_safety']

    data.drop(labels=['S7_safety'],
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

    The composite variable (called neighbourhood_safety) will have 3 levels:
    - Yes to all    == 1
    - Yes to some   == 2
    - No to all     == 3

    *** CHANGE ../../.. ***
    For each of the seven crime variables, combine ‘very common’ and ‘fairly common’ to create a composite
    ‘fairly or very common’ (these are the small number categories).

    Then bin responses like this:
    1. Response to all crime questions is “not at all common” (very safe neighbourhood). Justification is that if you
        perceive no threat at all this is the best possible state.
    2. Responds to 1+ question as “not very common” but no responses to ‘fairly or very common’ (safe neighbourhood).
        Justification is that on the whole these people probably feel safe but not all is perfect, so probably not
        quite as desirable as group 1.
    3. Responds to 1+ question as fairly or very common’ (not safe). Justification is that if perception of crime is
        very or fairly common, no matter what category, you are likely to feel that your neighbourhood safety is
        compromised.

    These might need tweaking but can we look at the three level distribution first

    Parameters
    ----------
    data : Pd.DataFrame
        A DataFrame containing corrected data from all years of Understanding Society (1990-2019)
    Returns
    -------
    data : Pd.DataFrame
        The same DataFrame now containing a composite housing quality variable
    """
    print('Generating composite for neighbourhood_safety...')

    # first make list of the columns we're interested in
    var_list = ['burglaries', 'car_crime', 'drunks', 'muggings', 'racial_abuse', 'teenagers', 'vandalism']

    # Now combine very common (1) with fairly common (2) and recode to 1-3
    for var in var_list:
        data[var][data[var] == 1] = 2
        data[var] = data[var] - 1

    data['safety'] = -9
    # First do very safe neighbourhood. All vars == 3 (not at all common) OR missing == -9
    # data['neighbourhood_safety'][(data['burglaries'] == 3)] = 3
    data.safety[(data['burglaries'].isin([3, -10, -9, -2, -3])) &
                (data['car_crime'].isin([3, -10, -9, -2, -3])) &
                (data['drunks'].isin([3, -10, -9, -2, -3])) &
                (data['muggings'].isin([3, -10, -10, -9, -2, -3])) &
                (data['teenagers'].isin([3, -10, -9, -2, -3])) &
                (data['vandalism'].isin([3, -10, -9, -2, -3]))] = 3

    # Now safe neighbourhood. Any var == 2 (not very common) but no var == 1 (very or fairly common)
    data.safety[((data['burglaries'].isin([2, -10, -9, -2, -3])) |
                 (data['car_crime'].isin([2, -10, -9, -2, -3])) |
                 (data['drunks'].isin([2, -10, -9, -2, -3])) |
                 (data['muggings'].isin([2, -10, -9, -2, -3])) |
                 (data['teenagers'].isin([2, -10, -9, -2, -3])) |
                 (data['vandalism'].isin([2, -10, -9, -2, -3])))
                &
                ((data['burglaries'] != 1) &
                 (data['car_crime'] != 1) &
                 (data['drunks'] != 1) &
                 (data['muggings'] != 1) &
                 (data['teenagers'] != 1) &
                 (data['vandalism'] != 1))] = 2
    # Now unsafe neighbourhood. Any var == 1 (very or fairly common)
    data.safety[(data['burglaries'].isin([1, -10, -9, -2, -3])) |
                (data['car_crime'].isin([1, -10, -9, -2, -3])) |
                (data['drunks'].isin([1, -10, -9, -2, -3])) |
                (data['muggings'].isin([1, -10, -9, -2, -3])) |
                (data['teenagers'].isin([1, -10, -9, -2, -3])) |
                (data['vandalism'].isin([1, -10, -9, -2, -3]))] = 1
    
    # If all missing then set back to -9
    data.safety[(data['burglaries'] < 0) &
                (data['car_crime'] < 0) &
                (data['drunks'] < 0) &
                (data['muggings'] < 0) &
                (data['teenagers'] < 0) &
                (data['vandalism'] < 0)] = -9

    data['neighbourhood_safety'] = data.safety

    # drop cols we don't need
    data.drop(labels=['safety'] + var_list,
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
    print('Generating composite for labour_state...')

    # grab anyone whop is Employed.
    who_employed = data.loc[data["labour_state"] == "Employed"]
    # there are around 14k missing values per year in emp_type.
    # Most of these can probably be removed with LOCF imputation.
    # Just ignoring anyone with missing emp_type value for now. Assume they're FT employed.

    # Grab anyone with emp_type 2 (part time employed) and reassign their labour state.
    who_parttime_employed = who_employed.loc[data["emp_type"] == 2].index
    data.loc[who_parttime_employed, "labour_state"] = "PT Employed"
    # Other and gov training are tiny classes (<50 per year) so just bin them into employed.
    data["labour_state"] = data["labour_state"].replace(["Government Training", "Other"], "Employed")
    # remove no longer needed variables.
    #data.drop(labels=['emp_type'],
    #          axis=1,
    #          inplace=True)
    return data


def generate_SIPHER_7_employment(data):
    """
    Based on SIPHER 7 guidelines, the employment variable should have 6 levels:
    1) FT employed
    2) PT employed
    3) job seeking
    4) FT education
    5) taking care of a family member with chronic illness or disability
    6) not working

    These can be generated by recoding 2 variables from Understanding Society:
    - jbstat : current labour force status
    - jbft_dv : full or part-time employee

    Some assumptions:
    - Unemployed from US (labour_state == 3) are job_seeking
    - Government training scheme (labour_state == 9) are full time education
    - Furloughed (labour_state == 12, only wave 11 onwards) are full time employed
    - Temporarily laid off / short-term working (== 13) are job_seeking

    Parameters
    ----------
    data

    Returns
    -------

    """
    # set up conditions for each employment type
    # NOTE: Some conditions are based on assumptions, see docstring above for some details
    conditions = [
        (data['labour_state_raw'].isin(['Employed', 'Self-employed'])) & (data['emp_type'].isin([1, -7, -9])),  # FT employed (assuming here that those without some missing values for emp_type are FT)
        (data['labour_state_raw'].isin(['Employed', 'Self-employed'])) & (data['emp_type'] == 2),  # PT employed
        (data['labour_state_raw'].isin(['Unemployed', 'Short-term Working'])),  # Job Seeking
        (data['labour_state_raw'].isin(['Student', 'Government Training'])),  # FT education
        (data['labour_state_raw'].isin(['Family Care'])),  # Family Care
        (data['labour_state_raw'].isin(['Retired', 'Maternity Leave', 'Sick/Disabled'])),  # Not working
    ]
    values = ['FT Employed', 'PT Employed', 'Job Seeking', 'FT Education', 'Family Care', 'Not Working']

    data['S7_labour_state'] = np.select(conditions, values)
    # Set to -9 if missing (currently when labour_state == 0)
    data['S7_labour_state'][data['S7_labour_state'] == '0'] = -9

    data.drop(labels=['labour_state_raw', 'emp_type'],
              axis=1,
              inplace=True)

    ############################################################
    # THIS IS BAD BUT NECESSARY, REPLACE WHEN POSSIBLE!!!!!!
    # Need to copy the wave 12 PT employment information as we are missing this info in wave 13
    PT_pidps_2020 = data['pidp'][(data['time'] == 2020) & (data['S7_labour_state'] == 'PT Employed')]
    data['S7_labour_state'][(data['pidp'].isin(PT_pidps_2020)) & (data['time'] == 2021)] = 'PT Employed'

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
    print('Calculating yearly energy cost...')

    # need to calculate expenditure on 4 types of fuel. (electric, gas, oil, other.)

    # start composite 'yearly_energy' variable.
    data['yearly_energy'] = -8

    # has_X variables are binary indicators for if a person pays for an energy source. electric/gas/oil/other/none
    # yearly_X bills are expenditure on a given fuel source.

    # first gas and electric.
    # if they pay a combined bill for gas and electric add the combined yearly bill to yearly_energy
    who_combined_bill = data['gas_electric_combined'] == 1 & ~data['yearly_gas_electric'].isin(US_utils.missing_types)
    data.loc[who_combined_bill, 'yearly_energy'] += data.loc[who_combined_bill, 'yearly_gas_electric']

    # If they pay separate bills add them separately. note remove anyone who declares they use an energy but expenditure is still missing.
    who_electric_bill = data['has_electric'] == 1 & ~data['yearly_electric'].isin(US_utils.missing_types)
    data.loc[who_electric_bill, 'yearly_energy'] += data.loc[who_electric_bill, "yearly_electric"]
    who_gas_bill = data['has_gas'] == 1 & ~data['yearly_gas'].isin(US_utils.missing_types)
    data.loc[who_gas_bill, 'yearly_energy'] += data.loc[who_gas_bill, 'yearly_gas']

    # do the same for oil.
    who_oil_bill = data['has_oil'] == 1 & ~data['yearly_oil'].isin(US_utils.missing_types)
    data.loc[who_oil_bill, 'yearly_energy'] += data.loc[who_oil_bill, 'yearly_oil']
    # same for other
    who_other_bill = data['has_other'] == 1 & ~data['yearly_other_fuel'].isin(US_utils.missing_types)
    data.loc[who_other_bill, 'yearly_energy'] += data.loc[who_other_bill, 'yearly_other_fuel']

    # if declare no energy expenditure or included in rent set value to 0.
    data.loc[data['has_none'] == 1, 'yearly_energy'] = 0
    data.loc[data['energy_in_rent'] == 1, 'yearly_energy'] = 0

    # force everyone with any expeniture values to missing.
    who_missing_gas_electric = data['gas_electric_combined'] == 1 & data['yearly_gas_electric'].isin(
        US_utils.missing_types)
    # if not combined bill. if declared electric or gas but missing expenditure set energy to -8
    who_missing_electric = (data['gas_electric_combined'] == 2) & (data['has_electric'] == 1) & (
        data['yearly_electric'].isin(US_utils.missing_types))
    who_missing_gas = (data['gas_electric_combined']) == 2 & (data['has_gas'] == 1) & (
        data['yearly_gas'].isin(US_utils.missing_types))
    # if declares oil or other but missing expenditure set to -8
    who_missing_oil = data['has_oil'] == 1 & data['yearly_oil'].isin(US_utils.missing_types)
    who_missing_other = data['has_other'] == 1 & data['yearly_other_fuel'].isin(US_utils.missing_types)

    # anyone who is missing any of these values
    data.loc[who_missing_gas_electric, 'yearly_energy'] = -8
    data.loc[who_missing_electric, 'yearly_energy'] = -8
    data.loc[who_missing_gas, 'yearly_energy'] = -8
    data.loc[who_missing_oil, 'yearly_energy'] = -8
    data.loc[who_missing_other, 'yearly_energy'] = -8

    # check over households. if someone is missing but another person in the house has a value. assign the missing person that value.
    # groupby to find max by hidp.
    data['yearly_energy'] = data.groupby('pidp')['yearly_energy'].transform('max')

    # TODO combined imputation rather than just adding to everyone who has missing in each category?
    # helps to preserve missing values.
    # e.g. everyone who has gas but not duel just has missing values replaced.
    # however for electric some people will have already imputed gas values, some actually missing and some duel values.
    # need a way to work out who is being set a new value from missing and who is adding t  a non-zero value.
    # probably loc functions conditioning on positive bills.
    # for now just naively adding things together. will be add differences between -9 and -1 but shouldnt matter too much.

    # print(sum(data['yearly_energy'] == -8))
    # print(sum(data['yearly_energy'].isin(US_utils.missing_types)), data.shape)

    # remove all but yearly_energy variable left.
    data.drop(labels=['yearly_gas', 'yearly_electric', 'yearly_oil', 'yearly_other_fuel', 'gas_electric_combined',
                      'yearly_gas_electric', 'has_electric', 'has_gas', 'has_oil', 'has_other', 'has_none',
                      'energy_in_rent'],
              axis=1,
              inplace=True)
    # everyone else in this composite doesn't know or refuses to answer so are omitted.
    return data


def generate_nutrition_composite(data):
    """
    Generate a composite for nutrition based on the frequency and amount of fruit and vegetable consumption.

    Consumption frequency variables are ordinal with 4 levels:
    1 : Never
    2 : 1-3 days
    3 : 4-6 days
    4: Every day

    Amount variables are continuous.

    To generate a composite, we will multiply the amount per day by the consumption frequency number. We won't get
    the actual consumption per week because we do not have the exact number of days, but we will get a proxy for it.
    I think then we can simply add the proxy variables for fruit and vegetables together, to get a composite of
    fruit and vegetable consumption.

    Parameters
    ----------
    data : pd.DataFrame
        US data with fruit and vegetable consumption variables.

    Returns
    -------
    data : pd.DataFrame
        US data with composite fruit and veg consumption variable, without the component vars.
    """
    print('Generating composite for nutrition_quality...')

    # First calculate intermediate composites (amount * no. days)
    data['fruit_comp'] = data['fruit_days'] * data['fruit_per_day']
    data['veg_comp'] = data['veg_days'] * data['veg_per_day']

    # Now add them together and remove intermediate vars
    data['nutrition_quality'] = data['fruit_comp'] + data['veg_comp']

    # if any of the intermediates have missing codes (less than 0) then nutrition_quality should also have that code
    data['nutrition_quality'][data['fruit_days'] < 0] = data['fruit_days']
    data['nutrition_quality'][data['fruit_per_day'] < 0] = data['fruit_per_day']
    data['nutrition_quality'][data['veg_days'] < 0] = data['veg_days']
    data['nutrition_quality'][data['veg_per_day'] < 0] = data['veg_per_day']

    data.drop(labels=['fruit_comp', 'fruit_days', 'fruit_per_day',
                      'veg_comp', 'veg_days', 'veg_per_day'],
              axis=1,
              inplace=True)

    return data


def generate_hh_structure(data):
    """
    Generate a variable for houshold composition by refactoring an existing US variable.

    We want to create 4 groups:
    1. Single adult no kids
    2. Single adult 1+ kids
    3. Multiple adults no kids
    4. Multiple adults 1+ kids

    Parameters
    ----------
    data : pd.DataFrame
        US data with US household composition variable (hhtype_dv)

    Returns
    -------
    data : pd.DataFrame
        US data with a hh_comp variable.
    """
    print('Generating composite for household structure...')

    # Which numbers in the original US hh_composition var correspond?
    # First create empty var
    data['hh_comp'] = -9

    ## Single adult no kids
    # 1, 2, 3
    data['hh_comp'][data['hh_composition'].isin([1, 2, 3])] = 1
    ## Single adult 1+ kids
    # 4, 5
    data['hh_comp'][data['hh_composition'].isin([4, 5])] = 2
    ## Multiple adults no kids
    # 6, 8, 16, 17, 19, 22
    data['hh_comp'][data['hh_composition'].isin([6, 8, 16, 17, 19, 22])] = 3
    ## Multiple adults 1+ kids
    # 10, 11, 12, 18, 20, 21, 23
    data['hh_comp'][data['hh_composition'].isin([10, 11, 12, 18, 20, 21, 23])] = 4

    data.drop(labels=['hh_composition'],
              axis=1,
              inplace=True)

    return data


def generate_marital_status(data):
    """
    Recoding the mastat_dv variable from US.

    Original has 9 levels (some below 1%), we will replace with 4:
    1. Single never partnered
    2. Partnered (married, civil partner, living as a couple)
    3. Separated (separated legally married, divorced, sep from civil partner, a former civil partner)
    4. Widowed (widowed, surviving civil partner)

    Parameters
    ----------
    data : pd.DataFrame
        US data with US marital status variable (marstat)

    Returns
    -------
    data : pd.DataFrame
        US data with a hh_comp variable.
    """
    print('Generating composite for marital status...')

    # first create empty var
    data['marital_status'] = -9

    ## Single never partnered
    # 1
    data['marital_status'][data['marstat'] == 1] = 'Single'
    ## Partnered
    # 2, 3, 10
    data['marital_status'][data['marstat'].isin([2, 3, 10])] = 'Partnered'
    ## Separated
    # 4, 5, 7, 8
    data['marital_status'][data['marstat'].isin([4, 5, 7, 8])] = 'Separated'
    ## Widowed
    # 6, 9
    data['marital_status'][data['marstat'].isin([6, 9])] = 'Widowed'

    data.drop(labels=['marstat'],
              axis=1,
              inplace=True)

    return data


def generate_physical_health_score(data):
    """
    For generating a physical health score from the physical parts of the SF-12 questionnaire.
    We will produce a continuous variable by adding the scores of 5 variables together, where lower scores
    equate to better physical health.

    Parameters
    ----------
    data : pd.DataFrame
        US data

    Returns
    -------
    data : pd.DataFrame
        US data with variables for parents education and ns-sec.
    """
    print('Generating composite for physical health...')

    ## first flip the var thats in the opposite direction
    data['pain_interfere_work'][data['pain_interfere_work'] > 0] = 6 - data['pain_interfere_work']

    # now create summary var and add to it
    data['phealth'] = 0
    data['phealth'][data['phealth_limits_modact'] > 0] += data['phealth_limits_modact']
    data['phealth'][data['phealth_limits_stairs'] > 0] += data['phealth_limits_stairs']
    data['phealth'][data['S7_physical_health'] > 0] += data['S7_physical_health']  # formerly phealth_limits_work
    data['phealth'][data['phealth_limits_work_type'] > 0] += data['phealth_limits_work_type']
    data['phealth'][data['pain_interfere_work'] > 0] += data['pain_interfere_work']

    # now a counter for how many of these variable are not missing
    data['counter'] = 0
    data['counter'][data['phealth_limits_modact'] > 0] += 1
    data['counter'][data['phealth_limits_stairs'] > 0] += 1
    data['counter'][data['S7_physical_health'] > 0] += 1  # formerly phealth_limits_work
    data['counter'][data['phealth_limits_work_type'] > 0] += 1
    data['counter'][data['pain_interfere_work'] > 0] += 1

    # finally, get the average of phealth for a mean summary score (then it doesn't matter if any are missing)
    # only do this where counter does not equal 0. These cases we will record as missing
    data['phealth'][data['counter'] != 0] = data['phealth'] / data['counter']

    # now set those missing all to missing
    data['phealth'][data['counter'] == 0] = -9

    data.drop(labels=['phealth_limits_modact', 'phealth_limits_stairs',
                      'phealth_limits_work_type', 'pain_interfere_work',
                      'counter'],
              axis=1,
              inplace=True)

    return data


#TODO: Complete this function. Collect information on parents education (where available) and use to predict educ
def generate_parents_education(data):
    """
    For predicting the highest education a 16 will attain in their life, we can use information on the parents
    education and NS-SEC if available.

    Parameters
    ----------
    data : pd.DataFrame
        US data

    Returns
    -------
    data : pd.DataFrame
        US data with variables for parents education and ns-sec.
    """

    # First we need to find parents (or adults in the same house as we won't be able to find a direct parental link)
    # Groupby hid then filter to make sure there is a 16 year old in the house
    grouped_dat = data.groupby(['hidp'], axis=1).filter(lambda d: (d.age != 16.0), axis=0)
    # filtered_dat = grouped_dat.filter(lambda d: (d['age'] != 16))
    # TODO: FINISH THIS!

    return data


def calculate_equivalent_income(data):
    """Calculate equivalent income based on provided SIPHER 7 variables

    Parameters
    ----------
        data: pd.DataFrame
            US data
    Returns
    -------
        data : pd.DataFrame
            US data with variable for equivalent income
    """
    print('Calculating equivalent income...')
    # This is a deterministic calculation based on the values from each of the SIPHER7 variables
    # Each level of each variable is assigned a weight, which are then used to modify the value for disposable
    # income to generate a value that is based on both the income and characteristics of a persons life

    # This was first done by one-hot encoding each of the S7 variables, but this would be clunky and inefficient
    # I'm going to try and do it slightly more efficiently

    # The goal here is to calculate an exponent term for modifying income to equivalent income:
    #   EquivalentIncome = Income*EXP(X)
    # Each weighting applies to the level

    # First set up dictionaries for each variable to hold its factor weights
    phys_health_dict = {
        5: 0,
        4: -0.116/1.282,
        3: -0.135/1.282,
        2: -0.479/1.282,
        1: -0.837/1.282,
        -9: -1,
        -8: -1,
        -7: -1,
        -1: -1,
        -2: -1,
        -10: -1
    }
    men_health_dict = {
        5: 0,
        4: -0.14/1.282,
        3: -0.215/1.282,
        2: -0.656/1.282,
        1: -0.877/1.282,
        -9: -1,
        -8: -1,
        -7: -1,
        -1: -1,
        -2: -1,
        -10: -1
    }
    loneliness_dict = {
        1: 0,
        2: -0.186/1.282,
        3: -0.591/1.282,
        -9: -1,
        -8: -1,
        -7: -1,
        -1: -1,
        -2: -1,
        -10: -1
    }
    employment_dict = {
        'FT Employed': 0,
        'PT Employed': 0.033/1.282,
        'Job Seeking': -0.283/1.282,
        'FT Education': -0.184/1.282,
        'Family Care': -0.755/1.282,
        'Not Working': -0.221/1.282,
        -9: -1,
        -8: -1,
        -7: -1,
        -1: -1,
        -2: -1,
        -10: -1
    }
    housing_dict = {
        'Yes to all': 0,
        'Yes to some': -0.235/1.282,
        'No to all': -0.696/1.282,
        '-9': -1,
        '-8': -1,
        '-7': -1,
        '-1': -1,
        '-2': -1,
        '-10': -1
    }
    nh_safety_dict = {
        'Hardly ever': 0,
        'Some of the time': -0.291/1.282,
        'Often': -0.599/1.282,
        '-9': -1,
        '-8': -1,
        '-7': -1,
        '-1': -1,
        '-2': -1,
        '-10': -1
    }

    # Now we add together weights for each factor level to generate the exponent term
    data['EI_exp_term'] = 0
    #pop['EI_exp_term'] = pop['EI_exp_term'] + phys_health_dict.get(pop['S7_physical_health'])
    data['EI_exp_term'] = data['EI_exp_term'] + data.apply(lambda x: phys_health_dict[x['S7_physical_health']], axis=1)
    data['EI_exp_term'] = data['EI_exp_term'] + data.apply(lambda x: men_health_dict[x['S7_mental_health']], axis=1)
    data['EI_exp_term'] = data['EI_exp_term'] + data.apply(lambda x: loneliness_dict[x['loneliness']], axis=1)
    data['EI_exp_term'] = data['EI_exp_term'] + data.apply(lambda x: employment_dict[x['S7_labour_state']], axis=1)
    data['EI_exp_term'] = data['EI_exp_term'] + data.apply(lambda x: housing_dict[x['S7_housing_quality']], axis=1)
    data['EI_exp_term'] = data['EI_exp_term'] + data.apply(lambda x: nh_safety_dict[x['S7_neighbourhood_safety']], axis=1)

    # finally do the calculation for equivalent income (EI = income^EI_exp_term)
    data['equivalent_income'] = data['hh_income'] * np.exp(data['EI_exp_term'])

    # If any of the variables involved are missing, then can't do calculation for equivalent income
    # These people will be removed in complete_case anyway so not having a value here won't matter
    var_list_num = ['S7_physical_health',
                    'S7_mental_health',
                    'loneliness']
    var_list_str = ['S7_labour_state',
                    'S7_housing_quality',
                    'S7_neighbourhood_safety']
    data['equivalent_income'][(data[var_list_num] < 0).any(axis=1)] = -9
    data['equivalent_income'][(data[var_list_str].isin(['-1', '-2', '-7', '-8', '-9', '-10'])).any(axis=1)] = -9

    data.drop(labels=['EI_exp_term'],
              axis=1,
              inplace=True)

    return data


def calculate_auditc_score(data):
    """
    Alcohol use disorders can be assessed via the AUDITC score. This score is derived from 3 questions that form part of
    the full 10 question AUDIT screening test, where AUDITC specifically focuses on consumption. The 3 questions are:

    1. How often do you have a drink containing alcohol?
    2. How many units of alcohol do you drink on a typical day when you are drinking?
    3. How often have you had 6 or more units if female, or 8 or more if male, on a single occasion in the last year?

    Each question is ordinal with 5 levels, depending on the 'severity' of the answer. We then score each question from
    0-4, with higher scores meaning higher 'severity'. The total across the 3 questions then creates a score from 0-12,
    with 0-4 meaning sensible drinking, 5-7 meaning hazardous drinking, and 8+ meaning harmful drinking.
    See following link for information on scoring:
    https://www.drinktalkingportal.co.uk/clinical-guidance/alcohol-abuse-screening/alcohol-audit-audit-c

    To calculate this score, we rely on 4 variables in Understanding Society shown at the following link:
    https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation?search_api_views_fulltext=auditc

    Question 1 above relies on auditc1 & auditc3, question 2 relies on auditc4, and question 3 uses auditc5.

    NOTE: The final variable used (auditc5) specifically mentions 6 or more drink frequency, rather than 6+/8+ units.
            This could be a mistake in the description or the actual question asked being incorrect (not the true AUDITC
            question). There's no information about which one it is, so I'm treating it the same as the AUDITC3 question
            for our purposes. Added benefit that this is simpler to code without checking for gender also.

    Parameters
    ----------
        data : pd.DataFrame
            US data
    Returns
    -------
        data : pd.DataFrame
            US data with variable for equivalent income
    """
    print('Calculating AUDITC score (alcohol use disorder)...')

    # AUDITC1 - How often do you have a drink containing alcohol
    data['temp_auditc1'] = -9
    data['temp_auditc1'][data['auditc1'] == 2] = 0  # no alcoholic drink in past 12 months
    data['temp_auditc1'][data['auditc2'] == 1] = 0  # always been non-drinker (maybe not necessary but thorough)
    data['temp_auditc1'][data['auditc3'] == 1] = 0  # Never drank in past 12 months (again might be doubling up)
    data['temp_auditc1'][data['auditc3'] == 2] = 1  # Drank in past 12 months: monthly or less
    data['temp_auditc1'][data['auditc3'] == 3] = 2  # Drank in past 12 months: 2-4 times per month
    data['temp_auditc1'][data['auditc3'] == 4] = 3  # Drank in past 12 months: 2-3 times per week
    data['temp_auditc1'][data['auditc3'] == 5] = 4  # Drank in past 12 months: 4+ times per week

    # AUDITC2 - How many units drank on typical day
    data['temp_auditc2'] = -9
    data['temp_auditc2'][data['auditc1'] == 2] = 0  # no alcoholic drink in past 12 months
    data['temp_auditc2'][data['auditc2'] == 1] = 0  # always been non-drinker (maybe not necessary but thorough)
    data['temp_auditc2'][data['auditc3'] == 1] = 0  # Never drank in past 12 months (again might be doubling up)
    data['temp_auditc2'][data['auditc4'] == 1] = 0  # Drinks on typical day: 1-2
    data['temp_auditc2'][data['auditc4'] == 2] = 1  # Drinks on typical day: 3-4
    data['temp_auditc2'][data['auditc4'] == 3] = 2  # Drinks on typical day: 5-6
    data['temp_auditc2'][data['auditc4'] == 4] = 3  # Drinks on typical day: 7-9
    data['temp_auditc2'][data['auditc4'] == 5] = 4  # Drinks on typical day: 10+

    # AUDITC3 - Six or more drinks frequency
    data['temp_auditc3'] = -9
    data['temp_auditc3'][data['auditc1'] == 2] = 0  # no alcoholic drink in past 12 months
    data['temp_auditc3'][data['auditc2'] == 1] = 0  # always been non-drinker (maybe not necessary but thorough)
    data['temp_auditc3'][data['auditc3'] == 1] = 0  # Never drank in past 12 months (again might be doubling up)
    data['temp_auditc3'][data['auditc5'] == 1] = 0  # Six or more drinks frequency: Never
    data['temp_auditc3'][data['auditc5'] == 2] = 1  # Six or more drinks frequency: Less than monthly
    data['temp_auditc3'][data['auditc5'] == 3] = 2  # Six or more drinks frequency: Monthly
    data['temp_auditc3'][data['auditc5'] == 4] = 3  # Six or more drinks frequency: Weekly
    data['temp_auditc3'][data['auditc5'] == 5] = 4  # Six or more drinks frequency: Daily or almost daily

    # Combined score
    data['auditc_score'] = 0
    data['auditc_score'][data['temp_auditc1'] >= 0] += data['temp_auditc1']
    data['auditc_score'][data['temp_auditc2'] >= 0] += data['temp_auditc2']
    data['auditc_score'][data['temp_auditc3'] >= 0] += data['temp_auditc3']
    # if any of the components are missing, set the final value as missing also
    data['auditc_score'][(data['temp_auditc1'] == -9) |
                   (data['temp_auditc2'] == -9) |
                   (data['temp_auditc3'] == -9)] = -9

    # Ordinal values
    data['auditc'] = '-9'
    data['auditc'][data['auditc_score'] == 0] = 'Non-drinker'  # 0 score is non-drinker
    data['auditc'][data['auditc_score'].isin(range(1, 5))] = 'Low Risk'  # 1-4 is sensible
    data['auditc'][data['auditc_score'].isin(range(5, 8))] = 'Increased Risk'  # 5-7 is hazardous
    data['auditc'][data['auditc_score'] >= 8] = 'High Risk'  # 8-12 is harmful

    data.drop(labels=['auditc1', 'auditc2', 'auditc3', 'auditc4', 'auditc5',
                      'temp_auditc1', 'temp_auditc2', 'temp_auditc3',
                      'auditc_score'],
              axis=1,
              inplace=True)

    return data


def generate_physical_activity_binary(data):
    """
    To determine what is a healthy level of physical activity, we are following government guidelines found here:
    https://www.gov.uk/government/publications/physical-activity-guidelines-adults-and-older-adults

    This document states that for adults and older adults (over the age of 19), the government recommends at least 150
    minutes of moderate activty, or 75 minutes of vigorous activity in a week. Understanding Society has some good
    variables on moderate and vigorous activity, with the caveat that they have only been asked on waves 7,9,11, and 12.

    For both moderate and vigorous activity, US includes a number of variables:
    - Number of days in past week did activity
    - Average hours and minutes per day of activity
    - Average hours and minutes per week of activity (if answered don't know to how much per day)

    With this, we can generate a binary variable for whether or not an individual is hitting the government exercise
    targets.

    Parameters
    ----------
        data : pd.DataFrame
            US data
    Returns
    -------
        data : pd.DataFrame
            US data with binary 'active' variable
    -------

    """
    # First do moderate activity
    # this is a combination of information from all moderate activity variables
    data['temp_mod_act'] = 0
    # hours per day * 60 (for minutes) where neither is missing
    data['temp_mod_act'][(data['mday'] >= 0) & (data['mdhrs'] >= 0)] += data['mday'] * (data['mdhrs'] * 60)
    # minutes per day
    data['temp_mod_act'][(data['mday'] >= 0) & (data['mdmin'] >= 0)] += data['mday'] * data['mdmin']
    # hours per week (asked separately I think for when hours per day is unknown)
    data['temp_mod_act'][data['mwhrs'] >= 0] += data['mwhrs']
    # minutes per week (mins per day unknown)
    data['temp_mod_act'][data['mwmin'] >= 0] += data['mwmin']
    # handle missing
    data['temp_mod_act'][(data['mday'] < 0) &
                         (data['mdhrs'] < 0) &
                         (data['mdmin'] < 0) &
                         (data['mwhrs'] < 0) &
                         (data['mwmin'] < 0)] = -9

    # now vigorous
    data['temp_vig_act'] = 0
    # hours per day * 60 (for minutes) where neither is missing
    data['temp_vig_act'][(data['vday'] >= 0) & (data['vdhrs'] >= 0)] += data['vday'] * (data['vdhrs'] * 60)
    # minutes per day
    data['temp_vig_act'][(data['vday'] >= 0) & (data['vdmin'] >= 0)] += data['vday'] * data['vdmin']
    # hours per week (asked separately I think for when hours per day is unknown)
    data['temp_vig_act'][data['vwhrs'] >= 0] += data['vwhrs']
    # minutes per week (mins per day unknown)
    data['temp_vig_act'][data['vwmin'] >= 0] += data['vwmin']
    # handle missing
    data['temp_vig_act'][(data['vday'] < 0) &
                         (data['vdhrs'] < 0) &
                         (data['vdmin'] < 0) &
                         (data['vwhrs'] < 0) &
                         (data['vwmin'] < 0)] = -9

    # Now do the calculations for a binary active variable
    data['active'] = -9
    # if either more than 150 mins moderate, or 75 mins vigorous, then active == TRUE
    data['active'][(data['temp_mod_act'] >= 150) | (data['temp_vig_act'] >= 75)] = 1
    #data['active'][data['temp_vig_act'] >= 75] = 1
    # if both less than 150 mins moderate and less than 75 mins vigorous, then active == FALSE
    data['active'][(data['temp_mod_act'] < 150) & (data['temp_vig_act'] < 75)] = 0
    # if both missing, then missing
    data['active'][(data['temp_mod_act'] == -9) & (data['temp_vig_act'] == -9)] = -9

    # drop cols no longer need
    data.drop(labels=['temp_mod_act', 'temp_vig_act',
                      'mday', 'mdhrs', 'mdmin', 'mwhrs', 'mwmin',
                      'vday', 'vdhrs', 'vdmin', 'vwhrs', 'vwmin'],
              axis=1,
              inplace=True)

    return data


def generate_matdep_proxy(data):
    """
    This function will create a single proxy from the information in the material deprivation variables (all named
    matdep{letter}). Each variable is a 4 level ordinal with the following levels:

    1 - I/We have this
    2 - Can't afford it
    3 - Don't need it now
    4 - Does not apply

    A score of 1 indicates a positive response.
    A score of 2 indicates a negative response.
    A score of 3 or 4 will be treated as a missing value.

    Each score of 1 will increment a material deprivation score variable by 1, and the final sum over all the variables
    will be divided by the number of non-missing items to get a score from 0-1.

    Parameters
    ----------
    data : pd.DataFrame
        US data with the material deprivation component variables.
    Returns
    -------
    data : pd.DataFrame
        US data with the combined matdep proxy created, and component variables removed.
    """
    # Create matdepscore variable and populate from the matdep variables
    # Matdepscore + 1 if individual indicates they have the specific variable
    # Then no increment if individual indicates they cannot afford it
    # Finally scores of 3 (Don't need it now) or 4 (Does not apply) will be treated as a missing value
    data['matdepscore'] = 0
    data['matdepscore'][data['matdepa'] == 1] += 1
    data['matdepscore'][data['matdepd'] == 1] += 1
    data['matdepscore'][data['matdepe'] == 1] += 1
    data['matdepscore'][data['matdepf'] == 1] += 1
    data['matdepscore'][data['matdepg'] == 1] += 1
    data['matdepscore'][data['matdeph'] == 1] += 1
    data['matdepscore'][data['matdepi'] == 1] += 1
    data['matdepscore'][data['matdepj'] == 1] += 1

    # counter to increment when values are not missing (negative or 3, 4)
    data['counter'] = 0
    data['counter'][data['matdepa'].isin([1, 2])] += 1
    data['counter'][data['matdepd'].isin([1, 2])] += 1
    data['counter'][data['matdepe'].isin([1, 2])] += 1
    data['counter'][data['matdepf'].isin([1, 2])] += 1
    data['counter'][data['matdepg'].isin([1, 2])] += 1
    data['counter'][data['matdeph'].isin([1, 2])] += 1
    data['counter'][data['matdepi'].isin([1, 2])] += 1
    data['counter'][data['matdepj'].isin([1, 2])] += 1

    # Now use the counter value and matdepscore to generate a score between 0 and 1
    data['matdepTEMP'] = data['matdepscore'] / data['counter']
    data['matdepTEMP'][data['counter'] == 0] = -9

    # now convert to 3 level ordinal
    data['matdep'] = -9
    data['matdep'][data['matdepTEMP'] == 0] = 1
    data['matdep'][(data['matdepTEMP'] > 0) & (data['matdepTEMP'] < 1)] = 2
    data['matdep'][data['matdepTEMP'] == 1] = 3

    # drop cols no longer need
    data.drop(labels=['matdepa', 'matdepd', 'matdepe', 'matdepf', 'matdepg', 'matdeph', 'matdepi', 'matdepj',
                      'matdepscore', 'counter', 'matdepTEMP'],
              axis=1,
              inplace=True)

    return data


def generate_chron_disease_proxy(data):
    """
    For a first pass at a chronic disease proxy variable, we are going to focus on the distinction between no chronic
    disease (CD), 1 CD, and more than 1. We think this will give us a fairly simple ordinal variable that has a strong
    correlation with SF_12_PCS.

    NOTE: There is a variable (hcond96) for none of the above conditions. I'm going to ignore this and just rely on
    the tally of CD's we create from each individual variable.

    Parameters
    ----------
    data : pd.DataFrame
        US data with the individual chronic disease variables.

    Returns
    -------
    data : pd.DataFrame
        US data with the chronic disease proxy, and component variables removed.
    """

    # first start the counter and increment with every non-missing positive response to each chronic condition
    data['cd_counter'] = 0
    data['cd_counter'][data['hcond1'] == 1] += 1  # Asthma
    data['cd_counter'][data['hcond2'] == 1] += 1  # Arthritis
    data['cd_counter'][data['hcond3'] == 1] += 1  # Congestive Heart Failure
    data['cd_counter'][data['hcond4'] == 1] += 1  # Coronary Heart Failure
    data['cd_counter'][data['hcond5'] == 1] += 1  # Angina
    data['cd_counter'][data['hcond6'] == 1] += 1  # Heart attack or myocardial infarction
    data['cd_counter'][data['hcond7'] == 1] += 1  # Stroke
    data['cd_counter'][data['hcond8'] == 1] += 1  # Emphysema
    data['cd_counter'][data['hcond10'] == 1] += 1  # Hypothyroidism
    data['cd_counter'][data['hcond11'] == 1] += 1  # Chronic Bronchitis
    data['cd_counter'][data['hcond12'] == 1] += 1  # Any kind of liver condition
    data['cd_counter'][data['hcond13'] == 1] += 1  # Cancer or malignancy
    data['cd_counter'][data['hcond14'] == 1] += 1  # Diabetes
    data['cd_counter'][data['hcond15'] == 1] += 1  # Epilepsy
    data['cd_counter'][data['hcond16'] == 1] += 1  # High blood pressure
    data['cd_counter'][data['hcond18'] == 1] += 1  # Other long standing/chronic condition
    data['cd_counter'][data['hcond19'] == 1] += 1  # Multiple Sclerosis
    data['cd_counter'][data['hcond20'] == 1] += 1  # H.I.V
    data['cd_counter'][data['hcond21'] == 1] += 1  # COPD

    # next we need a missing counter to find cases where all vars are missing
    data['cd_miss_counter'] = 0
    data['cd_miss_counter'][data['hcond1'] < 0] += 1  # Asthma
    data['cd_miss_counter'][data['hcond2'] < 0] += 1  # Arthritis
    data['cd_miss_counter'][data['hcond3'] < 0] += 1  # Congestive Heart Failure
    data['cd_miss_counter'][data['hcond4'] < 0] += 1  # Coronary Heart Failure
    data['cd_miss_counter'][data['hcond5'] < 0] += 1  # Angina
    data['cd_miss_counter'][data['hcond6'] < 0] += 1  # Heart attack or myocardial infarction
    data['cd_miss_counter'][data['hcond7'] < 0] += 1  # Stroke
    data['cd_miss_counter'][data['hcond8'] < 0] += 1  # Emphysema
    data['cd_miss_counter'][data['hcond10'] < 0] += 1  # Hypothyroidism
    data['cd_miss_counter'][data['hcond11'] < 0] += 1  # Chronic Bronchitis
    data['cd_miss_counter'][data['hcond12'] < 0] += 1  # Any kind of liver condition
    data['cd_miss_counter'][data['hcond13'] < 0] += 1  # Cancer or malignancy
    data['cd_miss_counter'][data['hcond14'] < 0] += 1  # Diabetes
    data['cd_miss_counter'][data['hcond15'] < 0] += 1  # Epilepsy
    data['cd_miss_counter'][data['hcond16'] < 0] += 1  # High blood pressure
    data['cd_miss_counter'][data['hcond18'] < 0] += 1  # Other long-standing/chronic condition
    data['cd_miss_counter'][data['hcond19'] < 0] += 1  # Multiple Sclerosis
    data['cd_miss_counter'][data['hcond20'] < 0] += 1  # H.I.V
    data['cd_miss_counter'][data['hcond21'] < 0] += 1  # COPD

    # 'hcond96': 'hcond96',  # Health Condition 96: None of these

    data['chron_disease'] = -9
    data['chron_disease'][data['cd_counter'] == 0] = 1  # No Chronic disease
    data['chron_disease'][data['cd_counter'] == 1] = 2  # 1 Chronic disease
    data['chron_disease'][data['cd_counter'] > 1] = 3  # 1+ Chronic disease

    # Now missing - when all (19) CD's are missing then the ordinal variable can be labelled missing
    data['chron_disease'][data['cd_miss_counter'] == 19] = -9  # All missing

    # drop cols no longer need
    data.drop(labels=['hcond1', 'hcond2', 'hcond3', 'hcond4', 'hcond5', 'hcond6', 'hcond7', 'hcond8', 'hcond10',
                      'hcond11', 'hcond12', 'hcond13', 'hcond14', 'hcond15', 'hcond16', 'hcond18', 'hcond19', 'hcond20',
                      'hcond21', 'hcond96',
                      'cd_counter', 'cd_miss_counter'],
              axis=1,
              inplace=True)

    return data



def calculate_children(data,
                       parity_max=PARITY_MAX_DEFAULT):
    """

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame containing corrected Understanding Society data
    Returns
    -------
    data : pd.DataFrame
        The same DataFrame containing a composite variable for number of children an individual has ever had

    """
    print('Generating composite for children per individual...')

    # data.to_csv("datadump.csv")
    pidps_all = data['pidp'].unique()
    pidps = data[data['sex'] == 'Female']['pidp'].unique()
    print("No. of pidps (all):", len(pidps_all))
    print("No. of pidps (females only):", len(pidps))

    # Initialise new column
    data['nkids_ind'] = data['nkids_ind_raw']

    pl = str(len(pidps))
    for i,pidp in enumerate(pidps):
        sys.stdout.write("\rProcessing pidp " + str(i+1) + " of " + pl + " (females only)")
        subframe = data[data['pidp'] == pidp][['pidp', 'nkids_ind_raw', 'nkids_ind_new', 'time']]
        # Calculate number of children if:
        # 1. Any pregnancies present (i.e. nkids_ind_new == 2)
        # 2. There are no negative values in nkids_ind_raw (indicating invalid values)
        if (2 in subframe['nkids_ind_new'].values) and not (subframe['nkids_ind_raw'].lt(0).any()):
            # Increment values according to cumulative sum
            # Note specific method avoids Pandas SettingWithCopyWarning
            # See here: https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
            data.loc[subframe.index, 'nkids_ind'] = subframe['nkids_ind_raw'] + (subframe['nkids_ind_new'] == 2).astype(int).cumsum()
            # print(data[['time', 'pidp', 'nkids_ind_raw', 'nkids_ind_new', 'nkids_ind']].loc[subframe.index])
        # elif (subframe['nkids_ind_raw'].lt(0).any()):
        #     print(data[['time', 'pidp', 'nkids_ind_raw', 'nkids_ind_new', 'nkids_ind']].loc[subframe.index])
    print("")

    # Reset any women with more than nmax children to nmax
    data.loc[(data['nkids_ind'] > parity_max) & (data['sex'] == "Female"), 'nkids_ind'] = parity_max

    # Drop interim variables as not used elsewhere in pipeline
    data.drop(labels=['nkids_ind_raw', 'nkids_ind_new'],
              axis=1,
              inplace=True)
    return data


def generate_difference_variables(data):
    # creating difference in hh income for lmm difference models.
    data = data.sort_values(by=['time'])
    diff_columns = ["hh_income", "SF_12_MCS", "SF_12_PCS", "nutrition_quality", 'matdep', "job_hours", 'hourly_wage']
    diff_column_names = [item + "_diff" for item in diff_columns]
    data[diff_column_names] = data.groupby(["pidp"])[diff_columns].diff().fillna(0)
    data['nutrition_quality_diff'] = data['nutrition_quality_diff'].astype(int)
    return data


def main():
    maxyr = US_utils.get_data_maxyr()
    # first collect and load the datafiles for every year
    print("Starting composite generation.")
    years = np.arange(2009, maxyr)
    file_names = [f"data/corrected_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # generate composite variables
    data = generate_composite_housing_quality(data)  # housing_quality.
    data = generate_hh_income(data)  # hh_income.
    data = calculate_hourly_wage(data)  # hourly_wage
    data = generate_SIPHER_7_neighbourhood_safety(data)  # S7_neighbourhood_safety (MUST RUN BEFORE OTHER NEIGHBOURHOOD_SAFETY var
    data = generate_composite_neighbourhood_safety(data)  # safety.
    # NOTE: Switching off the old labour_state var so I can generate the SIPHER 7 version with no problems
    #data = generate_labour_composite(data)  # labour state.
    data = generate_SIPHER_7_employment(data)  # SIPHER 7 employment status
    data = generate_energy_composite(data)  # energy consumption.
    data = generate_nutrition_composite(data)  # nutrition
    data = generate_hh_structure(data)  # household structure
    data = generate_marital_status(data)  # marital status
    data = generate_physical_health_score(data)  # physical health score
    data = calculate_equivalent_income(data)  # equivalent income
    data = calculate_auditc_score(data)  # alcohol use disorder for consumption (auditc)
    data = generate_physical_activity_binary(data)  # physical activity composite
    data = generate_matdep_proxy(data)  # Material Deprivation proxy
    data = generate_chron_disease_proxy(data)  # Chronic Disease proxy
    data = calculate_children(data)  # total number of biological children
    data = generate_difference_variables(data)  # difference variables for longitudinal/difference models.

    print('Finished composite generation. Saving data...')
    US_utils.save_multiple_files(data, years, "data/composite_US/", "")


if __name__ == "__main__":
    main()
