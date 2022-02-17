import pytest
import yaml
import pandas as pd
from os.path import exists
from daedalus.VphSpenserPipeline.ValidationEstimates import compare_estimates, compare_detailed_estimates
from scripts.run import run_pipeline
import os

def test_compare_summary_estimates():

    simulation_data_file = os.path.join('tests','data','ssm_E08000032_MSOA11_ppp_2011_simulation_reassigned.csv')

    ONS_data_file = os.path.join('persistent_data','MYEB3_summary_components_of_change_series_UK_(2019_geog20).csv')

    simulation_data = pd.read_csv(simulation_data_file)
    ONS_data = pd.read_csv(ONS_data_file)

    summary_df = compare_estimates(simulation_data, ONS_data, "E08000033", 2)

    summary_df.to_csv(os.path.join('tests','data','comparison_summary_df.csv'))

    assert (summary_df.shape[0]==1)

def test_compare_detailed_estimates():

    simulation_data_file = os.path.join('tests','data','ssm_E08000032_MSOA11_ppp_2011_simulation_reassigned.csv')

    ONS_data_file = os.path.join('persistent_data','MYEB2_detailed_components_of_change_series_EW_(2019_geog20).csv')

    simulation_data = pd.read_csv(simulation_data_file)
    ONS_data = pd.read_csv(ONS_data_file)

    summary_df_sum, summary_df_last  = compare_detailed_estimates(simulation_data,ONS_data,'E08000032',1)
    summary_df_sum.to_csv(os.path.join('tests','data','comparison_detailed_df.csv'))
    summary_df_last.to_csv(os.path.join('tests','data','comparison_detailed_df_last_year.csv'))

    assert (summary_df_sum.shape[0]>1)
    assert (summary_df_last.shape[0]>1)

def test_run_pipeline():

    configuration_file = os.path.join('tests', 'test_configs','default_config.yaml')
    location = 'E08000032'
    input_data_dir = os.path.join('tests', 'data')
    persistent_data_dir = 'persistent_data'
    output_dir = os.path.join('tests', 'outputs')

    run_pipeline(configuration_file, location, input_data_dir, persistent_data_dir, output_dir)

    assert exists(os.path.join(output_dir,location))

    # based on input location, get the input files that will be used in the simulation
    input_data_raw_filename = 'ssm_' + location + '_MSOA11_ppp_2011.csv'
    start_population_size = len(pd.read_csv("{}/{}".format(input_data_dir, input_data_raw_filename)))

    # output directory where all files from the run are saved
    output_data_filename = 'ssm_' + location + '_MSOA11_ppp_2011_simulation.csv'
    pop = pd.read_csv(os.path.join(output_dir,location, output_data_filename))

    end_population_size = len(pop[pop['alive'] == 'alive'])
    assert (start_population_size < end_population_size)