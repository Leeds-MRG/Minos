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
        return "EPCG"

    def __repr__(self):
        return "EPCG"

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
        view_columns = ["hh_income", 'yearly_energy', 'hidp']
        columns_created = ["income_boosted", 'intervention_cost', 'boost_amount']
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
                                   'intervention_cost': 0.,
                                   'boost_amount': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the energy downlift intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        # pop['hh_income'] -= pop['intervention_cost']
        # reset boost amount to 0 before calculating next uplift
        pop['yearly_energy'] += pop['intervention_cost']
        pop['intervention_cost'] = 0.

        # TODO some fine tuning around kwh and non-elec/gas use.
        # TODO check uniform household energy bills and intervention applied.
        # scale energy bill
        # https://policyinpractice.co.uk/energy-price-guarantee-low-income-households-will-still-struggle-this-winter/
        pop['yearly_energy'] += pop['intervention_cost']
        energy_mean = np.mean(pop.groupby(by='hidp')['yearly_energy'].mean())
        if energy_mean > 3000: # energy cap only active when the mean consumption is over 3500.
            # scale energy spending such that the mean yearly bill is 3000 pounds.
            # multiplicative scaling was used via capping of energy pricing per kWh.
            pop['intervention_cost'] = pop['yearly_energy'] * (1- (3000/energy_mean))
            pop['income_boosted'] = pop['intervention_cost'] != 0
            pop['boost_amount'] = pop['intervention_cost']
            #pop['intervention_cost'] = (energy_mean-3000)
            pop['yearly_energy'] -= pop['intervention_cost']
        print(f"Boost amount mean{np.mean(pop['intervention_cost'])}")
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount', 'intervention_cost', 'yearly_energy']])


class energyBaseline(Base):

    # actual high energy prices. with EPCG and EBSS serve as the ongoing 'baseline'?

    @property
    def name(self):
        return "energy_downlift"

    def __repr__(self):
        return "energyDownlift"

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
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0
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


class energyDownlift(Base):
    @property
    def name(self):
        return "energy_downlift"

    def __repr__(self):
        return "energyDownlift"

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
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0
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
        return "energyDownliftNoSupport"

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
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0

        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        # TODO is an 80% increase correct? More dynamic assumption needed?
        pop['boost_amount'] = (
                    -(pop['yearly_energy'] / 12) * (3.0 - 1))  # 130% of monthly fuel bill subtracted from dhi.
        pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (1.8 - 1))  # 80% of monthly fuel bill subtracted from dhi.
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
        return "energyBillSupportScheme"

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
                        "S7_labour_state",
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
        # pop['hh_income'] -= pop['boost_amount']
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        year = min(self.year, 2023)
        # TODO DOESNT WORK ANYMORE WITH BETTER ENERGY PRICING BY COMMODITY.
        #pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (
        #            energy_cap_prices[year] / 1300))  # 80% of monthly fuel bill subtracted from dhi.
        # pop['boost_amount'] = (-(pop['yearly_energy'] / 12) * (energy_cap_prices[year]/1300 - 1))  # 80% of monthly fuel bill subtracted from dhi.
        # first term is monthly fuel, second term is percentage increase of energy cap. 80% initially..?

        # Energy Bill Support Schemes (EBSS) interventions
        # £400 to all households base. £600 in Northern Ireland and Wales.
        if self.year >= 2022:
            pop['boost_amount'] += 400
            pop.loc[pop['region'] == "Northern Ireland", 'boost_amount'] += 200
            pop.loc[pop['region'] == "Wales", 'boost_amount'] += 200

            # £900 for those on means tested (need benefits variables)
            # TODO how is this determined? Needs extra variable from US. Work out what 'means tested' is and any US mapping.
            # £300 for households with pensioners (labour states)
            pensioner_houses = pop.loc[pop['S7_labour_state'] == "Retired", 'hidp']
            pop.loc[pop['hidp'].isin(pensioner_houses), 'boost_amount'] += 300
            # £150 for households with long term sick/disabled individuals.
            disability_houses = pop.loc[pop['S7_labour_state'] == "Sick/Disabled", 'hidp']
            pop.loc[pop['hidp'].isin(disability_houses), 'boost_amount'] += 150
            # £650 for those on universal credit
            universal_credit_houses = pop.loc[pop['universal_income'] == 1, 'hidp']
            pop.loc[pop['hidp'].isin(universal_credit_houses), 'boost_amount'] += 650
            # £150 for council tax bands A-D. Work out who has council_tax value between 1 and 4 in two stages.
            ct_band_D_houses = pop.loc[pop['council_tax'] <= 4, ['council_tax', 'hidp']]
            ct_band_A_D_houses = ct_band_D_houses.loc[ct_band_D_houses['council_tax'] >= 1, 'hidp']
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


