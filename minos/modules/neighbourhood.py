"""
Module for neighbourhood in Minos.
Calculation of change in neighbourhood quality in minos.
"""

import pandas as pd
from pathlib import Path
import minos.modules.r_utils as r_utils

class Neighbourhood:

    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run into the config and simulation object before simulation.setup().

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
        - Register any value producers/modifiers for neighbourhood
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
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream("neighbourhood")

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
                        'neighbourhood_safety',
                        'SF_12',
                        'labour_state',
                        'education_state',
                        'housing_quality',
                        'job_sec']
        #view_columns += self.transition_model.rx2('model').names
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


    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their neighbourhood
        pop = self.population_view.get(event.index, query="alive =='alive'")
        self.year = event.time.year

        ## Predict next neighbourhood value
        neighbourhood_prob_df = self.calculate_neighbourhood(pop)

        neighbourhood_prob_df["neighbourhood_safety"] = self.random.choice(neighbourhood_prob_df.index,
                                                                           list(neighbourhood_prob_df.columns),
                                                                           neighbourhood_prob_df)+1
        neighbourhood_prob_df.index = neighbourhood_prob_df.index.astype(int)

        # Draw individuals next states randomly from this distribution.
        # Update population with new neighbourhood
        self.population_view.update(neighbourhood_prob_df['neighbourhood_safety'])


    def calculate_neighbourhood(self, pop):
        """Calculate neighbourhood transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # load transition model based on year.
        # get the nearest multiple of 3+1 year. Data occur every 2011,2014,2017 ...
        year = max(self.year, 2011)
        mod = year % 3
        if mod == 0:
            year -= 2 # e.g. 2013 moves back two years to 2011.
        elif mod == 1:
            pass # e.g. 2011 is correct
        elif mod == 2:
            year -= 1 # e.g. 2012 moves back one year to 2011.

        year = min(year, 2014) # transitions only go up to 2014.
        transition_model = r_utils.load_transitions(f"neighbourhood/clm/neighbourhood_clm_{year}_{year + 3}")
        # The calculation relies on the R predict method and the model that has already been specified
        nextWaveNeighbourhood = r_utils.predict_next_timestep_clm(transition_model, pop)
        return nextWaveNeighbourhood

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'neighbourhood'


    def __repr__(self):
        return "Neighbourhood()"
