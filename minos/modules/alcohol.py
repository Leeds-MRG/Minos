"""
Module for alcohol in Minos.
Calculation of monthly household alcohol
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""

import pandas as pd
import minos.modules.r_utils as r_utils

class Alcohol:

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

        # Load in transition model

        return simulation


    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for alcohol
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
        self.random = builder.randomness.get_stream("alcohol")

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
                        'SF_12',
                        'education_state',
                        'labour_state',
                        'job_sec',
                        'hh_income',
                        'alcohol_spending']
        #view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=2)


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
        # Get living people to update their alcohol
        pop = self.population_view.get(event.index, query="alive =='alive'")
        self.year = event.time.year

        ## Predict next alcohol value
        newWaveAlcohol = self.calculate_alcohol(pop)
        newWaveAlcohol = pd.DataFrame(newWaveAlcohol, columns=["alcohol_spending"])
        # Set index type to int (instead of object as previous)
        newWaveAlcohol.index = newWaveAlcohol.index.astype(int)

        # Draw individuals next states randomly from this distribution.
        # Update population with new alcohol
        self.population_view.update(newWaveAlcohol['alcohol_spending'].astype(int))


    def calculate_alcohol(self, pop):
        """Calculate alcohol transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # load transition model based on year.
        year = min(self.year, 2018)
        transition_model = r_utils.load_transitions(f"alcohol/zip/alcohol_zip_{year}_{year + 1}")
        # The calculation relies on the R predict method and the model that has already been specified
        nextWaveAlcohol = r_utils.predict_next_timestep_alcohol_zip(transition_model, pop)
        return nextWaveAlcohol

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'alcohol'


    def __repr__(self):
        return "Alcohol()"