class goodHeatingDummy(Base):

    @property
    def name(self):
        return "good_heating_dummy"

    def __repr__(self):
        return "goodHeatingDummy"

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
        view_columns = ['alive',
                        'heating',
                        'housing_quality',
                        'hidp']

        columns_created = ['income_boosted', "boost_amount"]
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
                                   "boost_amount": 0 # who boosted?,
                                   },  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index, query="alive =='alive'")
        # get households with poor heating.
        poor_heating_houses = pop.loc[pop['heating'] == 0.,]['hidp']
        pop.loc[pop['hidp'].isin(poor_heating_houses), 'heating'] = 0.
        pop['income_boosted'] += (pop['heating'] == 0.)

        unheated_pop = pop.loc[pop['heating'] == 0.,]
        unheated_pop.loc[unheated_pop['housing_quality'] == "Medium", 'housing_quality'] = "High"
        unheated_pop.loc[unheated_pop['housing_quality'] == "Low", 'housing_quality'] = "Medium"
        pop.loc[pop['heating'] == 0., 'housing_quality'] = unheated_pop['housing_quality']

        # set heating cost to one.
        # pop['housing_quality'] = pop['housing_quality'].clip(0, 6)
        pop['heating'] = 1.
        pop['heating'] = pop['heating'].astype(int)
        self.population_view.update(pop[['heating', 'income_boosted']])


