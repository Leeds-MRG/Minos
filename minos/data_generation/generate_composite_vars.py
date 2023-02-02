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
    #data["housing_core_complete"] = (data.loc[:, core_list] >= 0).all(1)
    #data["housing_bonus_complete"] = (data.loc[:, bonus_list] >= 0).all(1)

    # sum up all non-negative values in both lists of vars
    data["housing_core_sum"] = data[core_list].gt(0).sum(axis=1)
    data["housing_bonus_sum"] = data[bonus_list].gt(0).sum(axis=1)

    # conditionally assign housing_quality var based on the housing sum values
    # first set conditions and values for 3 level var
    conditions = [
        (data["housing_core_sum"] > 0) & (data["housing_core_sum"] < 3),  # less than full core
        (data["housing_core_sum"] == 3) & (data["housing_bonus_sum"] >= 0) & (data["housing_bonus_sum"] < 3),
        # all core some bonus
        (data["housing_core_sum"] == 3) & (data["housing_bonus_sum"] == 3),  # all core all bonus
    ]
    values = [3, 2, 1]

    # Now apply conditions with numpy.select(), solution found here: https://datagy.io/pandas-conditional-column/
    data["housing_quality"] = np.select(conditions, values)
    # Set to -9 if missing (currently when housing_quality == 0)
    data['housing_quality'][data['housing_quality'] == 0] = -9

    # drop cols we don't need
    data.drop(labels=['housing_core_sum', 'housing_bonus_sum', 'fridge_freezer', 'washing_machine',
                     'tumble_dryer', 'dishwasher', 'microwave', 'heating'],
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
    data["hourly_wage"][(data["gross_paypm"] > 0) & (data["job_hours"] > 0)] = data["gross_paypm"] / (data["job_hours"] * 4.2)
    # Now calculate for self-employed (make sure s/emp pay not missing and hours worked over 0)
    #data["hourly_wage"][(~data["gross_pay_se"].isin([-8, -7])) & (data["job_hours_se"] > 0)] = data["gross_pay_se"] / (data["job_hours_se"] * 4)

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
    var_list = ['burglaries', 'car_crime', 'drunks', 'muggings', 'racial_abuse','teenagers', 'vandalism']

    # Now combine very common (1) with fairly common (2) and recode to 1-3
    for var in var_list:
        data[var][data[var] == 1] = 2
        data[var] = data[var] - 1

    data['safety'] = -9
    # First do very safe neighbourhood. All vars == 3 (not at all common)
    #data['neighbourhood_safety'][(data['burglaries'] == 3)] = 3
    data.safety[(data['burglaries'] == 3) & (data['car_crime'] == 3) & (data['drunks'] == 3) & (data['muggings'] == 3) &
                (data['teenagers'] == 3) & (data['vandalism'] == 3)] = 3
    # Now safe neighbourhood. Any var == 2 (not very common) but no var == 1 (very or fairly common)
    data.safety[((data['burglaries'] == 2) | (data['car_crime'] == 2) | (data['drunks'] == 2) | (data['muggings'] == 2) |
                 (data['teenagers'] == 2) | (data['vandalism'] == 2)) &
                ((data['burglaries'] != 1) & (data['car_crime'] != 1) & (data['drunks'] != 1) & (data['muggings'] != 1) &
                 (data['teenagers'] != 1) & (data['vandalism'] != 1))] = 2
    # Now unsafe neighbourhood. Any var == 1 (very or fairly common)
    data.safety[(data['burglaries'] == 1) | (data['car_crime'] == 1) | (data['drunks'] == 1) | (data['muggings'] == 1) |
                (data['teenagers'] == 1) | (data['vandalism'] == 1)] = 1

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
    print('Calculating yearly energy cost...')

    # need to calculate expenditure on 4 types of fuel. (electric, gas, oil, other.)

    # start composite 'yearly_energy' variable.
    data['yearly_energy'] = -8

    # has_X variables are binary indicators for if a person pays for an energy source. electric/gas/oil/other/none
    # yearly_X bills are expenditure on a given fuel source.

    # first gas and electric.
    # if they pay a combined bill for gas and electric add the combined yearly bill to yearly_energy
    who_combined_bill = data['gas_electric_combined']==1 & ~data['yearly_gas_electric'].isin(US_utils.missing_types)
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
    who_missing_gas_electric = data['gas_electric_combined'] == 1 & data['yearly_gas_electric'].isin(US_utils.missing_types)
    # if not combined bill. if declared electric or gas but missing expenditure set energy to -8
    who_missing_electric = (data['gas_electric_combined'] == 2) & (data['has_electric'] == 1) & (data['yearly_electric'].isin(US_utils.missing_types))
    who_missing_gas  = (data['gas_electric_combined']) == 2 & (data['has_gas'] == 1) & (data['yearly_gas'].isin(US_utils.missing_types))
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

    #print(sum(data['yearly_energy'] == -8))
    #print(sum(data['yearly_energy'].isin(US_utils.missing_types)), data.shape)

    # remove all but yearly_energy variable left.
    data.drop(labels=['yearly_gas', 'yearly_electric', 'yearly_oil', 'yearly_other_fuel', 'gas_electric_combined',
                      'yearly_gas_electric', 'has_electric', 'has_gas', 'has_oil', 'has_other', 'has_none', 'energy_in_rent'],
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


    data.drop(labels = ['fruit_comp', 'fruit_days', 'fruit_per_day',
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
    data['hh_comp'][data['hh_composition'].isin([1,2,3])] = 1
    ## Single adult 1+ kids
    # 4, 5
    data['hh_comp'][data['hh_composition'].isin([4,5])] = 2
    ## Multiple adults no kids
    # 6, 8, 16, 17, 19, 22
    data['hh_comp'][data['hh_composition'].isin([6,8,16,17,19,22])] = 3
    ## Multiple adults 1+ kids
    # 10, 11, 12, 18, 20, 21, 23
    data['hh_comp'][data['hh_composition'].isin([10,11,12,18,20,21,23])] = 4

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
    data['marital_status'][data['marstat'].isin([2,3,10])] = 'Partnered'
    ## Separated
    # 4, 5, 7, 8
    data['marital_status'][data['marstat'].isin([4,5,7,8])] = 'Separated'
    ## Widowed
    # 6, 9
    data['marital_status'][data['marstat'].isin([6,9])] = 'Widowed'

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
    data['phealth'][data['phealth_limits_work'] > 0] += data['phealth_limits_work']
    data['phealth'][data['phealth_limits_work_type'] > 0] += data['phealth_limits_work_type']
    data['phealth'][data['pain_interfere_work'] > 0] += data['pain_interfere_work']

    # now a counter for how many of these variable are not missing
    data['counter'] = 0
    data['counter'][data['phealth_limits_modact'] > 0] += 1
    data['counter'][data['phealth_limits_stairs'] > 0] += 1
    data['counter'][data['phealth_limits_work'] > 0] += 1
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
    #filtered_dat = grouped_dat.filter(lambda d: (d['age'] != 16))

    return data


def main():
    # first collect and load the datafiles for every year
    print("Starting composite generation.")
    years = np.arange(2009, 2020)
    file_names = [f"data/corrected_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # generate composite variables
    data = generate_composite_housing_quality(data)       # housing_quality.
    data = generate_hh_income(data)                       # hh_income.
    data = calculate_hourly_wage(data)                    # hourly_wage
    data = generate_composite_neighbourhood_safety(data)  # safety.
    data = generate_labour_composite(data)                # labour state.
    data = generate_energy_composite(data)                # energy consumption.
    data = generate_nutrition_composite(data)             # nutrition
    data = generate_hh_structure(data)                    # household structure
    data = generate_marital_status(data)                  # marital status
    data = generate_physical_health_score(data)           # physical health score

    print('Finished composite generation. Saving data...')
    US_utils.save_multiple_files(data, years, "data/composite_US/", "")


if __name__ == "__main__":
    main()
