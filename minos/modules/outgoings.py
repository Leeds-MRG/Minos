"""
Module for gross income in Minos.
Calculation of monthly household income
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import histplot
import numpy as np
import logging


class energyBills(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'energy_bills'

    def __repr__(self):
        return "energyBills()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for income
        - Add required columns to population data frame
        - Update other required items such as randomness stream.

        Parameters
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Load in inputs from pre-setup.
        # self.transition_model = builder.data.load("income_transition")
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        # self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ["age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        'job_sec',
                        'SF_12',
                        'pidp',
                        'hh_income',
                        'hh_income_diff',
                        "outgoings",
                        "oecd_equiv",
                        "hh_rent",
                        "hh_mortgage",
                        "council_tax",
                        "gross_hh_income",
                        # methods of gas and electricity payment. prepayment meters, fixed tariffs, etc.
                        "gas_electric_combined",
                        'council_tax',
                        'electric_payment',
                        'duel_payment',
                        'gas_payment',
                        'yearly_oil',
                        'yearly_gas_electric',
                        'yearly_gas',
                        'yearly_electric',
                        'yearly_other_fuel',
                        'yearly_energy'
                        ]

        # columns_created = ['hh_income_diff']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)  # + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        # builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=0)

        self.historic_yearly_electric = pd.read_csv("data/transitions/energy_prices/solid_historic.csv")
        self.historic_yearly_gas = pd.read_csv("data/transitions/energy_prices/gas_historic.csv")
        self.historic_yearly_solid = pd.read_csv("data/transitions/energy_prices/solid_historic.csv")
        self.historic_yearly_liquid = pd.read_csv("data/transitions/energy_prices/liquid_historic.csv")

        self.forecasted_yearly_electric = pd.read_csv("data/transitions/energy_prices/electric_arima.csv")
        self.forecasted_yearly_gas = pd.read_csv("data/transitions/energy_prices/gas_arima.csv")
        self.forecasted_yearly_solid = pd.read_csv("data/transitions/energy_prices/solid_arima.csv")
        self.forecasted_yearly_liquid = pd.read_csv("data/transitions/energy_prices/liquid_arima.csv")

        # calculate change in energy price relative to 2020 baseline.
        self.electric_reference = self.historic_yearly_electric.iloc[30]['x']
        self.gas_reference = self.historic_yearly_gas.iloc[30]['x']
        self.solid_reference = self.historic_yearly_solid.iloc[30]['x']
        self.liquid_reference = self.historic_yearly_liquid.iloc[30]['x']

    def on_initialize_simulants(self, pop_data):
        """  Initiate columns for hh_income when new simulants are added.
        Only column needed is the diff column for rate of change model predictions.

        Parameters
        ----------
            pop_data: vivarium.framework.population.SimulantData
            Custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """
        # Create frame with new 3 columns and add it to the main population frame.
        # This is the same for both new cohorts and newborn babies.
        # Neither should be dead yet.
        pop_update = pd.DataFrame({'gross_hh_income_diff': 0.,
                                   'hh_income_diff': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")

        # get new wholesale energy pricing for three categories. gas coal and solid/liquid aggregated.
        # calculate price increase relative to 2020 pricing.
        # adjust expenditure based on 2020 consumption.

        electric_price_ratio, gas_price_ratio, liquid_price_ratio, solid_price_ratio = self.energy_pricing_forecasts(
            event.time.year)

        # TODO individuals on fixed tariffs won't experience these changes in bills. how many of them can we account for. probably good info on distribution of tariffs over time.
        # TODO they were pretty much annhilated at the start of the crisis.
        # for people who pay bills for the three types seperately this is easy.
        # just calculate the 2020 to current pricing ratio and times out.
        #
        # For people on duel fuel bills this is more complicated.
        # For now im going to use OFGEM estimates suggesting the average household uses 11500 kwh of gas and 2700
        # kwh of electricity per year as of 2023. This gives a 115:27 ratio. can then use a weighted mean calculating
        # new duel fuel expenditure based on these ratios.

        # get people with seperate gas, electric and other fuel bills.
        # adjust their yearly gas, electric, and other expenditure accordingly.
        split_energy_bills_pop = pop.loc[pop['gas_electric_combined'] == 1,]

        # fixed tariffs according to gaspay variables. These prices don't change with market forces.
        fixed_tariffs = [1, 5, 8]

        # adjust gas pricing if not on a fixed tariff.
        split_energy_bills_pop.loc[
            ~split_energy_bills_pop['gas_payment'].isin(fixed_tariffs), "yearly_gas"] *= gas_price_ratio
        # adjust electric pricing if not on a fixed tariff.
        split_energy_bills_pop.loc[
            ~split_energy_bills_pop['electric_payment'].isin(fixed_tariffs), "yearly_electric"] *= electric_price_ratio

        # no fixed tariffs for oil and solid fuel as far as I can tell. adjust unconditionallty
        split_energy_bills_pop["yearly_oil"] *= liquid_price_ratio
        split_energy_bills_pop['yearly_other_fuel'] *= solid_price_ratio

        split_energy_bills_pop['yearly_energy'] = (split_energy_bills_pop['yearly_electric'] +
                                                   split_energy_bills_pop['yearly_gas'] +
                                                   split_energy_bills_pop['yearly_oil'] +
                                                   split_energy_bills_pop['yearly_other_fuel'])

        # adding updated price back into population.
        pop.loc[pop['gas_electric_combined']==1, 'yearly_energy'] = split_energy_bills_pop['yearly_energy']

        # get people on duel gas and electric fuel bills.
        # calcualte their yearly duel fuel consumption using a weighted mean

        # 2700, 11500 ratio of electric to gas kwh usage annualy on average according to OFGEM.
        # assuming this ratio nationwide is naive and
        # TODO can probably do better I.E. spatially disaggregated information on energy usage ratios in rural vs urban areas or by  LSOA.

        joint_energy_bills_pop = pop.loc[pop['gas_electric_combined'] == 2,]
        electric_gas_current_spend = joint_energy_bills_pop.loc[~joint_energy_bills_pop['duel_payment'].isin(fixed_tariffs), 'yearly_gas_electric']
        electric_gas_current_spend = (((2700*electric_price_ratio*electric_gas_current_spend)/(2700+11500)) +
                                     ((11500*gas_price_ratio*electric_gas_current_spend)/(2700+11500)))
        joint_energy_bills_pop.loc[~joint_energy_bills_pop['duel_payment'].isin(fixed_tariffs), 'yearly_gas_electric'] = electric_gas_current_spend

        joint_energy_bills_pop['yearly_energy'] = (split_energy_bills_pop['yearly_gas_electric'] +
                                                   split_energy_bills_pop['yearly_oil'] +
                                                   split_energy_bills_pop['yearly_other_fuel'])

        pop.loc[pop['gas_electric_combined'] == 2, 'yearly_energy'] = joint_energy_bills_pop['yearly_energy']


        # update yearly energy bill for application in gross hh income. literally just sum the gas, electic, duel and other together.
        self.population_view.update( pop['yearly_energy'])


    def energy_pricing_forecasts(self, year):
        # if year greater than current time need to use forecasted wholesale price.
        # otherwise before 2023 can use historical yearly whole pricing.

        if year >= 2023:
            electric_price = self.forecasted_yearly_electric.loc[year - 2023, "Point.Forecast"]
            gas_price = self.forecasted_yearly_gas.loc[year - 2023, "Point.Forecast"]
            solid_price = self.forecasted_yearly_solid.loc[year - 2023, "Point.Forecast"]
            liquid_price = self.forecasted_yearly_liquid.loc[year - 2023, "Point.Forecast"]

        else:
            electric_price = self.historic_yearly_electric.iloc[year - 1990]['x']
            gas_price = self.historic_yearly_gas.iloc[year - 1990]['x']
            solid_price = self.historic_yearly_solid.iloc[year - 1990]['x']
            liquid_price = self.historic_yearly_liquid.iloc[year - 1990]['x']

        # for now just taking mean of liquid and solid pricing to incorporate all 'other' fuel. don't have any finer
        # UKHLS detail than this and by ONS definition this encompasses all 'other' anyway except vehicle and motor
        # oils.

        electric_price /= self.electric_reference
        gas_price /= self.gas_reference
        liquid_price /= self.liquid_reference
        solid_price /= self.solid_reference
        return electric_price, gas_price, liquid_price, solid_price


def plot(self, pop, config):
    file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
    f = plt.figure()
    histplot(pop, x="hh_income", stat='density')
    plt.savefig(file_name)
    plt.close()


class rents(Base):

    def on_time_step(self):
        # calculate changes in rents. huge scope for heterogeneity here by region/household structure etc.
        pass


class mortgages(Base):

    def on_time_step(self):
        # calculate change in mortgage payments according to interest rates etc.
        pass
