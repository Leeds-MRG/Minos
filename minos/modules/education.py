""" File for adding new cohorts from Understanding Society data to the population"""

import pandas as pd


# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning

class Education:


    # In Daedalus pre_setup was done in the run_pipeline file. This way is tidier and more modular in my opinion.
    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run into the config and simulation object.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        # load in the starting year. This is the first cohort that is loaded.
        return simulation


    def setup(self, builder):
        """ Method for initialising the education module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream("education")

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ['pidp',
                        'age',
                        'sex',
                        'ethnicity',
                        'region',
                        'hh_income']
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=2)


    def on_initialize_simulants(self, pop_data):
        """ Initiate columns for education when new simulants are added.

        Parameters
        ----------
        pop_data : vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).

        Returns
        -------
        None.
        """


    def on_time_step(self, event):
        """ On time step check handle various education changes for people aged 16-30.

        Justification for certain age changes:
        - All children must now complete GCSE, so before age 17 must have attained GCSE
        - A-levels finish at 18, so anyone who achieves this level will have it applied before age 19
        -

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The `event` that triggered the function call.
        """


    # Special methods for vivarium.
    @property
    def name(self):
        return "education"


    def __repr__(self):
        return "Education()"