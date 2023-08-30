"""Loneliness Module for MINOS. Primarily estimates sclonely."""

import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import catplot
import logging


class SocialCohesion(Base):
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'social_cohesion'

    def __repr__(self):
        return "SocialCohesion()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Load in inputs from pre-setup.
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())
        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["sex",
                        'age',
                        'urban',
                        'hh_income',
                        'neighbourhood_safety',
                        'ethnicity',
                        'housing_tenure',
                        'region',
                        'education_state',
                        'social_cohesion']
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=5)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Construct transition probability distributions.
        # Draw individuals next states randomly from this distribution.
        # Adjust other variables according to changes in state. E.g. a birth would increase child counter by one.

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        soccoh_prob_df = self.calculate_loneliness(pop)

        soccoh_prob_df["loneliness"] = self.random.choice(soccoh_prob_df.index,
                                                              list(soccoh_prob_df.columns),
                                                              soccoh_prob_df) + 1
        soccoh_prob_df.index = pop.index

        self.population_view.update(soccoh_prob_df["social_cohesion"].astype(int))

    def calculate_loneliness(self, pop):
        """Calculate loneliness transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """

        logging.info("SOCIAL COHESION (BUCKNERS)")

        # load transition model based on year.
        if self.year < 2018:
            year = 2018
        else:
            year = self.year

        if self.cross_validation:
            # if cross-val, fix year to final year model
            year = 2019
        else:
            year = min(year, 2019)

        transition_model = r_utils.load_transitions(f"social_cohesion/clm/social_cohesion_{year}_{year + 1}", self.rpy2Modules, path=self.transition_dir)
        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_next_timestep_clm(transition_model, self.rpy2Modules, pop, 'social_cohesion')
        return prob_df

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"social_cohesion_barplot_{self.year}.pdf"
        densities = pd.DataFrame(pop['social_cohesion'].value_counts(normalize=True))
        densities.columns = ['densities']
        densities['social_cohesion'] = densities.index
        f = plt.figure()
        cat = catplot(data=densities, y='social_cohesion', x='densities', kind='bar', orient='h')
        plt.savefig(file_name)
        plt.close()
