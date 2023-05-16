"""
Module for nutrition in Minos.
Calculation of weekly consumption of fruit and veg.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base

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
                        'labour_state',
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
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

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
        newWaveNutrition = self.calculate_nutrition(pop).round(0).astype(int)
        newWaveNutrition = pd.DataFrame(newWaveNutrition, columns=["nutrition_quality"])
        # Set index type to int (instead of object as previous)
        newWaveNutrition.index = (newWaveNutrition.index.astype(int))
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
        return r_utils.predict_next_timestep_ols(transition_model, self.rpy2Modules, pop, 'nutrition_quality')


    # Special methods used by vivarium.
    @property
    def name(self):
        return 'nutrition'


    def __repr__(self):
        return "Nutrition()"
