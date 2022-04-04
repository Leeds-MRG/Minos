"""
Module for income in Minos.
Calculation of monthly household income
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""

import pandas as pd
from pathlib import Path
import statsmodels.api as sm
import statsmodels.formula.api as smf


class Income:

    @property
    def name(self):
        return 'income'


    def __repr__(self):
        return 'Income()'

    @staticmethod
    def write_config(config):
        """ Update config file with what this module needs to run.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for Minos.
        Returns
        -------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for Minos with added items needed for this module to run.
        """
        return config


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

        return simulation


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

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.lookup.build_table()

        # Assign randomness streams if necessary.
        self.randomness = builder.randomness.get_stream("income")

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        view_columns = ['age', 'sex', 'ethnicity', 'region']
        self.population_view = builder.population.get_view(
            ["alive"], query="alive == 'alive'"
        )

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step())


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


    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        ## Predict next income value
        # For predicting next income state, we will use the R predict functions

        # Draw individuals next states randomly from this distribution.
        # Update population with new income


    def calculate_income(self, index):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """

