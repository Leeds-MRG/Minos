"""Main file for running missing data correction on Understanding Societies in Python. """
import pandas as pd
import numpy as np
import os

import US_missing_description
import US_missing_deterministic as USmd
import US_missing_LOCF
import US_missing_data_correction as USmdc
import US_utils
import US_complete_case as UScc

def add_nobs_column(data):
    """ Add column for number of observations (nobs) per individual to data frame

    Parameters
    ----------
    data : pd.DataFrame
        Data frame to add number of observations column to.

    Returns
    -------
    data : pd.DataFrame
        Frame with column added.
    """
    # build counts data frame. two columns for number of observations and indiviudal ids.
    counts = pd.DataFrame(data["pidp"].value_counts())
    counts.columns = ["nobs"]
    counts["pidp"] = counts.index
    counts = counts.reset_index(drop=True)
    # Inner merge counts dataframe into main dataframe. Results in one column of nobs added to data.
    data = data.merge(counts, how="inner", on="pidp")
    return data


def main(output_dir):
    # Load in data.
    # Process data by year and pidp.
    years = np.arange(1991, 2020) # need the full range of US data for locf imputation.
    save_years = np.arange(2009, 2020) # only saving UKHLS data after 2009.

    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    data = add_nobs_column(data)
    data = US_utils.restrict_chains(data, 2) #grab people with two or more obs.

    # Plots for distribution of missingness before correction. May be better in a separate file/notebook.
    #US_missing_description.missingness_hist(data, "education_state", "age")
    #US_missing_description.missingness_hist(data, "labour_state", "age")
    #US_missing_description.missingness_bars(data, "education_state", "ethnicity")
    print("Raw data before correction")
    before = US_missing_description.missingness_table(data)

    # Correct deterministically missing data due to unemployment.
    columns = ["job_industry",
               "job_duration_m",
               "job_duration_y",
               "job_sec",
               "job_occupation"]
    data = USmd.det_missing(data, columns, USmd.is_unemployed, USmd.force_nine)
    print("After removing deterministically missing values.")
    after_det = US_missing_description.missingness_table(data)

    #f_columns = ["education_state", "depression", "depression_change",
    #             "labour_state", "job_duration_m", "job_duration_y", "job_occupation",
    #             "job_industry", "job_sec", "heating"]  # add more variables here.
    # define columns to be forward filled, back filled, and linearly interpolated.
    # note columns can be forward and back filled for immutables like ethnicity.
    f_columns = ['education_state', 'labour_state', 'job_sec', 'heating', 'ethnicity', 'sex', 'birth_year',
                 'yearly_gas', 'yearly_electric', 'yearly_gas_electric', 'yearly_oil', 'yearly_other_fuel'] # 'ncigs', 'ndrinks']
    fb_columns = ["sex", "ethnicity", "birth_year"]  # or here if they're immutable.
    li_columns = ["age"]
    data = US_missing_LOCF.locf(data, f_columns=f_columns, fb_columns=fb_columns)
    print("After LOCF correction.")
    after_locf = US_missing_description.missingness_table(data)
    data = US_missing_LOCF.interpolate(data, li_columns)
    print("After interpolation of linear variables.")
    after_interp = US_missing_description.missingness_table(data)

    # cut back to just save data. don't want to complete case rows that aren't used.
    data = data.loc[data["time"].isin(save_years)]
    # TODO MICE goes here to deal with remaining missing obs.

    # complete case analysis instead of MICE for now.
    #data = UScc.complete_case(data)
    #complete_case_vars = ['sex', 'ethnicity', 'region']
    #data = UScc.complete_case_varlist(data, complete_case_vars)
    #after_complete_case = US_missing_description.missingness_table(data)

    # TODO. complete case for just critical columns. merge with Luke's func.
    #data[["sex", "ethnicity", "region"]] = data[["sex", "ethnicity", "region"]].replace(US_utils.missing_types, np.nan)
    #i = data[["sex", "ethnicity", "region"]].dropna().index
    #data = data.loc[i,:]

    US_utils.save_multiple_files(data, save_years, output_dir, "")

    return data


if __name__ == "__main__":
    output = 'data/corrected_US/'
    data = main(output)
