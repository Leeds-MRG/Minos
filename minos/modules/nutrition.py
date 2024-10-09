"""
Module for nutrition in Minos.
Calculation of weekly consumption of fruit and veg.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import numpy as np
import logging

class Nutrition(Base):

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for tobacco
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
                        'age',
                        'sex',
                        'ethnicity',
                        'region',
                        'hh_income',
                        'SF_12_MCS',
                        'education_state',
                        'S7_labour_state',
                        'job_sec',
                        'hh_income',
                        'alcohol_spending',
                        'ncigs',
                        'nutrition_quality']
        #view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        logging.info("NUTRITION QUALITY")

        self.year = event.time.year

        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")

        ## Predict next income value
        newWaveNutrition = self.calculate_nutrition(pop).round(0).astype(int)
        newWaveNutrition = pd.DataFrame(newWaveNutrition, columns=["nutrition_quality"])
        # Set index type to int (instead of object as previous)
        newWaveNutrition.index = pop.index
        #newWaveNutrition['nutrition_quality'] = newWaveNutrition['nutrition_quality'].astype(float)

        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveNutrition['nutrition_quality'])

    def calculate_nutrition(self, pop):
        """Calculate loneliness transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        #year = min(self.year, 2018)
        transition_model = r_utils.load_transitions(f"nutrition_quality/ols/nutrition_quality_2018_2019", self.rpy2Modules, path=self.transition_dir)
        return r_utils.predict_next_timestep_ols(transition_model,
                                                      self.rpy2Modules,
                                                      pop,
                                                      'nutrition_quality')


    # Special methods used by vivarium.
    @property
    def name(self):
        return 'nutrition'


    def __repr__(self):
        return "Nutrition()"




class lmmYJNutrition(Base):

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for tobacco
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
        view_columns = ['time',
                        "age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        'hh_income',
                        'pidp',
                        'hidp',
                        'nutrition_quality',
                        #'nutrition_quality_diff',
                        'ncigs',
                        "SF_12_MCS"
                        ]

        #view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        self.gee_transition_model = r_utils.load_transitions(f"nutrition_quality/lmm/nutrition_quality_new_LMM", self.rpy2Modules,
                                                             path=self.transition_dir)
        #self.history_data = self.generate_history_dataframe("final_US", [2017, 2019, 2020], view_columns)

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
        pop = pop.sort_values('pidp')
        pop['nutrition_quality_new'] = pop['nutrition_quality']

        ## Predict next nutrition value
        newWaveNutrition = pd.DataFrame(columns=["nutrition_quality"])
        newWaveNutrition['nutrition_quality'] = self.calculate_nutrition(pop).round(0).astype(int)

        # Set index type to int (instead of object as previous)
        newWaveNutrition.index = pop.index

        nutrition_mean = np.mean(newWaveNutrition["nutrition_quality"])
        std_ratio = (np.std(pop['nutrition_quality'])/np.std(newWaveNutrition['nutrition_quality']))
        newWaveNutrition["nutrition_quality"] *= std_ratio
        newWaveNutrition["nutrition_quality"] -= ((std_ratio-1)*nutrition_mean)

        #newWaveNutrition['nutrition_quality'] = newWaveNutrition['nutrition_quality'].astype(float)
        newWaveNutrition['nutrition_quality'] = np.clip(newWaveNutrition['nutrition_quality'], 0, 110) # clipping because of idiot that eats 150 vegetables per week.
        #newWaveNutrition['nutrition_quality_diff'] = newWaveNutrition['nutrition_quality'] - pop['nutrition_quality']
        newWaveNutrition['nutrition_quality'] = newWaveNutrition['nutrition_quality'].astype(int)
        #newWaveNutrition['nutrition_quality_diff'] = newWaveNutrition['nutrition_quality_diff'].astype(int)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        #print('nutrition', np.mean(newWaveNutrition['nutrition_quality']))
        self.population_view.update(newWaveNutrition[['nutrition_quality']])#, 'nutrition_quality_diff']])

    def calculate_nutrition(self, pop):
        """Calculate loneliness transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        nextWaveNutrition = r_utils.predict_next_timestep_yj_gaussian_lmm(self.gee_transition_model,
                                                                       self.rpy2Modules,
                                                                       pop,
                                                                       dependent='nutrition_quality_new',
                                                                       reflect=False,
                                                                       log_transform= False,
                                                                       noise_std=1)#

        return nextWaveNutrition

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmYJNutrition'

    def __repr__(self):
        return "lmmYJNutrition()"


class lmmDiffNutrition(Base):

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for tobacco
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
                        'time',
                        'age',
                        'sex',
                        'ethnicity',
                        'region',
                        'hh_income',
                        'SF_12_MCS',
                        'education_state',
                        #'labour_state',
                        'job_sec',
                        'job_sector',
                        'hh_income',
                        #'alcohol_spending',
                        'ncigs',
                        'nutrition_quality']

        columns_created = ["nutrition_quality_diff"]
        #view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        self.transition_model = r_utils.load_transitions(f"nutrition_quality/lmm_diff/nutrition_quality_LMM_DIFF", self.rpy2Modules,
                                                             path=self.transition_dir)
        self.transition_model = r_utils.randomise_fixed_effects(self.transition_model, self.rpy2Modules, "glmm")

#self.history_data = self.generate_history_dataframe("final_US", [2017, 2019, 2020], view_columns)

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
        pop_update = pd.DataFrame({'nutrition_quality_diff': 0},
                                  index=pop_data.index)
        pop_update['nutrition_quality_diff'] = pop_update['nutrition_quality_diff'].astype(int)
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
        pop = pop.sort_values('pidp')
        pop['nutrition_quality_last'] = pop['nutrition_quality']

        ## Predict next income value
        newWaveNutrition = pd.DataFrame(columns=["nutrition_quality", "nutrition_quality_diff"])
        newWaveNutrition["nutrition_quality_diff"] = self.calculate_nutrition(pop).round(0).astype(int)

        # Set index type to int (instead of object as previous)
        newWaveNutrition.index = pop.index
        newWaveNutrition["nutrition_quality"] = pop['nutrition_quality'] + newWaveNutrition["nutrition_quality_diff"]
        #newWaveNutrition['nutrition_quality'] = newWaveNutrition['nutrition_quality'].astype(float)
        newWaveNutrition['nutrition_quality'] = np.clip(newWaveNutrition['nutrition_quality'], 0, 110) # clipping because of idiot that eats 150 vegetables per week.
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        print('nutrition', np.mean(newWaveNutrition['nutrition_quality']))
        self.population_view.update(newWaveNutrition[['nutrition_quality', 'nutrition_quality_diff']])

    def calculate_nutrition(self, pop):
        """Calculate loneliness transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """

        nextWaveNutrition = r_utils.predict_next_timestep_yj_gaussian_lmm(self.transition_model,
                                                                        self.rpy2Modules,
                                                                        pop,
                                                                        dependent='nutrition_quality_diff',
                                                                        reflect=False,
                                                                        yeo_johnson= True,
                                                                        noise_std=1.5)#

        return nextWaveNutrition
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmDiffNutrition'


    def __repr__(self):
        return "lmmDiffNutrition()"
