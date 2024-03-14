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

class lmmYJNetIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmYJ_net_income'

    def __repr__(self):
        return "lmmYJNetIncome()"

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
                        'time',
                        'hidp'
                        ]

        columns_created = ["FP10"]
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)  # + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=2)

        # just load this once.
        # self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj/hh_income_GEE_YJ", self.rpy2Modules,
        #                                             path=self.transition_dir)
        # self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_diff/hh_income_GEE_DIFF", self.rpy2Modules,
        #                                                     path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"net_hh_income/glmm/net_hh_income_new_GLMM", self.rpy2Modules,
                                                             path=self.transition_dir)
        # self.history_data = self.generate_history_dataframe("final_US", [2018, 2019], view_columns)
        # self.history_data["hh_income_diff"] = self.history_data['hh_income'] - self.history_data.groupby(['pidp'])['hh_income'].shift(1)

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
        pop_update = pd.DataFrame({#'net_hh_income_diff': 0.,
                                   "FP10": False,},
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
        # pop = pop.sort_values('pidp')
        self.year = event.time.year
        pop['net_hh_income_new'] = pop['net_hh_income']
        ## Predict next income value

        newWavenetIncome = pd.DataFrame(columns=['net_hh_income'])
        newWavenetIncome['net_hh_income'] = self.calculate_net_income(pop)
        newWavenetIncome.index = pop.index
        newWavenetIncome['hidp'] = pop['hidp']

        income_mean = np.median(newWavenetIncome["net_hh_income"])
        std_ratio = (np.std(pop['net_hh_income']) / np.std(newWavenetIncome["net_hh_income"]))
        newWavenetIncome["net_hh_income"] *= std_ratio
        newWavenetIncome["net_hh_income"] -= ((std_ratio - 1) * income_mean)

        #newWavenetIncome['net_hh_income'] -= 175

        newWavenetIncome['net_hh_income'] = newWavenetIncome.groupby('hidp')['net_hh_income'].transform("mean")
        newWavenetIncome['net_hh_income'] = newWavenetIncome['net_hh_income'].clip(-1000, 30000)


        newWavenetIncome['net_hh_income_diff'] = newWavenetIncome['net_hh_income'] - pop['net_hh_income']

        #newWavenetIncome[['hh_rent', 'hh_mortgage', "oecd_equiv", "council_tax", "yearly_energy", "outgoings"]] = pop[['hh_rent', 'hh_mortgage', "oecd_equiv", "council_tax", "yearly_energy", "outgoings"]]
        newWavenetIncome['yearly_energy'] = pop['yearly_energy']
        newWavenetIncome['oecd_equiv'] = pop['oecd_equiv']
        #newWavenetIncome['outgoings'] = pop['outgoings']
        newWavenetIncome['hh_rent'] = pop['hh_rent']
        newWavenetIncome['hh_mortgage'] = pop['hh_mortgage']
        newWavenetIncome['council_tax'] = pop['council_tax']


        # calculate disposable income from net income as per composite variable formula.
        newWavenetIncome['hh_income'] = self.subtract_outgoings(newWavenetIncome)
        # newWaveIncome["hh_income"] -= 75
        # #newWaveIncome['hh_income'] += self.generate_gaussian_noise(pop.index, 0, 1000)
        # print(std_ratio)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        # print("income", np.mean(newWaveIncome['hh_income']))

        income_mean = np.median(newWavenetIncome["hh_income"])
        std_ratio = (np.std(pop['hh_income']) / np.std(newWavenetIncome["hh_income"]))
        newWavenetIncome["hh_income"] *= std_ratio
        newWavenetIncome["hh_income"] -= ((std_ratio - 1) * income_mean)
        newWavenetIncome['hh_income'] = newWavenetIncome['hh_income'].clip(-2500, 15000)
        newWavenetIncome['hh_income'] -= 250

        newWavenetIncome['hh_income_diff'] = newWavenetIncome['hh_income'] - pop['hh_income']
        newWavenetIncome['FP10'] = (newWavenetIncome['yearly_energy'] / newWavenetIncome['hh_income'] > 0.1)
        print(np.mean(newWavenetIncome['hh_income']))
        self.population_view.update(
            newWavenetIncome[['net_hh_income', 'hh_income', 'hh_income_diff', 'net_hh_income_diff', "FP10"]])

    def calculate_net_income(self, pop):
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
        nextWavenetIncome = r_utils.predict_next_timestep_yj_gamma_glmm(self.gee_transition_model,
                                                                          self.rpy2Modules,
                                                                          pop,
                                                                          dependent='net_hh_income_new',
                                                                          yeo_johnson=True,
                                                                          reflect=False,
                                                                          noise_std=15)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWavenetIncome

    def subtract_outgoings(self, pop):
        """After calculating household income subtract outgoings including rent, mortgages, and other bills.

        Parameters
        ----------
        pop : pd.DataFrame
            Vivarium population dataframe

        Returns
        -------
        disposable_income : pd.Series
            Vector of household disposable incomes.
        """
        # Note ALL THESE OUTGOINGS VALUES ARE TRANSITIONED IN AN ADDITIONAL OUTGOINGS MODULE.
        # When the outgoings model is included these are dynamic. Otherwise, static prices.
        pop["outgoings"] = pop["hh_rent"] + pop["hh_mortgage"] + pop["council_tax"] #+ pop['yearly_energy']
        disposable_income = (pop["net_hh_income"] - pop["outgoings"]) / pop["oecd_equiv"]
        return disposable_income


    def generate_interview_date_var(self, data, year):
        """ Generate an interview date variable in the form YYYYMM

        Parameters
        ----------
        data : pandas.DataFrame
            The `data` containing interview year and month (hh_int_y, hh_int_m)
        Returns
        -------
        data : pandas.DataFrame
            Dataframe with interview date variable added
        """
        # Replace na with 0 (na is technically a float so messes up when converting to int) and convert to int then string
        # Format date to 2 sigfigs so we keep the form '08' instead of just '8'
        if year > 2023:
            if year >= 2028:
                data["Date"] = "2028Q1"
            else:
                data["hh_int_y"] = str(year)
                data["hh_int_m"] = (data["hh_int_m"] % 4) + 1
                data["Date"] = data["hh_int_y"] + "Q" + data["hh_int_m"]

        else:
            data["hh_int_y"] = str(year)
            data["hh_int_m"] = data["hh_int_m"].fillna(0).astype(int).astype(str).str.zfill(2)
            data["Date"] = data["hh_int_y"] + data["hh_int_m"]
            # now concatenate the date strings and handle cases of missings (-9, -8). Also replace 0 with -9
            data["Date"] = data["Date"].apply(lambda x: min(x, "202309")) # don't have data for end of the year yet..

        return data


    def inflation_adjustment(self, data, year, var):
        """ Adjust financial values for inflation using the Consumer Price Index (CPI)

        Parameters
        ----------
        data : pandas.DataFrame
            The `data` containing financial variable(s) to be adjusted.
        var : str
            Name of a financial variable to be adjusted.
        Returns
        -------
        data : pandas.DataFrame
            Dataframe with adjusted financial values.
        """
        # need interview date for adjustment
        data = self.generate_interview_date_var(data, year)
        # Inflation adjustment using CPI
        # read in CPI dataset
        if year < 2023:
            # if before present date use real inflation data.
            cpi = pd.read_csv('persistent_data/CPI_202309.csv')
        else:
            # else use OBR cpi forecasts. https://obr.uk/forecasts-in-depth/the-economy-forecast/inflation/#CPI
            cpi = pd.read_csv("persistent_data/CPI_quarterly_forecasts.csv")
            cpi = cpi.loc[cpi['Inflation'] == "CPI forecast index", ]
            cpi["Date"] = cpi["Quarter"]
            cpi["CPI"] = cpi["Value"]
            cpi["Value"] /= cpi.loc[4, "Value"] * 100 # scale to september 2023 as with the other index.

        # merge cpi onto data and do adjustment, then delete cpi column (keep date)
        data = pd.merge(data, cpi, on='Date', how='left')
        data[var] = (data[var] / data['CPI']) * 100
        data.drop(labels=['CPI', 'Unnamed: 0'], axis=1, inplace=True)

        return data

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()