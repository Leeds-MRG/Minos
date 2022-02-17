#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file generates composite variables for use in the SIPHER project investigating pathways to change in mental health
"""
import pandas as pd
import numpy as np
import US_utils


"""
Lets just take a minute and figure out what this script will actually do.

Starting with the housing quality variables, we are going to generate a housing_quality var.
This variable will be built from 6 others taken straight from Understanding Society:
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

Special cases are specific years when not all 6 vars are included, and so something will have to be done about that.
"""


def generate_composite_housing_quality(data):
    # first make list of the columns we're interested in
    sum_list = ['fridge_freezer', 'washing_machine', 'tumble_dryer', 'dishwasher', 'microwave', 'heating']
    # now create a boolean var that equals True only if all the values for each of these vars are non-negative (i.e. not missing)
    data["housing_complete"] =
    # sum up all non-negative values in sum_list vars
    data["housing_sum"] = data[sum_list].gt(0).sum(axis=1)

    # conditionally assign housing_quality var based on housing_sum
    # first set conditions and values for 3 level var
    conditions = [
        (data["housing_sum"] == 0),
        (data["housing_sum"] > 0) & (data["housing_sum"] < 6),
        (data["housing_sum"] == 6),
    ]
    values = [3, 2, 1]
    # Now apply conditions with numpy.select(), solution found here: https://datagy.io/pandas-conditional-column/
    data["housing_quality"] = np.select(conditions, values)

    return data


def main():
    # first collect and load the datafiles for every year
    years = np.arange(1990, 2019)
    file_names = [f"data/corrected_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # generate composite housing var
    data = generate_composite_housing_quality(data)

    print(len(data))
    print(data["housing_sum"].value_counts())
    print(data["housing_quality"].value_counts())


if __name__ == "__main__":
    main()
