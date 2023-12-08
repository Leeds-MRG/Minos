"""Module for estimating change in material deprivation variable derived from 21 US variables"""


import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import logging
from datetime import datetime as dt

class MaterialDeprivation(Base):
    @property
    def name(self):
        return "material_deprivation"

    def __repr__(self):
        return "MaterialDeprivation()"

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
        ''' HR 30/11/23 Retaining these from heating module for reference '''
        # view_columns = ["sex",
        #                 #"labour_state",
        #                 "SF_12",
        #                 "job_sec",
        #                 "ethnicity",
        #                 "age",
        #                 "housing_quality",
        #                 "hh_income",
        #                 "ncigs",
        #                 "heating",
        #                 "marital_status",
        #                 "urban",
        #                 'hhsize',
        #                 "housing_tenure",
        #                 "financial_situation"]
        ''' HR 30/11/23 Bare bones variables  '''
        view_columns = ['material_deprivation',
                        'hh_income',
                        # 'S7_labour_state',
                        ]
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=5)


    def on_time_step(self, event):
        """Produces material deprivation status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Construct transition probability distributions.
        # Draw next states randomly from this distribution.
        # Adjust other variables according to changes in state.

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        matdep_prob_df = self.calculate_matdep(pop)
        matdep_prob_df[0.] = 1 - matdep_prob_df[1.0]
        matdep_prob_df.index = pop.index
        matdep_prob_df["material_deprivation"] = self.random.choice(matdep_prob_df.index,
                                                                    list(matdep_prob_df.columns),
                                                                    matdep_prob_df)
        matdep_prob_df.index = pop.index
        matdep_prob_df['material_deprivation'] = matdep_prob_df['material_deprivation'].astype(int)
        self.population_view.update(matdep_prob_df["material_deprivation"])

    def calculate_matdep(self, pop):
        """Calculate material deprivation transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # load transition model based on year.
        year = 2019
        transition_model = r_utils.load_transitions(f"material_deprivation/logit/material_deprivation_{year}_{year+1}", self.rpy2_modules)
        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_next_timestep_logit(transition_model, self.rpy2_modules, pop, 'material_deprivation')
        prob_df.columns = [1.]
        return prob_df