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

class S7MentalHealth(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 's7mentalhealth'

    def __repr__(self):
        return "S7MentalHealth()"

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
                        'hh_income',
                        'region',
                        'housing_quality',
                        'S7_physical_health',
                        'S7_mental_health',
                        'loneliness']

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

        self.year = event.time.year

        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")

        # Predict next neighbourhood value
        men_health_prob_df = self.calculate_S7_mental_health(pop)

        men_health_prob_df["S7_mental_health"] = self.random.choice(men_health_prob_df.index,
                                                                       list(men_health_prob_df.columns),
                                                                       men_health_prob_df) + 1

        men_health_prob_df.index = men_health_prob_df.index.astype(int)

        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(men_health_prob_df['S7_mental_health'])

    def calculate_S7_mental_health(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # year
        if self.cross_validation:
            # if cross-val, fix year to final year model
            year = 2020
        else:
            year = min(self.year, 2020)

        # if simulation goes beyond real data in 2020 dont load the transition model again.
        if not self.transition_model or year <= 2020:
            self.transition_model = r_utils.load_transitions(f"S7_mental_health/clm/S7_mental_health_{year}_{year+1}", self.rpy2Modules, path=self.transition_dir)
            self.transition_model = r_utils.randomise_fixed_effects(self.transition_model, self.rpy2_modules, "clm")

        return r_utils.predict_next_timestep_clm(self.transition_model, self.rpy2Modules, pop, 'S7_mental_health')

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"S7_mental_health_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x = "S7_mental_health", stat='density')
        plt.savefig(file_name)
        plt.close('all')
