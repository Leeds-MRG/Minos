#!/usr/bin/env python3
import pandas as pd
import numpy as np
import datetime
from utils import get_age_bucket

def compare_estimates(simulation_data, ONS_data, location, n_years, previous_year_comparison = False, starting_year = 2011):
    '''Function that compares the outputs of the simulation with the estimates from
    the ONS. Total values are compared.
 Parameters
    ----------
    simulation_data_LAD : Dataframe
        Input data from the VPH simulation
    ONS_data : Dataframe
        Summary estimates from the ONS existing in the persistent data
    location: str
        LAD code for place to run the simulation
    n_years: int
        Number of years the simulation was ran for
    previous_year_comparison: bool
        In case we only want to compare the last year data
    starting_year: int
        Starting year of the simulation
    Returns:
        A dataframe with the comparison between the ONS and simulation data

    '''


    #allow division by 0
    np.seterr(divide='ignore', invalid='ignore')

    # make sure the variables are a datetime object for easier manipulation
    simulation_data['entrance_time'] = pd.to_datetime(simulation_data['entrance_time'], format="%Y-%m-%d %H:%M:%S")
    simulation_data['exit_time'] = pd.to_datetime(simulation_data['exit_time'], format="%Y-%m-%d %H:%M:%S")
    simulation_data['last_outmigration_time'] = pd.to_datetime(simulation_data['last_outmigration_time'], format="%Y-%m-%d %H:%M:%S")

    # select data from the input location
    ONS_data_LAD = ONS_data[ONS_data['ladcode20'] == location]
    simulation_data_LAD = simulation_data[simulation_data['location'] == location]

    # columns from the ONS_data that we are interested about
    columns = ['population','births','deaths','internal_in' ,'internal_out',  'international_in',
               'international_out']

    # list of years to compare
    years = [(starting_year+year) for year in range(1, n_years + 1)]

    # using data get the starting  and finishing time (min and max time)
    min_time = simulation_data_LAD['entrance_time'].min()
    total_max_time = simulation_data_LAD['entrance_time'].max()

    # calculate the max time base on adding the number of years the simulation run
    max_time = min_time + datetime.timedelta(days=365.25*n_years)

    # if the total_max_time is larger than the max_time calculated, assing this total_max time as the max time
    # (this can happen because we are running in 30 days bins and a 2 year simulation run might over run slighly)
    if (total_max_time > max_time) and (total_max_time - max_time) < datetime.timedelta(days=30):
        max_time = total_max_time

    # if we wan to compare data from the last year
    if previous_year_comparison:
        min_time = max_time - datetime.timedelta(days=365.25)
        years = [years[-1]]



    # look though years and variables to compare the ONS values and sumulated data
    total_values = {}

    total_values["location"] = location
    total_values["year"] = starting_year + n_years
    for col in columns:
        if col == 'population':
            continue
        count = 0
        for y in years:
            column_name = col + "_" + str(y)

            # cumulative sum the results for every relevant year
            count = count + ONS_data_LAD[column_name].sum()

        total_values["ONS_total_"+col] = count

    # the total population is total in evey year, so only choose the last year we are interested about
    total_values["ONS_total_population"] = ONS_data_LAD["population_" + str(starting_year + n_years)].sum()


    # get the summary stats from the simulation in a selected time perios
    total_values["simulation_population"] = len(simulation_data_LAD[simulation_data_LAD['alive'] == 'alive'])
    total_values["simulation_deaths"] = len(simulation_data_LAD[(simulation_data_LAD['alive'] == 'dead') & (simulation_data_LAD['exit_time'] > min_time) & (simulation_data_LAD['exit_time'] <= max_time)])
    total_values["simulation_international_out"] = len(simulation_data_LAD[(simulation_data_LAD['alive'] == 'emigrated') & (simulation_data_LAD['exit_time'] > min_time) & (simulation_data_LAD['exit_time'] <= max_time)])
    total_values["simulation_international_in"] = len(simulation_data_LAD[(simulation_data_LAD['immigrated'].astype(str) == 'Yes') & (simulation_data_LAD['entrance_time'] > min_time) & (simulation_data_LAD['entrance_time'] <= max_time)])
    total_values["simulation_internal_out"] = len(simulation_data[(simulation_data['internal_outmigration'] == 'Yes') & (simulation_data['last_outmigration_time'] > min_time) & (simulation_data['last_outmigration_time'] <= max_time)])
    total_values["simulation_births"] = len(simulation_data_LAD[(simulation_data_LAD['parent_id'] != -1) & (simulation_data_LAD['entrance_time'] > min_time) & (simulation_data_LAD['entrance_time'] <= max_time)])
    total_values["simulation_internal_in"] = len(simulation_data_LAD[simulation_data_LAD['internal_migration_in'] == 'Yes'])

    for col in columns:
        # get difference (absolute values and %) between ONS and simulation
        total_values["ONS_simulation_"+col+"_diff"] = total_values["simulation_"+col] - total_values["ONS_total_"+col]
        total_values["ONS_simulation_"+col+"_diff_%"] = \
            (total_values["simulation_"+col] - total_values["ONS_total_"+col])/float(total_values["ONS_total_"+col])*100

        # print some of the values and its comparisons
        print (col, "simulation: ", total_values["simulation_"+col],", ONS estimation ", total_values["ONS_total_"+col])
        print (col, "diff: ", round(total_values["ONS_simulation_"+col+"_diff"],2),"(",round(total_values["ONS_simulation_"+col+"_diff_%"],1),"%)")
        print ()

    # add the age range and sex in the input simulation sample
    total_values['age_start'] = simulation_data_LAD['age'].min()
    total_values['age_end'] = simulation_data_LAD['age'].max()
    total_values['sex'] = np.unique(simulation_data_LAD['sex'])

    return pd.DataFrame.from_dict([total_values])

