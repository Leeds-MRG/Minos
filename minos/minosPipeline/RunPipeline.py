#!/usr/bin/env python3
"""Script for initiating and running an Minos microsimulation."""
import logging
import os
from pathlib import Path
from rpy2.robjects.packages import importr

from vivarium import InteractiveContext

import minos.utils as utils

from minos.modules.ageing import Ageing
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
from minos.modules.job_hours import JobHours
from minos.modules.job_sec import JobSec
from minos.modules.hourly_wage import HourlyWage

from minos.modules.S7Labour import S7Labour
from minos.modules.S7Housing import S7Housing
from minos.modules.S7Neighbourhood import S7Neighbourhood
from minos.modules.S7MentalHealth import S7MentalHealth
from minos.modules.S7PhysicalHealth import S7PhysicalHealth
from minos.modules.S7EquivalentIncome import S7EquivalentIncome
from minos.modules.heating import Heating
from minos.modules.financial_situation import FinancialSituation
from minos.modules.behind_on_bills import BehindOnBills

from minos.modules.child_poverty_interventions import hhIncomeIntervention
from minos.modules.child_poverty_interventions import hhIncomeChildUplift
from minos.modules.child_poverty_interventions import hhIncomePovertyLineChildUplift
from minos.modules.child_poverty_interventions import childUplift
from minos.modules.child_poverty_interventions import ChildPovertyReductionRELATIVE
from minos.modules.child_poverty_interventions import ChildPovertyReductionRELATIVE_2
from minos.modules.child_poverty_interventions import ChildPovertyReductionABSOLUTE
from minos.modules.child_poverty_interventions import ChildPovertyReduction
from minos.modules.child_poverty_interventions import ChildPovertyReductionSUSTAIN
from minos.modules.living_wage_interventions import livingWageIntervention
from minos.modules.energy_interventions import energyDownlift, energyDownliftNoSupport
from minos.modules.energy_interventions import GBIS,goodHeatingDummy,fossilFuelReplacementScheme

# from minos.modules.metrics import ChildPovertyMetrics

# for viz.
from minos.outcomes.minos_distribution_visualisation import *



# Do this to suppress warnings from Vivariums code...
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# components = [eval(x) for x in config.components] # more adaptive way but security issues.
# last one in first one off. any module that requires another should be BELOW IT in this order.
# Note priority in vivarium modules supersedes this. two
# Outcome module goes first (last in sim)
components_map = {
    # Outcome module.
    "geeMWB()": geeMWB(),
    "geeYJMWB()": geeYJMWB(),
    "lmmYJMWB()": lmmYJMWB(),
    "lmmDiffMWB()": lmmDiffMWB(),
    "MWB()": MWB(),
    # Intermediary modules
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
    "FinancialSituation()": FinancialSituation(),
    "BehindOnBills()": BehindOnBills(),
    "Loneliness()": Loneliness(),
    "Nutrition()": Nutrition(),
    "lmmYJNutrition()": lmmYJNutrition(),
    "lmmDiffNutrition()": lmmDiffNutrition(),
    "nkidsFertilityAgeSpecificRates()": nkidsFertilityAgeSpecificRates(),
    "FertilityAgeSpecificRates()": FertilityAgeSpecificRates(),
    "Mortality()": Mortality(),
    "Education()": Education(),
    "JobHours()": JobHours(),
    "JobSec()": JobSec(),
    "HourlyWage()": HourlyWage(),
    "Ageing()": Ageing(),
}

SIPHER7_components_map = {  # SIPHER7 stuff
    "S7Labour()": S7Labour(),
    "S7Housing()": S7Housing(),
    "S7Neighbourhood()": S7Neighbourhood(),
    "S7MentalHealth()": S7MentalHealth(),
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

    "ChildPovertyReductionRELATIVE": ChildPovertyReductionRELATIVE(),
    "ChildPovertyReductionRELATIVE_2": ChildPovertyReductionRELATIVE_2(),
    "ChildPovertyReductionABSOLUTE": ChildPovertyReductionABSOLUTE(),
    "ChildPovertyReduction": ChildPovertyReduction(),
    "ChildPovertyReductionSUSTAIN": ChildPovertyReductionSUSTAIN(),
  
    "GBIS": GBIS(),
    "goodHeatingDummy": goodHeatingDummy(),
    "fossilFuelReplacementScheme": fossilFuelReplacementScheme(),

    "childUplift()": childUplift(),

    "25All": childUplift(),
    "50All": childUplift(),
    "75All": childUplift(),
    "100All": childUplift(),

    "25RelativePoverty": childUplift(),
    "50RelativePoverty": childUplift(),
    "75RelativePoverty": childUplift(),
    "100RelativePoverty": childUplift(),

    "10UniversalCredit": childUplift(),
    "20UniversalCredit": childUplift(),
    "25UniversalCredit": childUplift(),
    "30UniversalCredit": childUplift(),
    "35UniversalCredit": childUplift(),
    "40UniversalCredit": childUplift(),
    "45UniversalCredit": childUplift(),
    "50UniversalCredit": childUplift(),
    "60UniversalCredit": childUplift(),
    "70UniversalCredit": childUplift(),
    "75UniversalCredit": childUplift(),
    "80UniversalCredit": childUplift(),
    "90UniversalCredit": childUplift(),
    "100UniversalCredit": childUplift(),

    "25Priority": childUplift(),
    "50Priority": childUplift(),
    "75Priority": childUplift(),
    "100Priority": childUplift(),
}


intervention_kwargs_dict = {
    "25All": {"uplift_amount": 25, "uplift_condition": "who_kids"},
    "50All": {"uplift_amount": 50, "uplift_condition": "who_kids"},
    "75All": {"uplift_amount": 50, "uplift_condition": "who_kids"},
    "100All": {"uplift_amount": 50, "uplift_condition": "who_kids"},

    "25RelativePoverty": {"uplift_amount": 25, "uplift_condition": "who_below_poverty_line_and_kids"},
    "50RelativePoverty": {"uplift_amount": 50, "uplift_condition": "who_below_poverty_line_and_kids"},
    "75RelativePoverty": {"uplift_amount": 75, "uplift_condition": "who_below_poverty_line_and_kids"},
    "100RelativePoverty": {"uplift_amount": 100, "uplift_condition": "who_below_poverty_line_and_kids"},

    "10UniversalCredit": {"uplift_amount": 10, "uplift_condition": "who_universal_credit_and_kids"},
    "20UniversalCredit": {"uplift_amount": 20, "uplift_condition": "who_universal_credit_and_kids"},
    "25UniversalCredit": {"uplift_amount": 25, "uplift_condition": "who_universal_credit_and_kids"},
    "30UniversalCredit": {"uplift_amount": 30, "uplift_condition": "who_universal_credit_and_kids"},
    "35UniversalCredit": {"uplift_amount": 35, "uplift_condition": "who_universal_credit_and_kids"},
    "40UniversalCredit": {"uplift_amount": 40, "uplift_condition": "who_universal_credit_and_kids"},
    "45UniversalCredit": {"uplift_amount": 45, "uplift_condition": "who_universal_credit_and_kids"},
    "50UniversalCredit": {"uplift_amount": 50, "uplift_condition": "who_universal_credit_and_kids"},
    "60UniversalCredit": {"uplift_amount": 60, "uplift_condition": "who_universal_credit_and_kids"},
    "70UniversalCredit": {"uplift_amount": 70, "uplift_condition": "who_universal_credit_and_kids"},
    "75UniversalCredit": {"uplift_amount": 75, "uplift_condition": "who_universal_credit_and_kids"},
    "80UniversalCredit": {"uplift_amount": 80, "uplift_condition": "who_universal_credit_and_kids"},
    "90UniversalCredit": {"uplift_amount": 90, "uplift_condition": "who_universal_credit_and_kids"},
    "100UniversalCredit": {"uplift_amount": 100, "uplift_condition": "who_universal_credit_and_kids"},

    "25Priority": {"uplift_amount": 25, "uplift_condition": "who_vulnerable_subgroups"},
    "50Priority": {"uplift_amount": 50, "uplift_condition": "who_vulnerable_subgroups"},
    "75Priority": {"uplift_amount": 75, "uplift_condition": "who_vulnerable_subgroups"},
    "100Priority": {"uplift_amount": 100, "uplift_condition": "who_vulnerable_subgroups"},
}

replenishment_components_map = {
    "Replenishment()": Replenishment(),
    "NoReplenishment()": NoReplenishment(),
    "ReplenishmentNowcast()": ReplenishmentNowcast(),
    "ReplenishmentScotland()": ReplenishmentScotland(),
}

# metrics_map = {
#     "ChildPovertyMetrics()": ChildPovertyMetrics()
# }


