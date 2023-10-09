"""
Module for chronic disease in Minos.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
from seaborn import histplot
import matplotlib.pyplot as plt
import numpy as np
import logging


class ChronicDisease(Base):
    """Chronic Disease Module"""

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'chron_disease'

    def __repr__(self):
        return "ChronicDisease()"

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
                        'region',
                        'education_state',
                        'hh_income',
                        'SF_12_MCS',
                        'SF_12_PCS',
                        'marital_status',
                        'loneliness',
                        'ncigs',
                        'nutrition_quality',
                        'active',
                        'auditc',
                        'matdep',
                        'chron_disease']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        # builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

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

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        cd_prob_df = self.calculate_chron_disease(pop)

        cd_prob_df["chron_disease"] = self.random.choice(cd_prob_df.index,
                                                         list(cd_prob_df.columns),
                                                         cd_prob_df) + 1

        self.population_view.update(cd_prob_df["chron_disease"].astype(float))

    def calculate_chron_disease(self, pop):
        """Calculate chron_disease transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """

        # load transition model based on year.
        if self.cross_validation:
            # if cross-val, fix year to final year model
            year = 2019
        else:
            year = min(self.year, 2019)

        transition_model = r_utils.load_transitions(f"chron_disease/clm/chron_disease_{year}_{year + 1}",
                                                    self.rpy2_modules, path=self.transition_dir)
        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_next_timestep_clm(transition_model, self.rpy2_modules, pop, 'chron_disease')
        return prob_df
