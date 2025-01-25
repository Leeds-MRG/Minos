""" For now this file is simple. Extract from children datasets, get their ages and hidps. See how this lines up with indresp dataset and how much
missing data (if any) there is.

"""

import US_utils
import pandas as pd
import numpy as np
from collections import Counter
from math import isnan

import os
from os.path import dirname as up


def age_64bit_integer_stack(ages):
    """ convert a list of individual child ages into a 64-bit integer.
    each n 4 bits indicates the number of children age n in the household.
    indexed 0. so first four beats are the 'zero years old' children.
    e.g. bits 9-12 would be the number of children aged (3-1)=2.

    Parameters
    ----------
    ages: list
        list of child ages.
    Returns
    -------

    """
    c = Counter(ages)

    output_age = 0
    for age in range(15, 0, -1):  # looping through all possible child ages from 15 to 1 years old.
        output_age += c[age]  # add the age (in binary) and bit shift left four. stacking ages basically.
        output_age = output_age << 4
    output_age += c[0]  # final addition of 0 year olds but not bit shifting.

    return output_age


def integer_child_ages_to_nkids(ages):

    if isnan(ages):
        return ages

    mask = (1 << 4) - 1  # get last 4 bits of an integer with this mask. well known bit hack shenanigan.
    # https://stackoverflow.com/questions/36124773/how-to-get-last-n-bits-by-bit-op

    nkids = 0
    while ages:
        nkids += (ages & mask)  # get the last 4 bits. children of certain age bucket.
        ages = ages >> 4
    return nkids


