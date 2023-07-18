"""
Script for imputing missing values in the input populations, to ensure we have a full dataset with no missing values.

This script will read in the final population files (used for fitting transition models), and run through a couple of
things required to create the starting populations. These are:
1. Impute missing values using sklearn.impute functions
2. Do prediction of highest education
"""

import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer
from sklearn.impute import IterativeImputer

import US_utils


def iterative_impute(data):
    """

    Parameters
    ----------
    data

    Returns
    -------

    """
    print('Starting Iterative Imputation...')
    # first replace all missing numeric values with np.nan - imputer works differently for string and numeric
    # numeric_column_list = data.select_dtypes(include=np.number).columns.tolist()
    # numeric_data = data.select_dtypes(include=np.number)
    # numeric_data = US_utils.replace_missing_with_na(numeric_data, list(numeric_data))

    # first replace all missing values with np.nan for the imputer to target
    data = US_utils.replace_missing_with_na(data, list(data))

    # create an ordinal encoder to encode all categorical and string data as numeric (think np.float64 as default)
    # then encode data with this encoder
    ordinal_encoder = preprocessing.OrdinalEncoder().set_output(transform='pandas')
    encoded_data = ordinal_encoder.fit_transform(data)

    imputer = IterativeImputer(random_state=0,
                               max_iter=10,
                               verbose=2,
                               add_indicator=False,
                               keep_empty_features=False).set_output(transform='pandas')  # set output as pd dataframe

    imputed_data = imputer.fit_transform(encoded_data)

    # convert back to pd.DataFrame with correct column names
    #imputed_numeric = pd.DataFrame(np.squeeze(imputed_numeric),
    #                               columns=numeric_data.columns.tolist())

    # now reverse the previous encoding to bring back the categorical data
    imputed_data = ordinal_encoder.inverse_transform(imputed_data)

    return imputed_data


def knn_impute(data):
    """

    Parameters
    ----------
    data

    Returns
    -------

    """
    print('Starting KNN imputation...')

    # first replace all missing values with np.nan for the imputer to target
    data = US_utils.replace_missing_with_na(data, list(data))

    # create an ordinal encoder to encode all categorical and string data as numeric (think np.float64 as default)
    # then encode data with this encoder
    ordinal_encoder = preprocessing.OrdinalEncoder().set_output(transform='pandas')
    encoded_data = ordinal_encoder.fit_transform(data)

    # create imputer with n_neighbours == 1. This is equal to a hotdecking as the value is replaced with closest
    # neighbour. Not the most robust imputation strategy but purely for ensuring a start point in the model I think
    # this should be fine
    imputer = KNNImputer(n_neighbors=1)  # set output as pandas dataframe

    # Run imputation on all data
    print('Imputing numeric columns with KNN imputer...')
    #imputed_data = imputer.fit_transform(encoded_data)

    #test_chunk = encoded_data[encoded_data['time'] == 10.0]
    list_test_chunk = np.array_split(encoded_data, 10)

    imputed_data = imputer.fit_transform(list_test_chunk[0])

    # now reverse the previous encoding to bring back the categorical data
    imputed_data = ordinal_encoder.inverse_transform(imputed_data)

    return imputed_data


def simple_string_impute(data):
    """

    Parameters
    ----------
    data

    Returns
    -------

    """
    print('Starting simple imputation...')

    # select object dtypes (mainly string)
    str_data = data.select_dtypes(include=object)
    str_data_cols = str_data.columns.tolist()
    str_data = US_utils.replace_missing_with_na(str_data, str_data_cols)

    str_imputer = SimpleImputer(strategy='most_frequent',
                                copy=True).set_output(transform='pandas')  # set output as pandas dataframe

    print('Imputing string columns with simple imputer (using most frequent strategy)...')
    imputed_str_data = str_imputer.fit_transform(str_data)

    data = data.update(other=imputed_str_data,
                       overwrite=True)

    return data


def main():
    maxyr = US_utils.get_data_maxyr()

    print('Generating stock population...')
    years = np.arange(2009, maxyr)
    file_names = [f"data/final_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)


    # run through imputation
    data = iterative_impute(data)
    # data = knn_impute(data)
    # data = simple_string_impute(data)

    # TODO: Move wave data copy from generate_final_pop to here. Shouldn't be done before fitting models, but should be
    #   after imputation

    # save data
    US_utils.save_multiple_files(data, years, "data/stock/", "")
    # done

    """
    #numeric_data = data.select_dtypes(include=np.number)
    float_data = data.select_dtypes(include=float)
    float_data_cols = float_data.columns.tolist()
    float_data = US_utils.replace_missing_with_na(float_data, float_data_cols)
    """


if __name__ == '__main__':
    main()
