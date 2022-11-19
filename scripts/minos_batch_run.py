"""Minos model class for interaction with hpc."""

from pathlib import Path
import os
import pandas as pd
import minos.utils as utils
import argparse
import yaml
import logging
import datetime
import sys
import numpy as np
import subprocess
import itertools

from vivarium import InteractiveContext

from minos import utils

from minos.modules.mortality import Mortality
from minos.modules.replenishment import Replenishment
from minos.modules.replenishment_nowcast import replenishmentNowcast
from minos.modules.add_new_birth_cohorts import FertilityAgeSpecificRates
from minos.modules.housing import Housing
from minos.modules.income import Income
from minos.modules.mental_wellbeing import MWB
from minos.modules.labour import Labour
from minos.modules.neighbourhood import Neighbourhood
from minos.modules.alcohol import Alcohol
from minos.modules.tobacco import Tobacco
from minos.modules.loneliness import Loneliness
from minos.modules.nutrition import Nutrition
from minos.modules.education import Education

from minos.modules.intervention import hhIncomeIntervention
from minos.modules.intervention import hhIncomeChildUplift
from minos.modules.intervention import hhIncomePovertyLineChildUplift
from minos.modules.intervention import energyDownlift
from minos.modules.intervention import livingWageIntervention


# validate config function - validate conifgs, add parts that are needed.
# init components - check components in and initialise them.
# run - loop through msim
# save
# main