# HR 31/01/24 Updated again
# HR 03/08/23 Updated component priorities
# Order should be (see https://github.com/Leeds-MRG/Minos/issues/291):
# 0. Replenishment
# 1. Mortality
# 2. Fertility and ageing
# 3. Income
# 4. Intervention
# 5. Education
# 6. Everything else except mental wellbeing
# 7. Mental wellbeing, equivalent income (SIPHER7 only)
# 8. Metrics (to be added later)
def get_priorities():
    all_components_map = components_map | SIPHER7_components_map | intervention_components_map | replenishment_components_map
    component_priorities = {}
    component_priorities.update({el: 0 for el in replenishment_components_map})
    component_priorities.update({el: 1 for el in ["Mortality()"]})
    component_priorities.update({el: 2 for el in ["Ageing()"]})
    component_priorities.update({el: 3 for el in ["FertilityAgeSpecificRates()",
                                                  "nkidsFertilityAgeSpecificRates()"]})
    component_priorities.update({el: 4 for el in ["Education()"]})
    component_priorities.update({el: 5 for el in ['Income()',
                                                  'geeIncome()',
                                                  'geeYJIncome()',
                                                  'lmmDiffIncome()',
                                                  'lmmYJIncome()']})  # Any new income-based components to be added here
    component_priorities.update({el: 6 for el in intervention_components_map})

    and_finally = ['MWB()',
                   'geeMWB()',
                   "geeYJMWB()",
                   "lmmYJMWB()",
                   "lmmDiffMWB()",
                   'S7EquivalentIncome()',
                   "lmmYJPCS()"]

    everything_else = [el for el in list(components_map)
                       + list(SIPHER7_components_map) if el not in list(component_priorities) + and_finally]

    # print("Everything else:\n", everything_else)

    component_priorities.update({el: 7 for el in everything_else})
    component_priorities.update({el: 9 for el in and_finally})
    # component_priorities.update({el: 8 for el in metrics_map})

    return component_priorities, all_components_map


def get_intervention_kwargs(intervention):

    intervention_kwargs = {}  # default to em
    if intervention in intervention_kwargs_dict.keys():
        intervention_kwargs = intervention_kwargs_dict[intervention]
    return intervention_kwargs


def type_check(data):
    """
    We have an unfortunate problem with some variables where the type changes when being read in by Vivarium, which the
    framework cannot handle and so throws a paddy. This is particularly annoying with the difference between int and
    float, where the vast majority of int variables are read in as float and so struggle with being updated each wave
    when new values are assigned int. This function is an attempt to fix this once and for all.

    Parameters
    ----------
    data

    Returns
    -------

    """

    data['S7_mental_health'] = data['S7_mental_health'].astype(int)
    data['S7_physical_health'] = data['S7_physical_health'].astype(int)
    data['nutrition_quality_diff'] = data['nutrition_quality_diff'].astype(int)
    data['neighbourhood_safety'] = data['neighbourhood_safety'].astype(int)
    data['job_sec'] = data['job_sec'].astype(int)
    #data['S7_neighbourhood_safety'] = data['S7_neighbourhood_safety'].astype(str)
    data['nkids'] = data['nkids'].astype(float)
    data['financial_situation'] = data['financial_situation'].astype(int)
    data['behind_on_bills'] = data['behind_on_bills'].astype(int)

    return data


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
    # Check modules are valid and convert to modules
    components_raw = config['components']
    if intervention is not None:
        #components_raw += intervention
        components_raw.append(intervention)
        intervention_kwargs = get_intervention_kwargs(intervention)
        config.update({'intervention_parameters': intervention_kwargs})  # add dict of intervention kwargs to config.

    component_priority_map, component_name_map = get_priorities()
    components = [component_name_map[c] for c in components_raw if c in component_name_map]
    components_invalid = [component_name_map[c] for c in components_raw if c not in component_name_map]

    print("Components below were not recognised and were removed from simulation:\n", components_invalid)
    print("Priorities for components are below; change in components map if incorrect:")
    map_rev = {v: k for k, v in component_name_map.items()}
    for c in components:
        print(c, component_priority_map[map_rev[c]])

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

    # Attach module priorities to simulation for retrieval later by each module
    # simulation.component_priority_map = component_priority_map
    simulation._data.write("component_priority_map", component_priority_map)

    rpy2_modules = {"base": importr('base'),
                    "stats": importr('stats'),
                    "nnet": importr("nnet"),
                    "ordinal": importr('ordinal'),
                    "zeroinfl": importr("pscl"),
                    "bestNormalize": importr("bestNormalize"),
                    "VGAM": importr("VGAM"),
                    "lme4": importr("lme4"),
                    "randomForest": importr("randomForest"),
                    "MASS": importr("MASS"),
                    "ranger": importr("ranger")
                    }
    simulation._data.write("rpy2_modules",
                           rpy2_modules)

    logging.info("Components included:")
    # Run pre-setup method for each module.
    for component in components:
        simulation = component.pre_setup(config, simulation)
        # print(f"Presetup done for: {component}")
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

    # Force type casting for certain problem variables
    pop = type_check(pop)

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

    return output_data_filename
