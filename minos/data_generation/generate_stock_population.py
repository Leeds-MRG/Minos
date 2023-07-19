"""
Script for imputing missing values in the input populations, to ensure we have a full dataset with no missing values.

This script will read in the final population files (used for fitting transition models), and run through a couple of
things required to create the starting populations. These are:
1. Impute missing values using sklearn.impute functions
2. Do prediction of highest education
"""

import numpy as np
import pandas as pd
# from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer
from sklearn.impute import IterativeImputer
from sklearn.pipeline import Pipeline

import US_utils


def combined_impute(data):
    str_vars = data.select_dtypes(exclude=[float, int]).columns.tolist()

    trf1 = ColumnTransformer(transformers=[
        ('enc', MultiColumnLabelEncoder(columns=str_vars))
    ], remainder='passthrough',
        verbose=True)

    test = trf1.fit_transform()

    return data


def combined_impute2(data):
    """
    Different column types require a different imputer strategy. Namely:
    1. String columns need simple imputer for most frequent value
    2. Int columns can have the median value
    3. Float columns could have mean or iterative imputer, will test both

    Parameters
    ----------
    data

    Returns
    -------

    """
    print('Starting imputation step...')

    data = US_utils.replace_missing_with_na(data, list(data))

    data = data.convert_dtypes()

    str_vars = data.select_dtypes(exclude=[float, int]).columns.tolist()
    float_vars = data.select_dtypes(include=float).columns.tolist()
    int_vars = data.select_dtypes(include=int).columns.tolist()

    #str_vars = ['region']

    print('Beginning imputation pipeline...')
    impute_pipeline = ColumnTransformer(transformers=[
        ('int_impute', SimpleImputer(missing_values=pd.NA,
                                     strategy='median').set_output(transform='pandas'), int_vars),
        ('float_impute', SimpleImputer(missing_values=pd.NA,
                                       strategy='mean').set_output(transform='pandas'), float_vars),
        ('str_impute', SimpleImputer(missing_values=pd.NA,
                                     strategy='most_frequent').set_output(transform='pandas'), str_vars)
    ], remainder='passthrough',
        verbose=True,
        verbose_feature_names_out=False).set_output(transform='pandas')

    imputed_data = impute_pipeline.fit_transform(data)

    return imputed_data


def iterative_impute(data):
    """

    Parameters
    ----------
    data

    Returns
    -------

    """
    print('Starting Iterative Imputation...')

    # create an ordinal encoder to encode all categorical and string data as numeric (think np.float64 as default)
    # then encode data with this encoder
    # only want to run this on string vars as numeric ordinal should already be ok, so first select string vars
    str_vars = data.select_dtypes(exclude=[float, int]).columns.tolist()
    # str_vars = (data.applymap(type) == str).all(0)

    # unfortunately because the encoder is stupid we have to replace missing values in strings as something that is NOT
    # np.nan, so replacing with None and doing another replace to turn these back into np.nan
    ordinal_encoder = OrdinalEncoder(dtype=int,
                                     handle_unknown='use_encoded_value',
                                     unknown_value=-1,
                                     encoded_missing_value=-1).set_output(transform='pandas')

    # first create a mask for na values to replace them
    nan_mask = data[str_vars].isna()
    data[str_vars] = data[str_vars].mask(nan_mask.reindex(index=data[str_vars].index,
                                                          columns=data[str_vars].columns,
                                                          fill_value=False), '?')
    data_encoded = ordinal_encoder.fit_transform(data)
    # data_encoded[str_vars] = data[str_vars].mask(nan_mask.reindex(index=data_encoded[str_vars].index,
    #                                                              columns=data_encoded[str_vars].columns,
    #                                                              fill_value=False), np.nan)
    data_encoded[data_encoded == '?'] = np.nan
    data_encoded[data_encoded == -1] = np.nan

    # data.loc[data[str_vars].notna(), [str_vars]] = \
    #    ordinal_encoder.fit_transform(data[str_vars].dropna().values.reshape(-1, 1))
    # now put 'None' back to np.nan
    # data[str_vars] = data[str_vars].fillna(np.nan)
    # data[str_vars][data[str_vars] == 10000] = np.nan

    imputer = IterativeImputer(random_state=0,
                               max_iter=1,
                               verbose=2,
                               add_indicator=False,
                               keep_empty_features=False).set_output(transform='pandas')  # set output as pd dataframe

    imputed_data = imputer.fit_transform(data_encoded)

    # convert back to pd.DataFrame with correct column names
    # imputed_numeric = pd.DataFrame(np.squeeze(imputed_numeric),
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
    ordinal_encoder = OrdinalEncoder().set_output(transform='pandas')
    encoded_data = ordinal_encoder.fit_transform(data)

    # create imputer with n_neighbours == 1. This is equal to a hotdecking as the value is replaced with closest
    # neighbour. Not the most robust imputation strategy but purely for ensuring a start point in the model I think
    # this should be fine
    imputer = KNNImputer(n_neighbors=1)  # set output as pandas dataframe

    # Run imputation on all data
    print('Imputing numeric columns with KNN imputer...')
    # imputed_data = imputer.fit_transform(encoded_data)

    # test_chunk = encoded_data[encoded_data['time'] == 10.0]
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


def set_dtypes(data):
    """
    Getting the correct data type for each column becomes quite important when running through the sklearn imputation
    functions, as we will make different decisions based on dtype such as which columns to encode as numeric ordinal,
    and which to impute based on different schema (some best in iterative, some best through simple maybe imputing
    most common value).

    This is not simple however because Pandas read_csv function coerces a lot of data into simple types, missing things
    like ordinal or binary when the values are numeric. This function will attempt to set those dtypes based on some
    tests, like whether the unique values are 0/1 (binary) or 0-some smallish number (ordinal).

    Parameters
    ----------
    data

    Returns
    -------

    """
    # first worth trying the pandas dataframe function convert_dtypes for automatic conversion
    # might catch a couple of float columns that should be int or boolean
    # need to ensure that numeric -9s are converted to string first or everything gets left as object. Very annoying
    # but I've looked into fixing this in the earlier pipeline and it's unfortunately very difficult
    # so to fix, first get all object columns then convert -9 values to '-9'
    # obj_cols = data.select_dtypes(include=object).columns.tolist()
    # think this loop is inefficient but I'm absolutely over trying to find a vectorised way of doing it
    # for col in obj_cols:
    #    data[col][data[col] == -9] = '-9'

    # if we change all missing to np.nan before we do all of this processing it gets a bit easier (don't have to deal
    # with missing values when converting types)
    data = US_utils.replace_missing_with_na(data, list(data))

    data = data.convert_dtypes()
    # it only really managed to convert objects to strings, disappointing

    # next check can be for binaries, we can be converted to boolean type
    # this is the simplest check
    # get column names into a list for conversion
    # have to use object for check as select_dtypes doesn't allow for string
    str_categoricals = data.select_dtypes(include=object).columns.tolist()

    data[[str_categoricals]] = data[[str_categoricals]].astype('category')

    return data


def main():
    maxyr = US_utils.get_data_maxyr()

    print('Generating stock population...')
    years = np.arange(2009, maxyr)
    file_names = [f"data/final_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # set dtypes for later processing
    # data = set_dtypes(data)

    # need to convert some dtypes before imputation. Simplest way to do this is with pd.DataFrame.convert_dtypes()
    # this works best if we replace missing first
    #data = data.convert_dtypes()

    # run through imputation
    # data = iterative_impute(data)
    data = combined_impute2(data)
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