class Minos():

    def __init__(self, config_dir, run_id):
        # specify yaml config and update with some list of required kwargs.
        # print(sys.argv)
        # config_dir = kwargs["config_file"]
        # if running on hpc use argv arguments to get parameters.
        # if debugging/testing use a preset list of simple parameters.
        with open(config_dir) as config_file:
            config = yaml.full_load(config_file)

        config = self.validate_directories(config, "input_data_dir")
        config = self.validate_directories(config, "persistent_data_dir")
        config = self.validate_directories(config, "output_data_dir")

        # Vivarium needs an initial population size. Define it as the first cohort of US data.
        year_start = config['time']['start']['year']
        start_population_size = pd.read_csv(f"{config['input_data_dir']}/{year_start}_US_cohort.csv").shape[0]
        # Start population size added to config.
        config['population']['population_size'] = start_population_size
        print(f'Start Population Size: {start_population_size}')

        # Output directory where all files from the run will be saved.
        # Add date and time to output file name to make it unique. Prevents overwriting repeat model runs.
        # run_output_dir = os.path.join(config['output_data_dir'], str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
        # Or just assign them to some experiment folder.
        run_output_dir = os.path.join(config['output_data_dir'], config['output_destination'])

        # Make output directories if they do not exist.
        if not os.path.exists(config['output_data_dir']):
            print("Specified output directory does not exist. creating..")
            os.makedirs(config['output_data_dir'], exist_ok=True)
        if not os.path.exists(run_output_dir):
            print("Specified output destination does not exist. creating..")
            os.makedirs(run_output_dir, exist_ok=True)
        config['run_output_dir'] = run_output_dir


        # If doing plots check a plot directory is defined and if it exists.
        # If it is defined and exists add plot directory name to config.
        # If defined but does not exist. Create it and add to config.
        # If no plot directory name specified create a default /plots in run_output_dir.
        if config['do_plots']:
            if 'output_plots_dir' not in config.keys():
                output_plots_dir = os.path.join(run_output_dir, 'plots/')
                print(f"No directory for saving plots specified. Setting default as '{output_plots_dir}'")
            else:
                output_plots_dir = config['output_plots_dir']
            if not os.path.exists(output_plots_dir):
                print("Specified plots file for output does not exist. creating..")
                os.makedirs(output_plots_dir, exist_ok=True)
            config['output_plots_dir'] = output_plots_dir


        # default do_plots in config to false. takes a lot less memory but less verbose.


        # Start logging. Really helpful in arc4 with limited traceback available.
        logging.basicConfig(filename=os.path.join(run_output_dir, "minos.log"), level=logging.INFO)
        logging.info("pipeline start.")
        # run_output_dir = output_dir

        config['run_output_dir'] = run_output_dir

        print("Printing config: ")
        print(config)
        # Save the config to a yaml file with the minimal amount of information needed to reproduce results in the output folder.
        output_config_dir = os.path.join(run_output_dir, 'config_file.yml')
        with open(output_config_dir, 'w') as config_file:
            yaml.dump(config, config_file)
            print("Write config file successful")
        logging.info("Minimum YAML config file written before vivarium simulation object is declared.")

        components = self.initComponents(
            config)  # validate and initialise list of config components to be used in simulation.
        #
        config = utils.get_config(output_config_dir)
        print(config)
        simulation = InteractiveContext(components=components,
                                        configuration=config,
                                        plugin_configuration=utils.base_plugins(),
                                        setup=False)
        # Use pre_setup method for each module.
        # Do anything needed for each module's setup that cannot be done until the InteractiveContext object is created.
        # For example, some modules require persistent rate table data.
        # It is loaded into the simulation object at pre setup.

        # If this looks confusing look at the daedalus run script.
        # https://github.com/alan-turing-institute/daedalus/blob/master/daedalus/VphSpenserPipeline/RunPipeline.py
        # lines 55-101 are much more modular/flexible than before.
        # Its done this way in Daedalus because the vivarium_public_health modules are from a separate package.
        # Even then these classes could be appended with pre_setup functions.
        # This isn't the case with Minos as each module is bespoke and can be given a pre_setup method.
        # Basically, this is very pedantic but easier if a lot more preamble is needed later.

        # Run pre-setup method for each module.
        # Adds in any required data and config items.
        for component in components:
            print(f"Presetup done for: {component}")
            simulation = component.pre_setup(config, simulation)

        # Define unique parameter combinations for intervention. Used to generate unique save files later.
        # If no experiment parameters are defined by an intervention module this is the default for batch runs.
        if 'experiment_parameters' not in config:
            config.update({'experiment_parameters': [run_id]}, source=str(Path(__file__).resolve()))
            config.update({'experiment_parameters_names': ['run_id']}, source=str(Path(__file__).resolve()))

        # Save final config. If there are multiple runs save multiple configs each with a run id.
        config_output_dir = os.path.join(run_output_dir, f'final_config_file.yml')

        # file exists # TODO doesn't work..
        if run_id == 1:  # only write config file once on first run.
            with open(config_output_dir, 'w') as final_config_file:
                yaml.dump(config.to_dict(), final_config_file)
                print("Write final config file successful")
            logging.info("Final YAML config file written before vivarium simulation object is declared.")

        # Print start time for entire simulation.
        print('Start simulation setup')
        start_time = utils.get_time()
        print(start_time)
        logging.info('Start simulation setup')
        logging.info(start_time)

        # Run setup method for each module.
        simulation.setup()

        self.config = config
        self.simulation = simulation
        self.components = components

    def main(self):
        simulation = self.simulation
        config = self.config

        # get minos model and run it
        for year in range(1, config.time.num_years + 1):

            # Step forwards a year in monthly increments.
            simulation.run_for(duration=pd.Timedelta(days=365.25))

            # Print time when year finished running.
            print(f'Finished running simulation for year: {year}')
            wave_time = utils.get_time()
            logging.info(print(f'Finished running simulation for year: {year}'))
            logging.info(wave_time)

            # get population dataframe.
            pop = simulation.get_population()

            # Assign age brackets to the individuals.
            pop = utils.get_age_bucket(pop)

            # File name and save.
            print(config.experiment_parameters)
            params = config.experiment_parameters
            names = config.experiment_parameters_names
            output_data_filename = ""

            for i in range(len(params)):
                output_data_filename += names[i] + "_"
                output_data_filename += str(params[i]) + "_"

            output_data_filename += f"{config.time.start.year + year}.csv"
            output_file_path = os.path.join(config.run_output_dir, output_data_filename)
            pop.to_csv(output_file_path)
            print("Saved data to: ", output_file_path)
            print('In year: ', config.time.start.year + year)
            # Print some summary stats on the simulation.
            print('alive', len(pop[pop['alive'] == 'alive']))

            # Print metrics for desired module.
            # TODO: this can be extended towards a generalised metrics method for each module.
            if 'Mortality()' in config.components:
                print('dead', len(pop[pop['alive'] == 'dead']))
            if 'FertilityAgeSpecificRates()' in config.components:
                print('New children', len(pop[pop['parent_id'] != -1]))

            if config.do_plots:
                for component in self.components:
                    component.plot(pop, config)
        return config, simulation

    def save(self, save_method, destination, file_name):
        """After a full minos model run. There will be a large amount of save data to format for use on local machines or in plots."""

        # uses some generic save function, destination path, and file name.
        data = save_method(some_args)
        data.to_csv(os.join(destination, file_name))

    def validate_directories(self, config, dir_name, dir=None):
        """ Validate directory names for minos are already in the config or specified in the init kwargs.

        This has been redone from daedalus to use dictionary yaml configs rather than the vivarium config tree.

        Parameters
        ----------

        config : dict
            Yaml config dictionary to update.
        dir, dir_name : str
            What is the directory 'dir' and what is its name in the kwargs dictionary 'dir_name'. E.g. 'data/final_US/' and
            'input_data_dir'.
        Returns
        -------

        """

        """Check if file name is already in the config dictionary keys.
        If its not in the keys try adding it in.
        If no dir specified to add in return an error. The user has specified no dir value."""

        if dir_name not in config.keys():
            try:
                config.update({
                    dir_name: dir,
                }, source=str(Path(__file__).resolve()))
            except:
                raise RuntimeError(f'There is no {dir_name} information in the default config file, '
                                   f'please provide one with the --{dir_name} flag')
        return config

    def initComponents(self, config):
        components = []
        # Check each of the modules is present.
        # components = [eval(x) for x in config.components] # more adapative way but security issues.
        # last one in first one off. any module that requires another should be BELOW IT in this order.

        # Outcome module goes first (last in sim)
        if "MWB()" in config['components']:
            components.append(MWB())

        # Intermediary modules.
        if "Tobacco()" in config['components']:
            components.append(Tobacco())
        if "Alcohol()" in config['components']:
            components.append(Alcohol())
        if "Neighbourhood()" in config['components']:
            components.append(Neighbourhood())
        if "Labour()" in config['components']:
            components.append(Labour())
        if "Housing()" in config['components']:
            components.append(Housing())
        if "Income()" in config['components']:
            components.append(Income())
        if "Loneliness()" in config['components']:
            components.append(Loneliness())
        if "Nutrition()" in config['components']:
            components.append(Nutrition())
        if "FertilityAgeSpecificRates()" in config['components']:
            components.append(FertilityAgeSpecificRates())
        if "Mortality()" in config['components']:
            components.append(Mortality())
        if "Education()" in config['components']:
            components.append(Education())

        # Interventions
        if "hhIncomeIntervention()" in config['components']:
            components.append(hhIncomeIntervention())
        if "hhIncomeChildUplift()" in config['components']:
            components.append(hhIncomeChildUplift())
        if "hhIncomePovertyLineChildUplift()" in config['components']:
            components.append(hhIncomePovertyLineChildUplift())
        if "livingWageIntervention()" in config['components']:
            components.append(livingWageIntervention())
        if "energyDownlift()" in config['components']:
            components.append(energyDownlift())

        # Replenishment always go last. (first in sim)
        if "Replenishment()" in config['components']:
            components.append(Replenishment())
        if "replenishmentNowcast()" in config['components']:
            components.append(replenishmentNowcast())
        return components


