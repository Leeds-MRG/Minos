# -*- coding: utf-8 -*-
""" This file formats Understanding Society variables for using in a microsimulation.
It DOES NOT handle missing data. see US_missing.py.
"""
import pandas as pd
import numpy as np
import argparse

import US_utils

import US_format_raw_children_data

# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None  # default='warn' #supress SettingWithCopyWarning

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
## Sex.
sex_dict = US_utils.load_json(json_source, "sexes.json")
## Ethnicity.
# ethnicity_bhps_2002 = US_utils.load_json(json_source, "ethnicity_bhps_2002.json")
# ethnicity_bhps_2008 = US_utils.load_json(json_source, "ethnicity_bhps_2008.json")
ethnicity_ukhls = US_utils.load_json(json_source, "ethnicity_ukhls.json")
## Employment.
# labour_bhps = US_utils.load_json(json_source, "labour_status_bhps.json")
labour_ukhls = US_utils.load_json(json_source, "labour_status_ukhls.json")
## Education.
# education_bhps = US_utils.load_json(json_source, "education_bhps.json")
# Use simplified one for ukhls currently.
# education_ukhls = US_utils.load_json(json_source, "education_ukhls.json")
# education_ukhls = US_utils.load_json(json_source, "education_ukhls_simple.json")
education = US_utils.load_json(json_source, "education_gov.json")
## Depression.
depression = US_utils.load_json(json_source, "depression.json")
depression_change = US_utils.load_json(json_source, "depression_change.json")
## Heating.
# heating_bhps = US_utils.load_json(json_source, "heating_bhps.json")
heating_ukhls = US_utils.load_json(json_source, "heating_ukhls.json")
## Location
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
    # data["MSOA"] = "no_location"
    # data["location"] = "no_location"
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
    data["time"] = year
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
    # TODO probably worth splitting these by dataset  source. indresp/hhresp etc.
    # Converted these into one dict because its annoying to edit two data frames.
    attribute_dict = {'birthy': "birth_year",  # birth year.
                      'cduse5': 'fridge_freezer',  # has fridge
                      'cduse6': 'washing_machine',  # has washing machine
                      'cduse7': 'tumble_dryer',  # has tumble dryer
                      'cduse8': 'dishwasher',  # has dishwasher
                      'cduse9': 'microwave',  # has microwave
                      'crburg': 'burglaries',  # neighbourhood burglaries
                      'crcar': 'car_crime',  # neighbourhood car crime
                      'crdrnk': 'drunks',  # neighbourhood drunks
                      'crmugg': 'muggings',  # neighbourhood muggings
                      'crrace': 'racial_abuse',  # neighbourhood racial abuse
                      'crteen': 'teenagers',  # neighbourhood teenager issues
                      'crvand': 'vandalism',  # neighbourhood vandalism issues
                      'ctband_dv': 'council_tax',  # council tax derived.
                      'dvage': 'age',  # age derived.
                      'fihhmnnet1_dv': 'hh_netinc',  # household net income derived
                      'gor_dv': 'region',  # government region
                      'hheat': 'heating',  # household heating
                      'hidp': 'hidp',  # household id
                      'ieqmoecd_dv': 'oecd_equiv',  # Modified OECD equivalence scale
                      'intdatem': 'hh_int_m',  # household interview month
                      'intdatey': 'hh_int_y',  # household interview year
                      'jbbgm': 'job_duration_m',  # what month started job.
                      'jbbgy': 'job_duration_y',  # what year started job
                      'jbft_dv': 'emp_type',  # part or full time employment
                      'jbnssec8_dv': 'job_sec',  # job nssec code
                      'jbsic07_cc': 'job_industry',  # Standard Industry SIC 2007 codes.
                      # Note SIC/SOC are updated every decade but have been consistently mapped for all 13 waves.
                      'jbsoc10_cc': 'job_occupation',  # Standard Occupation SOC 2010 codes.
                      'jbstat': 'labour_state_raw',  # labour state
                      'ncigs': 'ncigs',  # typical daily cigarettes smoked.
                      # TODO no ncigs data for waves 1, 3, 4. There is 'smofrq' variable for 3 and 4 but uses binned ordinal values.
                      #  not really applicable without random generation.
                      'pidp': 'pidp',  # personal identifier
                      'qfhigh_dv': 'education_state',  # highest education state
                      'nqfhigh_dv': 'newest_education_state', # has any new qualification been achieved.
                      # TODO another ethnicity var seems to have fewer missing? https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ethn_dv
                      'racel_dv': 'ethnicity',  # ethnicity derived.
                      'rentgrs_dv': 'hh_rent',  # household monthly rent.
                      #'scghqi': 'depression_change',  # depression change GHQ.
                      'sclonely': 'loneliness',  # is lonely.
                      # sclonely only available in waves 9-11. scsf7 may be a good substitute.
                      'sex': 'sex',  # biological sex.
                      'sf12mcs_dv': 'SF_12',  # SF12 mental component summary
                      'sf12pcs_dv': 'SF_12p',  # SF12 physical component summary
                      'smoker': 'smoker',  # Currently smokes.
                      # TODO waves present roughly matches ncigs. no data for waves 1-5.
                      # for waves 2 and 5 similar variable 'smnow' could be used.
                      'xpmg_dv': 'hh_mortgage',  # household monthly mortgage payments.
                      'xpaltob_g3': "alcohol_spending",  # monthly household spending on alcohol.
                      ## ---------------------
                      ## Weight variables
                      'indscus_xw': "weight1",  # Cross-sectional analysis weight (wave 1)
                      'indscub_xw': "weight2_5",  # Cross-sectional analysis weight (waves 2-5)
                      'indscui_xw': "weight6p",  # Cross-sectional analysis weight (waves 6+)
                      ## ---------------------
                      ## All variables relating to number of children
                      'nkids_dv': 'nkids',  # number of children in household
                      'lnprnt': 'nkids_ind_raw',  # number of children ever had by individual at first interview
                      'preg': 'nkids_ind_new',  # whether had a child (actually a pregnancy) since last interview
                      ## ---------------------
                      'ypdklm': 'ndrinks',  # last month number of drinks. audit scores probably better.
                      'xpelecy': 'yearly_electric',  # yearly electricty expenditure
                      'xpgasy': 'yearly_gas',  # yearly gas expenditure
                      'xpduely': 'yearly_gas_electric',  # yearly both expenditure.
                      'xpoily': 'yearly_oil',  # yearly oil expenditure.
                      'xpsfly': 'yearly_other_fuel',  # yearly other fuel (wood?)
                      'fuelhave1': 'has_electric',  # spends money on electrictiy
                      'fuelhave2': 'has_gas',  # spends money on gas
                      'fuelhave3': 'has_oil',  # spends money on oil
                      'fuelhave4': 'has_other',  # has some other fuel source.
                      'fuelhave96': 'has_none',  # has no fuel source.
                      'fuelduel': 'gas_electric_combined', # are gas and electric bills separate or combined?
                       # Nutrition vars
                       'wkfruit': 'fruit_days', # number of days respondent eats fruit per week
                       'fruitamt':'fruit_per_day', # amount of fruit eaten on days when eating fruit
                       'wkvege': 'veg_days', # no. days respondent eats veg per week
                       'vegeamt': 'veg_per_day', # amt. veg eaten on veg eating days
                       # hourly wage stuff (Keeping self-employed and small business vars just in case)
                       'basrate': 'hourly_rate',  # basic pay hourly rate
                       'paygu_dv': 'gross_paypm',  # usual gross pay per month: current job
                       'jspayg': 'gross_pay_se',  # Monthly self-employed gross pay
                       'jbhrs': 'job_hours',  # no. of hours normally worked in a week
                       'jshrs': 'job_hours_se',  # s/emp: hours normally worked in a week
                       'jspayu': 'job_inc',  # average income from job/business
                       'jspayw': 'jb_inc_per',  # job/business income: pay period (weeks)
                       # Private/Public sector var for living wage intervention
                       'jbsect': 'job_sector',  # Whether employee of private or non-private organisation
                      # SF12 MICE vars
                      'rentinc2': 'energy_in_rent',  # is it combined into rent?
                      'xphsdba': 'behind_on_bills',  # behind on energy bills?
                      'finnow': 'financial_situation',  # financial situation
                      'finfut': 'future_financial_situation',  # expected near future financial situation.
                      'lkmove': "likely_move",  # likelihood of moving house
                      'scghqi': 'ghq_depression',  # ghq depression
                      'scghql': 'ghq_happiness',  # ghq general happiness
                      # 'sf1': 'sf1', # sf1 score
                      'hcondn17': 'clinical_depression',  # has clinical depression.
                      'scsf1': 'scsf1',  # sf1 score including proxy surveys
                      'scsf2a': 'phealth_limits_modact',  # physical health limits moderate activities
                      'scsf2b': 'phealth_limits_stairs',  # physical health limits several flights of stairs
                      'scsf3a': 'S7_physical_health',  # physical health limits work.
                      'scsf3b': 'phealth_limits_work_type',  # physical health limits kind of work
                      'scsf4a': 'S7_mental_health',  # mental health limits work.
                      'scsf5': 'pain_interfere_work',  # pain interfered with work
                      'scsf7': 'health_limits_social',  # health limits social life.
                      'hhtype_dv': 'hh_composition',  # household composition
                      'mastat_dv': 'marstat',  # marital status
                      'hhsize': 'hhsize', # number of people in household
                      'tenure_dv': 'housing_tenure', # housing tenure type (owned, rented etc.)
                      'urban_dv': 'urban', # urban or rural household.
                      # There are dozens of benefits variables in US this seems like
                      # the simplest and most complete for our purposes.
                      'benbase4': 'universal_credit',
                      # receives core benefits (I.E. universal credit/means tested benefits).
                      }

    # Some variables change names halfway through UKHLS.
    # Assign different keys to variable names depending on year.

    # clinical depression changes in wave 10.
    if year < 2017:
        attribute_dict["hcond17"] = "depression"
    else:
        attribute_dict["hcondcode38"] = "depression"

    # All attributes have a wave dependent suffix apart from identifiersb (pidp, hidp etc.).
    # Adjust attribute_columns as necessary.
    # E.g age -> a_age, age -> b_age ... for waves of ukhls.
    attribute_columns = list(attribute_dict.keys())
    attribute_columns = US_utils.wave_prefix(attribute_columns, year)

    # Attribute names are consistent over all waves.
    # Future work may give these prefixes as well for flat (opposed to tall) data structure.
    column_names = list(attribute_dict.values())
    return attribute_columns, column_names