def compare_detailed_estimates(simulation_data, ONS_data, location, n_years):
    '''Function that compares the outputs of the simulation with the estimates from
    the ONS. Detailed gender and age values are compared for the cumulative sum over the years and also the last year.
 Parameters
    ----------
    simulation_data : Dataframe
        Input data from the VPH simulation
    ONS_data : Dataframe
        Summary estimates from the ONS existing in the persistent data
    location: str
        LAD code for place to run the simulation
    n_years: int
        Number of years the simulation was ran for
    Returns:
        Two dataframes with the comparison between the ONS and simulation data for the cummulative sum and the last year
    '''

    # select data from the input location
    ONS_data = ONS_data[ONS_data['ladcode20'] == location]

    # in case the data doesn't have it, turn age into an age bucket for agregation
    age_bucket = ["0to15", "16to19", "20to24", "25to29", "30to44", "45to59", "60to74", "75plus"]
    simulation_data = get_age_bucket(simulation_data)
    ONS_data = get_age_bucket(ONS_data)


    # loop over sex and age bucket for the detailed comparison
    df_list_sum = []
    df_list_last_year = []

    for sex in [1,2]:

        # select data for a given sex
        simulation_data_sex = simulation_data[simulation_data['sex']==sex]
        ONS_data_sex = ONS_data[ONS_data['sex']==sex]

        for age in age_bucket:

            # now sub select data for a given age bucket
            simulation_data_sex_age = simulation_data_sex[simulation_data_sex['age_bucket'] == age]
            ONS_data_sex_age = ONS_data_sex[ONS_data_sex['age_bucket'] == age]

            # compute the cumulative sum comparison statistics on the sub sample (age and sex specific)
            df_sum = compare_estimates(simulation_data_sex_age, ONS_data_sex_age, location, n_years)

            # compute the last year comparison statistics on the sub sample (age and sex specific)
            df_last_year = compare_estimates(simulation_data_sex_age, ONS_data_sex_age, location, n_years, True)


            df_list_sum.append(df_sum)
            df_list_last_year.append(df_last_year)

    df_output_sum = pd.concat(df_list_sum)
    df_output_last = pd.concat(df_list_last_year)

    return df_output_sum, df_output_last