if __name__ == "__main__":
    # python3 scripts/minos_batch_run.py --config_file "config/controlConfig.yaml" --input_data_dir "data/final_US/" --persistent_data_dir "persistent_data" --output_data_dir "output"
    # Parse arguments if running this file from a terminal.
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation")

    parser.add_argument("-c", "--config_file", type=str, metavar="config-file",
                        help="the model config file (YAML)")
    # parser.add_argument('--location', help='LAD code', default=None)
    # parser.add_argument('--input_data_dir', help='directory where the input data is', default=None)
    # parser.add_argument('--persistent_data_dir', help='directory where the persistent data is', default=None)
    # parser.add_argument('--output_data_dir', type=str, help='directory where the output data is saved', default=None)
    parser.add_argument("-r", "--run_id", type=int, metavar="config-file",
                        help="the model config file (YAML)")

    args = vars(parser.parse_args())
    # input_kwargs = vars(args) # cast args as a dict.

    # Assemble lists into grand list of all combinations.
    # Each experiment will use one item of this list.
    # input_kwargs['parameter_lists'] = parameter_lists
    print(args)
    config_file = args['config_file']
    run_id = args['run_id']
    minos_run = Minos(config_file, run_id)
    minos_run.main()

# TODO. add in args for variance in uplift value, percentage pop, and number of repetitions.
