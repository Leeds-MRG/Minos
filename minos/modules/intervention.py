"""
Module for applying any interventions to the base population from replenishment.
"""

import itertools
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from minos.modules.base_module import Base
from minos.data_generation import generate_composite_vars as gcv
import os
from os.path import dirname as up


class hhIncomeIntervention():

    @property
    def name(self):
        return "hh_income_intervention"

    def __repr__(self):
        return "hhIncomeIntervention()"

    # In Daedalus pre_setup was done in the run_pipeline file. This way is tidier and more modular in my opinion.
    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run into the config and simulation object.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run.

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run with updated config/inputs.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        # nothing done here yet. transition models specified by year later.
        print("print sys argv")
        print(sys.argv)
        print(config.keys())
        uplift = [0, 1000, 10000]  # uplift amount
        percentage_uplift = [10, 25, 75]  # uplift proportion.
        run_id = np.arange(1, 50 + 1, 1)  # 50 repeats for each combination of the above parameters
        parameter_lists = list(itertools.product(*[uplift, percentage_uplift, run_id]))
        if 'run_id' in config.keys():
            # Pick a set of parameters according to task_id arg from batch run.
            run_id = config['run_id']
        else:
            # If no task id specified (you should) choose the first task as a test.
            run_id = 1
        parameters = parameter_lists[run_id]
        config.update({'experiment_parameters': parameters}, source=str(Path(__file__).resolve()))
        config.update({'experiment_parameters_names': ['uplift', 'prop', 'id']}, source=str(Path(__file__).resolve()))

        self.uplift = parameters[0]
        self.prop = parameters[1]

        return simulation

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income"]
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the hh_income intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        pop['hh_income'] -= (self.uplift * pop["income_boosted"])  # reset boost if people move out of bottom decile.
        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        who_uplifted = pop['hh_income'] <= pop['hh_income'].quantile(self.prop / 100)
        pop['income_boosted'] = who_uplifted
        pop['boost_amount'] = (self.uplift * pop["income_boosted"])
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) for debugging. to ensure mean value is feasible. errors can hugely inflate it.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(who_uplifted)}")
        logging.info(f"\t...which is {(sum(who_uplifted) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'].mean()}")


####################################################################################################################

class hhIncomeChildUplift(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "hh_income_20_uplift"

    def __repr__(self):
        return "hhIncomeChildUplift()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income", 'nkids']
        columns_created = ["income_boosted", "boost_amount"]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the hh_income child uplift intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # print(np.mean(pop['hh_income'])) # for debugging purposes.
        # TODO probably a faster way to do this than resetting the whole column.
        # pop['hh_income'] -= pop['boost_amount']  # reset boost if people move out of bottom decile.
        # pop['boost_amount'] = 0
        pop['boost_amount'] = (
                    25 * 30.436875 * pop['nkids'] / 7)  # £25 per week * 30.463/7 weeks per average month * nkids.
        pop['income_boosted'] = (pop['boost_amount'] != 0)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(pop['income_boosted']) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'][pop['income_boosted']].mean()}")


