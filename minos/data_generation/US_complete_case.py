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

    data = data.reset_index(drop=True)
    return data


def complete_case_custom_years(data, var, years):
    print("Processing {} for custom years {}".format(var, years))

    # Replace all missing values in years (below 0) with NA, and drop the NAs
    data[var][data['time'].isin(years)] = data[var][data['time'].isin(years)].replace(US_utils.missing_types, np.nan)
    # data[var][data['time'].isin(years)].replace(US_utils.missing_types, np.nan, inplace=True) # Avoids Pandas SettingWithCopyWarning
    data = data[~(data['time'].isin(years) & data[var].isna())]

    return data


def cut_outliers(df, lower, upper, var):
    """Take values of a column within the lower and upper percentiles

    E.g. if lower = 5 upper = 95. removes the top and bottom 5% from the data."""
    P = np.nanpercentile(df[var], [lower, upper])
    new_df = df.loc[((df[var] > P[0]) & (df[var] < P[1])), ]
    return new_df


if __name__ == "__main__":
    maxyr = US_utils.get_data_maxyr()

    years = np.arange(2009, maxyr)
    file_names = [f"data/composite_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    complete_case_vars = ["housing_quality", 'marital_status', 'yearly_energy', "job_sec",
                          "education_state", 'region', "age", "job_sector", 'financial_situation', #'SF_12',
                          "housing_tenure",
                          "nkids_ind", 'S7_labour_state', 'job_hours']
    # REMOVED:  'job_sector', 'labour_state'

    data = complete_case_varlist(data, complete_case_vars)
    data = data.loc[~(data['child_ages'].str.contains('-9') is True)]  # remove any household with dodgy age chains.

    # Need to do correction on some variables individually as they are only in the dataset in specific years
    # doing complete case without the year range taken into account removes the whole years data
    # make sure its int not float (need to convert NA to 0 for this to work)
    data = complete_case_custom_years(data, 'loneliness', years=[2017, 2018, 2019, 2020, 2021])
    # Now do same for neighbourhood_safety
    data = complete_case_custom_years(data, 'neighbourhood_safety', years=[2011, 2014, 2017, 2020])
    data = complete_case_custom_years(data, 'S7_neighbourhood_safety', years=[2011, 2014, 2017, 2020])
    # ncigs missing for wave 1, 3 & 4 (although smoker missing for wave 5 (2013) which causes trouble)
    # therefore going to set all -8 (inapplicable due to non-smoker) to 0 for 2013 only
    data['ncigs'][(data['time'] == 2013) & (data['ncigs'] == -8)] = 0
    data = complete_case_custom_years(data, 'ncigs', years=list(range(2013, 2022, 1)))
    # Nutrition only present in 2014
    data = complete_case_custom_years(data, 'nutrition_quality', years=[2015, 2017, 2019, 2021])

    # Complete case for some vars in 2015 as it was messing up the cross-validation runs
    #data = complete_case_custom_years(data, 'job_sector', years=[2014])
    data = complete_case_custom_years(data, 'hh_income', years=[2015])

    # SIPHER 7 complete case stuff
    data = complete_case_custom_years(data, 'S7_physical_health', years=list(range(2010, 2022, 1)))
    data['S7_physical_health'] = data['S7_physical_health'].astype(int)
    data = complete_case_custom_years(data, 'S7_mental_health', years=list(range(2010, 2022, 1)))
    data['S7_mental_health'] = data['S7_mental_health'].astype(int)
    data = complete_case_custom_years(data, 'S7_labour_state', years=list(range(2009, 2022, 1)))


    drop_columns = [#'financial_situation',  # these are just SF12 MICE columns for now. see US_format_raw.py
                    'ghq_depression',
                    'scsf1',
                    'clinical_depression',
                    'ghq_happiness',
                    'likely_move',
                    'newest_education_state',
                    'health_limits_social',
                    'future_financial_situation',
                    'behind_on_bills']  # some columns are used in analyses elsewhere such as MICE and not
                                        # featured in the final model.
                                        # remove them here or as late as needed.
                                        
    data = data.drop(labels=drop_columns, axis=1)
    data = cut_outliers(data, 0.1, 99.9, "hh_income")

    US_utils.save_multiple_files(data, years, "data/complete_US/", "")
