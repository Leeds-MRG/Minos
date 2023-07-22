"""
Script for imputing missing values in the input populations, to ensure we have a full dataset with no missing values.

This script will read in the final population files (used for fitting transition models), and run through a couple of
things required to create the starting populations. These are:
1. Impute missing values using sklearn.impute functions
2. Do prediction of highest education
"""

import argparse
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
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

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


def wave_data_copy(data, var, copy_year, paste_year, var_type):
    """
    Imputer is finding it quite difficult in some cases

    Parameters
    ----------
    data : pd.dataframe
        Dataframe of all variables across all years
    var : str
        String variable we want to copy onto another year
    copy_year : int
        Year to copy data from
    paste_year : int
        Year to paste data to

    Returns
    -------
    data_merged : pd.dataframe
        Final dataset with {var} copied from {copy_year} to {paste_year}
    """
    print(f"Copying wave {copy_year} {var} onto wave {paste_year} sample...")

    # get temporary dataframe of pidp, time, and nutrition_quality from 2019
    tmp = data[['pidp', 'time', var]][data['time'] == copy_year]
    # change time to 2018 for tmp
    tmp['time'] = paste_year

    # replace -9 values in 2020 with Nonetype
    data['nutrition_quality'][data['time'] == paste_year] = None

    # now merge and combine the two separate nutrition_quality columns (now with suffix') into one col
    data_merged = data.merge(right=tmp,
                             how='left',
                             on=['pidp', 'time'])

    # set up merge labels
    var_x = var + '_x'
    var_y = var + '_y'

    data_merged[var] = -9
    data_merged[var][data_merged['time'] != paste_year] = data_merged[var_x]
    data_merged[var][data_merged['time'] == paste_year] = data_merged[var_y]
    # drop intermediate columns
    data_merged.drop(labels=[var_x, var_y], axis=1, inplace=True)

    # last step is to impute the still missing with the median value (code is different for continuous vs ordinal vars).
    # Without this we would have to drop all the missing values, meaning anybody not in wave 11 would be removed.
    # This is dodgy because we don't know who should actually be missing, but I don't know what else to do
    if var_type == 'continuous':
        data_merged[var][(data_merged['time'] == paste_year) & (data_merged[var].isna())] = \
            data_merged[var][data_merged['time'] == paste_year].median()
    elif var_type == 'ordinal':
        data_merged[var][(data_merged['time'] == paste_year) & (data_merged[var].isna())] = \
            data_merged[var][data_merged['time'] == paste_year].value_counts().index[0]

    return data_merged


def combined_simple_impute(data):
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

    # force some variables to the right type
    imputed_data['ncigs'] = imputed_data['ncigs'].astype(int)

    return imputed_data


