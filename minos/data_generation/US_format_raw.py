#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This file formats Understanding Society variables for using in a microsimulation.
It DOES NOT handle missing data. see US_missing.py.
"""
import pandas as pd
import numpy as np
import os

import US_utils

# TODO there is an issue with the connection between the BHPS and ukhls waves. (see format_time)
""" There seems to be a gap between 2007-2008 where people who were in the old 
study do not transfer to the new one until next year. Need to find out why this is.

This is most likely me missing some variable in the data which would better serve
as a time variable. (e.g. interview year/month).

For now just assume the end of BHPS and start of ukhls occur in the same year.
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
# Sex.
sex_dict = US_utils.load_json(json_source, "sexes.json")
# Ethnicity.
ethnicity_bhps_2002 = US_utils.load_json(json_source, "ethnicity_bhps_2002.json")
ethnicity_bhps_2008 = US_utils.load_json(json_source, "ethnicity_bhps_2008.json")
ethnicity_ukhls = US_utils.load_json(json_source, "ethnicity_ukhls.json")
# Employment.
labour_bhps = US_utils.load_json(json_source, "labour_status_bhps.json")
labour_ukhls = US_utils.load_json(json_source, "labour_status_ukhls.json")
# Education.
education_bhps = US_utils.load_json(json_source, "education_bhps.json")
# Use simplified one for ukhls currently.
# education_ukhls = US_utils.load_json(json_source, "education_ukhls.json")
education_ukhls = US_utils.load_json(json_source, "education_ukhls_simple.json")
# Depression.
depression = US_utils.load_json(json_source, "depression.json")
depression_change = US_utils.load_json(json_source, "depression_change.json")
# Heating.
heating_bhps = US_utils.load_json(json_source, "heating_bhps.json")
heating_ukhls = US_utils.load_json(json_source, "heating_ukhls.json")
# Location
region_dict = US_utils.load_json(json_source, "region.json")


def format_sex(data):
    """ Format sex data.

    Parameters
    ----------
    data : pd.DataFrame
        Data to process genders of.
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
    Returns
    -------
    data : pd.DataFrame
        Data with location formatting.

    """
    # No spatial data yet so does nothing.
    data["MSOA"] = "no_location"
    data["location"] = "no_location"
    data["region"] = data["region"].astype(str).map(region_dict)
    return data


def format_mental_state(data):
    """ Format mental health data.

    Parameters
    ----------
    data : pd.DataFrame
        US data with raw depression columns.

    Returns
    -------
    data : pd.DataFrame
        US data with formatted depression columns.
    """
    # TODO Only using binary values for now. Makes it easier to show off traditional binary models.
    data["depression"] = data["depression"].astype(str).map(depression)
    data["depression_change"] = data["depression_change"].astype(str).map(depression_change)
    return data


def format_academic_year(data):
    """ Format academic year variables.

    Parameters
    ----------
    data : pd.DataFrame
        US data with raw academic year columns.

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
                         "hidp",  # Cross wave household identified
                         "sex",  # Sex.
                         "age",  # Age.
                         "doby",  # Birth Year.
                         "qfachi",  # Highest education
                         # "hiqual_dv",  # Highest education
                         "scghqi",  # GHQ Depression.
                         "hlprbi",  # Clinical Depression.
                         "jbstat",  # Labour status.
                         "jbnssec8_dv",  # NSSEC code.
                         "cduse5",  # fridge/freezer
                         "cduse6",  # washing machine
                         "cduse7",  # tumble dryer
                         "cduse8",  # dishwasher
                         "cduse9",  # microwave oven
                         "gor_dv",  # Government Region Derived.
                         "hsprbk",  # accom: lack of adequate heating
                         "basrate", # basic pay hourly rate
                         "paygu_dv", # usual gross pay per month: current job
                         "jspayg",  # Monthly self employed gross pay
                         "jbhrs",    # no. of hours normally worked in a week
                         "jshrs",   # s/emp: hours normally working per week
                         "paytyp",  # salaried or paid by the hour
                         "paygl",   # gross pay last payment
                         "payg_dv",  # gross pay per month in current job : last payment
                         "paygwc",   # pay period: gross pay
                         "jspayu",  # average income from job/business
                         "jspayw"   # job/business income: pay period (weeks)
                         ]

    column_names = ["pidp",  # pidp
                    "hidp",  # hidp
                    "sex",  # sex
                    "age",  # age
                    "birth_year",  # doby
                    "education_state",  # qfachi. Was hiqual_dv but too much missing.
                    "depression_change",  # scghqi
                    "depression",  # hlprbi
                    "labour_state",  # jbstat
                    "job_sec",  # jbnssec8_dv
                    "fridge_freezer",  # cduse5
                    "washing_machine",  # cduse6
                    "tumble_dryer",  # cduse7
                    "dishwasher",  # cduse8
                    "microwave",  # cduse9
                    "region",  # gor_dv
                    "heating",  # hsprbk
                    "hourly_rate",  # basrate
                    "gross_paypm",  # paygu_dv
                    "gross_pay_se", # jspayg
                    "job_hours",     # jbhrs
                    "job_hours_se",     # jshrs
                    "pay_type",      # paytyp
                    "gross_paylp",  # paygl
                    "gross_ppmlp",   #payg_dv
                    "gross_period",  # paygwc
                    "jb_inc",       # jspayu
                    "jb_inc_per"    #jspayw
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


def format_bhps_education(data):
    """ Format US education data.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame before formatting educations.

    Returns
    -------
    data : pd.DataFrame
        Data after formatting educations.
    """
    # Map education codes to readable strings.
    data["education_state"] = data["education_state"].astype(str).map(education_bhps)
    return data


def format_bhps_employment(data):
    """ Format employment variables.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame to format employment for.

    Returns
    -------
    data : Pd.DataFrame
        Data with formatted education column.
    """
    # Remap job status ints to strings.
    data["labour_state"] = data["labour_state"].astype(str).map(labour_bhps)
    return data


def format_bhps_heating(data):
    """ Format heating variable.

        Parameters
        ----------
        data : pd.DataFrame
            Data frame to format heating for.

        Returns
        -------
        data : Pd.DataFrame
            Data with formatted heating column.
    """
    ## Need to reverse the binary heating variable as it is in the opposite orientation to the corresponding ukhls var
    data["heating"] = data["heating"].fillna(-9)  # have to replace a single NA value before mapping
    data["heating"] = data["heating"].astype(int).astype(str).map(heating_bhps)  # convert to int then string then map
    return data


######################
# ukhls Wave Functions
######################


def format_ukhls_columns(year):
    """ Specify subset of ukhls columns to be used in microsim.

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

    attribute_columns = ["pidp",  # Cross wave personal identifier.
                         "hidp",  # Cross wave household identified
                         "sex",  # Sex.
                         "dvage",  # Age.
                         "doby_dv",  # Birth Year.
                         "racel_dv",  # Ethnicity.
                         "qfhigh_dv",  # Highest Qualification.
                         # "hiqual_dv",  # Highest Qualification.
                         "scghqi",  # GHQ depression.
                         "jbstat",  # job status
                         "jbsic07_cc",  # SIC code for job (if any).
                         "jbnssec8_dv",  # NSSEC socioeconomic code.
                         "cduse5",  # deep freeze or fridge freezer
                         "cduse6",  # washing machine
                         "cduse7",  # tumble dryer
                         "cduse8",  # dishwasher
                         "cduse9",  # microwave oven
                         "hheat",
                         "gor_dv",  # Government Region Derived.
                         "sf12mcs_dv",   # SF-12 Mental Component Summary (PCS)
                         "basrate",  # basic pay hourly rate
                         "paygu_dv",  # usual gross pay per month: current job
                         "seearngrs_dv",  # self employment earnings - gross
                         "jbhrs",  # no. of hours normally worked in a week
                         "jshrs",  # s/emp: hours normally working per week
                         "paytyp",  # salaried or paid by the hour
                         "paygl",   # gross pay last payment
                         "payg_dv",  # gross pay per month in current job : last payment
                         "paygwc",   # pay period: gross pay
                         "jspayu",  # average income from job/business
                         "jspayw"   # job/business income: pay period (weeks)
                         ]
    # New names for the above columns.
    column_names = ["pidp",
                    "hidp",
                    "sex",
                    "age",
                    "birth_year",
                    "ethnicity",
                    "education_state",
                    "depression_change",
                    "labour_state",
                    "job_industry",
                    "job_sec",
                    "fridge_freezer",   # cduse5
                    "washing_machine",  # cduse6
                    "tumble_dryer",  # cduse7
                    "dishwasher",  # cduse8
                    "microwave",  # cduse9
                    "heating",  # hheat
                    "region",  # region
                    "SF-12",   # sf12mcs_dv
                    "hourly_rate",  # basrate
                    "gross_paypm",  # paygu_dv
                    "gross_pay_se",  # seearngrs_dv
                    "job_hours",     # jbhrs
                    "job_hours_se",  # jshrs
                    "pay_type",      # paytyp
                    "gross_paylp",  # paygl
                    "gross_ppmlp",   #payg_dv
                    "gross_period",  # paygwc
                    "jb_inc",       # jspayu
                    "jb_inc_per"    #jspayw
                    ]

    # Variables that change names for ukhls data.
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
    # clinical depression changes in wave 10.
    if year < 2017:
        attribute_columns += ["hcond17"]  # Clinical depression.
        column_names += ["depression"]
    else:
        attribute_columns += ["hcondcode38"]  # Clinical depression.
        column_names += ["depression"]

    # All attributes have a wave dependent suffix apart from identifiersb (pidp, hidp etc.).
    # Adjust attribute_columns as necessary.
    # E.g age -> a_age, age -> b_age ... for waves of ukhls.

    attribute_columns = US_utils.ukhls_wave_prefix(attribute_columns, year)

    return attribute_columns, column_names


def format_ukhls_ethnicity(data):
    """ Format ethnicity variables.


    Parameters
    ----------
    data : pd.DataFrame
        Raw data to format ethnicities of.


    Returns
    -------
    data : pd.DataFrame
        Data with ethnicities formatted.
    """
    # Map ethnicity integers to strings.
    data["ethnicity"] = data["ethnicity"].astype(str).map(ethnicity_ukhls)
    return data


def format_ukhls_education(data):
    """ Format US education data.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame before formatting educations.
    Returns
    -------
    data : pd.DataFrame
        Data after formatting educations.
    """
    # Map education ints to strings.
    data["education_state"] = data["education_state"].astype(str).map(education_ukhls)
    return data


def format_ukhls_employment(data):
    """ Format employment columns for data.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame to format employment for.

    Returns
    -------
    data : Pd.DataFrame
        Which wave of data is being saved.
    """
    # TODO Code moved to US_missing_deterministic. move problem description somewhere too.
    """Correct some incorrectly missing data here.
    Some people are registered as unemployed but are missing job codes.
    Makes them impossible to differentiate with those who are missing for other reasons.
    Hence will assign anyone who is unemployed SIC/SOC/NSSEC code 0.
    0 is undefined in all 3 sets.
    Calculate people who are unemployed (labour state 2) but registered as missing in SIC codes.
    Assign these people 0 value SIC/SOC/NSSEC codes. Also set their job duration to 0.

    There are a lot of potential reasons for this.
    People who transition job status mid year and arent properly recorded.
`       E.g. check pid 274047 this person retires in April 2008.
    They are incorrectly recorded as still employed by Sept. 2008 but have no company data at all.
    They are incorrectly employed and have -8 for SOC/SIC/NSSEC values because they have no company.

    Seems to be a clash between behaviour for the majority of the year and
    current behaviour.
    For now just assume they are unemployed and assign their industries to 0."""

    # Remap job statuses.
    data["labour_state"] = data["labour_state"].astype(str).map(labour_ukhls)
    return data


def format_ukhls_heating(data):
    """ Format heating variable.

        Parameters
        ----------
        data : pd.DataFrame
            Data frame to format heating for.

        Returns
        -------
        data : Pd.DataFrame
            Data with formatted heating column.
    """
    ## Need to reverse the binary heating variable as it is in the opposite orientation to the corresponding ukhls var
    data["heating"] = data["heating"].astype(str).map(heating_ukhls)
    return data


