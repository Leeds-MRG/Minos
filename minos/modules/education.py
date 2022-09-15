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
                        'hh_income',
                        'education_state',
                        'max_educ']
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
        - All children must now complete GCSE, so before age 17 must have attained GCSE (level 2)
        - A-levels and equivalent finish at 18, so anyone who achieves this will have it applied before age 19 (level 3)
        -

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The `event` that triggered the function call.
        """
        self.year = event.time.year

        # Level 2 is equivalent to GCSE level, which everyone should have achieved by the age of 17
        # No need to test max_educ for this one, everyone stays in education to 16 now minimum
        level2 = self.population_view.get(event.index, query="alive=='alive' and age == 17 and labour_state=='Student'")
        # Update education state and apply back to population view
        level2['education_state'][level2['education_state'] < 2] = 2
        self.population_view.update(level2['education_state'])

        # Level 3 is equivalent to A-level, so make this change by age 19 if max_educ is 3 or larger
        level3 = self.population_view.get(event.index, query="alive=='alive' and age == 19 and labour_state=='Student' and max_educ >= 3")
        level3['education_state'][level3['education_state'] < 3] = 3
        self.population_view.update(level3['education_state'])

        # Level 5 is nursing/medical and HE diploma, so make this change by age 22 if max_educ is 5
        level5 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 22 and labour_state=='Student' and max_educ == 5")
        level5['education_state'][level5['education_state'] < 5] = 5
        self.population_view.update(level5['education_state'])

        # Level 6 is 1st degree or teaching qual (not PGCE), so make this change by age 22 if max_educ is 6 or larger
        level6 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 22 and labour_state=='Student' and max_educ >= 6")
        level6['education_state'][level6['education_state'] < 6] = 6
        self.population_view.update(level6['education_state'])

        # Level 7 is higher degree (masters/PhD), so make this change by age 25 if max_educ is 7
        level7 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 26 and labour_state=='Student' and max_educ == 7")
        level7['education_state'][level7['education_state'] < 7] = 7
        self.population_view.update(level7['education_state'])


    # Special methods for vivarium.
    @property
    def name(self):
        return "education"


    def __repr__(self):
        return "Education()"
