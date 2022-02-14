#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This file formats Understanding Society variables for using in a microsimulation.
It DOES NOT handle missing data. see US_missing.py.
"""
import pandas as pd  # You know.
import numpy as np  # You know.
import data.US_utils as US_utils  # Utility functions for US. loading/saving data etc.
import os

# TODO there is an issue with the connection between the BHPS and UKLHS waves. (see format_time)
""" There seems to be a gap between 2007-2008 where people who were in the old 
study do not transfer to the new one until next year. Need to find out why this is.

This is most likely me missing some variable in the data which would better serve
as a time variable. (e.g. interview year/month).

For now just assume the end of BHPS and start of UKLHS occur in the same year.
Record years by the END date. The first wave is SEP 90 - SEP 91 so is recorded as 
1991_US_Cohort.csv. 
"""

"""
Load persistent JSON data dictionaries for US. These are data dictionaries that simplify categorical variables
from integers to strings for easier readability. Its easier to see white british, black-african than digits 1, 5.

These dictionaries also simplify some variables for use in a microsim. 
E.g. education state has a large number of equivalent qualifications (O-Level, GCSE, CSE, etc.) compressed into one.
While this destroys some detail it makes it much easier to make transition models particularly for rare items.

NOTE there are some time dependent dictionaries here. BHPS changes formatting in 2002 for ethnicity so there are 
two ethnicity dictionaries to reflect that. The time prefix indicates when the change takes place or the end of the 
dataset (2008 for BHPS).
"""

# Where are all persistent files for US data. E.g. int to string variable encodings.
json_source = "persistent_data/JSON/"
# Sex dict.
sex_dict = US_utils.load_json(json_source, "sexes.json")
# Ethnicity dicts.
ethnicity_bhps_2002 = US_utils.load_json(json_source, "ethnicity_bhps_2002.json")
ethnicity_bhps_2008 = US_utils.load_json(json_source, "ethnicity_bhps_2008.json")
ethnicity_uklhs = US_utils.load_json(json_source, "ethnicity_uklhs.json")
# Employment.
labour_status_bhps = US_utils.load_json(json_source, "labour_status_bhps.json")
labour_status_uklhs = US_utils.load_json(json_source, "labour_status_uklhs.json")
# Education.
education_bhps = US_utils.load_json(json_source, "education_bhps.json")
# Use simplified one for uklhs currently.
# education_uklhs = US_utils.load_json(json_source, "education_uklhs.json")
education_uklhs = US_utils.load_json(json_source, "education_uklhs_simple.json")
# depression
depression_dict = US_utils.load_json(json_source, "depression.json")

def format_sex(data, year):
    """ Format sex data.

    Parameters
    ----------
    data : pd.DataFrame
        Data to process genders of.
    year : int
        The year of the wave being processed.
    Returns
    -------
    data : pd.DataFrame
        Data with processed genders.

    """
    # Remap sex data from ints to strings. Easier to interpret.
    data["sex"] = data["sex"].astype(str).map(sex_dict)
    return data


def format_location(data, year):
    """ Format any spatial data. Does nothing yet.

    Parameters
    ----------
    data : pd.DataFrame
        Data before location formatting.
    year : int
        The year of the wave being processed.
    Returns
    -------
    data : pd.DataFrame
        Data with location formatting.

    """
    # No spatial data yet so does nothing.
    data["MSOA"] = "no_location"
    data["location"] = "no_location"
    return data


def format_mental_state(data, year):
    """ Format mental health data.

    Parameters
    ----------
    data : pd.DataFrame
        US data with raw depression columns.
    year : int
        The year of the wave being processed.

    Returns
    -------
    data : pd.DataFrame
        US data with formatted depression columns.
    """
    # TODO Only using binary values for now. Makes it easier to show off traditional binary models.
    data["ethnicity"].astype(str).map(depression_dict)
    return data


def format_academic_year(data, year):
    """ Format academic year variables.

    Parameters
    ----------
    data : pd.DataFrame
        US data with raw academic year columns.
    year : int
        The `year` of the wave being processed.

    Returns
    -------
    data: pd.DataFrame
        The data frame with the academic year column added.

    """
    # If someone is 15 years old force them to be born after september.
    # They have to be in the graduating GCSE academic year.
    # No other birth months can be inferred.
    # I thought about using the interview month as well but it doesnt really help.
    # Can be combined with birth_year to determine if their birthday is before/after the interview.
    # Pretty sure it academic year cannot be fully derived from this.
    # TODO I dont have special access to birth month data. Give random months as a stop gap.
    data["birth_month"] = 0
    new_months = data.loc[data["age"] == 15, "birth_month"].apply(lambda x: np.random.randint(9, 13))
    data.loc[data["age"] == 15, "birth_month"] = new_months
    new_months = data.loc[data["age"] > 15, "birth_month"].apply(lambda x: np.random.randint(1, 13))
    data.loc[data["age"] > 15, "birth_month"] = new_months

    data["academic_year"] = data["birth_year"]
    # Everyone born before September is bumped down to the previous academic year.
    data.loc[data["birth_month"] < 9, "academic_year"] -= 1
    return data


def format_time(data, year):
    """Format any time variables in US.

    Parameters
    ----------
    data : pd.DataFrame
        Data without time formatting.
    year : int
        The `year` of the wave being processed.

    Returns
    -------
    data : pd.DataFrame
        Data with time formatting.
    """
    # See to do messages at the top of the file.
    # Theres some wierd overlap in the pidp data. Theres essentially a gap in September 2008 with noone in it from
    # BHPS which makes transition models fail.
    # Following 2 lines are a stupid work around.
    # if self.year <= 2008:
    #    self.year += 1
    data["time"] = year
    return data


##########################
# BHPS specific functions.
##########################

def format_bhps_columns(year):
    """ Get BHPS literal and formatted column names.

    Parameters
    ----------
    year : int
        The year of the wave being processed.
    Returns
    -------
    attribute_columns, column_names : str
        The literal attribute_columns names used from BHPS data. (ba_age, ba_qfachi...)
        Corresponding cleaner column_names for use in a microsim. (age, education_state...)
    """
    # consistent column names accross all waves
    attribute_columns = ["pidp",  # Cross wave identifier
                         "sex",  # Sex.
                         "age",  # Age.
                         "doby",  # Birth Year.
                         "qfachi",  # Highest education
                         # "hiqual_dv",  # Highest education
                         "scghqi",  # Depression.
                         "jbstat",  # Labour status.
                         "jbnssec8_dv",  # NSSEC code.
                         ]

    column_names = ["pidp",
                    "sex",
                    "age",
                    "birth_year",
                    "education_state",
                    "depression_state",
                    "labour_state",
                    "job_sec",
                    ]

    # Variables that change names over dataset.
    # First up is job duration. Changes names in wave 6,
    if year < 1996:
        attribute_columns += ["cjsbgm", "cjsbgy"]  # Month and year when current employment started.
        column_names += ["job_duration_m", "job_duration_y"]
    else:
        attribute_columns += ["cjsbgm", "cjsbgy4"]  # Month and year when current employment started.
        column_names += ["job_duration_m", "job_duration_y"]

    # Name of SIC code variable changes for some reason half way through.
    if year >= 2001:
        attribute_columns += ["jbsic92"]  # SIC 92 codes
        column_names += ["job_industry"]
    else:
        attribute_columns += ["jbsic"]  # SIC 92 codes.
        column_names += ["job_industry"]

    # Name change for race as well.
    if year <= 2001:
        attribute_columns += ["race"]
        column_names += ["ethnicity"]  # Ethnicity.
    elif year > 2001:
        attribute_columns += ["racel_bh"]
        column_names += ["ethnicity"]  # Ethnicity.

    # SOC codes updated every decade.
    if year < 2000:
        attribute_columns += ["jbsoc90_cc"]
        column_names += ["job_occupation"]  # Occupation code.
    else:
        attribute_columns += ["jbsoc00_cc"]
        column_names += ["job_occupation"]  # Occupation code.

    # Add wave specific letters of BHPS variable names.
    # Do not add letters to cross wave variables (IDs).
    # The format here is ba_sex for wave 1, bb_sex for wave 2 and so on..
    # pidp stays the same for all waves.
    attribute_columns = US_utils.bhps_wave_prefix(attribute_columns, year)

    return attribute_columns, column_names


def format_bhps_ethnicity(data, year):
    """ Format ethnicities for BHPS data.

    Parameters
    ----------
    data : pd.DataFrame
        Raw data to format ethnicities of.
    year : int
        The year of the wave being processed.
    Returns
    -------
    data : pd.DataFrame
        Data with ethnicities formatted.
    """

    # Mapping changes in 2002 as categories expanded.
    if year > 2001:
        eth_dict = ethnicity_bhps_2008
    else:
        eth_dict = ethnicity_bhps_2002
    # Map ethnicity int codes to strings.
    data["ethnicity"] = data["ethnicity"].astype(str).map(eth_dict)
    return data


def format_bhps_education(data, year):
    """ Format US education data.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame before formatting educations.
    year : int
        The `year` of the wave being processed.

    Returns
    -------
    data : pd.DataFrame
        Data after formatting educations.
    """
    education_dict = education_bhps
    # Map education codes to readable strings.
    data["education_state"] = data["education_state"].astype(str).map(education_dict)
    return data


def format_bhps_employment(data, year):
    """ Format employment variables.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame to format employment for.
    year : int
        The year of the wave being processed.

    Returns
    -------
    data : Pd.DataFrame
        Data with formatted education column.
    """
    # TODO this is a mess.
    """Correct some incorrectly missing data here.
    Some people are registered as unemployed but are missing job codes.
    Makes them impossible to differentiate with those who are missing for other reasons.
    Hence will assign anyone who is unemployed SIC/SOC/NSSEC code 0.
    0 is undefined in all 3 sets.
    """
    # Calculate people who are unemployed (labour state 2) but registered as missing in SIC codes.
    # Assign these people 0 value SIC/SOC/NSSEC codes. Also set their job duration to 0.
    #na_soc_index = data["job_industry"].isin([-1, -2, -7, -8, -9])
    #unemployed_index = ~data["labour_state"].isin([2])
    #missing_because_unemployed = na_soc_index & unemployed_index
    #mbe_index = missing_because_unemployed.loc[missing_because_unemployed is True].index
    #job_columns = ["job_industry", "job_occupation", "job_sec",
    #               "job_duration_m", "job_duration_y"]
    #data.loc[mbe_index, job_columns] = 0

    # TODO Format not missing at random (NMAR) job rows. I.E. missing for a specific reason.
    # TODO move this to missing data correction.
    """
    There are a lot of potential reasons for this.
    People who transition job status mid year and arent properly recorded.
