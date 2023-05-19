"""Module for applying any interventions to the base population from replenishment."""
import itertools
import sys

import pandas as pd
import numpy as np
from pathlib import Path
from minos.modules.base_module import Base

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
        builder.event.register_listener("time_step", self.on_time_step, priority=3)

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

class hhIncomeChildUplift(Base):
    """Uplift by £20 per week per child in each household. """

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
        builder.event.register_listener("time_step", self.on_time_step, priority=3)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # print(np.mean(pop['hh_income'])) # for debugging purposes.
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']  # reset boost if people move out of bottom decile.
        pop['boost_amount'] = (25 * 30.436875 * pop['nkids'] / 7) # £25 per week * 30.463/7 weeks per average month * nkids.
        pop['income_boosted'] = (pop['boost_amount'] != 0)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


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
        builder.event.register_listener("time_step", self.on_time_step, priority=3)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False, # who boosted?
                                   'boost_amount': 0.}, # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']
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
        builder.event.register_listener("time_step", self.on_time_step, priority=3)


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
        pop = self.population_view.get(event.index, query="alive =='alive' and job_sector == 2")
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']
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
        #pop.drop(labels='who_uplifted', inplace=True)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of household composition.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


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
        builder.event.register_listener("time_step", self.on_time_step, priority=3)


    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,  # who boosted?
                                   'boost_amount': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)


    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        # TODO is an 80% increase correct? More dynamic assumption needed?
        pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (1.8 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes constant fuel expenditure beyond negative hh income. need some kind of energy module to adjust behaviour..
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


### some test on time steps for variious scotland interventions
#scotland only.
# pop = self.population_view.get(event.index, query="alive =='alive' and region=='Scotland'")

#disabled people. labour state.
# pop = self.population_view.get(event.index, query="alive =='alive' and labour_state=='Sick/Disabled'")
#unemployed adults. unemployed labour state.
# pop = self.population_view.get(event.index, query="alive =='alive' and labour_state=='Unemployed'")

#minority ethnic households
# pop = pop.loc[pop['ethnicity'].isin(minorities) # BAN,BLA,BLC,CHI,IND,OBL,WHO,OAS,PAK any others?

#child poverty priority groups (3+ children, mother under 25). nkids >3/ nkids >0 and female and under 25. further groups depend on data.)
# pop = self.population_view.get(event.index, query="alive =='alive' and nkids>=3")
# pop = self.population_view.get(event.index, query="alive =='alive' and age<=25 and nkids>0")

#young adults (under 25). obvious.
# pop = self.population_view.get(event.index, query="alive =='alive' and age<=25")

#those with no formal qualifications. Education level 0.
# pop = self.population_view.get(event.index, query="alive =='alive' and education_state==0")


# Doubling briding payment from 130 to 260 per month per child. analogous to child uplift.

# fuel insecurity fund to 20 million. most interesting one here in my opinion for my PhD. particularly in terms of defining a set fund and how to optimally apply it.
# constraining scotland to only use 20 million for energy expenditure.
# requires full scale population or reduction of money to be proportional.

#funding to Local authorities for more flexible management of energy bills. seems idealistic and hard to implement without extensive data on how each LA would react. needs much more research.
# again needs full spatial population as MINOS input.

#moratorium on rent/evictions. not sure how easy this would be. can freeze rents but no eviction variables.

# debt relief on most financially vulnerable. (again no debt variables.) have financial condition variables which may be useful instead?

# island households fund. spatial policy should be easy to cut by island super outputs but need a list of them from somewhere (spatial policy...).

# subtract income based on yearly energy.
# change by year according to EPG caps.
# Apr 2021 - £1138
# Oct 2021 - £1277
# Apr 2022 - £1971
# Oct 2022 - £2500
# Apr 2023 - £3000
# TODO this is a bit naive. can it be improved? see broadbent paper.
energy_cap_prices = {2017: 1300, #TODO could be refined tobe more precise
                     2018: 1300,
                     2019: 1308,
                     2020: 1286,
                     2021: 1333,
                     2022: 2316,
                     2023: 3500}

class energyPriceCapGuarantee(Base):
    @property
    def name(self):
        return "energyPriceCapGuarantee"

    def __repr__(self):
        return "energyPriceCapGuarantee()"

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
        self.year = event.time.year
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        # TODO is an 80% increase correct? More dynamic assumption needed?
        year = min(self.year, 2023)
        #pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (energy_cap_prices[year]/1300-1))  # 80% of monthly fuel bill subtracted from dhi.
        pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (energy_cap_prices[year]/1300))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes constant fuel expenditure beyond negative hh income. need some kind of energy module to adjust behaviour..
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

class energyBillSupportScheme(Base):
    @property
    def name(self):
        return "energyBillSupportScheme"

    def __repr__(self):
        return "energyBillSupportScheme()"

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
        view_columns = ['yearly_energy',
                        "region",
                        "hidp",
                        "labour_state",
                        'hh_income',
                        "universal_income",
                        "council_tax"]
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
        self.year = event.time.year
        # DONT SUBTRACT FROM INCOME AS IT SEEMS TO UNDO ITSELF AAAAAAAAA.
        #pop['hh_income'] -= pop['boost_amount']
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        year = min(self.year, 2023)
        pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (energy_cap_prices[year]/1300))  # 80% of monthly fuel bill subtracted from dhi.
        #pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (energy_cap_prices[year]/1300 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        # Energy Bill Support Schemes (EBSS) interventions
        # £400 to all households base. £600 in Northern Ireland and Wales.
        if self.year >= 2022:
            pop['boost_amount'] += 400
            pop.loc[pop['region']=="Northern Ireland", 'boost_amount'] += 200
            pop.loc[pop['region']=="Wales", 'boost_amount'] += 200

            # £900 for those on means tested (need benefits variables)
            # TODO how is this determined? Needs extra variable from US. Work out what 'means tested' is and any US mapping.
            # £300 for households with pensioners (labour states)
            pensioner_houses = pop.loc[pop['labour_state']=="Retired", 'hidp']
            pop.loc[pop['hidp'].isin(pensioner_houses), 'boost_amount'] += 300
            # £150 for households with long term sick/disabled individuals.
            disability_houses = pop.loc[pop['labour_state']=="Sick/Disabled", 'hidp']
            pop.loc[pop['hidp'].isin(disability_houses), 'boost_amount'] += 150
            # £650 for those on universal credit
            universal_credit_houses = pop.loc[pop['universal_income']==1, 'hidp']
            pop.loc[pop['hidp'].isin(universal_credit_houses), 'boost_amount'] += 650
            # £150 for council tax bands A-D. Work out who has council_tax value between 1 and 4 in two stages.
            ct_band_D_houses = pop.loc[pop['council_tax']<=4, ['council_tax', 'hidp']]
            ct_band_A_D_houses = ct_band_D_houses.loc[ct_band_D_houses['council_tax']>=1, 'hidp']
            pop.loc[pop['hidp'].isin(ct_band_A_D_houses), 'boost_amount'] += 150

        # discounting based on tariff type (prepayment meters/fixed rate tariffs/ all different (cant do this..)
            # TODO see elecpay/gaspay.
            # Long term government net zero plans. estimating 15% reduction in household energy bills
            # for now assume linear reduction in energy costs from 0% to 15% by 2030.
            # TODO naive?
            # TODO any other boosts suggested by new gov plans. any specifically by subgroups?
        pop['boost_amount'] = pop['boost_amount'].clip(upper=0.001)
        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']

        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes no social change. just go very negative which has major detrimental effects.
        # TODO add in reduction due to energy crisis that varies by year.

        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

