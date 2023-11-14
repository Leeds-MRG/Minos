"""
This script will predict the total number of working hours for an individual in employment.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import histplot
import numpy as np
import logging

class JobHours(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'job_hours'

    def __repr__(self):
        return "JobHours()"

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
                        'urban',
                        'pidp',
                        'nkids',
                        'S7_labour_state',
                        'job_hours',
                        'job_hours_diff'
                        ]


        #columns_created = ['hh_income_diff']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)# + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=3)

        # just load this once.
        #self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj/hh_income_GEE_YJ", self.rpy2Modules,
        #                                             path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_diff/hh_income_GEE_DIFF", self.rpy2Modules,
        #                                                     path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"job_hours/glmm/job_hours_GLMM", self.rpy2Modules,
                                                             path=self.transition_dir)
        #self.history_data = self.generate_history_dataframe("final_US", [2018, 2019], view_columns)
        #self.history_data["hh_income_diff"] = self.history_data['hh_income'] - self.history_data.groupby(['pidp'])['hh_income'].shift(1)

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
        pop_update = pd.DataFrame({'job_hours_diff': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # First predict for people in employment
        pop = self.population_view.get(event.index, query="alive == 'alive' and S7_labour_state == 'FT Employed' or S7_labour_state == 'PT Employed'")
        #  & 'S7_labour_state' == 'FT Employed' or 'S7_labour_state' == 'PT Employed'

        ## predicting job hours for employed individuals
        #pop = pop.sort_values('pidp')
        self.year = event.time.year
        pop['job_hours_last'] = pop['job_hours']
        ## Predict next job_hours value
        newWaveJobHours = pd.DataFrame(columns=['job_hours'])
        newWaveJobHours['job_hours'] = self.calculate_job_hours(pop)
        newWaveJobHours.index = pop.index

        newWaveJobHours['job_hours_diff'] = newWaveJobHours['job_hours'] - pop['job_hours']
        job_hours_mean = np.mean(newWaveJobHours["job_hours"])
        std_ratio = (np.std(pop['job_hours'])/np.std(newWaveJobHours["job_hours"]))
        newWaveJobHours["job_hours"] *= std_ratio
        newWaveJobHours["job_hours"] -= ((std_ratio-1)*job_hours_mean)
        # #newWaveJobHours['job_hours'] += self.generate_gaussian_noise(working_pop.index, 0, 1000)
        #print(std_ratio)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income

        # merge back onto pop so we can be sure we're updating the correct people
        pop = pop.drop(labels=['job_hours', 'job_hours_diff'], axis=1)
        pop['job_hours'] = newWaveJobHours['job_hours']
        #pop["job_hours"] = np.clip(pop["job_hours"], 0, 10000)  # job_hours has to be positive
        pop['job_hours_diff'] = newWaveJobHours['job_hours_diff']

        #print("job_hours", np.mean(newWaveJobHours['job_hours']))
        self.population_view.update(pop[['job_hours', 'job_hours_diff']])

        # Now people not in employment
        non_working_pop = self.population_view.get(event.index,
                                       query="alive == 'alive' and S7_labour_state != 'FT Employed' and S7_labour_state != 'PT Employed'")
        #  & 'S7_labour_state' == 'FT Employed' or 'S7_labour_state' == 'PT Employed'

        # save previous value to calculate diff
        non_working_pop['job_hours_last'] = non_working_pop['job_hours']
        # simply set job_hours to 0 as these people are not in work
        non_working_pop['job_hours'] = 0.0
        # now calculate diff (although probably not useful)
        non_working_pop['job_hours_diff'] = non_working_pop['job_hours'] - non_working_pop['job_hours']

        self.population_view.update(non_working_pop[['job_hours', 'job_hours_diff']])

    def calculate_job_hours(self, pop):
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
        nextWaveJobHours = r_utils.predict_next_timestep_yj_gamma_glmm(self.gee_transition_model,
                                                                       self.rpy2Modules,
                                                                       pop,
                                                                       dependent='job_sec',
                                                                       yeo_johnson=False,
                                                                       reflect=False,
                                                                       noise_std=5)  # 0.45 for yj. 5? for non yj.
        # get new hh income diffs and update them into history_data.
        #self.update_history_dataframe(pop, self.year-1)
        #new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        #next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveJobHours
