"""Functions for applying complete case missingness correction to
Understanding Society data."""

import numpy as np
import pandas as pd

import US_utils

def complete_case(data):
    """ main function for complete case.
    Parameters
    ----------
    data : pd.DataFrame
        US data to perform complete case correction on.
    Returns
    -------
    data : pd.DataFrame
        Corrected data.
    """
    data = data.replace(US_utils.missing_types, np.nan)
    data = data.dropna(axis=0)
    return data


def complete_case_varlist(data, varlist):
    """ Function for complete case only on specific vars (from varlist).
    Parameters
    ----------
    data : pd.DataFrame
        US data to perform complete case correction on.
    varlist : list
        List of variables for which to perform complete case on
    Returns
    -------
    data : pd.DataFrame
        Corrected data.
    """
    for var in varlist:
        data[var] = data[var].replace(US_utils.missing_types, np.nan)
        data = data.dropna(axis=0, subset=[var])

    #data[varlist] = data[varlist].replace(US_utils.missing_types, np.nan)

    #data = data.dropna(axis=0)
    data = data.reset_index(drop=True)
    return data


def complete_case_custom_years(data, var, years):

    # Replace all missing values in years (below 0) with NA, and drop the NAs
    data[var][data['time'].isin(years)] = data[var][data['time'].isin(years)].replace(US_utils.missing_types, np.nan)
    data = data[~(data['time'].isin(years) & data[var].isna())]

    return data


if __name__ == "__main__":
    maxyr = US_utils.get_data_maxyr()

    years = np.arange(2009, maxyr)
    file_names = [f"data/composite_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    complete_case_vars = ["housing_quality", 'marital_status', 'yearly_energy', "job_sec",
                          "education_state", 'region', "age"]  # many of these
    # REMOVED:  'job_sector', 'labour_state'

    data = complete_case_varlist(data, complete_case_vars)

    # Need to do correction on some variables individually as they are only in the dataset in specific years
    # doing complete case without the year range taken into account removes the whole years data
    # make sure its int not float (need to convert NA to 0 for this to work)
    data = complete_case_custom_years(data, 'loneliness', years=[2017, 2018, 2019, 2020])
    # Now do same for neighbourhood_safety
    data = complete_case_custom_years(data, 'neighbourhood_safety', years=[2011, 2014, 2017])
    # ncigs missing for wave 1 only
    data = complete_case_custom_years(data, 'ncigs', years=list(range(2013, 2020, 1)))
    # Nutrition only present in 2014
    data = complete_case_custom_years(data, 'nutrition_quality', years=[2015, 2017, 2019])

    drop_columns = ['financial_situation', # these are just SF12 MICE columns for now. see US_format_raw.py
                    'ghq_depression',
                    'scsf1',
                    'clinical_depression',
                    'ghq_happiness',
                    'phealth_limits_work',
                    'likely_move',
                    'newest_education_state',
                    'health_limits_social',
                    'future_financial_situation',
                    'behind_on_bills',
                    'mhealth_limits_work'] # some columns are used in analyses elsewhere such as MICE and not featured in the final model.
    # remove them here or as late as needed.
    data = data.drop(labels=drop_columns, axis=1)

    US_utils.save_multiple_files(data, years, "data/complete_US/", "")