class GBIS(Base):

    @property
    def name(self):
        return "great_british_insulation_scheme"

    def __repr__(self):
        return "GBIS"

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
                        "S7_labour_state",
                        # 'hh_income',
                        # "universal_income",
                        # "council_tax",
                        'heating',
                        'housing_quality',
                        'dwelling_type',
                        'number_of_rooms',
                        'number_of_bedrooms',
                        'council_tax_band',
                        'yearly_oil'
                        ]
        columns_created = ["income_boosted", 'boost_amount', 'intervention_cost']
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
        pop_update = pd.DataFrame({'income_boosted': False,  # who boosted?,
                                   'boost_amount': 0.,
                                   'intervention_cost': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)

        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """
        1.
        2.
        3.
        4.
        5.

        Parameters
        ----------
        event

        Returns
        -------

        """

        # get the population
        pop = self.population_view.get(event.index, query="alive =='alive'")

        # who gets the intervention?
        # get intervened households in right CT bands.
        # bands A-E not in england.
        non_england_band_E = pop.loc[
            (pop['council_tax_band'] == 5.) * (pop['region'].isin(['Scotland', "Wales"])), 'hidp']
        #bands A-D in england.
        bands_A_D = pop.loc[pop['council_tax_band'].isin([1., 2., 3., 4.]), 'hidp']
        # only intervene on households that have not already received intervention.
        not_intervened = pop.loc[pop['income_boosted'] == False, 'hidp']
        # get FP10 positive?
        # get low heatng?
        eligible_hidps = set(list(bands_A_D) + list(non_england_band_E)).intersection(not_intervened)

        pop['new_income_boosted'] = False
        pop.loc[pop['hidp'].isin(eligible_hidps), 'new_income_boosted'] = True



        # what does the intervention do?  what do houses get?
        # assume all houses here gain cavity wall insulation.
        # https://energyadvicehelpline.org/insulation-save-you-on-energy-bills/
        # 455 detached, 265 semi, 155 terrace, 200 bungalow, 125 apartment.

        # assuming all households in rural areas can't get cavity insulation.
        # use solid wall insulation instead? more expensive but larger savings. households before 1990.

        # TODO check households on housing quality as well.
        pop.loc[pop["new_income_boosted"] == True, "heating"] = 1


        # TODO heterogeneity/validation in the boost amount.
        pop['boost_amount'] = pop['new_income_boosted'] * 125.

        # adjust by dwelling type. more savings with more rooms.
        pop.loc[pop['dwelling_type'] == 1, 'boost_amount'] *= 200 / 125  # adjust to 200 for houses.
        # cant differentiate between house types for now.
        # pop.loc[pop['dwelling_type']==2, 'income_boosted'] *= 1 # no savings for apartments
        pop.loc[pop['dwelling_type'] == 3, 'boost_amount'] *= 200 / 125  # bungalows

        pop['boost_amount'] *= pop['number_of_bedrooms'] * 1.2  # adjust by number of rooms.
        # best we can do in lieu of square footage.

        # subtract insulation savings from energy bills.
        # NB THIS COST SHOULD ONLY SUBTRACTED ONCE WHEN THE PERSON IS INTERVENED UPON FOR THE FIRST TIME!!!
        pop['yearly_energy'] -= pop['boost_amount']
        # pop['income_boosted'] = pop['hh_income']<0.6*np.median(pop['hh_income'])


        # adjust by rural/urban?

        # adjust income variables
        # pop['yearly_energy'] -= pop['boost_amount']

        # how much does it cost?
        pop['intervention_cost'] = pop['new_income_boosted'] * 7500.  # get cost. adjust by household etc. as abiove.
        # adjust cost by dwelling type.

        # adjust by dwelling type. more savings with more rooms.
        pop.loc[pop['dwelling_type'] == 1, 'intervention_cost'] *= 1.5  # adjust to 200 for houses.
        # cant differentiate between house types for now.
        # pop.loc[pop['dwelling_type']==2, 'income_boosted'] *= 1 # no savings for apartments
        pop.loc[pop['dwelling_type'] == 3, 'intervention_cost'] *= 1.5  # bungalows

        #pop.loc[pop['number_of_rooms'] < 0, 'number_of_bedrooms'] = 2
        pop['intervention_cost'] *= pop['number_of_bedrooms'] * 1.1  # adjust by number of rooms.
        # best we can do in lieu of square footage.

        # adjust costs further by number of rooms in lieu of terraced/detached housing type.

        # adjust based on government region? rural/urban?

        # TODO two waves for cavity/solid insulation.

        # adding people boosted on this wave to overall population of previously boosted households.
        pop['income_boosted'] += pop['new_income_boosted']

        # update population
        self.population_view.update(pop[['intervention_cost', 'income_boosted', "boost_amount",
                                         'heating', 'yearly_energy', 'housing_quality']])


class fossilFuelReplacementScheme(Base):

    @property
    def name(self):
        return "fossil_fuel_replacement_scheme"

    def __repr__(self):
        return "fossilFuelReplacementScheme"

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
        view_columns = ["region",
                        "hidp",
                        "S7_labour_state",
                        'hh_income',
                        # "universal_credit",
                        'heating',
                        'housing_quality',
                        'yearly_electric',
                        'yearly_gas',
                        'dwelling_type',
                        'number_of_rooms',
                        "FP10",
                        'yearly_energy',
                        'yearly_oil']
        columns_created = ["income_boosted", 'intervention_cost']
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
                                   'intervention_cost': 0.},  # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        # get households on gas expenditure.
        # replace with similar electrical hour percentage.
        # standing charges issues?

        # get the whole population
        pop = self.population_view.get(event.index, query="alive =='alive'")

        # who recieves the intervention? low income households with electrical consumption?
        # TODO get some fraction of households rather than absolutely everyone.
        # get households with gas/other fuel consumption. low income/FP10?
        who_low_income = pop.loc[pop['hh_income'] < 0.6 * np.median(pop['hh_income']), "hidp"]
        who_energy_poor = pop.loc[pop["FP10"] == True, "hidp"]
        not_intervened = pop.loc[pop['income_boosted'] == False, 'hidp']
        eligible_hidps = set(list(who_low_income) + list(who_energy_poor)).intersection(not_intervened)

        pop.loc[pop['hidp'].isin(eligible_hidps), 'income_boosted'] = True  # get low income low energy households.

        # what is the intervention. convert gas and fuel other usage to electrical. find paper estimate conversion costs.
        # TODO heterogeneity in conversion costs. particularly RE: current contracts and standing charges.
        electric_to_gas_cost_ratio = 2.7
        # TODO this is the real meat of the intervention. need to vary kwh cost ratios and usage dependent on scenarios.
        # e.g. if a boiler tax comes in how does this ratio change and make electical heating more viable?
        pop['yearly_gas_to_electric'] = pop['yearly_gas'] * electric_to_gas_cost_ratio * pop[
            'income_boosted']  # convert from 2.7:1 kwh costs
        pop[
            'yearly_gas_to_electric'] *= 0.5  # convert to half as much kwh used as electric heating much more efficient.

        pop.loc[pop['income_boosted'] == True, 'yearly_gas'] = 0.
        pop['yearly_electric'] += pop['yearly_gas_to_electric']
        pop['yearly_energy'] -= pop['yearly_gas_to_electric']

        # TODO do the same fuel oil/other.
        electric_to_gas_cost_ratio = 0.5  # TODO get a real number.
        pop['yearly_oil_to_electric'] = pop['yearly_oil'] * electric_to_gas_cost_ratio * pop[
            'income_boosted']  # convert from 2.7:1 kwh costs
        pop[
            'yearly_oil_to_electric'] *= 0.5  # convert to half as much kwh used as electric heating much more efficient.

        pop.loc[pop['income_boosted'] == True, 'yearly_oil'] = 0.
        pop['yearly_electric'] += pop['yearly_oil_to_electric']
        pop['yearly_energy'] -= pop['yearly_oil_to_electric']

        #  how much does this cost? estimate cost for heat pump systems based on housing size, type and location.
        # boiler replacements etc.
        # intervention cost as with GBIS.

        # how much does it cost?
        #
        pop['intervention_cost'] = 7500.  # get cost. adjust by household etc. as abiove.
        # adjust cost by dwelling type.

        # adjust by dwelling type. more savings with more rooms.
        pop.loc[pop['dwelling_type'] == 1, 'intervention_cost'] *= 2  # adjust to 200 for houses.
        # cant differentiate between house types for now.
        # pop.loc[pop['dwelling_type']==2, 'income_boosted'] *= 1 # no savings for apartments
        pop.loc[pop['dwelling_type'] == 3, 'intervention_cost'] *= 2  # bungalows

        pop['intervention_cost'] *= pop['number_of_rooms'] * 1.2  # adjust by number of rooms.

        # update the population
        self.population_view.update(pop[['yearly_electric', 'yearly_gas',
                                         'yearly_oil', 'yearly_energy',
                                         'intervention_cost', 'income_boosted']])
