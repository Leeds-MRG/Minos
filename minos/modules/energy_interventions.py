import itertools
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from minos.modules.base_module import Base


class EPCG(Base):
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
        #pop['hh_income'] -= pop['boost_amount']
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        # TODO is an 80% increase correct? More dynamic assumption needed?
        #pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (2.3 - 1))  # 130% of monthly fuel bill subtracted from dhi.
        pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (1.8 - 1))  # 80% of monthly fuel bill subtracted from dhi.
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
        #pop['hh_income'] -= pop['boost_amount']
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        # TODO is an 80% increase correct? More dynamic assumption needed?
        pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (3.0 - 1))  # 130% of monthly fuel bill subtracted from dhi.
        #pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (1.8 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes constant fuel expenditure beyond negative hh income. need some kind of energy module to adjust behaviour..
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])


class EBSS(Base):

    @property
    def name(self):
        return "EBSS"

    def __repr__(self):
        return "EBSS()"

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
        view_columns = ["hh_income",
                        'yearly_energy',
                        "region",
                        "hidp",
                        "labour_state"]
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
        #pop['net_hh_income'] -= pop['boost_amount']

        # NOTE ENERGY PRICE INCREASES NOW PART OF THE OUTGOINGS MODULE>
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        #year = min(self.year, 2023)
        #pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (energy_cap_prices[year]/1300))  # 80% of monthly fuel bill subtracted from dhi.
        #pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (energy_cap_prices[year]/1300 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        # Energy Bill Support Schemes (EBSS) interventions
        # £400 to all households base. £600 in Northern Ireland and Wales.
        if self.year >= 2022:
            # flat boost amount for everybody.
            pop['boost_amount'] += 400
            # extra boosts for NI and Wales.
            #TODO Scotland/LAs?
            pop.loc[pop['region']=="Northern Ireland", 'boost_amount'] += 200
            pop.loc[pop['region']=="Wales", 'boost_amount'] += 200

            # £900 for those on means tested (need benefits variables. UC?)
            # TODO how is this determined? Needs extra variable from US. Work out what 'means tested' is and any US mapping.
            # £300 for households with pensioners (labour states)
            pensioner_houses = pop.loc[pop['labour_state']=="Retired", 'hidp']
            pop.loc[pop['hidp'].isin(pensioner_houses), 'boost_amount'] += 300
            # £150 for households with disabled individuals.
            pensioner_houses = pop.loc[pop['labour_state']=="Sick/Disabled", 'hidp']
            pop.loc[pop['hidp'].isin(pensioner_houses), 'boost_amount'] += 150

            # discounting based on tariff type (prepayment meters/fixed rate tariffs/ all different (cant do this..)
            # TODO see elecpay/gaspay.
            # Long term government net zero plans. estimating 15% reduction in household energy bills
            # for now assume linear reduction in energy costs from 0% to 15% by 2030.
            # TODO naive?
            # TODO any other boosts suggested by new gov plans. any specifically by subgroups?

        # income given does not exceed energy expenditure nor is it negative.
        pop['boost_amount'] = pop['boost_amount'].clip(upper=0.001) * (pop['boost_amount'] >= pop['yearly_energy'])

        pop['income_boosted'] = pop['boost_amount'] != 0
        pop['hh_income'] += pop['boost_amount']

        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO assumes no social change. just go very negative which has major detrimental effects.
        # TODO add in reduction due to energy crisis that varies by year.

        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])



class GBIS(Base):
    # Great British Insulation Scheme (GBIS) intervention for retrofitting low income households with insulation.

    @property
    def name(self):
        return "GBIS"

    def __repr__(self):
        return "GBIS()"

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
        view_columns = ["net_hh_income",
                        'yearly_energy',
                        "region",
                        "hidp",
                        "labour_state",
                        'gross_hh_income']
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
        self.population_view.update(pop[['gross_hh_income', 'income_boosted', 'boost_amount']])


class netZeroGasReplacement(Base):

    @property
    def name(self):
        return "energyPoverty"

    def __repr__(self):
        return "energyPoverty()"

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
        view_columns = ["net_hh_income",
                        'yearly_energy',
                        "region",
                        "hidp",
                        "labour_state",
                        'gross_hh_income']
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
        self.population_view.update(pop[['gross_hh_income', 'income_boosted', 'boost_amount']])

