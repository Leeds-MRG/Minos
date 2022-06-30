#!/usr/bin/env python3
"""Script for initiating and running an Minos microsimulation."""
import logging
import os
from pathlib import Path

import pandas as pd

from vivarium import InteractiveContext

import minos.utils as utils

from minos.modules.mortality import Mortality
from minos.modules.replenishment import Replenishment
from minos.modules.add_new_birth_cohorts import FertilityAgeSpecificRates
#from minos.modules.depression import Depression
#from minos.modules.employment import Employment
from minos.modules.housing import Housing
from minos.modules.income import Income
from minos.modules.mental_wellbeing import MWB

def RunPipeline(config, start_population_size, run_output_dir):
    """ Run the daedalus Microsimulation pipeline

   Parameters
    ----------
    config : ConfigTree
        Config file to run the pipeline
    start_population_size: int
        Size of the starting population
    Returns
    --------
     A dataframe with the resulting simulation
    """
    # Start population size added to config.
    config.update({
        'population': {
            'population_size': start_population_size,
        }}, source=str(Path(__file__).resolve()))

    components = []
    # Check each of the modules is present.
    #components = [eval(x) for x in config.components] # more adapative way but security issues.
    # last one in first one off. any module that requires another should be BELOW IT in this order.
    if "MWB()" in config.components:
        components.append(MWB())
    if "Housing()" in config.components:
        components.append(Housing())
    if "Income()" in config.components:
        components.append(Income())
    if "FertilityAgeSpecificRates()" in config.components:
        components.append(FertilityAgeSpecificRates())
    if "Mortality()" in config.components:
        components.append(Mortality())
    if "Replenishment()" in config.components:
        components.append(Replenishment())


    logging.info("Final YAML config file written.")

    # Initiate vivarium simulation object but DO NOT setup yet.
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
    for component in components:
        print(f"Presetup done for: {component}")
        simulation = component.pre_setup(config, simulation)

    # Print start time for entire simulation.
    print('Start simulation setup')
    utils.get_time()
    logging.info('Start simulation setup')
    logging.info(utils.get_time())

    # Run setup method for each module.
    simulation.setup()

    # Print time when modules are setup and the simulation starts.
    print('Start running simulation')
    utils.get_time()
    logging.info(print('Start running simulation'))
    logging.info(utils.get_time())

    # output files path
    file_out_dir = os.path.join(config.output_dir, run_output_dir, 'AM_simulation')
    os.makedirs(file_out_dir)

    # Loop over years in the model duration. Step the model forwards a year and save data/metrics.
    for year in range(1, config.time.num_years + 1):

        # Step forwards a year in monthly increments.
        simulation.run_for(duration=pd.Timedelta(days=365.25))

        # Print time when year finished running.
        print(f'Finished running simulation for year: {year}')
        utils.get_time()
        logging.info(print(f'Finished running simulation for year: {year}'))
        logging.info(utils.get_time())

        # get population dataframe.
        pop = simulation.get_population()

        # Assign age brackets to the individuals.
        pop = utils.get_age_bucket(pop)

        # File name and save.
        output_data_filename = 'AM_simulation_year_' + str(year) + '.csv'
        pop.to_csv(os.path.join(file_out_dir, output_data_filename))

        print('In year: ', config.time.start.year + year)
        # Print some summary stats on the simulation.
        print('alive', len(pop[pop['alive'] == 'alive']))

        # Print metrics for desired module.
        # TODO: this can be extended towards a generalised metrics method for each module.
        if 'Mortality()' in config.components:
            print('dead', len(pop[pop['alive'] == 'dead']))
        if 'FertilityAgeSpecificRates()' in config.components:
            print('New children', len(pop[pop['parent_id'] != -1]))

    return simulation