def format_council_tax(data):
    """Format any council tax data for calculation of monthly overheads."""


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

    See following for the levels and associated numeric codes:
    - None of the above : 0
    - Other School Certification : 1
    - GCSE/O level : 2
    - Standard/o/lower : 2
    - CSE : 2
    - AS level : 3
    - A level : 3
    - International Baccalaureate : 3
    - Welsh Baccalaureate : 3
    - Scottish Highers : 3
    - Cert 6th year studies : 3
    - Nursing/other med qual : 5
    - Diploma in HE : 5
    - Teaching qual not PGCE : 6
    - 1st Degree or equivalent : 6
    - Higher degree : 7
    - Other higher degree : 7

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
    who_new_education = data.loc[~data['newest_education_state'].isin(US_utils.missing_types)].index
    data.loc[who_new_education, 'education_state'] = data.loc[who_new_education, 'newest_education_state']
    data["education_state"] = data["education_state"].astype(str).map(education)
    #print(data['education_state'].value_counts())
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
    data["labour_state_raw"] = data["labour_state_raw"].astype(str).map(labour_ukhls)
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


def format_analysis_weight(data, year):
    """
    Add and format analysis weight variable.
    Combining the three weight variables that cover different waves into one.

    Parameters
    ----------
    data : pd.DataFrame
        Data frame to add weight to.

    Returns
    -------
    data : Pd.DataFrame
        Data with formatted weight column.
    """
    data['weight'] = -9
    if year == 2009:
        data['weight'] = data['weight1']
    if year in range(2010, 2014):
        data['weight'] = data['weight2_5']
    if year > 2013:
        data['weight'] = data['weight6p']

    # can now drop all three columns as this is done yearly
    # drop cols we don't need
    data.drop(labels=['weight1', 'weight2_5', 'weight6p'],
              axis=1,
              inplace=True)
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
    if year < 2009:
        merge_key = f"b{wave_letter}_hidp"
    else:
        merge_key = f"{wave_letter}_hidp"

    # merge the data on the hidp variable and return combined dataframe.
    # Code here prevents duplicate columns that occur in both datasets. 44444
    # combined = indresp.merge(right=hhresp, on=merge_key, suffixes=('', '_delme'))
    combined = indresp.merge(right=hhresp, how='left', on=merge_key, suffixes=('', '_delme'))  # HR 444
    combined = combined[[c for c in combined.columns if not c.endswith("_delme")]]
    return combined


