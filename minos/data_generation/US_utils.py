""" Utilities for handling Understanding Societies data in preprocessing, missing data handling, and in Minos.

"""
import os
import pandas as pd
import numpy as np
import json
import glob
from string import ascii_lowercase as alphabet  # For creating wave specific attribute columns. See get_ukhls_columns.
import pickle

########################
# Single wave functions.
########################

def check_output_dir(output):
    """Check an output data directory exists and create it if it does not.

    Parameters
    ----------
    output : str
        Where is data being output?
    Returns
    -------
    None
    """
    if not os.path.isdir(output):
        os.mkdir(output)
        print(f"Output directory not found. Creating directory to save data at {output}")


def save_file(data, destination, prefix, year):
    """Save formatted US data to a new file.

    Parameters
    ----------
    data : pd.DataFrame
        Data to save.
    year : int
        Which wave of data is being saved.
    Returns
    -------
    None
    """
    check_output_dir(destination)
    output_file_name = destination + prefix + f"{year}_US_cohort.csv"
    data.to_csv(output_file_name, index=False)
    print(f"wave for {year} saved to {output_file_name}")


def load_file(file_name):
    """ Given a file directory load a dta as a pandas DataFrame.

    Parameters
    --------
    file_name : str
        Path of the file to read data from.

    Returns
    ------
    data : pandas.DataFrame
        Data read from the dta with name file_name.
    """
    data = pd.read_stata(file_name, convert_categoricals=False)
    return data

def save_json(data, destination):
    """Save python dictionaries to JSON.

    Parameters
    ----------
    data : dict
        What dictionary is being saved?
    destination : str
        Where is it being saved?
    Returns
    -------
    None
    """
    with open(destination, 'w') as fp:
        json.dump(data, fp)

def load_json(file_source, file_name):
    """ Load a JSON data dictionary.

    Parameters
    ----------
    file_source, file_name : str
        Where is the file stored and what is its name.

    Returns
    -------
    data : dict
        Loaded json dictionary.
    """
    f = open(file_source + file_name)
    data = json.load(f)
    f.close()
    return data


def get_wave_letter(year):
    """ Get wave letter based on year for US data.

    Waves 1990-2008 are waves A-R of BHPS. 2009-2020 are waves 1-11 of UKHLS.

    Examples
    --------
    For year 1992 this will return wave string "c".

    Parameters
    ----------
    year : int
        What year is it?
    Returns
    -------
    wave_letter : str
        Letter that corresponds to wave.
    """
    # UKHLS naming convention.
    # Wave for 2009 begins with a_, b_, c_,...
    if year < 2009:
        wave_number = year - 1991
    else:
        wave_number = year - 2009
    wave_letter = alphabet[wave_number]
    return wave_letter

def US_file_name(year, source, section):
    """ Get file name for given year of US data.

    Note this has changed recently. Used to be each wave has a separate file but now all waves are in a
    single directory. Removes one level of pathing.

    Examples
    --------
    For wave year 1992 this will return string
    "bhps/bc_indresp.dta".

    Parameters
    ----------
    year : int
        What year is it?
    source, section : str
        Where is the data and what part of it is being loaded
    Returns
    -------
    file_name : str
        Returns the file_name
    """
    # BHPS naming convention
    # ba, bb, bc, ...
    # UKHLS naming convention.
    # Wave for 2009 begins with a_, b_, c_,...
    wave_letter = get_wave_letter(year)
    if year < 2009:  # bhps
        file_name = f"bhps/b{wave_letter}_{section}.dta"
    else:  # ukhls
        file_name = f"ukhls/{wave_letter}_{section}.dta"
    file_name = source + file_name  # add directory onto front.
    return file_name


def wave_prefix(columns, year):
    """ Determine wave prefix for ukhls wave data.

    Parameters
    ----------
    columns : list
        A list of column names to add wave prefixes to.
    year : int
        Which wave year is being processed.

    Returns
    -------
    columns : list
        Column names with wave prefixes added.
    """
    #wave_letter = alphabet[year - 2008]
    wave_letter = get_wave_letter(year)
    if year < 2009:
        wave_letter = 'b' + wave_letter

    exclude = ["pidp"]
    for i, item in enumerate(columns):
        if item not in exclude:
            columns[i] = wave_letter + "_" + item  # Looks stupid but needed to update the list.
    return columns


