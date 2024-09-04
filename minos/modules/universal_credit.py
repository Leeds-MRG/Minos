"""Module for estimating change in universal_credit variable"""


import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import logging
from datetime import datetime as dt

class UniversalCredit(Base):
    @property
    def name(self):
        return "universal_credit"

    def __repr__(self):
        return "UniversalCredit()"

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

        # Assign randomness streams if necessary. Only useful if seeding counterfactuals.
        self.random = builder.randomness.get_stream(self.generate_run_crn_key())


        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        'hh_income'
                        ]
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
        # Construct transition probability distributions.
        # Draw individuals next states randomly from this distribution.
        # Adjust other variables according to changes in state. E.g. a birth would increase child counter by one.

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        UC_prob_df = self.calculate_universal_credit(pop)
        UC_prob_df[0.] = 1 - UC_prob_df[1.0]
        UC_prob_df.index = pop.index
        UC_prob_df["universal_credit"] = self.random.choice(UC_prob_df.index,
                                                        list(UC_prob_df.columns),
                                                        UC_prob_df)
        UC_prob_df.index = pop.index
        UC_prob_df['universal_credit'] = UC_prob_df['universal_credit'].astype(int)
        self.population_view.update(UC_prob_df["universal_credit"])

    def calculate_universal_credit(self, pop):
        """Calculate heating transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # load transition model based on year.
        year = 2019
        #transition_model = r_utils.load_transitions(f"heating/logit/heating_{year}_{year+1}", self.rpy2Modules)
        if not self.transition_model or year <= 2020:
            self.transition_model = r_utils.load_transitions(
                f"universal_credit/logit/universal_credit_{year}_{year + 1}",
                self.rpy2Modules,
                path=self.transition_dir)
            self.transition_model = r_utils.randomise_fixed_effects(self.transition_model,
                                                                    self.rpy2Modules,
                                                                    "logit",
                                                                    seed=self.run_seed)

        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_next_timestep_logit(model=self.transition_model,
                                                      rpy2_modules=self.rpy2Modules,
                                                      current=pop,
                                                      dependent='universal_credit')
        prob_df.columns = [1.]
        return prob_df