def format_data(year, data, verbose):
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
    attribute_columns, column_names = format_ukhls_columns(year)
    data = US_utils.subset_data(data, attribute_columns, column_names, verbose)

    # Format columns by categories.
    # Categories that are formatted the same regardless of wave.
    data = format_sex(data)
    data = format_academic_year(data)
    #data = format_mental_state(data)
    data = format_time(data, year)
    data = format_location(data, year)

    data = format_ukhls_ethnicity(data)
    data = format_ukhls_employment(data)
    data = format_ukhls_education(data)
    data = format_ukhls_heating(data)

    #if year == 2014 or year == 2020: #only adding these child age chains to input data years for now.
    if year >= 2014:
        data = US_format_raw_children_data.main(data, year)
    data = format_analysis_weight(data, year)

    return data


def main(wave_years: list, file_source: str, verbose: bool, file_output: str) -> None:
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

        data = format_data(year, indresp_hhresp, verbose)

        # check for and remove any null rows (1 created in bhps due to merge)
        data = data.loc[~data["pidp"].isnull()]

        # Save formatted data
        US_utils.save_file(data, file_output, "", year)


if __name__ == "__main__":

    maxyr = US_utils.get_data_maxyr()
    years = np.arange(1991, maxyr)  # need bhps for locf imputation. only keep years 2009-2021.

    # Take source from command line args (or most likely from Makefile variable)
    parser = argparse.ArgumentParser(description="Raw Data formatting from Understanding Society")
    parser.add_argument("-s", "--source_dir", required=True, type=str,
                        help="The source directory for Understanding Society data.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Enable verbose output.")
    args = parser.parse_args()

    # Get source from args
    source = args.source_dir
    verbose = args.verbose
    # source = "/Users/robertclay/UKDA-6614-stata/stata/stata13_se/" # hardcoded source for debugging.
    output = "data/raw_US/"

    main(years, source, verbose, output)
