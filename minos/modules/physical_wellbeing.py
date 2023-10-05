"""
Module for income in Minos.
Calculation of monthly household income
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
from seaborn import histplot
import matplotlib.pyplot as plt


class SF_12_PCS(Base):
    """Physical Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'sf_12_pcs'

    def __repr__(self):
        return "SF_12_PCS()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ['pidp',
                        'sex',
                        'ethnicity',
                        'age',
                        'education_state',
                        'S7_labour_state',
                        'job_sec',
                        'hh_income',
                        'SF_12_PCS',
                        'housing_quality',
                        'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness',
                        'financial_situation',
                        'auditc',
                        'active']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=9)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        self.year = event.time.year

        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")

        ## Predict next income value
        newWavePCS = self.calculate_pcs(pop)
        newWavePCS = pd.DataFrame(newWavePCS, columns=["SF_12_PCS"])
        # Set index type to int (instead of object as previous)
        newWavePCS.index = newWavePCS.index.astype(int)

        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWavePCS['SF_12_PCS'])

    def calculate_pcs(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # year can only be 2017 as its the only year with data for all vars
        year = 2017
        transition_model = r_utils.load_transitions(f"SF_12_PCS/ols/SF_12_PCS_{year}_{year+1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)
        return r_utils.predict_next_timestep_ols(transition_model, self.rpy2Modules, pop, 'SF_12_PCS')

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"pcs_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="SF_12_PCS", stat='density')
        plt.savefig(file_name)
        plt.close('all')


class lmmYJPCS(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'glmm_pcs'

    def __repr__(self):
        return "lmmYJPCS()"

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
        self.rpy2_modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ['pidp',
                        'sex',
                        'ethnicity',
                        'age',
                        'time',
                        #'education_state',
                        #'labour_state',
                        #'job_sec',
                        'hh_income',
                        'SF_12_MCS',
                        'SF_12_MCS_diff',
                        'SF_12_PCS',
                        'SF_12_PCS_diff',
                        'housing_quality',
                        #'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness',
                        'financial_situation',
                        'active',
                        'auditc',]

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=9)

        #only need to load this once for now.
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/lmm/SF_12_LMM", self.rpy2_modules, path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"SF_12_PCS/glmm/SF_12_PCS_GLMM", self.rpy2_modules, path=self.transition_dir)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.
        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        self.year = event.time.year
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop = pop.sort_values('pidp') #sorting aligns index to make sure individual gets their correct prediction.
        pop["SF_12_PCS_last"] = pop["SF_12_PCS"]

        # Predict next mwb value
        newWavePWB = pd.DataFrame(columns=['SF_12_PCS'])
        newWavePWB['SF_12_PCS'] = self.calculate_pwb(pop)
        newWavePWB.index = pop.index
        #newWavePWB["SF_12_PCS"] -= 1

        sf12_mean = np.mean(newWavePWB["SF_12_PCS"])
        std_ratio = (11/np.std(newWavePWB["SF_12_PCS"]))
        newWavePWB["SF_12_PCS"] *= (11/np.std(newWavePWB["SF_12_PCS"]))
        newWavePWB["SF_12_PCS"] -= ((std_ratio-1)*sf12_mean)
        newWavePWB["SF_12_PCS"] -= 1.5
        #newWavePWB["SF_12_PCS"] += (50 - np.mean(newWavePWB["SF_12_PCS"]))
        newWavePWB["SF_12_PCS"] = np.clip(newWavePWB["SF_12_PCS"], 0, 100) # keep within [0, 100] bounds of SF12.
        newWavePWB["SF_12_PCS_diff"] = newWavePWB["SF_12_PCS"] - pop["SF_12_PCS"]
        # Update population with new SF_12_PCS
        #print(np.mean(newWavePWB["SF_12_PCS"]))
        #print(np.std(newWavePWB["SF_12_PCS"]))
        self.population_view.update(newWavePWB[['SF_12_PCS', "SF_12_PCS_diff"]])


    def calculate_pwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        out_data = r_utils.predict_next_timestep_yj_gamma_glmm(self.gee_transition_model,
                                                               self.rpy2_modules,
                                                               current= pop,
                                                               dependent='SF_12_PCS',
                                                               reflect=True,
                                                               yeo_johnson= True,
                                                               mod_type='gamma',
                                                               noise_std= 0.1)  # 5 for non yj, 0.35 for yj
        return out_data