def main(input_raw_data, year):

    # # Download children datasets in one at a time
    # child_name = US_utils.US_file_name(year, "../UKDA-6614-stata/stata/stata13_se/", "child")  # Get hidp, pidp, age
    # child_data = US_utils.load_file(child_name)
    #
    # # Format child data
    # attribute_columns = US_utils.wave_prefix(['hidp', 'age_dv'], year)
    # child_data = child_data[attribute_columns]
    # child_data.columns = ['hidp', 'age']
    #
    # child_data.loc[child_data['age'] == 16, 'age'] = 15  # Force max child age to 15 years old
    # child_data['is_child'] = True
    # child_data['is_adult'] = False
    # child_data['time'] = year
    #
    # # Assign adults from indresp data as adults, i.e. over 16s
    # #US_data = pd.read_csv(f"data/composite_US/{year}_US_cohort.csv")
    # input_raw_data['is_child'] = False
    # input_raw_data['is_adult'] = True
    # #collaped_children_US_with_children = collapsed_children_US.merge(child_data, 'inner', on='hidp')
    # collapsed_children_US_with_children = pd.concat([input_raw_data, child_data])
    #
    # # Removing orphans
    # # Calculating number of adults per hidp; if 0 adults in the house the children are orphans?
    # #orphans = collapsed_children_US_with_children.groupby(['hidp']).filter(lambda x : sum(x['is_adult']) == 0)
    # collapsed_children_US_with_children = collapsed_children_US_with_children.groupby('hidp').filter(lambda x : sum(x['is_adult']) > 0)
    #
    #
    # # Sanity check for number of child rows vs declared nkids
    # actual_children = collapsed_children_US_with_children.groupby(['hidp'])['is_child'].sum()
    # declared_children = collapsed_children_US_with_children.groupby(['hidp'])['nkids'].max()
    # # print(sum(np.abs(actual_children - declared_children)))  # Sum absolute error, where lower is better
    #
    # # Grab children and join ages into a string separated by "-"
    # final_US_with_children = collapsed_children_US_with_children.sort_values(by=['hidp', 'age'], ascending =True)
    # #final_US_with_children['age'] = final_US_with_children['age'].astype(str)
    # #chained_ages = final_US_with_children.loc[final_US_with_children['is_child'] == True, ].groupby('hidp', as_index=False)['age'].apply('_'.join)
    # chained_ages = final_US_with_children.loc[final_US_with_children['is_child'] == True, ].groupby('hidp', as_index=True)['age'].apply(age_64bit_integer_stack)
    #
    # # Merge chained child ages back onto adults in the dataframe, then tidy up generated child rows and columns needed
    # #collapsed_children_US = pd.merge(final_US_with_children, chained_ages, how='left', on='hidp')
    # #collapsed_children_US['child_ages'] = collapsed_children_US['age_y']  # sort out two age columns from the merge
    #
    # # Map chained child ages back onto adults in the dataframe
    # final_US_with_children['child_ages'] = final_US_with_children['hidp'].map(dict(chained_ages))
    # final_US_with_children.loc[final_US_with_children['child_ages'].isna(), 'child_ages'] = 0
    # final_US_with_children['child_ages'] = final_US_with_children['child_ages'].astype(int)

    # # Remove children
    # final_US_with_children = final_US_with_children.loc[final_US_with_children['is_adult'] == 1, ]
    #
    # final_US_with_children['true_nkids'] = final_US_with_children['child_ages'].apply(integer_child_ages_to_nkids)
    #
    #
    # # People with NA child values either have no children or their children aren't present in the child data for some reason
    # # Set everyone with no children and NA child ages to custom missing value "childless"
    # # Some households have positive nkids but their children aren't in the child dataset so can't determine their ages; set these to missing (-9)
    # # Maybe need to estimate ages from age bins instead for these
    # # Maybe these are all newborns? There are three in one year though, which may be triplets, but unlikely
    # final_US_with_children['child_ages'] = final_US_with_children.groupby(['hidp'])['child_ages'].transform('first')
    # final_US_with_children['nkids'] = final_US_with_children.groupby(['hidp'])['nkids'].transform('max')
    #
    # # Remove children
    # final_US_with_children = final_US_with_children.loc[final_US_with_children['is_adult'] == 1, ]
    #
    # # Households with nkids > 0 but no children in the child dataset: assign better error values
    # # Force children to 0 for these 20 or so weird households with children not in the dataset (newborns?)
    # # Suspect these are 16 yos in the 15 and under data for some reason, could be human error in US
    # """Per UKHLS. This is the total number of children aged 15 or under in the household. Count includes children
    # whose age is unknown if the interview outcome code indicates that the person is a child ineligible
    # for interview or a child eligible for a youth interview. """
    # # Given how few of these children there are, just going to ignore them.
    # # If we add up the child age buckets variables in UKHLS, presumably would see the same gaps
    # final_US_with_children.loc[(final_US_with_children['nkids'] != 0) & (final_US_with_children['child_ages']==0), 'nkids'] = 0
    #
    # # Households with discrepancies between recorded nkids and actual nkids in the children data, assuming as above
    # # There are a few ineligible children who are added to nkids but ages aren't recorded
    # # Ignoring them; assign nkids values according to number of recorded child ages per house
    # discrepant_nkids = final_US_with_children.loc[final_US_with_children['nkids'] - final_US_with_children['true_nkids'] != 0, ['true_nkids']]
    # final_US_with_children.loc[final_US_with_children['nkids'] - final_US_with_children['true_nkids'] != 0, ['nkids']] = discrepant_nkids
    #
    #
    # who_childless = (final_US_with_children['child_ages'].isna()) & (final_US_with_children['nkids'] == 0.0)
    #
    # #collapsed_children_US.loc[who_childless, 'child_ages'] = "childless"  # No children in household
    #
    #
    # final_US_with_children.reset_index(inplace=True, drop=True)
    # final_US_with_children = final_US_with_children.drop(['is_adult', 'is_child', "true_nkids"], axis=1)
    #
    # # Save data
    # #US_utils.save_file(final_US_with_children, "children_ages_US/", "", year)
    # return final_US_with_children
    return input_raw_data


if __name__ == '__main__':

    years = np.arange(1991, 2020)
    # file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data_path = os.path.join(up(up(up(__file__))))
    file_names = [os.path.join(data_path, f"data/raw_US/{item}_US_cohort.csv") for item in years]
    data = US_utils.load_multiple_data(file_names)
    main(data, 2020)
