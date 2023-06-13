"""
Module for income in Minos.
Calculation of monthly household income
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""

import pandas as pd
from pathlib import Path
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
from seaborn import histplot
import matplotlib.pyplot as plt
import numpy as np


class MWB(Base):
    """Mental Well-Being Module"""

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'mwb'

    def __repr__(self):
        return "MWB()"

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
        # self.transition_coefficients = builder.

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
                        'labour_state',
                        'job_sec',
                        'hh_income',
                        'SF_12',
                        'housing_quality',
                        'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness',
                        'SF_12_diff']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        # builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=6)

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
        pop_update = pd.DataFrame({'SF_12_diff': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

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
        newWaveMWB = self.calculate_mwb(pop)
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=['SF_12'])
        # newWaveMWB = newWaveMWB.rename(columns={"new_dependent": "SF_12",
        #                                         "predicted": "SF_12_diff"})
        # newWaveMWB = newWaveMWB.to_frame(name='SF_12')
        # Set index type to int (instead of object as previous)
        newWaveMWB.index = pop.index
        SF_12sd = np.std(newWaveMWB["SF_12"])
        #add noise to force variance to 100.
        newWaveMWB['SF_12'] += self.generate_gaussian_noise(newWaveMWB.index, 0, 10/SF_12sd)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income

        self.population_view.update(newWaveMWB['SF_12'])

    def calculate_mwb(self, pop):
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
        transition_model = r_utils.load_transitions(f"SF_12/ols/SF_12_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)

        return r_utils.predict_next_timestep_ols(transition_model,
                                                      self.rpy2Modules,
                                                      pop,
                                                      'SF_12')

    def calculate_mwb_rateofchange(self, pop):
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
        transition_model = r_utils.load_transitions(f"SF_12/ols_diff/SF_12_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)

        return r_utils.predict_next_timestep_ols_diff(transition_model,
                                                 self.rpy2Modules,
                                                 pop,
                                                 'SF_12',
                                                 year=self.year)

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"mwb_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="SF_12", stat='density')
        plt.savefig(file_name)
        plt.close('all')


class geeMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'geeMWB'

    def __repr__(self):
        return "geeMWB()"

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
                        'education_state',
                        'labour_state',
                        'job_sec',
                        'hh_income',
                        'SF_12',
                        'housing_quality',
                        'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=9)

        self.max_sf12 = None
        #only need to load this once for now.
        self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee/SF_12_GEE", self.rpy2_modules)

    def update_prediction_population(self, current_pop):
        """ Update longitudinal data frame of past observations with current information.

        Remove those not alive and sort by pidp and time so gee R model can read it.

        Parameters
        ----------
        current_pop

        Returns
        -------

        """
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
        if self.max_sf12 == None:
            self.max_sf12 = np.max(pop["SF_12"])
            self.SF12_std = np.std(pop["SF_12"])

        ## Predict next income value
        newWaveMWB = self.calculate_mwb(pop)
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=["SF_12"])
        # Set index type to int (instead of object as previous)
        newWaveMWB.index = pop.index

        SF12_mean = np.mean(newWaveMWB["SF_12"])
        # scale SF12 to have standard deviation 10.
        newWaveMWB['SF_12'] += self.generate_gaussian_noise(newWaveMWB.index, 0, (self.SF12_std/np.std(newWaveMWB["SF_12"]))**2)

        #print(np.mean(newWaveMWB["SF_12"]))
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveMWB['SF_12'])


    def calculate_mwb(self, pop):
        """Calculate income transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        year = min(self.year, 2018)
        return self.max_sf12 - r_utils.predict_next_timestep_gee(self.gee_transition_model, self.rpy2_modules, pop, 'SF_12')



class geeYJMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'gee_yj_mwb'

    def __repr__(self):
        return "geeYJMWB()"

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
                        'labour_state',
                        #'job_sec',
                        'hh_income',
                        'SF_12',
                        'housing_quality',
                        #'phealth',
                        #'ncigs',
                        #'nutrition_quality',
                        #'neighbourhood_safety',
                        'loneliness']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=9)

        self.max_sf12 = None
        #only need to load this once for now.
        self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj/SF_12_GEE_YJ", self.rpy2_modules)

    def update_prediction_population(self, current_pop):
        """ Update longitudinal data frame of past observations with current information.

        Remove those not alive and sort by pidp and time so gee R model can read it.

        Parameters
        ----------
        current_pop

        Returns
        -------

        """
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
        if self.max_sf12 == None:
            self.max_sf12 = np.max(pop["SF_12"])

        ## Predict next income value
        # reflect SF_12 so right skewed and yj transform works.
        pop["SF_12"] = self.max_sf12 - pop["SF_12"]
        newWaveMWB = self.calculate_mwb(pop)
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=["SF_12"])
        newWaveMWB["SF_12"] = self.max_sf12 - newWaveMWB["SF_12"] # reflect SF_12 back to being left skewed.
        newWaveMWB["SF_12"] = np.clip(newWaveMWB["SF_12"], 0, 100)
        # Set index type to int (instead of object as previous)
        newWaveMWB.index = pop.index


        #print(np.mean(newWaveMWB["SF_12"]))
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveMWB['SF_12'])


    def calculate_mwb(self, pop):
        """Calculate income transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        return r_utils.predict_next_timestep_yj_gaussian_gee(self.gee_transition_model, self.rpy2_modules, pop, 'SF_12', 0.5)