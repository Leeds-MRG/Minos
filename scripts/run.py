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

    ############## READ CONFIG AND ARGS ##############
    ## Read config and set up some variables from the command line args
    config = utils.read_config(args.config)
    scenario = args.intervention
    subdir = args.subdir

    # If intervention arg not present, we must be doing a baseline run
    if not args.intervention:
        scenario = 'baseline'

    # if no runtime present, this is not a batch run and the current time should be used
    if not args.runtime:
        runtime = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    else:  ## if runtime present its been supplied by a batch submission script to keep all the runs in the same directory
        runtime = args.runtime

    # if no subdir present, create empty string so os.join can ignore it
    if not args.subdir:
        subdir = ''

    ############## INITIAL VARIABLES ##############
    ## Define some initial vars that vivarium needs
    # start year
    year_start = config['time']['start']['year']

    if (args.runID) and ("scaled" in args.config):
        new_input_dir = config['base_input_data_dir'] + (
                "_" + str(((args.runID - 1) // 10) + 1))  # every 10 runs uses same pop.
        config.update({'input_data_dir': new_input_dir})
    else:
        config.update({'input_data_dir': config['base_input_data_dir']})

    # start_population_size (use size of prepared input population in start year)
    start_population_size = pd.read_csv(f"{config['input_data_dir']}/{year_start}_US_cohort.csv").shape[0]
    print(f'Start Population Size: {start_population_size}')

    ############## DIRECTORIES ##############
    # Output directory structure
    # Format - '<top_level_output>/<output_subdirectory>/<baseline_or_intervention>/<runtime>'
    run_output_dir = os.path.join(config['output_data_dir'], subdir, scenario,
                                  runtime)
    run_output_plots_dir = os.path.join(run_output_dir, 'plots/')

    ## Create directories if necessary
    # top level output dir. This should only need to happen on first run
    if not os.path.exists(config['output_data_dir']):
        print("Specified output directory does not exist. creating..")
        os.makedirs(config['output_data_dir'], exist_ok=True)
    # run specific output dir. This should happen every run
    if not os.path.exists(run_output_dir):
        print("Specified output sub-directory does not exist. creating..")
        os.makedirs(run_output_dir, exist_ok=True)
    # Make run specific plots directory
    if not os.path.exists(run_output_plots_dir):
        print("Specified plots file for output does not exist. creating..")
        os.makedirs(run_output_plots_dir, exist_ok=True)

    # Make logs dir for batch runs
    if args.runID:
        log_dir = os.path.join(run_output_dir, 'logs')
        if not os.path.exists(log_dir):
            print("Creating log directory for batch runs...")
            os.makedirs(log_dir, exist_ok=True)

    ############## CONFIG ##############
    # Add some more important things to the config file (mostly derived from command line args)
    add_to_config = {}

    # Always required
    add_to_config.update({
        'run_output_dir': run_output_dir,
        'run_output_plots_dir': run_output_plots_dir,
        'population': {'population_size': start_population_size, },
        'scenario': scenario
    })

    # only for batch runs
    if args.runID:
        # Add run ID to config if present
        add_to_config.update({
            'run_ID': args.runID,
            'run_ID_names': 'run_id'
        }, source=str(Path(__file__).resolve()))

    # Now update the Vivarium ConfigTree object
    config.update(add_to_config)

    # generate config filename for saving to output directory
    output_config_file = os.path.join(run_output_dir, 'config_file.yml')
    # only save the config file once (on run 1 for batch runs)
    if args.runID:
        if args.runID == 1:
            with open(output_config_file, 'w') as config_file:
                yaml.dump(config.to_dict(), config_file)
                print("Write config file successful")
    else:
        with open(output_config_file, 'w') as config_file:
            yaml.dump(config.to_dict(), config_file)
            print("Write config file successful")

    # TODO: Remove this from the config and turn it into a completely separate make command to run AFTER simulation
    # Leaving the default in to do nothing for now.
    # if 'do_plots' not in config.keys():
    #    config['do_plots'] = False

    ############## LOGGING ##############
    # Start logging. Really helpful in arc4 with limited traceback available.
    if args.runID:
        logfile = os.path.join(run_output_dir, 'logs', f'run_{args.runID}_minos.log')
    else:
        logfile = os.path.join(run_output_dir, 'minos.log')

    # have to add force=True - see stackoverflow for why https://stackoverflow.com/questions/30861524/logging-basicconfig-not-creating-log-file-when-i-run-in-pycharm
    logging.basicConfig(filename=logfile,
                        format='%(asctime)s %(message)s',
                        level=logging.INFO,
                        force=True)

    logging.info("Minimum YAML config file written before vivarium simulation object is declared.")
    logging.info(f"Start population size: {start_population_size}")
    logging.info(f"Running with configuration file: {args.config}")
    logging.info(f"Output directory: {run_output_dir}")
    logging.info(f"Beginning a {scenario} simulation.")
    if args.runID:
        logging.info(f"This is run {args.runID} of a batch run.")
    logging.info(
        f"Beginning simulation in {config.time.start.year}, running for {config.time.num_years} years until {config.time.end.year}")
    logging.info("Pipeline start...")
    # TODO: Add more here.

    ############## RUN PIPELINE ##############
    # Different call for intervention or cross_validation
    if args.intervention:
        RunPipeline(config, intervention=args.intervention)
    else:
        RunPipeline(config)

    print('Finished running the full simulation')


# This __main__ function is used to run this script in a console. See daedalus github for examples.
if __name__ == "__main__":

    ## CHANGING HOW THIS SCRIPT WORKS
    # Now only taking config and output directory as command line arguments, the rest can come from config.
    # logging.basicConfig(filename="test.log", level=logging.INFO)
    # logging.info("Collecting command line arguments...")
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation",
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter
                                     # For multi-line formatting in help text
                                     )

    parser.add_argument("-c", "--config", required=True, type=str, dest='config',
                        help="Model config file (YAML)")
    parser.add_argument("-o", "--output_subdir", type=str, dest='subdir', default=None,
                        help='Sub-directory within output/ where the data from this specific run is saved')
    parser.add_argument("-r", "--run_id", type=int, dest='runID', default=None,
                        help="(Optional) Unique run ID specified to distinguish between multiple runs in a batch submission")
    parser.add_argument("-t", "--time", type=str, dest='runtime', default=None,
                        help="(Optional) Runtime variable supplied by batch run scripts, so all batch outputs are kept in the same folder.")
    parser.add_argument("-i", "--intervention", type=str, dest="intervention", default=None,
                        help=
                        """(Optional) Specify the intervention you want to run. Currently implemented interventions are:
                                   - hhIncomeIntervention
                                   - hhIncomeChildUplift
                                   - hhIncomePovertyLineChildUplift
                                   - livingWageIntervention
                                   - energyDownlift""")

    args = parser.parse_args()
    configuration_file = args.config

    run(args)