def subset_data(data, required_columns, column_names, substitute = True):
    """ Take desired columns from US data and rename them.

    Parameters
    ----------
    data : pd.DataFrame
        Loaded in data from csv.
    required_columns : list
        Which subset of columns is being taken.
    column_names : list
        New names for dataframe columns. Makes it clearer for use in microsim.
    substitute : bool
        If specified variables arent present in a specific wave of US data then substitute
        it with an empty column for that wave. For example depression (hcond17) is not available in wave 2 of UKHLS but
        is available in all other waves. Setting substitute = True replaces the variable in wave 2 with an empty column.
        Is entirely empty data but preserves consistent data across all waves for later imputation. Otherwise will
        raise a key error.

    Returns
    -------
    data : pd.DataFrame
        Subset of initial data with desired columns.
    """
    # If a column is missing substitute in a dummy column of missings (-9). Keeps data consistent when variables are
    # are missing from certain waves. Don't go nuts though.
    if substitute:
        for item in required_columns:
            if item not in data.columns:
                data[item] = -9
                print(f"Warning! {item} not found in current wave. Substituting a dummy column. "
                      + "Set substitute = False in the subset_data function to suppress this behaviour.")
    # Take subset of data for required columns and rename them.
    data = data[required_columns]
    data.columns = column_names
    return data


def restrict_variable(data, variable, lower, upper):
    """ Restrict a variable to within two bounds

    E.g. get all individuals between ages 20 and 30.

    Parameters
    ----------
    data : pandas.DataFrame
        The data to be subsetted.
    variable : str
        Which data column is being restricted
    lower, upper : int
        The lower and upper bounds to restrict between.
    Returns
    -------
    data : pandas.DataFrame
        The `data` between the specified ages.
    """
    data = data.loc[data[variable] <= upper]
    data = data.loc[lower <= data[variable]]
    return data


######################
# Many wave functions.
######################


def save_multiple_files(data, years, destination, prefix):
    """ Save formatted wave data. Split it up into years and save as individual csvs.


    Parameters
    ----------
    data : pandas.DataFrame
        The final `data` waves to be saved.
    years : list
        List of ints. Which years of waves are being saved.
    destination, prefix : str
        What destination is file being sent to.
        What prefix goes in front of file names. e.g. "", "missing", "a_", etc.
    Returns
    -------
    None.

    """
    check_output_dir(destination)
    for year in years:
        wave_data = data.loc[data["time"] == year]
        file_name = f"{destination}{prefix}{year}_US_cohort.csv"
        wave_data.to_csv(file_name, index=False)
        print(f"Data for {year} saved to {file_name}.")


def load_multiple_data(file_names):
    """Load in many waves of data.

    Parameters
    ----------
    file_names : list
        List of file_names to extract data for.
    Returns
    -------
    data : pandas.DataFrame
        Data array of data from given wave years. Its all one block so there
        may be repeats for each unique pid.
    """
    # load wave by year and mash them into one big frame.
    data = pd.DataFrame()
    for item in file_names:
        wave = pd.read_csv(item)
        data = pd.concat([data, wave], sort=False)
    data = data.reset_index(drop=True)  # Reset index so they are unique. drop=True does not keep it as a new column.
    return data


def restrict_chains(data, k):
    """Restrict data to people with at least k rows.

    Parameters
    ----------
    data : pandas.DataFrame
        The `data` from US to be subsetted.
    k : int
        The minimum number of measurements needed for a person to be kept.
    Returns
    -------
    data : pandas.DataFrame
        The subsetted data of people with at least k entires.
    """
    # How many entries does each person have.
    # Take Ids of anyone with at least k values.
    # Subset the main data frame to remove anyone with less than k values.
    id_counts = data["pidp"].value_counts()
    trajectories_ids = list(id_counts.loc[id_counts >= k].index)
    data = data.loc[data["pidp"].isin(trajectories_ids)]
    return data


