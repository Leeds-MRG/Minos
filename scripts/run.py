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


def run(args):
    """

    Parameters
    ----------
    args : ArgumentParser.Namespace
       Command line arguments of parameters for the model run
    Returns
    -------
    simulation : Vivarium.Simulation.InteractiveContext
        Simulation object after running for n timesteps
    """
    # Read in config from file and set up some object vars
    config = utils.read_config(args.config)

    # Vivarium needs an initial population size. Define it as the first cohort of US data.
    year_start = config['time']['start']['year']
    start_population_size = pd.read_csv(f"{config['input_data_dir']}/{year_start}_US_cohort.csv").shape[0]
    print(f'Start Population Size: {start_population_size}')

    # If run_id or int arg not present, set value to empty string. This is for os.path.join and creating output directory
    if not args.runID:
        run_id = ''
    if not args.intervention:
        intervention = ''
    # Output directory where all files from the run will be saved.
    # Join file name with the time to prevent overwriting.
    # Add runID in if present for batch runs, and int if present for specific intervention
    run_output_dir = os.path.join(config['output_data_dir'], args.subdir, intervention,
                                  str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
    run_output_plots_dir = os.path.join(run_output_dir, 'plots/')

    # Add important things to the config file
    # - output directories
    # - population size
    config.update({
        'run_output_dir': run_output_dir,
        'run_output_plots_dir': run_output_plots_dir,
        'population': {'population_size': start_population_size}
    }, source=str(Path(__file__).resolve()))


    if args.runID:
        # Add run ID to config if present
        config.update({
            'experiment_parameters': [run_id],
            'experiment_parameters_names': ['run_id']
        }, source=str(Path(__file__).resolve()))
    if args.intervention:
        # Add intervention to config if present
        config.update({
            'intervention': intervention
        }, source=str(Path(__file__).resolve()))

    ## Create directories if necessary
    # Make the output/ directory if not exists. This should only need to happen on first run
    if not os.path.exists(config['output_data_dir']):
        print("Specified output directory does not exist. creating..")
        os.makedirs(config['output_data_dir'], exist_ok=True)
    # Make run specific output directory if it does not exist. This should happen every run
    if not os.path.exists(run_output_dir):
        print("Specified output sub-directory does not exist. creating..")
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

    #print("Printing config: ")
    #print(config)
    # Save the config to a yaml file with the minimal amount of information needed to reproduce results in the output folder.
    output_config_file = os.path.join(run_output_dir, 'config_file.yml')

    # only save the config file once (on run 1 for multiple runs, or just once for single runs)
    if run_id:
        if run_id == 1:
            with open(output_config_file, 'w') as config_file:
                yaml.dump(config.to_dict(), config_file)
                print("Write config file successful")
    else:
        with open(output_config_file, 'w') as config_file:
            yaml.dump(config.to_dict(), config_file)
            print("Write config file successful")
    logging.info("Minimum YAML config file written before vivarium simulation object is declared.")

    # Run the microsimulation via RunPipeline.
    # Different call for intervention or not
    if args.intervention:
        simulation = RunPipeline(config, run_output_dir, intervention=args.intervention)
    else:
        simulation = RunPipeline(config, run_output_dir)

    print('Finished running the full simulation')

    return simulation


# This __main__ function is used to run this script in a console. See daedalus github for examples.
if __name__ == "__main__":

    ## CHANGING HOW THIS SCRIPT WORKS
    # Now only taking config and output directory as command line arguments, the rest can come from config.
    logging.basicConfig(filename="test.log", level=logging.INFO)
    logging.info("pipeline start.")
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation",
                                        usage = 'use "%(prog)s --help" for more information',
                                        formatter_class = argparse.RawTextHelpFormatter # For multi-line formatting in help text
    )

    parser.add_argument("-c", "--config", required=True, type=str, metavar="config-file",
                        help="Model config file (YAML)")
    parser.add_argument("-o", "--output_subdir", type=str, metavar="subdir", dest='subdir', default=None,
                        help='Sub-directory within output/ where the data from this specific run is saved')
    parser.add_argument("-r", "--run_id", type=int, metavar="runID", dest='runID', default=None,
                        help="(Optional) Unique run ID specified to distinguish between multiple runs in a batch submission")
    parser.add_argument("-i", "--intervention", type=str, metavar="intervention", dest="intervention", default=None,
                        help=
    """(Optional) Specify the intervention you want to run. Currently implemented interventions are:
       - hhIncomeIntervention
       - hhIncomeChildUplift
       - hhIncomePovertyLineChildUplift
       - livingWageIntervention
       - energyDownlift""")

    args = parser.parse_args()
    configuration_file = args.config

    simulation = run(args)