`       E.g. check pid 274047 this person retires in April 2008.
    They are incorrectly recorded as still employed by Sept. 2008 but have no company data at all.
    They are incorrectly employed and have -8 for SOC/SIC/NSSEC values because they have no company.

    Seems to be a clash between behaviour for the majority of the year and
    current behaviour.
    For now just assume they are unemployed and assign their industries to 0."""

    # Whos job data is totally NA. Assign them unemployed and no job industry.
    #who_falsely_employed = data.loc[np.sum(data[job_columns] == np.nan, 1) == 3].index
    #data.loc[who_falsely_employed, job_columns] = 0
    #data.loc[who_falsely_employed, "labour_state"] = 3

    """There are other nmar states that could be correct such as 
    students with part time jobs incorrectly registering as FT employed.
    Also have the disabled/retired to consider."""

    # Remap job status ints to strings.
    labour_state_dict = labour_status_bhps
    data["labour_state"] = data["labour_state"].astype(str).map(labour_state_dict)
    return data


######################
# UKLHS Wave Functions
######################


def format_uklhs_columns(year):
    """ Specify subset of UKLHS columns to be used in microsim.

    Parameters
    ----------
    year : int
        The year of the wave being processed.

    Returns
    -------
    attribute_columns, column_names: str
        The attribute_columns names directly from US data. Which columns will be extracted.
        The simplified column_names that are used in the microsim.
    """

    attribute_columns = ["pidp",  # Cross wave identifier.
                         "sex",  # Sex.
                         "dvage",  # Age.
                         "doby_dv",  # Birth Year.
                         "racel_dv",  # Ethnicity.
                         "qfhigh_dv",  # Highest Qualification.
                         # "hiqual_dv",  # Highest Qualification.
                         "scghqi",  # GHQ depression.
                         "jbstat",  # job status
                         "jbsic07_cc",  # SIC code for job (if any).
                         "jbnssec8_dv"  # NSSEC socioeconomic code.
                         ]
    # New names for the above columns.
    column_names = ["pidp",
                    "sex",
                    "age",
                    "birth_year",
                    "ethnicity",
                    "education_state",
                    "depression_state",
                    "labour_state",
                    "job_industry",
                    "job_sec"
                    ]

    # Variables that change names for UKLHS data.
    # Attributes for job duration.
    # First wave of employment attribute names are different.
    # 7th wave also changes names.
    if year < 2009:
        attribute_columns += ["jbbgm", "jbbgy"]  # What month and year did current employment start.
        column_names += ["job_duration_m", "job_duration_y"]
    elif year < 2014:
        attribute_columns += ["jbbgdatm", "jbbgdaty"]  # What month and year did current employment start.
        column_names += ["job_duration_m", "job_duration_y"]
    else:
        attribute_columns += ["jbbgm", "jbbgy"]  # What month and year did current employment start.
        column_names += ["job_duration_m", "job_duration_y"]

    # SOC codes updated every decade.
    if year < 2010:
        attribute_columns += ["jbsoc00_cc"]
        column_names += ["job_occupation"]
    else:
        attribute_columns += ["jbsoc10_cc"]
        column_names += ["job_occupation"]

    # All attributes have a wave dependent suffix apart from identifiersb (pidp, hidp etc.).
    # Adjust attribute_columns as necessary.
    # E.g age -> a_age, age -> b_age ... for waves of UKLHS.

    attribute_columns = US_utils.uklhs_wave_prefix(attribute_columns, year)

    return attribute_columns, column_names


def format_uklhs_ethnicity(data, year):
    """ Format ethnicity variables.


    Parameters
    ----------
    data : pd.DataFrame
        Raw data to format ethnicities of.
    year : int
        The year of the wave being processed.

    Returns
    -------
    data : pd.DataFrame
        Data with ethnicities formatted.
    """
    # Map ethnicity integers to strings.
    data["ethnicity"] = data["ethnicity"].astype(str).map(ethnicity_uklhs)
    return data


def format_uklhs_education(data, year):
    """ Format US education data.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame before formatting educations.
    year : int
        The year of the wave being processed.
    Returns
    -------
    data : pd.DataFrame
        Data after formatting educations.
    """
    # Map education ints to strings.
    data["education_state"] = data["education_state"].astype(str).map(education_uklhs)
    return data


def format_uklhs_employment(data, year):
    """ Format employment columns for data.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame to format employment for.
    year : int
        The year of the wave being processed.

    Returns
    -------
    data : Pd.DataFrame
        Which wave of data is being saved.
    """
    # TODO this is a mess.
    # TODO Format not missing at random (NMAR) job rows. I.E. missing for a specific reason. Move to missing data.

    """Correct some incorrectly missing data here.
    Some people are registered as unemployed but are missing job codes.
    Makes them impossible to differentiate with those who are missing for other reasons.
    Hence will assign anyone who is unemployed SIC/SOC/NSSEC code 0.
    0 is undefined in all 3 sets.
    Calculate people who are unemployed (labour state 2) but registered as missing in SIC codes.
    Assign these people 0 value SIC/SOC/NSSEC codes. Also set their job duration to 0.
    """
    #na_soc_index = data["job_industry"].isin([-1, -2, -7, -8, -9])
    #unemployed_index = ~data["labour_state"].isin([2])
    #missing_because_unemployed = na_soc_index & unemployed_index
    #mbe_index = missing_because_unemployed.loc[missing_because_unemployed is True].index
    #job_columns = ["job_industry", "job_occupation", "job_sec", "job_duration_m", "job_duration_y"]
    #data.loc[mbe_index, job_columns] = 0

    """
    There are a lot of potential reasons for this.
    People who transition job status mid year and arent properly recorded.
`       E.g. check pid 274047 this person retires in April 2008.
    They are incorrectly recorded as still employed by Sept. 2008 but have no company data at all.
    They are incorrectly employed and have -8 for SOC/SIC/NSSEC values because they have no company.

    Seems to be a clash between behaviour for the majority of the year and
    current behaviour.
    For now just assume they are unemployed and assign their industries to 0."""

    # Whos job data is totally NA. Assign them unemployed and no job industry.
    #who_falsely_employed = data.loc[np.sum(data[job_columns] == np.nan, 1) == 3].index
    #data.loc[who_falsely_employed, job_columns] = 0
    #data.loc[who_falsely_employed, "labour_state"] = 3

    # Remap job statuses.
    labour_state_dict = labour_status_uklhs
    data["labour_state"] = data["labour_state"].astype(str).map(labour_state_dict)
    return data


def format_data(year, file_name):
    """ Main function for formatting US data. Loads formats and saves each wave sequentially.

    Parameters
    ----------
    year : int
        The `year` of the wave being processed.
    file_name : str
        What is the path of the raw US data file to be processed. e.g. "path/ba_indresp.dta")
    Returns
    -------
    None
    """
    # Load file and take desired subset of columns.
    data = US_utils.load_file(file_name)
    if year <= 2007:
        attribute_columns, column_names = format_bhps_columns(year)
    else:
        attribute_columns, column_names = format_uklhs_columns(year)
    data = US_utils.subset_data(data, attribute_columns, column_names)

    # Format columns by categories.
    # Categories that are formatted the same regardless of wave.
    data = format_sex(data, year)
    data = format_academic_year(data, year)
    data = format_mental_state(data, year)
    data = format_time(data, year)

    # Categories that vary for bhps/uklhs waves.
    if year <= 2007:
        data = format_bhps_ethnicity(data, year)
        data = format_bhps_employment(data, year)
        data = format_bhps_education(data, year)
    elif year > 2007:
        data = format_uklhs_ethnicity(data, year)
        data = format_uklhs_employment(data, year)
        data = format_uklhs_education(data, year)
    return data


def main(wave_years: list, file_source: str, file_output: str, file_section: str) -> None:
    """ Main file for processing raw US data.

    Parameters
    ----------
    wave_years: list
        What years to process data for. Data goes from 1990-2021 currently.
    file_source, file_output, file_section: str
        Where is source of the raw US data.
        Where should processed data be output to.
        Which section of US data is being used. Usually independent response (indresp).
    """

    # Loop over wave years and format data.
    for year in wave_years:
        # Two types of wave with different naming conventions and variables.
        # The BHPS waves circa 2008 and UKLHS waves post 2009 have different classes for processing.
        file_name = US_utils.US_file_name(year, file_source, file_section)
        data = format_data(year, file_name)
        # Save formatted data
        US_utils.save_file(data, file_output, "", year)


if __name__ == "__main__":
    years = np.arange(1990, 2019)
    source = "/home/luke/Documents/MINOS/UKDA-6614-stata/stata/stata13_se/"
    output = "data/raw_US/"
    section = "indresp"
    os.mkdir(output)
    main(years, source, output, section)
