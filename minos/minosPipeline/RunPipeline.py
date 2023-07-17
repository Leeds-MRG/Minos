#!/usr/bin/env python3
"""Script for initiating and running an Minos microsimulation."""
import logging
import os
from pathlib import Path
from rpy2.robjects.packages import importr

# Do this to suppress warnings from Vivariums code...
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from vivarium import InteractiveContext

import minos.utils as utils

from minos.modules.mortality import Mortality
from minos.modules.replenishment import Replenishment
from minos.modules.replenishment import NoReplenishment
from minos.modules.replenishment_nowcast import ReplenishmentNowcast
from minos.modules.replenishment_scotland import ReplenishmentScotland
from minos.modules.add_new_birth_cohorts import FertilityAgeSpecificRates, nkidsFertilityAgeSpecificRates
from minos.modules.housing import Housing
from minos.modules.income import Income, geeIncome, geeYJIncome, lmmDiffIncome, lmmYJIncome
from minos.modules.mental_wellbeing import MWB, geeMWB, geeYJMWB, lmmDiffMWB, lmmYJMWB
from minos.modules.labour import Labour
from minos.modules.neighbourhood import Neighbourhood
from minos.modules.alcohol import Alcohol
from minos.modules.tobacco import Tobacco
from minos.modules.loneliness import Loneliness
from minos.modules.education import Education
from minos.modules.nutrition import Nutrition, lmmYJNutrition, lmmDiffNutrition

from minos.modules.S7Labour import S7Labour
from minos.modules.S7Housing import S7Housing
from minos.modules.S7Neighbourhood import S7Neighbourhood
from minos.modules.S7MentalHealth import S7MentalHealth
from minos.modules.S7PhysicalHealth import S7PhysicalHealth
from minos.modules.S7EquivalentIncome import S7EquivalentIncome
from minos.modules.heating import Heating
from minos.modules.financial_situation import financialSituation

from minos.modules.intervention import hhIncomeIntervention
from minos.modules.intervention import hhIncomeChildUplift
from minos.modules.intervention import hhIncomePovertyLineChildUplift
from minos.modules.intervention import livingWageIntervention
from minos.modules.intervention import energyDownlift, energyDownliftNoSupport

# for viz.
from minos.outcomes.minos_distribution_visualisation import *


def validate_components(config_components, intervention):
    """

    Parameters
    ----------
    config_components: list
        List of reprs from vivarium modules
    intervention: bool
        Is an intervention included in the modules list?

    Returns
    -------
        component_list: list
            List of component module classes.
    """

    #components = [eval(x) for x in config.components] # more adapative way but security issues.
    # last one in first one off. any module that requires another should be BELOW IT in this order.
    # Note priority in vivarium modules supercedes this. two
    # Outcome module goes first (last in sim)
    components_map = {
        # Outcome module.
        "geeMWB()": geeMWB(),
        "geeYJMWB()": geeYJMWB(),
        "lmmYJMWB()": lmmYJMWB(),
        "lmmDiffMWB()": lmmDiffMWB(),
        "MWB()": MWB(),
        #Intermediary modules
        "Tobacco()": Tobacco(),
        "Alcohol()": Alcohol(),
        "Neighbourhood()": Neighbourhood(),
        "Labour()": Labour(),
        "Heating()": Heating(),
        "Housing()": Housing(),
        "geeIncome()": geeIncome(),
        "geeYJIncome()": geeYJIncome(),
        "lmmDiffIncome()": lmmDiffIncome(),
        "lmmYJIncome()": lmmYJIncome(),
        "Income()": Income(),
        "financialSituation()": financialSituation(),
        "Loneliness()": Loneliness(),
        "Nutrition()": Nutrition(),
        "lmmYJNutrition()": lmmYJNutrition(),
        "lmmDiffNutrition()": lmmDiffNutrition(),
        "nkidsFertilityAgeSpecificRates()": nkidsFertilityAgeSpecificRates(),
        "FertilityAgeSpecificRates()": FertilityAgeSpecificRates(),
        "Mortality()": Mortality(),
        "Education()": Education(),
    }

    SIPHER7_components_map = {  # SIPHER7 stuff
        "S7Labour()" : S7Labour(),
        "S7Housing()" : S7Housing(),
        "S7Neighbourhood()": S7Neighbourhood(),
        "S7MentalHealth()" : S7MentalHealth(),
        "S7PhysicalHealth()": S7PhysicalHealth(),
        "S7EquivalentIncome()": S7EquivalentIncome()
    }

    intervention_components_map = {        #Interventions
        "hhIncomeIntervention": hhIncomeIntervention(),
        "hhIncomeChildUplift": hhIncomeChildUplift(),
        "hhIncomePovertyLineChildUplift": hhIncomePovertyLineChildUplift(),
        "livingWageIntervention": livingWageIntervention(),
        "energyDownlift": energyDownlift(),
        "energyDownliftNoSupport": energyDownliftNoSupport(),
    }

    replenishment_components_map = {
        "Replenishment()": Replenishment(),
        "NoReplenishment()": NoReplenishment(),
        "ReplenishmentNowcast()": ReplenishmentNowcast(),
        "ReplenishmentScotland()": ReplenishmentScotland(),
    }

    component_list = []
    replenishment_component = []
    for component in config_components:
        if component in components_map.keys():
            # add non intervention components
            component_list.append(components_map[component])
        elif component in SIPHER7_components_map.keys():
            component_list.append(SIPHER7_components_map[component])
        elif component in replenishment_components_map.keys():
            replenishment_component.append(replenishment_components_map[component])
        else:
            print("Warning! Component in config not found when running pipeline. Are you sure its in the minos/minosPipeline/RunPipeline.py script?")

    # TODO: include some error handling for choosing interventions
    # Can do this using assertions
    # i.e. try { AssertThat(intervention is in list(<int1>, <int2>) ...
    # or even cleverer if we can get the repr()'s from the intervention classes to automate this step
    if intervention in intervention_components_map.keys():
        # add intervention components.
        component_list.append(intervention_components_map[intervention])

    component_list += replenishment_component # make sure replenishment component goes LAST. intervention goes second to last.
    return component_list


def RunPipeline(config, intervention=None):
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
    # Check each of the modules is present.

    # Replenishment always go last. (first in sim)
    components = validate_components(config['components'], intervention)

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

    rpy2_modules = {"base": importr('base'),
                    "stats": importr('stats'),
                    "nnet": importr("nnet"),
                    "ordinal": importr('ordinal'),
                    "zeroinfl": importr("pscl"),
                    "bestNormalize": importr("bestNormalize"),
                    "VGAM": importr("VGAM"),
                    "lme4": importr("lme4"),
                    }
    simulation._data.write("rpy2_modules",
                           rpy2_modules)

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
    if 'run_ID' in config.keys():
        print(config.run_ID)
        output_data_filename += str(config.run_ID).zfill(4) + '_' # pad with zeros so files are saved in correct order.
        output_data_filename += str(config.run_ID_names) + '_'

    # Now add year to output file name
    output_data_filename += f"{config.time.start.year + year}.csv"

    return(output_data_filename)