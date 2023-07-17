"""
Script for imputing missing values in the input populations, to ensure we have a full dataset with no missing values.

This script will read in the final population files (used for fitting transition models), and run through a couple of
things required to create the starting populations. These are:
1. Impute missing values using sklearn.impute functions
2. Do prediction of highest education
"""

import numpy as np
from sklearn.impute import SimpleImputer


def impute(data):
    """

    Parameters
    ----------
    data

    Returns
    -------

    """
    return data


def main():
    # load in data
    # run through imputation
    # one var at a time? Too slow, all at once if possible
    # save data
    # done


if __name__ == '__main__()':
    main()