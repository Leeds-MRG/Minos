"""
Module for housing in Minos.
Upgrade of household appliances
Possible future work for moving households and changing household composition (e.g. marrying/births)
"""

import pandas as pd
from pathlib import Path
from minos.modules import r_utils

class Housing:

    @property
    def name(self):
        return "housing"

    def __repr__(self):
        return "Housing()"

    # In Daedalus pre_setup was done in the run_pipeline file. This way is tidier and more modular in my opinion.
    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run into the config and simulation object.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run.

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run with updated config/inputs.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        # nothing done here yet. transition models specified by year later.
        return simulation

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

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream("housing")
        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["sex",
                        "labour_state",
                        "SF_12",
                        "job_sec",
                        "ethnicity",
                        "age",
                        "housing_quality",
                        "hh_income",]
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=3)

    def on_initialize_simulants(self, pop_data):
        """  Initiate columns for mortality when new simulants are added.

        Parameters
        ----------
        pop_data: vivarium.framework.population.SimulantData
            Custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        Returns
        -------
        None
        """
        # Initiate any columns created by this module and add them to the main population.
        # No synthetic columns for housing currently. Maybe housing history variables added here.
        return pop_data

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

        housing_prob_df = self.calculate_housing(pop)

        housing_prob_df["housing_quality"] = self.random.choice(housing_prob_df.index, list(housing_prob_df.columns), housing_prob_df)+1
        housing_prob_df.index = housing_prob_df.index.astype(int)

        self.population_view.update(housing_prob_df["housing_quality"])

    def calculate_housing(self, pop):
        """Calculate housing transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # load transition model based on year.
        year = min(self.year, 2018)
        transition_model = r_utils.load_transitions(f"housing/clm/housing_clm_{year}_{year+1}")
        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_next_timestep_clm(transition_model, pop)
        return prob_df