def combined_clever_impute(data):

    data = US_utils.replace_missing_with_na(data, list(data))

    data = data.convert_dtypes()

    str_vars = data.select_dtypes(exclude=[float, int]).columns.tolist()
    float_vars = data.select_dtypes(include=float).columns.tolist()
    int_vars = data.select_dtypes(include=int).columns.tolist()

    """
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
    data_encoded[data_encoded == '?'] = np.nan
    data_encoded[data_encoded == -1] = np.nan
    """

    """
    # use pd.factorize to encode string variables as int
    # factorize only works on 1D array so need to do this in loop (replace with apply if can be bothered later)
    var_label_list = []
    for i, var in enumerate(str_vars):
        data[var], labels = pd.factorize(data[var])
        var_label_list.append(labels)
        data[var][data[var] == -1] = np.nan
    """

    # another go at encoding string vars with a bit of dictionary magic and replace
    transform_dict = {}
    for col in str_vars:
        cats = pd.Categorical(data[col]).categories
        d = {}
        for i, cat in enumerate(cats):
            d[cat] = str(i)
        transform_dict[col] = d

    encoded_data = data.replace(transform_dict)
    encoded_data[str_vars] = encoded_data[str_vars].fillna('-1')
    encoded_data[str_vars] = encoded_data[str_vars].astype(int)

    print('Beginning imputation pipeline...')
    impute_pipeline = ColumnTransformer(transformers=[
        ('int_str_impute', IterativeImputer(missing_values=np.nan,
                                        initial_strategy='median',
                                        random_state=0,
                                        verbose=2,
                                        estimator=KNeighborsRegressor(n_neighbors=5)).set_output(transform='pandas'), int_vars),
        ('float_impute', IterativeImputer(missing_values=np.nan,
                                          initial_strategy='mean',
                                          random_state=0,
                                          verbose=2).set_output(transform='pandas'), float_vars),
        ('str_impute', IterativeImputer(missing_values=-1.0,
                                        initial_strategy='median',
                                        random_state=0,
                                        verbose=2,
                                        max_iter=15,
                                        estimator=RandomForestRegressor(
                                            # We tuned the hyperparameters of the RandomForestRegressor to get a good
                                            # enough predictive performance for a restricted execution time.
                                            n_estimators=4,
                                            max_depth=10,
                                            bootstrap=True,
                                            max_samples=0.5,
                                            n_jobs=2,
                                            random_state=0,
                                        )).set_output(transform='pandas'),
         str_vars),
    ], remainder='passthrough',
        verbose=True,
        verbose_feature_names_out=False).set_output(transform='pandas')

    """
    KNeighborsRegressor(n_neighbors=1)
    RandomForestRegressor(
        # We tuned the hyperparameters of the RandomForestRegressor to get a good
        # enough predictive performance for a restricted execution time.
        n_estimators=4,
        max_depth=10,
        bootstrap=True,
        max_samples=0.5,
        n_jobs=2,
        random_state=0,
    )
    """

    # n_nearest_features=10,

    imputed_data = impute_pipeline.fit_transform(encoded_data)

    # now reverse the previous encoding to bring back the categorical data
    #imputed_data = ordinal_encoder.inverse_transform(imputed_data)

    """
            ('int_impute', IterativeImputer(missing_values=pd.NA,
                                        initial_strategy='median',
                                        random_state=0,
                                        n_nearest_features=10).set_output(transform='pandas'), int_vars),
        ('float_impute', IterativeImputer(missing_values=pd.NA,
                                          initial_strategy='mean',
                                          random_state=0,
                                          n_nearest_features=10).set_output(transform='pandas'), float_vars),
            ('int_impute', KNNImputer(missing_values=pd.NA,
                                  n_neighbors=1).set_output(transform='pandas'), int_vars),
        ('float_impute', KNNImputer(missing_values=pd.NA,
                                    n_neighbors=1).set_output(transform='pandas'), float_vars),
    """

    """
    for i, var in enumerate(str_vars):
        data[var], labels = pd.factorize(data[var])
        var_label_list.append(labels)
        data[var][data[var] == -1] = np.nan
    """
    # round any float values that should not be float
    imputed_data[str_vars] = round(imputed_data[str_vars])
    imputed_data[int_vars] = round(imputed_data[int_vars]).astype(int)

    # now to inverse tranformation using the transform dict
    inverse_transform_dict = {}
    for col, d in transform_dict.items():
        inverse_transform_dict[col] = {int(v): k for k, v in d.items()}

    # put int values back to string for inverse transform
    #imputed_data[str_vars] = imputed_data[str_vars].astype(str)

    imputed_data = imputed_data.replace(inverse_transform_dict)

    # for some reason we still have 8 records with missing marital status, so just going to force these to partnered as
    # thats the largest group
    imputed_data['marital_status'][imputed_data['marital_status'] == -1.0] = 'Partnered'
    imputed_data['loneliness'][imputed_data['loneliness'] == -1.0] = 'Sometimes'

    # handle impossible or highly improbable values
    # SF_12
    imputed_data['SF_12'][imputed_data['SF_12'] > 100] = 80
    imputed_data['SF_12'][imputed_data['SF_12'] < 0] = 10
    # nutrition_quality
    imputed_data['nutrition_quality'][imputed_data['nutrition_quality'] > 200] = 20.0
    # physical health should be integer not float
    imputed_data['phealth'] = round(imputed_data['phealth']).astype(int)
    # ncigs can't be negative
    imputed_data['ncigs'][imputed_data['ncigs'] < 0] = 0

    return imputed_data


def main(cross_validation):
    # get max year of data
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
    #data = combined_simple_impute(data)
    data = combined_clever_impute(data)
    # data = knn_impute(data)
    # data = simple_string_impute(data)

    # TODO: Move wave data copy from generate_final_pop to here. Shouldn't be done before fitting models, but should be
    #   after imputation

    # save data
    US_utils.save_multiple_files(data, years, "data/stock/", "")

    # cross validation
    if cross_validation:

        US_utils.check_output_dir("data/stock/cross_validation")

        # read in pidp split
        split = pd.read_csv('data/cv_pidp_split.csv')

        # Now create separate transition and simulation datasets and save them in subfolders of final_US
        bat1 = data[data['pidp'].isin(split['split0'])]
        bat2 = data[data['pidp'].isin(split['split1'])]
        bat3 = data[data['pidp'].isin(split['split2'])]
        bat4 = data[data['pidp'].isin(split['split3'])]
        bat5 = data[data['pidp'].isin(split['split4'])]

        US_utils.save_multiple_files(bat1, years, "data/stock/cross_validation/batch1/", "")
        US_utils.save_multiple_files(bat2, years, "data/stock/cross_validation/batch2/", "")
        US_utils.save_multiple_files(bat3, years, "data/stock/cross_validation/batch3/", "")
        US_utils.save_multiple_files(bat4, years, "data/stock/cross_validation/batch4/", "")
        US_utils.save_multiple_files(bat5, years, "data/stock/cross_validation/batch5/", "")
    # done

    """
    #numeric_data = data.select_dtypes(include=np.number)
    float_data = data.select_dtypes(include=float)
    float_data_cols = float_data.columns.tolist()
    float_data = US_utils.replace_missing_with_na(float_data, float_data_cols)
    """


if __name__ == '__main__':
    # Use argparse to select between normal and cross-validation
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation",
                                     usage='use "%(prog)s --help" for more information')

    parser.add_argument("-c", "--cross_validation", dest='crossval', action='store_true', default=False,
                        help="Select cross-validation mode to produce cross-validation populations.")

    args = parser.parse_args()
    cross_validation = args.crossval

    main(cross_validation)