def combine_indresp_hhresp(year, indresp_name, hhresp_name):
    """ Function to collect and merge the indresp and hhresp files for a specific year.

    Parameters
    ----------
    year : int
        The `year` of the wave being processed.
    indresp_name : str
        The name of the indresp file for specific year
    hhresp_name : str
        Name of the hhresp file for specific year
    Returns
    -------
    indresp_hhresp: Pd.DataFrame
        Dataframe containing indresp and hhresp data combined on hid
    """
    # load both indresp and hhresp files
    indresp = US_utils.load_file(indresp_name)
    hhresp = US_utils.load_file(hhresp_name)

    # calculate wave letter based on year, and generate hidp variable name for use as merge key
    wave_letter = US_utils.get_wave_letter(year)
    if year < 2008:
        merge_key = f"b{wave_letter}_hidp"
    else:
        merge_key = f"{wave_letter}_hidp"

    # merge the data on the hipd variable and return
    combined = indresp.merge(right=hhresp, on=merge_key, suffixes=('', '_delme'))
    combined = combined[[c for c in combined.columns if not c.endswith("_delme")]]
    return combined


def format_data(year, data):
    """ Main function for formatting US data. Loads formats and saves each wave sequentially.

    Parameters
    ----------
    year : int
        The `year` of the wave being processed.
    data : Pd.DataFrame
        Pandas DataFrame containing both indresp and hhresp data merged on hidp
    Returns
    -------
    data : Pd.DataFrame
        Returns a formatted dataframe to be saved as csv
    """
    # Load file and take desired subset of columns.
    # data = US_utils.load_file(file_name)
    if year <= 2007:
        attribute_columns, column_names = format_bhps_columns(year)
    else:
        attribute_columns, column_names = format_ukhls_columns(year)
    data = US_utils.subset_data(data, attribute_columns, column_names)

    # Format columns by categories.
    # Categories that are formatted the same regardless of wave.
    data = format_sex(data)
    data = format_academic_year(data)
    data = format_mental_state(data)
    data = format_time(data, year)
    data = format_location(data, year)
    ukhls_heat_skipyrs = [2010, 2012, 2014]

    # Categories that vary for bhps/ukhls waves.
    if year <= 2007:
        data = format_bhps_ethnicity(data, year)
        data = format_bhps_education(data)
        data = format_bhps_employment(data)
        data = format_bhps_heating(data) # no data before 1996.
    elif year > 2007:
        data = format_ukhls_ethnicity(data)
        data = format_ukhls_employment(data)
        data = format_ukhls_education(data)
        #if year not in ukhls_heat_skipyrs:
        data = format_ukhls_heating(data)

    return data


def main(wave_years: list, file_source: str, file_output: str) -> None:
    """ Main file for processing raw US data.

    Parameters
    ----------
    wave_years: list
        What years to process data for. Data goes from 1990-2021 currently.
    file_source, file_output : str
        Where is minos of the raw US data.
        Where should processed data be output to.
        Which section of US data is being used. Usually independent response (indresp).
    """

    # Loop over wave years and format data.
    for year in wave_years:
        # Two types of wave with different naming conventions and variables.
        # The BHPS waves circa 2008 and ukhls waves post 2009 have different classes for processing.

        # Merge the indresp and hhresp files for a particular year then format
        indresp_name = US_utils.US_file_name(year, file_source, "indresp")
        hhresp_name = US_utils.US_file_name(year, file_source, "hhresp")
        indresp_hhresp = combine_indresp_hhresp(year, indresp_name, hhresp_name)

        data = format_data(year, indresp_hhresp)

        # check for and remove any null rows (1 created in bhps due to merge)
        data = data.loc[~data["pidp"].isnull()]

        # Save formatted data
        US_utils.save_file(data, file_output, "", year)


if __name__ == "__main__":
    years = np.arange(1990, 2019)

    source = "/home/luke/Documents/MINOS/UKDA-6614-stata/stata/stata13_se/"
    if os.environ.get("USER") == 'robertclay':
        source = "/Users/robertclay/data/UKDA-6614-stata/stata/stata13_se/"  # different data source depending on user.

    output = "data/raw_US/"
    # section = "indresp"

    main(years, source, output)
