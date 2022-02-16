#!/usr/bin/env python3
import os
import pandas as pd
import argparse
from VphSpenserPipeline import compare_estimates, compare_detailed_estimates
from VphSpenserPipeline import get_migrants, reassign_internal_migration_to_LAD

def run_validation(location, input_location_path, persistent_data_dir):
    """ Function that run the ONS-Simmulation comparisons for a given location

    Parameters
    ----------
    location: str
        LAD code for place to run the simulation
    input_location_path: str
        Path to the directory with the input dataset for the given location
    persistent_data_dir: str
        Path to the directory where the ONS files are found.
    """

    # read the ONS estimation files
    ONS_summary_file = os.path.join(persistent_data_dir,'MYEB3_summary_components_of_change_series_UK_(2019_geog20).csv')
    ONS_detailed_file = os.path.join(persistent_data_dir,'MYEB2_detailed_components_of_change_series_EW_(2019_geog20).csv')

    ONS_summary_data = pd.read_csv(ONS_summary_file)
    ONS_detailed_data = pd.read_csv(ONS_detailed_file)

    # path to the simulation files
    list_pop_dir = [i for i in os.listdir(input_location_path) if i.startswith('year_')]


    # for each year run the comparisons
    for year_dir in list_pop_dir:

        year = int(list(year_dir)[-1])
        simulation_data = pd.read_csv(os.path.join(input_location_path, year_dir,'ssm_'+location+'_MSOA11_ppp_2011_simulation_'+year_dir+'_reassigned.csv'))

        summary_df_sum = compare_estimates(simulation_data, ONS_summary_data, location, year)
        summary_df_sum_detailed, summary_df_last_detailed = compare_detailed_estimates(simulation_data, ONS_detailed_data, location, year)

        output_dir = os.path.join(input_location_path, year_dir)

        summary_df_sum_detailed.to_csv(os.path.join(output_dir, 'comparison_detailed_'+location+'_cumulative_sum_'+year_dir+'.csv'))
        summary_df_last_detailed.to_csv(os.path.join(output_dir, 'comparison_detailed_'+location+'_by_'+year_dir+'.csv'))
        summary_df_sum.to_csv(os.path.join(output_dir,'comparison_summary_'+location+'_cumulative_sum_'+year_dir+'.csv'))


    # run comparison for the total simmulation
    final_file = 'ssm_'+location+'_MSOA11_ppp_2011_simulation_reassigned.csv'

    # get the number of years that the simulatio ran for (should be the same at the highest values for the year subdirectories)
    total_year = [int(list(y)[-1]) for y in list_pop_dir]
    year = 2011 + max(total_year)

    simulation_data = pd.read_csv(os.path.join(input_location_path,final_file))

    summary_df_sum = compare_estimates(simulation_data, ONS_summary_data, location, max(total_year))
    summary_df_sum_detailed, summary_df_last_detailed = compare_detailed_estimates(simulation_data, ONS_detailed_data,
                                                                                   location, max(total_year))

    output_dir = os.path.join(input_location_path)
    summary_df_sum_detailed.to_csv(
        os.path.join(output_dir, 'comparison_detailed_' + location + '_cumulative_sum_' + str(year) + '.csv'))
    summary_df_last_detailed.to_csv(
        os.path.join(output_dir, 'comparison_detailed_' + location + '_by_' + str(year) + '.csv'))
    summary_df_sum.to_csv(
        os.path.join(output_dir, 'comparison_summary_' + location + '_cumulative_sum_' + str(year) + '.csv'))


def run_all_validations(simulation_dir, persistent_data_dir, list_pop_locations_dir, pool_migrants):
    """
    Run validation comparison in all existing locations present in a directory

    simulation_dir : string
        Path where the outputs of all simulations are found
    persistent_data_dir: str
        Path to the directory where the ONS files are found.
    list_pop_locations_dir: list
    pool_migrants: pandas DataFrame
    """

    for location in list_pop_locations_dir:
        print('----------------------------------------------')
        print('Re-assigning inviduals that migrated to ',location)
        print('----------------------------------------------')
        print()
        reassign_internal_migration_to_LAD(location, simulation_dir, pool_migrants)

        print('-----------------------------------')
        print ('Running validation for: ',location)
        print('-----------------------------------')
        print ()

        run_validation(location,os.path.join(simulation_dir,location),persistent_data_dir)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Validation of the dynamic microsimulation")

    parser.add_argument('--simulation_dir', help='directory where the simulated population files are stored', default=None)
    parser.add_argument('--persistent_data_dir', help='directory where the persistent data is', default=None)
    parser.add_argument('--location', help='LAD code (in case you want to run a specific location)', default=None)

    args = parser.parse_args()

    list_pop_locations_dir = [i for i in os.listdir(args.simulation_dir) if i.startswith('E')]

    print ('-------------------------------------------------------------')
    print ('Getting pool of individuals that migrated internally between LADs')
    print ('-------------------------------------------------------------')
    print()

    pool_migrants = get_migrants(args.simulation_dir, list_pop_locations_dir)

    if args.location:
        reassign_internal_migration_to_LAD(args.location, args.simulation_dir, pool_migrants)
        # if location is given as an input, then only run validation in that location
        run_validation(args.location, os.path.join(args.simulation_dir,args.location), args.persistent_data_dir)
    else:
        # if no location is given as an input, then run validation in all locations in that path
        run_all_validations(args.simulation_dir, args.persistent_data_dir, list_pop_locations_dir, pool_migrants)

