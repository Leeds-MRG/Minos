"""Functions for applying complete case missingness correction to
Understanding Society data."""

import numpy as np
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
        #data[var] = data[var].dropna(axis=0)

    data = data.dropna(axis=0)
    data = data.reset_index(drop=True)
    return data


if __name__ == "__main__":

    years = np.arange(2009, 2020)
    file_names = [f"data/composite_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    complete_case_vars = ["job_sec", "labour_state", "education_state", "housing_quality", "age",
                          'yearly_energy', 'region'] # many of these
    data = complete_case_varlist(data, complete_case_vars)

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

