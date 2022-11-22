#!/usr/bin/env python3
"""This is the main script for running the Minos pipeline. It loads in directory names and handles the
overall initiation from a yaml file for the microsimulaton."""
from pathlib import Path
import os
import pandas as pd
import minos.utils as utils
import argparse
import yaml
import logging
import datetime

from minos.minosPipeline.RunPipeline import RunPipeline


def validate_directories(config, input_data_dir, persistent_data_dir, output_dir):
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
    return input_data_dir, persistent_data_dir, output_dir


def run(args):
    """
    Given an basic input config file and data directory information configure the minos pipeline and run it.

    Parameters
    ----------
    configuration_file : ConfigTree
        Config yaml file of variables needed to run the pipeline.
    """
    # Read in config from file and set up some object vars
    config = utils.read_config(args.config)
    output_dest = args.subdir

    # Vivarium needs an initial population size. Define it as the first cohort of US data.
    year_start = config['time']['start']['year']
    start_population_size = pd.read_csv(f"{config['input_data_dir']}/{year_start}_US_cohort.csv").shape[0]
    print(f'Start Population Size: {start_population_size}')

    # Output directory where all files from the run will be saved.
    # Join file name with the time to prevent overwriting.
    run_output_dir = os.path.join(config['output_data_dir'], output_dest, str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
    run_output_plots_dir = os.path.join(run_output_dir, 'plots/')

    # Add important things to the config file
    # output directory
    # population size
    config.update({
        'run_output_dir': run_output_dir,
        'run_output_plots_dir': run_output_plots_dir,
        'population' : {'population_size' : start_population_size}
    }, source=str(Path(__file__).resolve()))

    ## Create directories if necessary
    # Make the output/ directory if not exists. This should only need to happen on first run
    if not os.path.exists(config['output_data_dir']):
        print("Specified output directory does not exist. creating..")
        os.makedirs(config['output_data_dir'], exist_ok=True)
    # Make run specific output directory if it does not exist. This should happen every run
    if not os.path.exists(run_output_dir):
        print("Specified output destination does not exist. creating..")
        os.makedirs(run_output_dir, exist_ok=True)
    # Make run specific plots directory
    if not os.path.exists(run_output_plots_dir):
        print("Specified plots file for output does not exist. creating..")
        os.makedirs(run_output_plots_dir, exist_ok=True)

    # TODO: Remove this from the config and turn it into a completely separate make command to run AFTER simulation
    # Leaving the default in to do nothing for now.
    #if 'do_plots' not in config.keys():
    #    config['do_plots'] = False

    # Start logging. Really helpful in arc4 with limited traceback available.
    logging.basicConfig(filename=os.path.join(run_output_dir, "minos.log"), level=logging.INFO)
    logging.info("Pipeline start")

    print("Printing config: ")
    print(config)
    # Save the config to a yaml file with the minimal amount of information needed to reproduce results in the output folder.
    output_config_file = os.path.join(run_output_dir, 'config_file.yml')
    with open(output_config_file, 'w') as config_file:
        yaml.dump(config.to_dict(), config_file)
        print("Write config file successful")
    logging.info("Minimum YAML config file written before vivarium simulation object is declared.")

    # Run the microsimulation via runPipeline.
    simulation = RunPipeline(config, start_population_size, run_output_dir)
    # Grab the final simulant population.
    # pop = simulation.get_population()
    print('Finished running the full simulation')
    # Save the output file to a csv.

    return simulation


def run_pipeline_OLD(configuration_file, input_data_dir=None, persistent_data_dir=None, output_dir=None):
    """
    Given an basic input config file and data directory information configure the minos pipeline and run it.

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
    # Validate if data directories are supplied in args or in yaml config.
    # TODO seems overly complicated. Could probably just put them in config.
    #input_data_dir, persistent_data_dir, output_dir = validate_directories(config, input_data_dir,
    #                                                                       persistent_data_dir, output_dir)
    # Print initial pop size.
    year_start = config.time.start.year
    start_population_size = pd.read_csv(f"data/final_US/{year_start}_US_cohort.csv").shape[0]
    print('Start Population Size: {}'.format(start_population_size))

    # Output directory where all files from the run will be saved.
    # Join file name with the time to prevent overwriting.
    run_output_dir = os.path.join(output_dir, str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
    run_output_plots_dir = os.path.join(run_output_dir, 'plots/')
    #run_output_dir = output_dir

    config.update({
        'run_output_dir': run_output_dir,
        'run_output_plots_dir': run_output_plots_dir,
    }, source=str(Path(__file__).resolve()))

    # Make output directory if it does not exist.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    os.makedirs(run_output_dir, exist_ok=True)
    os.makedirs(run_output_plots_dir, exist_ok=True)

    # Save the yaml file with the minimal amount of information needed to reproduce results in the output folder.
    with open(os.path.join(run_output_dir, 'config_file_.yml'), 'w') as config_file:
        yaml.dump(config.to_dict(), config_file)
        print("Write config file successful")
    logging.info("Minimum YAML config file written.")

    # Run the microsimulation via runPipeline.
    simulation = RunPipeline(config, start_population_size, run_output_dir)
    # Grab the final simulant population.
    #pop = simulation.get_population()
    print('Finished running the full simulation')
    # Save the output file to a csv.

    return simulation

# This __main__ function is used to run this script in a console. See daedalus github for examples.
if __name__ == "__main__":

    ## CHANGING HOW THIS SCRIPT WORKS
    # Now only taking config and output directory as command line arguments, the rest can come from config.
    logging.basicConfig(filename="test.log", level=logging.INFO)
    logging.info("pipeline start.")
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation")

    parser.add_argument("-c", "--config", required=True, type=str, metavar="config-file",
                        help="the model config file (YAML)")
    #parser.add_argument('--location', help='LAD code', default=None)
    #parser.add_argument('--input_data_dir', help='directory where the input data is', default=None)
    #parser.add_argument('--persistent_data_dir', help='directory where the persistent data is', default=None)
    #parser.add_argument('--output_dir', type=str, help='directory where the output data is saved', default=None)

    parser.add_argument("-o", "--output_subdir", type=str, metavar="subdir", dest='subdir',
                        help='sub-directory within output/ where the output data from this specific run is saved',
                        default=None)

    args = parser.parse_args()
    configuration_file = args.config
    #python scripts/short_run.py -c config/default_short_config.yaml --location E08000032 --input_data_dir data --persistent_data_dir persistent_data --output_dir output

    simulation = run(args)

    #simulation = run_pipeline_OLD(configuration_file, args.input_data_dir, args.persistent_data_dir, args.output_dir)
