#!/usr/bin/env python3
"""Script for initiating and running an Minos microsimulation."""
import logging
import os
from pathlib import Path

# Do this to suppress warnings from Vivariums code...
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from vivarium import InteractiveContext

import minos.utils as utils

from minos.modules.mortality import Mortality
from minos.modules.replenishment import Replenishment, NoReplenishment
from minos.modules.add_new_birth_cohorts import FertilityAgeSpecificRates, nkidsFertilityAgeSpecificRates
from minos.modules.housing import Housing
from minos.modules.income import Income
from minos.modules.mental_wellbeing import MWB
from minos.modules.labour import Labour
from minos.modules.neighbourhood import Neighbourhood
from minos.modules.alcohol import Alcohol
from minos.modules.tobacco import Tobacco
from minos.modules.loneliness import Loneliness
from minos.modules.education import Education
from minos.modules.nutrition import Nutrition


from minos.modules.intervention import hhIncomeIntervention
from minos.modules.intervention import hhIncomeChildUplift
from minos.modules.intervention import hhIncomePovertyLineChildUplift
from minos.modules.intervention import livingWageIntervention
from minos.modules.intervention import energyDownlift

# for viz.
from minos.validation.minos_distribution_visualisation import *

def RunPipeline(config, run_output_dir, intervention=None):
    """ Run the daedalus Microsimulation pipeline

   Parameters
    ----------
    config : ConfigTree
        Config file to run the pipeline
    run_output_dir : String
        Directory
    Returns
    --------
     A dataframe with the resulting simulation
    """

    components = []
    # Check each of the modules is present.
    #components = [eval(x) for x in config.components] # more adapative way but security issues.
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
    if "nkidsFertilityAgeSpecificRates()" in config['components']:
        components.append(nkidsFertilityAgeSpecificRates())
    if "FertilityAgeSpecificRates()" in config['components']:
        components.append(FertilityAgeSpecificRates())
    if "Mortality()" in config['components']:
        components.append(Mortality())
    if "Education()" in config['components']:
        components.append(Education())

    # Interventions (if necessary)
    if intervention:
        if intervention == 'hhIncomeIntervention':
            components.append(hhIncomeIntervention())
        if intervention == 'hhIncomeChildUplift':
            components.append(hhIncomeChildUplift())
        if intervention == 'hhIncomePovertyLineChildUplift':
            components.append(hhIncomePovertyLineChildUplift())
        if intervention == 'livingWageIntervention':
            components.append(livingWageIntervention())
        if intervention == 'energyDownlift':
            components.append(energyDownlift())

    # Replenishment always go last. (first in sim)
    if "NoReplenishment()" in config['components']:
        components.append(NoReplenishment())
    if "Replenishment()" in config['components']:
        components.append(Replenishment())
    if "replenishmentNowcast()" in config['components']:
        components.append(replenishmentNowcast())

    # Initiate vivarium simulation object but DO NOT setup yet.
    simulation = InteractiveContext(components=components,
                                    configuration=config,
                                    plugin_configuration=utils.base_plugins(),
                                    setup=False)

    # If this looks confusing look at the daedalus run script.
    # https://github.com/alan-turing-institute/daedalus/blob/master/daedalus/VphSpenserPipeline/RunPipeline.py
    # lines 55-101 are much more modular/flexible than before.
    # Its done this way in Daedalus because the vivarium_public_health modules are from a separate package.
    # Even then these classes could be appended with pre_setup functions.
    # This isn't the case with Minos as each module is bespoke and can be given a pre_setup method.
    # Basically, this is very pedantic but easier if a lot more preamble is needed later.

    logging.info("Components included:")
    # Run pre-setup method for each module.
    for component in components:
        simulation = component.pre_setup(config, simulation)
        print(f"Presetup done for: {component}")
        logging.info(f"\t{component}")

    # Print start time for entire simulation.
    print('Start simulation setup')
    start_time = utils.get_time()
    print(f"Started simulation setup at {start_time}")
    logging.info(f'Running simulation setup...')

    # Run setup method for each module.
    simulation.setup()

    # Print time when modules are setup and the simulation starts.
    config_time = utils.get_time()
    print(f'Simulation loop start at {config_time}')

    ###
    # Save population BEFORE start of the simulation. This is for comparisons and change from baseline
    pop = simulation.get_population()
    pop = utils.get_age_bucket(pop)
    # File name and save
    output_data_filename = get_output_data_filename(config)
    output_file_path = os.path.join(config.run_output_dir, output_data_filename)
    pop.to_csv(output_file_path)
    print("Saved initial data to: ", output_file_path)
    logging.info(f"Saved initial data to: {output_file_path}")


    logging.info('Simulation loop start...')
    # Loop over years in the model duration. Step the model forwards a year and save data/metrics.
    for year in range(1, config.time.num_years + 1):

        logging.info(f'Begin simulation for year {config.time.start.year + year}')

        # Step forwards a year in monthly increments.
        simulation.run_for(duration=pd.Timedelta(days=365.25))

        # Print time when year finished running.
        print(f'Finished running simulation for year: {config.time.start.year + year}')
        logging.info(f'Finished running simulation for year: {config.time.start.year + year}')

        # get population dataframe.
        pop = simulation.get_population()

        # Assign age brackets to the individuals.
        pop = utils.get_age_bucket(pop)

        # File name and save
        output_data_filename = get_output_data_filename(config, year)

        output_file_path = os.path.join(config.run_output_dir, output_data_filename)
        pop.to_csv(output_file_path)
        print("Saved data to: ", output_file_path)
        logging.info(f"Saved data to: {output_file_path}")

        # Print some summary stats on the simulation.
        print('alive', len(pop[pop['alive'] == 'alive']))
        logging.info(f"Total alive: {len(pop[pop['alive'] == 'alive'])}")

        # Print metrics for desired module.
        # TODO: this can be extended towards a generalised metrics method for each module.
        if 'Mortality()' in config.components:
            print('dead', len(pop[pop['alive'] == 'dead']))
            logging.info(f"Total dead: {len(pop[pop['alive'] == 'dead'])}")
        if 'FertilityAgeSpecificRates()' in config.components:
            print('New children', len(pop[pop['parent_id'] != -1]))
            logging.info(f"New children: {len(pop[pop['parent_id'] != -1])}")

        #for component in components:
        #    component.plot(pop, config)

    return simulation


def get_output_data_filename(config, year=0):
    # File name and save.
    output_data_filename = ""

    # Add experiment parameters to output file name if present
    if 'experiment_parameters' in config.keys():
        print(config.experiment_parameters)
        output_data_filename += str(config.experiment_parameters) + '_'
        output_data_filename += str(config.experiment_parameters_names) + '_'

    # Now add year to output file name
    output_data_filename += f"{config.time.start.year + year}.csv"

    return(output_data_filename)