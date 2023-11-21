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


class lmmYJGrossIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmYJ_gross_income'

    def __repr__(self):
        return "lmmYJGrossIncome()"

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
                        "gross_hh_income",
                        "outgoings",
                        "oecd_equiv",
                        "hh_rent",
                        "hh_mortgage",
                        "council_tax",
                        ]

        columns_created = ['gross_hh_income_diff']
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
        self.gee_transition_model = r_utils.load_transitions(f"hh_income/glmm/hh_income_new_GLMM", self.rpy2Modules,
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
        pop_update = pd.DataFrame({'gross_hh_income_diff': 0.},
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
        pop['gross_hh_income_new'] = pop['gross_hh_income']
        ## Predict next income value

        newWaveGrossIncome = pd.DataFrame(columns=['gross_hh_income'])
        newWaveGrossIncome['gross_hh_income'] = self.calculate_gross_income(pop)
        newWaveGrossIncome.index = pop.index

        newWaveGrossIncome['gross_hh_income_diff'] = newWaveGrossIncome['gross_hh_income'] - pop['gross_hh_income']
        income_mean = np.mean(newWaveGrossIncome["gross_hh_income"])
        std_ratio = (np.std(pop['gross_hh_income']) / np.std(newWaveGrossIncome["gross_hh_income"]))
        newWaveGrossIncome["gross_hh_income"] *= std_ratio
        newWaveGrossIncome["gross_hh_income"] -= ((std_ratio - 1) * income_mean)
        # newWaveIncome["hh_income"] -= 75
        # #newWaveIncome['hh_income'] += self.generate_gaussian_noise(pop.index, 0, 1000)
        # print(std_ratio)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        # print("income", np.mean(newWaveIncome['hh_income']))
        newWaveGrossIncome[['hh_rent', 'hh_mortgage', "oecd_equiv", "council_tax"]] = pop[['hh_rent', 'hh_mortgage', "oecd_equiv", "council_tax"]]
        newWaveGrossIncome['hh_income'] = self.subtract_outgoings(newWaveGrossIncome)
        newWaveGrossIncome['hh_income_diff'] = newWaveGrossIncome['hh_income'] - pop['hh_income']

        self.population_view.update(
            newWaveGrossIncome[['gross_hh_income', 'hh_income', 'hh_income_diff', 'gross_hh_income_diff']])

    def calculate_gross_income(self, pop):
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
        nextWaveGrossIncome = r_utils.predict_next_timestep_yj_gamma_glmm(self.gee_transition_model,
                                                                          self.rpy2Modules,
                                                                          pop,
                                                                          dependent='gross_hh_income_new',
                                                                          yeo_johnson=True,
                                                                          reflect=False,
                                                                          noise_std=0.175)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveGrossIncome

    def subtract_outgoings(self, pop):
        """After calculating household income subtract outgoings including rent, mortgages, and other bills."""
        pop["outgoings"] = pop["hh_rent"] + pop["hh_mortgage"] + pop["council_tax"]
        return (pop["gross_hh_income"] - pop["outgoings"]) / pop["oecd_equiv"]

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()