def generate_interview_date_var(data):
    """ Generate an interview date variable in the form YYYYMM

    Parameters
    ----------
    data : pandas.DataFrame
        The `data` containing interview year and month (hh_int_y, hh_int_m)
    Returns
    -------
    data : pandas.DataFrame
        Dataframe with interview date variable added
    """
    # Replace na with 0 (na is technically a float so messes up when converting to int) and convert to int then string
    # Format date to 2 sigfigs so we keep the form '08' instead of just '8'
    data["hh_int_y"] = data["hh_int_y"].fillna(0).astype(int).astype(str)
    data["hh_int_m"] = data["hh_int_m"].fillna(0).astype(int).astype(str).str.zfill(2)
    # now concatenate the date strings and handle cases of missings (-9, -8). Also replace 0 with -9
    data["Date"] = data["hh_int_y"] + data["hh_int_m"]
    data["Date"][data["Date"] == '0'] = '-9'
    data["Date"][data["Date"] == '-9-9'] = '-9'
    data["Date"][data["hh_int_y"] == -9] = '-9'
    data["Date"][data["hh_int_m"] == -9] = '-9'
    data["Date"][data["Date"] == '-8-8'] = '-8'
    data["Date"] = data["Date"].astype(int)  # need it as an int as that what CPI dataset uses

    return data


def inflation_adjustment(data, var):
    """ Adjust financial values for inflation using the Consumer Price Index (CPI)

    Parameters
    ----------
    data : pandas.DataFrame
        The `data` containing financial variable(s) to be adjusted.
    var : str
        Name of a financial variable to be adjusted.
    Returns
    -------
    data : pandas.DataFrame
        Dataframe with adjusted financial values.
    """
    # need interview date for adjustment
    data = generate_interview_date_var(data)
    # Inflation adjustment using CPI
    # read in CPI dataset
    cpi = pd.read_csv('persistent_data/CPI_202010.csv')
    # merge cpi onto data and do adjustment, then delete cpi column (keep date)
    data = pd.merge(data, cpi, on='Date', how='left')
    data[var] = (data[var] / data['CPI']) * 100
    data.drop(labels=['CPI', 'Unnamed: 0'], axis=1, inplace=True)

    return data


def get_data_maxyr():
    """
    This function will calculate the final year of raw Understanding Society input data so we don't have to update
    the value in every script every time we try to pull the newest wave of US.

    Parameters
    ----------
    raw_US_dir : str
        Path to raw Understanding Society directory (UKDA-6614-stata)

    Returns
    -------
    maxyr : int
        The final year of US data in the input data directory.
    """
    print('Calculating max year of data...')

    # hardcoding this because its simpler than passing it as command line arg to each datagen script
    # TODO: find a way to run this func once in US_format_raw.py and save somewhere for easy access
    #   Maybe a Makefile arg would make more sense?
    raw_US_dir = '../UKDA-6614-stata/stata/stata13_se/ukhls/'

    # Get a list of the filenames in the raw US directory
    #   drop the _indresp.dta suffix
    #   convert the characters into numbers
    #   calculate max year from max number

    indresp_filelist = [os.path.basename(x) for x in glob.glob(raw_US_dir + '*_indresp.dta')]
    wave_list = []
    for string in indresp_filelist:
        wave_list.append(string.replace("_indresp.dta", ""))
    wave_list = sorted(wave_list)

    # if letters == number from a=1 b=2 c=3 etc. then get number from wave letter
    wave_numlist = [ord(char) - 96 for char in wave_list]

    # now calculate max year
    # first year of ukhls data is 2009
    maxyr = 2009 + max(wave_numlist)

    return maxyr


def replace_missing_with_na(data, column_list):

    data[column_list] = data[column_list].replace(missing_types, np.nan)

    return data


missing_types = ['-1', '-2', '-7', '-8', '-9', '-10',
                 -1., -2., -7., -8., -9., -10.,
                 -1, -2, -7, -8, -9, -10,
                 '-1.0', '-2.0', '-7.0', '-8.0', '-9.0', '-10.0',
                 "Dont Know", "Refused", "Proxy", "Inapplicable", "Missing"]
