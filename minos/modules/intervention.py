"""Module for applying any interventions to the base population from replenishment."""
import itertools
import sys

import pandas as pd
import numpy as np
from pathlib import Path


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
            # Pick a set of parameters according to task_id arg from minos_batch_run.py.
            run_id = config['run_id']
        else:
            # If no task id specified (you should) choose the first task as a test.
            run_id = sys.argv[4] - 1
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
        builder.event.register_listener("time_step", self.on_time_step)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

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


####################################################################################################################

class hhIncomeChildUplift():
    """Uplift by £20 per week per child in each household. """

    @property
    def name(self):
        return "hh_income_20_uplift"

    def __repr__(self):
        return "hhIncomeChildUplift()"

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
        #print("print sys argv")
        #print(sys.argv)
        if 'run_id' in config.keys():
            run_id = config['run_id']
        else:
            # If no task id specified (you should) choose the first task as a test.
            run_id = 0
        # specify parameters unique to this experiment. used to produce save directories later.
        parameters = [run_id]  # just the run_id is unique for £20 uplifts no change in amount/percentage of pop.
        config.update({'experiment_parameters': parameters}, source=str(Path(__file__).resolve()))
        config.update({'experiment_parameters_names': ['id']}, source=str(Path(__file__).resolve()))

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
        builder.event.register_listener("time_step", self.on_time_step)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # print(np.mean(pop['hh_income'])) # for debugging purposes.
        # TODO probably a faster way to do this than resetting the whole column.
        pop['hh_income'] -= pop['boost_amount']  # reset boost if people move out of bottom decile.
        pop['boost_amount'] = (20 * 30.436875 * pop['nkids'] / 7) # £20 per week * 30.463/7 weeks per average month * nkids.
        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


########################################################################################################################
class hhIncomePovertyLineChildUplift():
    """uplift intervention module. £20 uplift per child for households below the poverty line."""

    @property
    def name(self):
        return "hh_income_poverty_live_20_uplift"

    def __repr__(self):
        return "hhIncomePovertyLineChildUplift()"

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
        if 'run_id' in config.keys():
            # Pick a set of parameters according to task_id arg from minos_batch_run.py.
            run_id = config['run_id']
        else:
            # If no task id specified (you should) choose the first task as a test.
            run_id = sys.argv[4] - 1
        parameters = [run_id]
        config.update({'experiment_parameters': parameters}, source=str(Path(__file__).resolve()))
        config.update({'experiment_parameters_names': ['run_id']}, source=str(Path(__file__).resolve()))

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
        builder.event.register_listener("time_step", self.on_time_step)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False, # who boosted?
                                   'boost_amount': 0.}, # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        pop['hh_income'] -= pop['boost_amount']
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        who_uplifted = (pop['hh_income'] <= np.nanmedian(pop['hh_income']) * 0.6) #
        pop['boost_amount'] = (who_uplifted * 20 * 30.436875 / 7) # £20 per child per week uplift for everyone under poverty line.

        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        pop['income_boosted'] = who_uplifted
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


class livingWageIntervention():
    """Living Wage Intervention. Increase hh_income for anyone who doesn't earn a living wage to bridge the gap."""

    @property
    def name(self):
        return "living_wage_intervention"

    def __repr__(self):
        return "livingWageIntervention()"

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
        if 'run_id' in config.keys():
            # Pick a set of parameters according to task_id arg from minos_batch_run.py.
            run_id = config['run_id']
        else:
            # If no task id specified (you should) choose the first task as a test.
            run_id = int(sys.argv[4])-1
            #run_id = 0
        parameters = [run_id]
        config.update({'experiment_parameters': parameters}, source=str(Path(__file__).resolve()))
        config.update({'experiment_parameters_names': ['id']}, source=str(Path(__file__).resolve()))

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
        view_columns = ['hh_income', 'hourly_wage', 'job_hours', 'region', 'sex', 'ethnicity']
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step)


    def on_initialize_simulants(self, pop_data):
        """
        Parameters
        ----------
        pop_data
        Returns
        -------
        """
        pop_update = pd.DataFrame({'income_boosted': False, # who boosted?
                                   'boost_amount': 0.}, # hh income boosted by how much?
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
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        pop['hh_income'] -= pop['boost_amount']
        # Subset everyone who earns below the minimum wage, which is different for London vs non London
        #pop['who_uplifted'] = ((pop['hourly_wage'][pop['region'] != 'London'] < 9.90) | + \
        #    (pop['hourly_wage'][pop['region'] == 'London'] < 11.05)) & (pop['hourly_wage'][pop['hourly_wage'] > 0])
        # Now get who gets uplift (different for London/notLondon)
        who_uplifted_London = pop['hourly_wage'] > 0
        who_uplifted_London *= pop['region'] == 'London'
        who_uplifted_London *= pop['hourly_wage'] < 11.05
        who_uplifted_notLondon = pop['hourly_wage'] > 0
        who_uplifted_notLondon *= pop['region'] != 'London'
        who_uplifted_notLondon *= pop['hourly_wage'] < 9.90
        # Calculate boost amount (difference between hourly wage and living wage multiplied by hours worked in a week (extended to month))
        # boost_amount = hourly_wage_diff * hours_worked_monthly
        #pop['boost_amount'] = (9.90 - pop['hourly_wage'][pop['region'] != 'London']) * (pop['job_hours'] * 4.2) * pop['who_uplifted'] | + \
        #    (11.05 - pop['hourly_wage'][pop['region'] == 'London']) * (pop['job_hours'] * 4.2) * pop['who_uplifted']
        pop['boost_amount'] = (11.05 - pop['hourly_wage']) * (pop['job_hours'] * 4.2) * who_uplifted_London
        pop['boost_amount'] += (9.90 - pop['hourly_wage']) * (pop['job_hours'] * 4.2) * who_uplifted_notLondon


        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        pop['income_boosted'] = who_uplifted_notLondon | who_uplifted_London
        #pop.drop(labels='who_uplifted', inplace=True)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of household composition.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


class energyDownlift:
    @property
    def name(self):
        return "hh_income_80_energy_downlift"

    def __repr__(self):
        return "hhIncome80EnergyDownlift()"

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
        if 'run_id' in config.keys():
            # Pick a set of parameters according to task_id arg from minos_batch_run.py.
            run_id = config['run_id']
        else:
            # If no task id specified (you should) choose the first task as a test.
            run_id = sys.argv[4] - 1
        parameters = [run_id]
        config.update({'experiment_parameters': parameters}, source=str(Path(__file__).resolve()))
        config.update({'experiment_parameters_names': ['run_id']}, source=str(Path(__file__).resolve()))

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
        builder.event.register_listener("time_step", self.on_time_step)


    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,  # who boosted?
                                   'boost_amount': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)


    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        pop['hh_income'] -= pop['boost_amount']
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        pop['boost_amount'] = (-(pop['yearly_gas_electric'] / 12) * (1.8 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes constant fuel expenditure beyond negative hh income. need some kind of energy module to adjust behaviour..
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])
