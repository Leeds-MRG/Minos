#!/usr/bin/env python3
"""Script for initiating and running an AngryMob microsimulation."""
import datetime
import logging
import os
from pathlib import Path

import pandas as pd

from vivarium import InteractiveContext

import utils as utils

from minos.modules.mortality import Mortality
from minos.modules.replenishment import Replenishment
from minos.modules.add_new_birth_cohorts import FertilityAgeSpecificRates
from minos.modules import Depression
from minos.modules import Employment


def RunPipeline(config, start_population_size):
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
    # TODO: python 3.10 will have case switching which makes this much prettier in terms of module initiation.

    #components = [eval(x) for x in config.components]

    # last one in first one off. any module that requires another should be BELOW IT in this order.
    if "Depression()" in config.components:
        components.append(Depression())
    if "Employment()" in config.components:
        components.append(Employment())
   #if "Education()" in config.components:
   #     components.append(Education())
    if "FertilityAgeSpecificRates()" in config.components:
        components.append(FertilityAgeSpecificRates())
    if "Mortality()" in config.components:
        components.append(Mortality())
    if "Replenishment()" in config.components:
        components.append(Replenishment())

    # Run write_config method for each class loading required attributes to the yaml.
    for component in components:
        print(f"Written Config for: {component}")
        config = component.write_config(config)

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
    # This isn't the case with AngryMob as each module is bespoke and can be given a pre_setup method.
    # Basically, this is very pedantic but easier if a lot more preamble is needed later.

    # Run pre-setup method for each module.
    for component in components:
        print(f"Presetup done for: {component}")
        simulation = component.pre_setup(config, simulation)

    # Print start time for entire simulation.
    print('Start simulation setup')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Run setup method for each module.
    simulation.setup()

    # Print time when modules are setup and the simulation starts.
    print('Start running simulation')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Loop over years in the model duration. Step the model forwards a year and save data/metrics.
    for year in range(1, config.time.num_years + 1):

        # Step forwards a year in monthly increments.
        simulation.run_for(duration=pd.Timedelta(days=365.25))

        # Print time when year finished running.
        print('Finished running simulation for year:', year)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        pop = simulation.get_population()

        # Assign age brackets to the individuals.
        pop = utils.get_age_bucket(pop)

        # Save the output file to csv. Give data its own subdirectory for the given year.
        year_output_dir = os.path.join(os.path.join(config.output_dir, 'year_' + str(year)))
        os.makedirs(year_output_dir, exist_ok=True)

        # File name and save.
        output_data_filename = 'AM_simulation_year_' + str(year) + '.csv'
        pop.to_csv(os.path.join(year_output_dir, output_data_filename))

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