########################################################################################################################
class hhIncomePovertyLineChildUplift(Base):
    """uplift intervention module. £20 uplift per child for households below the poverty line."""

    @property
    def name(self):
        return "hh_income_poverty_live_20_uplift"

    def __repr__(self):
        return "hhIncomePovertyLineChildUplift()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income"]
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,  # who boosted?
                                   'boost_amount': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        logging.info("INTERVENTION:")
        logging.info(
            f"\tApplying effects of the hh_income poverty line child uplift intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        # pop['hh_income'] -= pop['boost_amount']
        # pop['boost_amount'] = 0
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        who_uplifted = (pop['hh_income'] <= np.nanmedian(pop['hh_income']) * 0.6)  #
        pop['boost_amount'] = (
                    who_uplifted * 25 * 30.436875 / 7)  # £20 per child per week uplift for everyone under poverty line.

        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        pop['income_boosted'] = who_uplifted
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(pop['income_boosted']) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'][pop['income_boosted']].mean()}")


class livingWageIntervention(Base):
    """Living Wage Intervention. Increase hh_income for anyone who doesn't earn a living wage to bridge the gap."""

    @property
    def name(self):
        return "living_wage_intervention"

    def __repr__(self):
        return "livingWageIntervention()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().
        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.
        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ['hh_income', 'hourly_wage', 'job_hours', 'region', 'sex', 'ethnicity', 'alive', 'job_sector']
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        """
        Parameters
        ----------
        pop_data
        Returns
        -------
        """
        pop_update = pd.DataFrame({'income_boosted': False,  # who boosted?
                                   'boost_amount': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """
        Parameters
        ----------
        event
        Returns
        -------
        """

        logging.info("INTERVENTION:")
        logging.info(
            f"\tApplying effects of the living wage intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive' and job_sector == 2")
        # TODO probably a faster way to do this than resetting the whole column.
        # pop['hh_income'] -= pop['boost_amount']
        # pop['boost_amount'] = 0
        # Now get who gets uplift (different for London/notLondon)
        who_uplifted_London = pop['hourly_wage'] > 0
        who_uplifted_London *= pop['region'] == 'London'
        who_uplifted_London *= pop['hourly_wage'] < 11.95
        who_uplifted_notLondon = pop['hourly_wage'] > 0
        who_uplifted_notLondon *= pop['region'] != 'London'
        who_uplifted_notLondon *= pop['hourly_wage'] < 10.90
        # Calculate boost amount (difference between hourly wage and living wage multiplied by hours worked in a week (extended to month))
        # boost_amount = hourly_wage_diff * hours_worked_monthly
        pop['boost_amount'] = (11.95 - pop['hourly_wage']) * (pop['job_hours'] * 4.2) * who_uplifted_London
        pop['boost_amount'] += (10.90 - pop['hourly_wage']) * (pop['job_hours'] * 4.2) * who_uplifted_notLondon

        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        pop['income_boosted'] = who_uplifted_notLondon | who_uplifted_London
        # pop.drop(labels='who_uplifted', inplace=True)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of household composition.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(who_uplifted_London) + sum(who_uplifted_notLondon)}")
        logging.info(
            f"\t...which is {((sum(who_uplifted_London) + sum(who_uplifted_notLondon)) / len(pop)) * 100}% of the total population.")
        logging.info(f"\t\tLondon n: {sum(who_uplifted_London)}")
        logging.info(f"\t\tLondon %: {(sum(who_uplifted_London) / len(pop[pop['region'] == 'London'])) * 100}")
        logging.info(f"\t\tNot London n: {sum(who_uplifted_notLondon)}")
        logging.info(f"\t\tNot London %: {(sum(who_uplifted_notLondon) / len(pop[pop['region'] != 'London'])) * 100}")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'][pop['income_boosted'] == True].sum()}")
        logging.info(f"\t\tLondon: {pop[who_uplifted_London]['boost_amount'].sum()}")
        logging.info(f"\t\tNot London: {pop[who_uplifted_notLondon]['boost_amount'].sum()}")
        logging.info(f"\tMean weekly boost amount: {pop['boost_amount'][pop['income_boosted'] == True].mean()}")
        logging.info(f"\t\tLondon: {pop[who_uplifted_London]['boost_amount'].mean()}")
        logging.info(f"\t\tNot London: {pop[who_uplifted_notLondon]['boost_amount'].mean()}")


class energyDownlift(Base):
    @property
    def name(self):
        return "energy_downlift"

    def __repr__(self):
        return "energyDownlift()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income", 'yearly_energy']
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,  # who boosted?
                                   'boost_amount': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the energy downlift intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        # pop['hh_income'] -= pop['boost_amount']
        # pop['boost_amount'] = 0
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        # TODO is an 80% increase correct? More dynamic assumption needed?
        # pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (2.3 - 1))  # 130% of monthly fuel bill subtracted from dhi.
        pop['boost_amount'] = (
                    -(pop['yearly_energy'] / 12) * (1.8 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes constant fuel expenditure beyond negative hh income. need some kind of energy module to adjust behaviour..
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people downlifted: {sum(pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(pop['income_boosted']) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'][pop['income_boosted']].mean()}")


class energyDownliftNoSupport(Base):
    @property
    def name(self):
        return "energy_downlift_no_support"

    def __repr__(self):
        return "energyDownliftNoSupport()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income", 'yearly_energy']
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=3)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,  # who boosted?
                                   'boost_amount': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        # pop['hh_income'] -= pop['boost_amount']
        # pop['boost_amount'] = 0
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        # TODO is an 80% increase correct? More dynamic assumption needed?
        pop['boost_amount'] = (
                    -(pop['yearly_energy'] / 12) * (3.0 - 1))  # 130% of monthly fuel bill subtracted from dhi.
        # pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (1.8 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes constant fuel expenditure beyond negative hh income. need some kind of energy module to adjust behaviour..
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


class ChildPovertyReductionRANDOM(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_random"

    def __repr__(self):
        return "ChildPovertyReductionRANDOM()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income", 'nkids', 'hidp']
        columns_created = ["income_boosted", "boost_amount"]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child poverty reduction intervention in year {event.time.year}...")

        # This intervention will reduce the % of children living in families in relative poverty to a defined proportion
        # by a set end year. As a first attempt, we will reduce the numbers to fewer than 10% of children living in
        # relative poverty by 2030

        # STEPS;
        # 1. Calculate median hh_income over all households
        # 2. Calculate total kids in sample
        # 3. Find all households in relative poverty
        # 4. Calculate the proportion of children in relative poverty (hh_income < 60% of median hh_income in that year)
        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        # 7. Profit

        # set parameters
        end_year = 2030
        target_pov_prop = 0.1

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")
        # Reset the previous income_boosted for testing
        full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        self.population_view.update(full_pop[['income_boosted', 'boost_amount']])
        median_income = full_pop['hh_income'].median()
        # 2. Total number of kids
        nkids_total = full_pop['nkids'].sum()
        # TODO probably a faster way to do this than resetting the whole column.
        # full_pop['hh_income'] -= full_pop['boost_amount']  # reset boost
        # 3. Find all households in relative poverty
        relative_poverty_threshold = median_income * 0.6
        target_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                    f"{relative_poverty_threshold}")
        # 4. Calculate the proportion of children in relative poverty
        target_pop_nkids = target_pop['nkids'].sum()
        prop_in_poverty = target_pop_nkids / nkids_total
        print(f"Percentage of children in poverty: {prop_in_poverty * 100}")

        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # we need to reduce this proportion down to 10% by 2030, so we can calculate the number of years we have left
        # and then the proportion to reduce in that year
        years_remaining = end_year - event.time.year

        if prop_in_poverty > target_pov_prop:
            prop_above_target = prop_in_poverty - target_pov_prop
        else:
            prop_above_target = 0

        if years_remaining > 0:  # before 2030
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 0:  # in 2030
            proportion_to_uplift = prop_above_target
        elif years_remaining < 0:  # after 2030, fix to target level
            proportion_to_uplift = prop_above_target
        print(f"Proportion to uplift by {end_year}: {prop_above_target}")
        print(f"Proportion to uplift this year: {proportion_to_uplift}")

        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        nkids_to_uplift = round(target_pop_nkids * proportion_to_uplift)

        # 7. Randomly select households by hidp until we hit the nkids_to_uplift target
        target_hidps = []
        kids = 0
        for i in target_pop.sample(frac=1).iterrows():
            if (kids + i[1]['nkids']) <= nkids_to_uplift:
                kids += i[1]['nkids']
                target_hidps.append(i[1]['hidp'])
            if kids >= nkids_to_uplift:
                break

        print(f"Number of households to uplift: {len(target_hidps)}")
        print(f"Number of children to uplift: {target_pop[target_pop['hidp'].isin(target_hidps)]['nkids'].sum()}")

        # 8. Calculate boost amount for each household and apply
        uplift_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & hidp.isin({target_hidps})")
        uplift_pop['boost_amount'] = median_income - uplift_pop['hh_income']
        uplift_pop['income_boosted'] = (uplift_pop['boost_amount'] != 0)
        uplift_pop['hh_income'] += uplift_pop['boost_amount']

        # 9. Update original population with uplifted values
        self.population_view.update(uplift_pop[['hh_income', 'income_boosted', 'boost_amount']])

        target_pop2 = self.population_view.get(event.index,
                                               query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                     f"{relative_poverty_threshold}")

        print(f"Proportion of children in poverty AFTER intervention: {target_pop2['nkids'].sum() / nkids_total}")

        # 10. Logging
        logging.info(f"\tNumber of people uplifted: {sum(uplift_pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(uplift_pop['income_boosted']) / len(full_pop)) * 100}% of the total "
                     f"population.")
        logging.info(f"\t...and {(sum(uplift_pop['income_boosted']) / len(target_pop)) * 100}% of the population in"
                     f"poverty.")
        logging.info(f"\tTotal boost amount: {uplift_pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount across households in poverty: "
                     f"{uplift_pop['boost_amount'][uplift_pop['income_boosted']].mean()}")


class ChildPovertyReductionSUSTAIN(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_sustain"

    def __repr__(self):
        return "ChildPovertyReductionSUSTAIN()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income", 'nkids', 'hidp']
        columns_created = ["income_boosted", "boost_amount"]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child poverty reduction intervention in year {event.time.year}...")

        # This intervention will reduce the % of children living in families in relative poverty to a defined proportion
        # by a set end year. As a first attempt, we will reduce the numbers to fewer than 10% of children living in
        # relative poverty by 2030

        # STEPS;
        # 1. Calculate median hh_income over all households
        # 2. Calculate total kids in sample
        # 3. Find all households in relative poverty
        # 4. Calculate the proportion of children in relative poverty (hh_income < 60% of median hh_income in that year)
        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        # 7. Profit

        # set parameters
        end_year = 2030
        target_pov_prop = 0.1

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")
        # Reset the previous income_boosted for testing
        # full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        self.population_view.update(full_pop[['boost_amount']])
        median_income = full_pop['hh_income'].median()
        # 2. Total number of kids
        nkids_total = full_pop['nkids'].sum()

        # # HR 07/11/23 Correcting method of calculating total number of kids in full pop
        # Select first instance of each hidp to avoid duplicating nkids
        # nkids_total = full_pop.drop_duplicates(subset=['hidp'], keep='first')['nkids'].sum()
        # full_pop_nodupes = full_pop.drop_duplicates(subset=['hidp'], keep='first')
        # nkids_pop = full_pop_nodupes['nkids'].sum()
        # print('## TOTAL KIDS ## ')
        # print('Method 1 (simple sum): {}'.format(nkids_total))
        # print('Method 2 (unique HHs): {}'.format(nkids_pop))

        # TODO probably a faster way to do this than resetting the whole column.
        # full_pop['hh_income'] -= full_pop['boost_amount']  # reset boost
        # 3. Find all households in relative poverty
        relative_poverty_threshold = median_income * 0.6
        target_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                    f"{relative_poverty_threshold}")
        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['boost_amount'][(target_pop['income_boosted'] == True) &  # previously uplifted
                                   (target_pop['hh_income'] < median_income)] = median_income - target_pop['hh_income']
        target_pop['hh_income'] = target_pop['hh_income'] + target_pop['boost_amount']
        self.population_view.update(target_pop[['hh_income', 'boost_amount']])
        target_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                    f"{relative_poverty_threshold}")
        # 4. Calculate the proportion of children in relative poverty
        target_pop_nkids = target_pop['nkids'].sum()
        prop_in_poverty = target_pop_nkids / nkids_total
        print(f"Percentage of children in poverty: {prop_in_poverty * 100}")

        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # we need to reduce this proportion down to 10% by 2030, so we can calculate the number of years we have left
        # and then the proportion to reduce in that year
        years_remaining = end_year - event.time.year

        if prop_in_poverty > target_pov_prop:
            prop_above_target = prop_in_poverty - target_pov_prop
        else:
            prop_above_target = 0

        if years_remaining > 0:  # before 2030
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 0:  # in 2030
            proportion_to_uplift = prop_above_target
        elif years_remaining < 0:  # after 2030, fix to target level
            proportion_to_uplift = prop_above_target
        print(f"Proportion to uplift by {end_year}: {prop_above_target}")
        print(f"Proportion to uplift this year: {proportion_to_uplift}")

        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        nkids_to_uplift = round(target_pop_nkids * proportion_to_uplift)

        # 7. Randomly select households by hidp until we hit the nkids_to_uplift target
        target_hidps = []
        kids = 0
        for i in target_pop.sample(frac=1).iterrows():
            if (kids + i[1]['nkids']) <= nkids_to_uplift:
                kids += i[1]['nkids']
                target_hidps.append(i[1]['hidp'])
            if kids >= nkids_to_uplift:
                break

        print(f"Number of households to uplift: {len(target_hidps)}")
        print(f"Number of children to uplift: {target_pop[target_pop['hidp'].isin(target_hidps)]['nkids'].sum()}")

        # 8. Calculate boost amount for each household and apply
        uplift_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & hidp.isin({target_hidps})")
        uplift_pop['boost_amount'] = median_income - uplift_pop['hh_income']
        uplift_pop['income_boosted'] = (uplift_pop['boost_amount'] != 0)
        uplift_pop['hh_income'] += uplift_pop['boost_amount']

        # 9. Update original population with uplifted values
        self.population_view.update(uplift_pop[['hh_income', 'income_boosted', 'boost_amount']])

        target_pop2 = self.population_view.get(event.index,
                                               query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                     f"{relative_poverty_threshold}")

        print(f"Proportion of children in poverty AFTER intervention: {target_pop2['nkids'].sum() / nkids_total}")

        # 10. Logging
        logging.info(f"\tNumber of people uplifted: {sum(uplift_pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(uplift_pop['income_boosted']) / len(full_pop)) * 100}% of the total "
                     f"population.")
        logging.info(f"\t...and {(sum(uplift_pop['income_boosted']) / len(target_pop)) * 100}% of the population in"
                     f"poverty.")
        logging.info(f"\tTotal boost amount: {uplift_pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount across households in poverty: "
                     f"{uplift_pop['boost_amount'][uplift_pop['income_boosted']].mean()}")


''' HR 20/11/23 Default intervention parameters - PUTTING HERE FOR TESTING BUT MAY MOVE LATER '''
CONFIG_DEFAULT = {'child_poverty_target': 1,
                  'target_year': 2030,
                  'target_poverty_proportion': 0.05,
                  'input_population': 'all',
                  'target_group': 'all',
                  'intervention_method': 1,
                  'intervention_amount': 25,
                  }

POVERTY_STATE_MAP = {1: 'relative_poverty',
                     2: 'absolute_poverty',
                     3: 'low_income_material_deprivation',
                     4: 'persistent_poverty'}


class ChildPovertyIntervention(Base):
    """ Intervention to address UK gov/Scottish Government's four child poverty targets """

    @property
    def name(self):
        return "child_poverty_intervention"

    def __repr__(self):
        return "ChildPovertyIntervention()"

    @staticmethod
    def pre_setup(config, simulation):

        # Grab all intervention parameters; anything in config overrides defaults
        intervention_parameters = {**CONFIG_DEFAULT, **config}

        # Attach to simulation object for retrieval during setup
        simulation._data.write("intervention_parameters",
                               intervention_parameters)

        return simulation

    def setup(self, builder):

        # Grab intervention parameters parsed in pre-setup
        self.intervention_parameters = builder.data.load("intervention_parameters")

        # print('\n## TESTING')
        # print('Intervention params passed from pre-setup to setup:')
        # for param, value in self.intervention_parameters.items():
        #     print('Param name: {}, value: {}'.format(param, value))
        # print('##\n')

        # Specify and create/add all variables required for operation of intervention
        view_columns = ['time',
                        "hh_income",
                        'nkids',
                        'hidp',
                        'pidp',
                        'relative_poverty_percentile',
                        'relative_poverty',
                        'absolute_poverty_percentile',
                        'absolute_poverty',
                        'low_income_material_deprivation',
                        'relative_poverty_history',
                        'persistent_poverty',
                        ]
        columns_created = ["total_boost_amount",
                           "times_boosted",
                           ]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Specify what to do at a time step
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'total_boost_amount': 0.0,
                                   'times_boosted': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child poverty reduction intervention in year {event.time.year}...")

        cpt = self.intervention_parameters['child_poverty_target']
        int_amount = self.intervention_parameters['intervention_amount']
        int_method = self.intervention_parameters['intervention_method']
        target_year = self.intervention_parameters['target_year']
        target_proportion = self.intervention_parameters['target_poverty_proportion']

        print("CP target {}".format(cpt))
        print('Intervention method {}'.format(int_method))
        print('Payment amount: {} p/c p/w'.format(int_amount))

        year = event.time.year
        pop = self.population_view.get(event.index, query='alive == "alive"')
        # hidp_sub = pop.loc[pop['time'] == year].drop_duplicates(subset=['hidp'], keep='first')

        ''' Intervention method 1: apply Scottish Child Payment '''
        if int_method == 1:
            pop = apply_child_payment(pop,
                                      poverty_state=POVERTY_STATE_MAP[cpt],
                                      amount=int_amount)

        ''' Intervention method 2: supplement hh_income such that CP target met by target year, aka "inverse" method '''
        if int_method == 2:
            pop = apply_target_payment(pop,
                                       poverty_state=POVERTY_STATE_MAP[cpt],
                                       target_year=target_year,
                                       target_proportion=target_proportion)

        # median_yearly = hidp_sub.loc[hidp_sub['hh_income'] > 0.0]['hh_income'].median()
        # print("Median income for year {}: {}".format(year, median_yearly))

        # Update population with boosted income and associated variables
        self.population_view.update(pop[['hh_income',
                                         'times_boosted',
                                         'total_boost_amount',
                                         ]])

        # Output some stats
        in_pp = len(pop.loc[pop['relative_poverty'].astype(int) == 1])
        all_valid = len(pop.loc[pop['relative_poverty'].astype(int).isin([0, 1])])
        prop = 100*in_pp/all_valid
        print('Proportion of people in relative poverty: {}/{} = {:.3f}'.format(in_pp, all_valid, prop))

        in_pp = len(pop.loc[pop['absolute_poverty'].astype(int) == 1])
        all_valid = len(pop.loc[pop['absolute_poverty'].astype(int).isin([0, 1])])
        prop = 100*in_pp/all_valid
        print('Proportion of people in absolute poverty: {}/{} = {:.3f}'.format(in_pp, all_valid, prop))

        in_pp = len(pop.loc[pop['low_income_material_deprivation'].astype(int) == 1])
        all_valid = len(pop.loc[pop['low_income_material_deprivation'].astype(int).isin([0, 1])])
        prop = 100*in_pp/all_valid
        print('Proportion of people with low income and material deprivation: {}/{} = {:.3f}'.format(in_pp, all_valid, prop))

        in_pp = len(pop.loc[pop['persistent_poverty'].astype(int) == 1])
        all_valid = len(pop.loc[pop['persistent_poverty'].astype(int).isin([0, 1])])
        prop = 100*in_pp/all_valid
        print('Proportion of people in persistent poverty: {}/{} = {:.3f}'.format(in_pp, all_valid, prop))


''' HR 21/11/23 Scottish Child Payment implementation
    Must be tested against functionality of Rob's child payment intervention '''
def apply_child_payment(data,
                        poverty_state=POVERTY_STATE_MAP[CONFIG_DEFAULT['child_poverty_target']],
                        amount=CONFIG_DEFAULT['intervention_amount'],
                        ):

    # Payment is weekly, so must convert to monthly to agree with hh_income
    monthly_amount = 52*amount/12
    # print("Weekly/monthly amount: {}/{}".format(amount, monthly_amount))

    # Create map of children per eligible household; slight overkill to avoid duplicate values of nkids per hh
    eligible = data.loc[data[poverty_state].astype(int) == 1]
    nkids_map = dict(zip(eligible['hidp'], eligible['nkids']))

    # Apply child payment to hh income of everyone eligible per number of kids in hh
    data.loc[eligible.index, 'hh_income'] += monthly_amount*data['hidp'].map(nkids_map)

    # Increment boost info
    data.loc[eligible.index, 'times_boosted'] += 1
    data.loc[eligible.index, 'total_boost_amount'] += 12 * monthly_amount

    return data


''' HR 21/11/23 "Inverse problem" intervention to supplement hh income to be above poverty threshold
    Must be tested against functionality of Luke's SUSTAIN intervention code '''
def apply_target_payment(data,
                         poverty_state=POVERTY_STATE_MAP[CONFIG_DEFAULT['child_poverty_target']],
                         target_year=CONFIG_DEFAULT['target_year'],
                         target_proportion=CONFIG_DEFAULT['target_poverty_proportion'],
                         ):

    return data


# if __name__ == "__main__":
#
#     ''' HR 20/11/23 For child poverty testing '''
#     files = ['2016_US_cohort.csv',
#              # '2017_US_cohort.csv',
#              # '2018_US_cohort.csv',
#              # '2019_US_cohort.csv',
#              # '2020_US_cohort.csv',
#              ]
#
#     # Get five years data to check persistent poverty sequence logic
#     # Copied some from US_utils.load_multiple_data
#     data = pd.concat([pd.read_csv(os.path.join(up(up(up(__file__))), 'data', 'corrected_US', el)) for el in files])
#     data = data.reset_index(drop=True)
#
#     data = gcv.generate_hh_income(data)
#     data = gcv.generate_child_material_deprivation(data)
#     data = gcv.calculate_poverty_variables(data)
#
#     data['times_boosted'] = 0
#     data['total_boost_amount'] = 0.0
#     data = apply_child_payment(data)


### some test on time steps for variious scotland interventions
# scotland only.
# pop = self.population_view.get(event.index, query="alive =='alive' and region=='Scotland'")

# disabled people. labour state.
# pop = self.population_view.get(event.index, query="alive =='alive' and labour_state=='Sick/Disabled'")
# unemployed adults. unemployed labour state.
# pop = self.population_view.get(event.index, query="alive =='alive' and labour_state=='Unemployed'")

# minority ethnic households
# pop = pop.loc[pop['ethnicity'].isin(minorities) # BAN,BLA,BLC,CHI,IND,OBL,WHO,OAS,PAK any others?

# child poverty priority groups (3+ children, mother under 25). nkids >3/ nkids >0 and female and under 25. further groups depend on data.)
# pop = self.population_view.get(event.index, query="alive =='alive' and nkids>=3")
# pop = self.population_view.get(event.index, query="alive =='alive' and age<=25 and nkids>0")

# young adults (under 25). obvious.
# pop = self.population_view.get(event.index, query="alive =='alive' and age<=25")

# those with no formal qualifications. Education level 0.
# pop = self.population_view.get(event.index, query="alive =='alive' and education_state==0")


# Doubling briding payment from 130 to 260 per month per child. analogous to child uplift.

# fuel insecurity fund to 20 million.
# constraining scotland to only use 20 million for energy expenditure.
# requires full scale population or reduction of money to be proportional.

# funding to Local authorities for more flexible management of energy bills. seems idealistic and hard to implement without extensive data on how each LA would react. needs much more research.
# again needs full spatial population as MINOS input.

# moratorium on rent/evictions. not sure how easy this would be. can freeze rents but no eviction variables.

# debt relief on most financially vulnerable. (again no debt variables.) have financial condition variables which may be useful instead?

# island households fund. spatial policy should be easy to cut by island super outputs but need a list of them from somewhere (spatial policy...).
