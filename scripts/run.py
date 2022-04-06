#!/usr/bin/env python3
"""This is the main script for running the AngryMob pipeline. It loads in directory names and handles the
overall initiation from a yaml file for the microsimulaton."""
from pathlib import Path
import os
import pandas as pd
import minos.utils as utils
import argparse
import yaml
import logging
import datetime

from minos.VphSpenserPipeline.RunPipeline import RunPipeline


def run_pipeline(configuration_file, input_data_dir=None, persistent_data_dir=None, output_dir=None):
    """
    Given an basic input config file and data directory information configure the
     vivarium public health spenser pipeline and run it.

    Parameters
    ----------
    configuration_file : ConfigTree
        Config yaml file of variables needed to run the pipeline.
    input_data_dir: str
        Path to the directory with input data.
    persistent_data_dir: str
        Path to the directory where the files persistently needed over the whole microsimulation run
        such as rate/probability/demographic tables.
    output_dir: str
        Path to the directory where the output data should be saved.
    """
    
    config = utils.get_config(configuration_file)

    # Check for input directory and add it the console.
    if input_data_dir:
        config.update({
            'input_data_dir': input_data_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            input_data_dir = config.input_data_dir
        except:
            raise RuntimeError('There is no input_data_dir information in the default '
                  'config file, please provide one with the --input_data_dir flag')
    # Check for persistent directory and add it to the console.
    if persistent_data_dir:
        config.update({
            'persistent_data_dir': persistent_data_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            persistent_data_dir = config.persistent_data_dir
        except:
            raise RuntimeError('There is no persistent_data_dir information in the default '
                  'config file, please provide one with the --persistent_data_dir flag')
    # Check for output directory.
    if output_dir:
        output_dir = output_dir
        config.update({
            'output_dir': output_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            output_dir = config.output_dir
        except:
            raise RuntimeError('There is no output_dir information in the default '
                  'config file, please provide one with the --output_dir flag')

    # Print initial pop size.
    year_start = config.time.start.year
    start_population_size = pd.read_csv(f"data/composite_US/{year_start}_US_cohort.csv").shape[0]
    print('Start Population Size: {}'.format(start_population_size))

    # Output directory where all files from the run will be saved.
    # Join file name with the time to prevent overwriting.
    run_output_dir = os.path.join(output_dir, str(datetime.datetime.now())[:19])
    #run_output_dir = output_dir

    config.update({
        'run_output_dir': run_output_dir,
    }, source=str(Path(__file__).resolve()))

    # Make output directory if it does not exist.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    os.makedirs(run_output_dir, exist_ok=True)

    # Save the yaml file with the minimal amount of information needed to reproduce results in the output folder.
    with open(os.path.join(run_output_dir, 'config_file_.yml'), 'w') as config_file:
        yaml.dump(config.to_dict(), config_file)
        print("Write config file successful")
    logging.info("Minimum YAML config file written.")

    # Run the microsimulation via runPipeline.
    simulation = RunPipeline(config, start_population_size)
    # Grab the final simulant population.
    pop = simulation.get_population()
    print('Finished running the full simulation')
    # Save the output file to a csv.
    simulant_data_filename = 'output_US_simulation.csv'
    pop.to_csv(os.path.join(run_output_dir, simulant_data_filename))

    # Print summary metrics on the simulation.
    print('alive', len(pop[pop['alive'] == 'alive']))

    if 'Mortality()' in config.components:
        print('dead', len(pop[pop['alive'] == 'dead']))
    if 'FertilityAgeSpecificRates()' in config.components:
        print('New children', len(pop[pop['parent_id'] != -1]))

    return simulation

# This __main__ function is used to run this script in a console. See daedalus github for examples.
if __name__ == "__main__":

    logging.basicConfig(filename="test.log", level=logging.INFO)
    logging.info("pipeline start.")
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation")

    parser.add_argument("-c", "--config", required=True, type=str, metavar="config-file",
                        help="the model config file (YAML)")
    #parser.add_argument('--location', help='LAD code', default=None)
    parser.add_argument('--input_data_dir', help='directory where the input data is', default=None)
    parser.add_argument('--persistent_data_dir', help='directory where the persistent data is', default=None)
    parser.add_argument('--output_dir', type=str, help='directory where the output data is saved', default=None)

    args = parser.parse_args()
    configuration_file = args.config
    #python scripts/short_run.py -c config/default_short_config.yaml --location E08000032 --input_data_dir data --persistent_data_dir persistent_data --output_dir output

    simulation = run_pipeline(configuration_file, args.input_data_dir, args.persistent_data_dir, args.output_dir)
