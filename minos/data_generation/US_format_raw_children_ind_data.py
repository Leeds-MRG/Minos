""" For now this file is simple. Extract from children datasets, get their ages and hidps. See how this lines up with indresp dataset and how much
missing data (if any) there is.

"""

import US_utils
from US_utils import missing_types as mt
from US_format_raw_children_data import age_64bit_integer_stack, integer_child_ages_to_nkids
import pandas as pd
import numpy as np
from collections import Counter
from math import isnan

import os
from os.path import dirname as up

DATA_PATH = os.path.join(up(up(up(__file__))))


# HR 29/01/25 Get birth spacing - i.e. years between ages of children - from integer-form child ages
def get_birth_spacing(ages):
    spacings = []
    age_list = integer_child_ages_to_list(ages)
    spacings = np.diff(age_list)
    return spacings


# HR 29/01/25 Get list of child ages from integer-form child ages
def integer_child_ages_to_list(ages):

    # Mask to get last four digits of binary integer
    # Adapted from here: https://stackoverflow.com/questions/36124773/how-to-get-last-n-bits-by-bit-op
    mask = (1 << 4) - 1

    age_list = []
    # Get maximum possible age bucket from length of integer
    max_age = round((len(bin(ages)) - 2)/4)
    age_bucket = 0
    while ages:
        nkids = (ages & mask)  # Get last four bits, i.e. number of children in age bucket
        age_list += ([age_bucket] * nkids)  # Add that many kids to list
        ages = ages >> 4  # Shift child ages by four bits, i.e. by one value of possible child ages
        age_bucket += 1
    return age_list


def main(adult_data, year):

    # Download children datasets in one at a time
    child_name = US_utils.US_file_name(year, os.path.join(DATA_PATH, "../UKDA-6614-stata/stata/stata13_se/"), "child")  # Get child data
    child_data = US_utils.load_file(child_name)

    # Format child data
    child_vars = ['age_dv',  # Age of child at interview
                  'pn1pid',  # PIDP of first natural parent
                  'pn2pid',  # PIDP of second natural parent
                  'pn1sex',  # Sex of first natural parent
                  'pn2sex',  # Sex of second natural parent
                  'pns1pid',  # PIDP of first natural/adoptive/step-parent
                  'pns2pid',  # PIDP of second natural/adoptive/step-parent
                  'pns1sex',  # Sex of first natural/adoptive/step-parent
                  'pns2sex',  # Sex of second natural/adoptive/step-parent
                  ]
    attribute_columns = US_utils.wave_prefix(child_vars, year)
    child_data = child_data[attribute_columns]
    wave_letter = US_utils.get_wave_letter(year)
    child_data.columns = [el.split(wave_letter + '_', 1)[1] if el.startswith(wave_letter) else el for el in child_vars]  # Necessary as US_utils.wave_prefix mutates child_vars

    child_data.loc[child_data['age_dv'] == 16, 'age_dv'] = 15  # Force max child age to 15 years old

    # Add columns from parent columns in child data
    childless_value = 0
    id_cols = ('pn1pid', 'pn2pid')
    for parent_id in id_cols:
        parent_map = child_data.groupby(parent_id)['age_dv'].apply(list)
        parent_map.index.name = 'pidp'
        adult_data[parent_id + '_ages'] = adult_data['pidp'].map(parent_map).fillna(childless_value)
        # Awkward method to create empty lists for no children, but can't pass "[]" directly as Pandas thinks it's a list of values to replace
        adult_data.loc[adult_data[parent_id + '_ages'] == childless_value, parent_id + '_ages'] = adult_data[parent_id + '_ages'].apply(lambda x: [])

    # Combine children from both IDs
    child_age_cols = [el + '_ages' for el in id_cols]
    adult_data['child_ages_list'] = adult_data[child_age_cols].sum(axis=1)  # Add lists across columns
    adult_data['child_ages_list'] = adult_data['child_ages_list'].apply(lambda x: sorted(list(x)))  # Sort ages
    # adult_data['nkids_ind_u16'] = adult_data['child_ages_list'].str.len()  # Count U16 children
    adult_data['child_ages_ind'] = adult_data['child_ages_list'].apply(age_64bit_integer_stack)  # Convert to binary format

    ### BLOCK FOR TESTING
    # # Count unassigned children, i.e. children with no parents given
    # all_children = len(child_data)
    # no_parents_natural = len(child_data.loc[(child_data['pn1pid'].isin(mt)) &
    #                                         (child_data['pn2pid'].isin(mt))])
    # no_parents_any = len(child_data.loc[(child_data['pn1pid'].isin(mt)) &
    #                                     (child_data['pn2pid'].isin(mt)) &
    #                                     (child_data['pns1pid'].isin(mt)) &
    #                                     (child_data['pns2pid'].isin(mt))])
    #
    # print('\nProcessing individual child ages for {}...'.format(year))
    # print('Children with natural parents not present: {}/{} ({}%)'.format(no_parents_natural, all_children, 100*no_parents_natural/all_children))
    # print('Children with any parents not present: {}/{} ({}%)'.format(no_parents_any, all_children, 100*no_parents_any/all_children))
    ###

    # Drop extraneous columns
    cols_to_drop = child_age_cols + ['child_ages_list']
    adult_data.drop(columns=cols_to_drop, inplace=True)
    return adult_data


if __name__ == '__main__':

    # HR 29/01/25 All below for testing
    year = 2014
    years = np.arange(2014, year+1)
    # file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    file_names = [os.path.join(DATA_PATH, f"data/raw_US/{item}_US_cohort.csv") for item in years]
    data = US_utils.load_multiple_data(file_names)
    input_data = data.loc[data['time'] == year].copy()
    adult_data = main(input_data, year)
