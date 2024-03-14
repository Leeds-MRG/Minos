"""
Module for estimating household outgoings (rent, council tax, and mortgages) (and yearly energy?)
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import histplot
import numpy as np
import logging



"""
Module for net income in Minos.
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
import os

class lmmYJOutgoings(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmYJ_outgoings'

    def __repr__(self):
        return "lmmYJOutgoings()"

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
        # view_columns = ['pidp',
        #                'age',
        #                'sex',
        #                'ethnicity',
        #                'region',
        #                'hh_income',
        #                'job_sec',
        #                #'labour_state',
        #                'education_state',
        #                'SF_12',
        #                'weight',
        #                #'housing_quality',
        #                'job_sector']
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
                        "net_hh_income",
                        "outgoings",
                        "oecd_equiv",
                        "hh_rent",
                        "hh_mortgage",
                        "council_tax",
                        'net_hh_income_diff',
                        "yearly_energy",
                        'hh_int_m',
                        'housing_tenure',
                        'time',
                        'hidp'
                        ]

        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)  # + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=2)

        # just load this once.
        # self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj/hh_income_GEE_YJ", self.rpy2Modules,
        #                                             path=self.transition_dir)
        # self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_diff/hh_income_GEE_DIFF", self.rpy2Modules,
        #                                                     path=self.transition_dir)
        self.rent_transition_model = r_utils.load_transitions(f"hh_rent/glmm/hh_rent_new_GLMM", self.rpy2Modules,
                                                             path=self.transition_dir)
        self.mortgage_transition_model = r_utils.load_transitions(f"hh_mortgage/glmm/hh_mortgage_new_GLMM", self.rpy2Modules,
                                                              path=self.transition_dir)
        self.council_tax_transition_model = r_utils.load_transitions(f"council_tax/glmm/council_tax_new_GLMM", self.rpy2Modules,
                                                                  path=self.transition_dir)
        # self.history_data = self.generate_history_dataframe("final_US", [2018, 2019], view_columns)
        # self.history_data["hh_income_diff"] = self.history_data['hh_income'] - self.history_data.groupby(['pidp'])['hh_income'].shift(1)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        # various renters.
        # TODO investigate specific renting categories heterogeneity. E.g. renting from local authority?
        pop = self.population_view.get(event.index, query="alive =='alive' & housing_tenure >= 3")
        self.year = event.time.year
        pop['hh_rent_last'] = pop['hh_rent']
        ## Predict next income value

        newWaveRent = pd.DataFrame(columns=['hh_rent'])
        newWaveRent['hh_rent'] = self.calculate_hh_rent(pop)

        newWaveRent.index = pop.index
        newWaveRent['hidp'] = pop['hidp']
        newWaveRent['hh_rent'] = newWaveRent.groupby('hidp')['hh_rent'].transform(np.max)
        newWaveRent['hh_rent'] = newWaveRent['hh_rent'].clip(0, 4000)

        #rent_mean = np.median(newWaveRent["hh_rent"])
        #std_ratio = (np.std(pop['hh_rent']) / np.std(newWaveRent["hh_rent"]))
        #newWaveRent["hh_rent"] *= std_ratio
        #newWaveRent["hh_rent"] -= ((std_ratio - 1) * rent_mean)
        #newWaveRent['hh_rent'] -= np.min(newWaveRent['hh_rent'])
        newWaveRent['hh_rent'] = newWaveRent['hh_rent'].clip(0, 4000)
        #newWaveRent['hh_mortgage'] = 0.

        print(f"Rent: {np.median(newWaveRent['hh_rent'])}")
        self.population_view.update(newWaveRent[['hh_rent']])

        #mortgagers
        pop = self.population_view.get(event.index, query="alive =='alive' & housing_tenure == 2")
        pop['hh_mortgage_last'] = pop['hh_mortgage']

        newWaveMortgage = pd.DataFrame(columns=['hh_mortgage'])
        newWaveMortgage['hh_mortgage'] = self.calculate_hh_mortgage(pop)
        newWaveMortgage.index = pop.index
        newWaveMortgage['hidp'] = pop['hidp']
        newWaveMortgage['hh_mortgage'] = newWaveMortgage['hh_mortgage'].clip(0, 10000)
        newWaveMortgage['hh_mortgage'] = newWaveMortgage.groupby('hidp')['hh_mortgage'].transform(np.max)

        #newWaveMortgage['hh_mortgage'] += 50

        #mortgage_mean = np.mean(newWaveMortgage["hh_mortgage"])
        #std_ratio = (np.std(pop['hh_mortgage'] + 1) / np.std(newWaveMortgage["hh_mortgage"]))
        #newWaveMortgage["hh_mortgage"] *= std_ratio
        #newWaveMortgage["hh_mortgage"] -= ((std_ratio - 1) * mortgage_mean)

        newWaveMortgage['hh_mortgage'] = newWaveMortgage['hh_mortgage'].clip(0, 6000)
        #newWaveMortgage['hh_rent'] = 0.

        print(f"Mortgage: {np.mean(newWaveMortgage['hh_mortgage'])}")
        self.population_view.update(newWaveMortgage[['hh_mortgage']])

        # property owners
        pop = self.population_view.get(event.index, query="alive =='alive' & housing_tenure == 1")
        pop['hh_rent'] = 0.
        pop['hh_mortgage'] = 0.

        self.population_view.update(pop[['hh_mortgage', 'hh_rent']])

        pop = self.population_view.get(event.index, query="alive =='alive'")
        newWaveCouncilTax = pd.DataFrame(columns=['council_tax'])
        newWaveCouncilTax['council_tax'] = self.calculate_council_tax(pop)
        newWaveCouncilTax.index = pop.index
        newWaveCouncilTax['hidp'] = pop['hidp']

        newWaveCouncilTax['council_tax'] = newWaveCouncilTax.groupby('hidp')["council_tax"].transform(np.median)
        print(f"Council tax: {np.median(pop['council_tax'])}")
        self.population_view.update(newWaveCouncilTax[['council_tax']])


    def calculate_hh_rent(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        nextWavenetIncome = r_utils.predict_next_timestep_yj_gamma_glmm(self.rent_transition_model,
                                                                        self.rpy2Modules,
                                                                        pop,
                                                                        dependent='hh_rent_new',
                                                                        yeo_johnson=False,
                                                                        reflect=False,
                                                                        noise_std=5)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWavenetIncome

    def calculate_hh_mortgage(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        nextWaveMortgage = r_utils.predict_next_timestep_yj_gamma_glmm(self.mortgage_transition_model,
                                                                        self.rpy2Modules,
                                                                        pop,
                                                                        dependent='hh_mortgage_new',
                                                                        yeo_johnson=False,
                                                                        reflect=False,
                                                                        noise_std=5)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveMortgage



    def calculate_council_tax(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        nextWaveCouncilTax = r_utils.predict_next_timestep_yj_gamma_glmm(self.council_tax_transition_model,
                                                                        self.rpy2Modules,
                                                                        pop,
                                                                        dependent='council_tax_new',
                                                                        yeo_johnson=False,
                                                                        reflect=False,
                                                                        noise_std=1)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveCouncilTax

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()



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
                        "net_hh_income",
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
                        'yearly_energy',
                        'housing_tenure',
                        'heating',
                        "housing_quality",
                        'hidp'
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

        self.historic_yearly_electric = pd.read_csv("persistent_data/energy_prices/solid_historic.csv")
        self.historic_yearly_gas = pd.read_csv("persistent_data/energy_prices/gas_historic.csv")
        self.historic_yearly_solid = pd.read_csv("persistent_data/energy_prices/solid_historic.csv")
        self.historic_yearly_liquid = pd.read_csv("persistent_data/energy_prices/liquid_historic.csv")

        self.forecasted_yearly_electric = pd.read_csv("persistent_data/energy_prices/electric_arima.csv")
        self.forecasted_yearly_gas = pd.read_csv("persistent_data/energy_prices/gas_arima.csv")
        self.forecasted_yearly_solid = pd.read_csv("persistent_data/energy_prices/solid_arima.csv")
        self.forecasted_yearly_liquid = pd.read_csv("persistent_data/energy_prices/liquid_arima.csv")

        # calculate change in energy price relative to 2020 baseline.
        self.electric_reference = self.historic_yearly_electric.iloc[30]['x']
        self.gas_reference = self.historic_yearly_gas.iloc[30]['x']
        self.solid_reference = self.historic_yearly_solid.iloc[30]['x']
        self.liquid_reference = self.historic_yearly_liquid.iloc[30]['x']

        self.transition_model = r_utils.load_transitions(f"yearly_energy/glmm/yearly_energy_new_GLMM", self.rpy2Modules,
                                                             path=self.transition_dir)

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

        joint_energy_bills_pop['yearly_energy'] = (joint_energy_bills_pop['yearly_gas_electric'] +
                                                   joint_energy_bills_pop['yearly_oil'] +
                                                   joint_energy_bills_pop['yearly_other_fuel'])

        pop.loc[pop['gas_electric_combined'] == 2, 'yearly_energy'] = joint_energy_bills_pop['yearly_energy']


        pop['next_yearly_energy'] = pop['yearly_energy']
        newWaveYearlyEnergy = pd.DataFrame(self.calculate_yearly_energy(pop))
        newWaveYearlyEnergy.columns = ['yearly_energy']
        newWaveYearlyEnergy.index = pop.index
        pop['yearly_energy'] = newWaveYearlyEnergy['yearly_energy']
        pop['yearly_energy'] = pop['yearly_energy'].clip(-1000, 25000)
        pop['yearly_energy'] = pop.groupby(by=['hidp'])['yearly_energy'].transform("mean")
        # update yearly energy bill for application in gross hh income. literally just sum the gas, electic, duel and other together.
        self.population_view.update(pop['yearly_energy'])
        print(f"Yearly energy: {np.mean(pop['yearly_energy'])}")

    def calculate_yearly_energy(self, pop):
        # load transition model based on year.
        nextWaveYearlyEnergy = r_utils.predict_next_timestep_yj_gamma_glmm(self.transition_model,
                                                                        self.rpy2Modules,
                                                                        pop,
                                                                        dependent='yearly_energy_new',
                                                                        yeo_johnson=False,
                                                                        reflect=False,
                                                                        noise_std=1.5)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveYearlyEnergy

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


