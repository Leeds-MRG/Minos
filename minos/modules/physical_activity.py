"""Module for estimating change in active variable for subjective ability to heat ones home"""


import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import logging
from datetime import datetime as dt


class PhysicalActivity(Base):
    @property
    def name(self):
        return "physical_activity"

    def __repr__(self):
        return "PhysicalActivity()"

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
        self.rpy2_modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.

        # Assign randomness streams if necessary. Only useful if seeding counterfactuals.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())


        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["sex",
                        "SF_12_MCS",
                        'SF_12_PCS',
                        "ethnicity",
                        "age",
                        "education_state",
                        "hh_income",
                        'region',
                        "active"]
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

        active_prob_df = self.calculate_active(pop)
        active_prob_df[0.] = 1. - active_prob_df[1]
        active_prob_df.index = pop.index
        active_prob_df["active"] = self.random.choice(active_prob_df.index,
                                                      list(active_prob_df.columns),
                                                      active_prob_df)
        active_prob_df.index = pop.index
        self.population_view.update(active_prob_df["active"])

    def calculate_active(self, pop):
        """Calculate active transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # load transition model based on year.
        if self.cross_validation:
            # if cross-val, fix year to 2018. 2019 model has vastly reduced sample for some reason
            year = 2018
        else:
            year = min(self.year, 2018)
        transition_model = r_utils.load_transitions(f"active/logit/active_{year}_{year+1}", self.rpy2_modules)
        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_next_timestep_logit(transition_model, self.rpy2_modules, pop, 'active')
        prob_df.columns = [1.]
        return prob_df
