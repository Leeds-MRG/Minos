""" File for adding new cohorts from Understanding Society data to the population"""

import pandas as pd
from minos.modules.base_module import Base

# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning


class Replenishment(Base):


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
        # load in pop_projections for reweighting
        #projections = pd.read_csv('pop_projections_2008-2070.csv')
        # write pop_projections into simulation object as they are used every wave
        #simulation._data.write('pop_projections_2008-2070')
        # load in the starting year. This is the first cohort that is loaded.
        return simulation


    def setup(self, builder):
        """ Method for initialising the depression module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """
        self.current_year = builder.configuration.time.start.year

        # Define which columns are seen in builder.population.get_view calls.
        # Also defines which columns are created by on_initialize_simulants.
        view_columns = ['pidp',
                        'age',
                        'sex',
                        'education_state',
                        'alive',
                        'ethnicity',
                        'entrance_time',
                        'time',
                        'exit_time',
                        'labour_state',
                        'job_industry',
                        'job_occupation',
                        'job_sec',
                        'job_duration_m',
                        'job_duration_y',
                        'depression',
                        'academic_year',
                        'hidp',
                        'birth_month',
                        'birth_year',
                        'nobs',
                        'region',
                        'SF_12',
                        'hh_int_y',
                        'hh_int_m',
                        'Date',
                        'housing_quality',
                        'hh_income',
                        'neighbourhood_safety',
                        'ncigs',
                        'alcohol_spending',
                        'smoker',
                        'loneliness',
                        'weight',
                        'ndrinks',
                        'nkids',
                        'max_educ',
                        'yearly_energy',
                        'job_sector',
                        'SF_12p',
                        'gross_pay_se',
                        'nutrition_quality',
                        'job_hours_se',
                        'hourly_rate',
                        'job_hours',
                        'job_inc', 
                        'jb_inc_per', 
                        'hourly_wage', 
                        'gross_paypm',
                        'phealth',
                        'marital_status',
                        'hh_comp']

        # Shorthand methods for readability.
        self.population_view = builder.population.get_view(view_columns)  # view simulants
        self.simulant_creater = builder.population.get_simulant_creator()  # create simulants.
        self.register = builder.randomness.register_simulants  # register new simulants to CRN streams (seed them).

        # load in population projection data for reweighting and generate a lookup table
        #pop_projections = builder.data.load('pop_projections_2008-2070')
        #self.pop_projections = builder.lookup.build_table(pop_projections,
        #                                                  key_columns=['sex'],
        #                                                  parameter_columns=['year', 'age'],
        #                                                  value_columns=['count'])


        # Defines how this module initialises simulants when self.simulant_creater is called.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=view_columns)
        # Register ageing, updating time and replenishment events on time_step.
        builder.event.register_listener('time_step', self.age_simulants)
        #builder.event.register_listener('time_step', self.update_time)
        builder.event.register_listener('time_step', self.on_time_step, priority=0)


    def on_initialize_simulants(self, pop_data):
        """ function for loading new waves of simulants into the population from US data.

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

        # placeholder
        new_population = pd.DataFrame()

        # On the initial setup phase just load in the first wave of data
        if pop_data.user_data["sim_state"] == "setup":
            # Load in initial data frame.
            # Add entrance times and convert ages to floats for pd.timedelta to handle.
            #new_population = pd.read_csv(f"data/final_US/{self.current_year}_US_cohort.csv")
            new_population = pd.read_csv(f"data/final_US/2017_US_cohort.csv")  # FORCE START IN 2017
            new_population.loc[new_population.index, "entrance_time"] = new_population["time"]
            new_population.loc[new_population.index, "age"] = new_population["age"].astype(float)
        elif pop_data.user_data["cohort_type"] == "replenishment":
            # After setup only load in 16 year old agents from the 2018 datafile at each wave
            #new_population = pd.read_csv(f"data/final_US/2018_US_cohort.csv")
            #new_population = new_population[(new_population['age'] == 16)]

            # After setup only load in agents from new cohorts who arent yet in the population frame via ids (PIDPs).
            new_population = pop_data.user_data["new_cohort"]
            new_population.loc[new_population.index, "entrance_time"] = pop_data.user_data["creation_time"]
            new_population.loc[new_population.index, "age"] = new_population["age"].astype(float)

        elif pop_data.user_data["cohort_type"] == "births":
            # If we're adding new births need to generate all US data columns from scratch (yay).
            # This is an empty frame apart from two critical entrance time and age columns.
            # Everything else is added by other modules.
            new_population = pd.DataFrame(index=pop_data.index)
            new_population.loc[new_population.index, "entrance_time"] = pop_data.user_data["creation_time"]
            new_population.loc[new_population.index, "age"] = 0.

        # Force index of new cohort to align with index of total population data frame
        # otherwise this will overwrite some sims.
        # A new population frame of one sim will overwrite the sim at index 0.
        new_population.index = pop_data.index

        # Register simulants entrance time and age to CRN. I.E keep them seeded.
        # Add new simulants to the overall population frame.
        self.register(new_population[["entrance_time", "age"]])
        self.population_view.update(new_population)


    def on_time_step(self, event):
        """ On time step add new simulants to the module.
        New simulants to be added must be 16 years old, and will be reweighted to fit some constraints defined
        from census key statistics (principal population projections).

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The `event` that triggered the function call.
        """

        # Only add new cohorts on the october of each year when the data is taken.
        # If its october update the current year and load in new cohort data.
        # Also update the time variable with the new year for everyone (dead people also)
        pop = self.population_view.get(event.index, query='pidp > 0')
        if event.time.month == 10 and event.time.year == self.current_year + 1:
            self.current_year += 1
            pop['time'] += 1
            self.population_view.update(pop)
            # Base year for the simulation is 2018, so we'll use this to select our replenishment pop
            new_wave = pd.read_csv(f"data/replenishing/replenishing_pop_2019-2070.csv")
            # Now select the population for the current year
            new_wave = new_wave[(new_wave['time'] == event.time.year)]
            # TODO: Check how the population size changes over time now that we're only adding in 16 year olds
            # It might mean that the pop shrinks over time, as the counts within age groups is generally between 250-500
            # respondents (16-~80 year olds, older ages can have far less)
        else:
            # otherwise dont load anyone in.
            new_wave = pd.DataFrame()


        # Get alive population.
        #pop = self.population_view.get(event.index, query='pidp > 0 and alive == "alive"')
        # Check new data has any simulants in it before adding to frame.
        if new_wave.shape[0] > 0:
            #new_cohort = new_wave.loc[~new_wave["pidp"].isin(pop["pidp"])]

            # new wave of simulants need a unique pidp value
            # can achieve this by adding the year and month to each pidp plus 1,000,000 (pidps are 8 digit numbers)
            # I've checked this and made sure that we'll never get a duplicate pidp
            #new_wave['pidp'] = new_wave['pidp'] + event.time.year + event.time.month + 1000000

            # re-weight incoming population (currently just by sex)
            #new_wave = self.reweight_repl_input(new_wave)

            # How many agents to add.
            cohort_size = new_wave.shape[0]
            # This dictionary appears again in generate_initial_population later.
            # It is the user_data attribute of pop_data. It can be empty if you want but anything needed to initalise
            # simulants is required here. For now, its only the creation time.
            # This is a remnant from daedalus that needs simplifying.
            new_cohort_config = {'sim_state': 'time_step',
                                 'creation_time': event.time,
                                 'new_cohort': new_wave,
                                 'cohort_type': "replenishment",
                                 'cohort_size': cohort_size}

            # Create simulants and add them to the population data frame.
            # The method used can be changed in setup via builder.population.initializes_simulants.
            self.simulant_creater(cohort_size, population_configuration=new_cohort_config)


    def age_simulants(self, event):
        """
        Age everyone by the length of the simulation time step in days

        Parameters
        ----------
        event : builder.event
            some time point at which to run the method.
        """
        # get alive people and add time in years to their age.
        population = self.population_view.get(event.index, query="alive == 'alive'")
        population['age'] += event.step_size / pd.Timedelta(days=365.25)
        self.population_view.update(population)


    def update_time(self, event):
        """
        Update time variable by the length of the simulation time step in days

        Parameters
        ----------
        event : builder.event
            some time point at which to run the method.
        """
        # get alive people and add time in years to their age.
        population = self.population_view.get(event.index, query="alive == 'alive'")
        population['time'] += event.step_size / pd.Timedelta(days=365.25)
        self.population_view.update(population)


    # Special methods for vivarium.
    @property
    def name(self):
        return "replenishment"


    def __repr__(self):
        return "Replenishment()"





class NoReplenishment(Base):

    def setup(self, builder):
        """ Method for initialising the depression module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """
        self.current_year = builder.configuration.time.start.year

        # Define which columns are seen in builder.population.get_view calls.
        # Also defines which columns are created by on_initialize_simulants.
        view_columns = ['pidp',
                        'age',
                        'sex',
                        'education_state',
                        'alive',
                        'ethnicity',
                        'entrance_time',
                        'time',
                        'exit_time',
                        'labour_state',
                        'job_industry',
                        'job_occupation',
                        'job_sec',
                        'job_duration_m',
                        'job_duration_y',
                        'depression',
                        'academic_year',
                        'hidp',
                        'birth_month',
                        'birth_year',
                        'nobs',
                        'region',
                        'SF_12',
                        'hh_int_y',
                        'hh_int_m',
                        'Date',
                        'housing_quality',
                        'hh_income',
                        'neighbourhood_safety',
                        'ncigs',
                        'alcohol_spending',
                        'smoker',
                        'loneliness',
                        'weight',
                        'ndrinks',
                        'nkids',
                        'max_educ',
                        'yearly_energy',
                        'job_sector',
                        'SF_12p',
                        'gross_pay_se',
                        'nutrition_quality',
                        'job_hours_se',
                        'hourly_rate',
                        'job_hours',
                        'job_inc',
                        'jb_inc_per',
                        'hourly_wage',
                        'gross_paypm']

        # Shorthand methods for readability.
        self.population_view = builder.population.get_view(view_columns)  # view simulants
        self.simulant_creater = builder.population.get_simulant_creator()  # create simulants.
        self.register = builder.randomness.register_simulants  # register new simulants to CRN streams (seed them).

        # load in population projection data for reweighting and generate a lookup table
        #pop_projections = builder.data.load('pop_projections_2008-2070')
        #self.pop_projections = builder.lookup.build_table(pop_projections,
        #                                                  key_columns=['sex'],
        #                                                  parameter_columns=['year', 'age'],
        #                                                  value_columns=['count'])


        # Defines how this module initialises simulants when self.simulant_creater is called.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=view_columns)
        # Register ageing, updating time and replenishment events on time_step.
        builder.event.register_listener('time_step', self.age_simulants)
        builder.event.register_listener('time_step', self.on_time_step, priority=0)


    def on_initialize_simulants(self, pop_data):
        """ function for loading new waves of simulants into the population from US data.

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

        # placeholder
        new_population = pd.DataFrame()

        # On the initial setup phase just load in the first wave of data
        if pop_data.user_data["sim_state"] == "setup":
            # Load in initial data frame.
            # Add entrance times and convert ages to floats for pd.timedelta to handle.
            new_population = pd.read_csv(f"data/final_US/{self.current_year}_US_cohort.csv")
            new_population.loc[new_population.index, "entrance_time"] = new_population["time"]
            new_population.loc[new_population.index, "age"] = new_population["age"].astype(float)

        elif pop_data.user_data["cohort_type"] == "replenishment":
            # After setup only load in 16 year old agents from the 2018 datafile at each wave
            #new_population = pd.read_csv(f"data/final_US/2018_US_cohort.csv")
            #new_population = new_population[(new_population['age'] == 16)]

            # After setup only load in agents from new cohorts who arent yet in the population frame via ids (PIDPs).
            new_population = pd.DataFrame(columns=["entrance_time", "age"])
            new_population = pop_data.user_data["new_cohort"]
            new_population.loc[new_population.index, "entrance_time"] = pop_data.user_data["creation_time"]
            new_population.loc[new_population.index, "age"] = new_population["age"].astype(float)


        # Force index of new cohort to align with index of total population data frame
        # otherwise this will overwrite some sims.
        # A new population frame of one sim will overwrite the sim at index 0.
        new_population.index = pop_data.index

        # Register simulants entrance time and age to CRN. I.E keep them seeded.
        # Add new simulants to the overall population frame.
        self.register(new_population[["entrance_time", "age"]])
        self.population_view.update(new_population)


    def on_time_step(self, event):
        """ On time step add new simulants to the module.
        New simulants to be added must be 16 years old, and will be reweighted to fit some constraints defined
        from census key statistics (principal population projections).

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The `event` that triggered the function call.
        """
        # no replenishment after initial cohort. do nothing...
        pass


    def age_simulants(self, event):
        """
        Age everyone by the length of the simulation time step in days

        Parameters
        ----------
        event : builder.event
            some time point at which to run the method.
        """
        # get alive people and add time in years to their age.
        population = self.population_view.get(event.index, query="alive == 'alive'")
        population['age'] += event.step_size / pd.Timedelta(days=365.25)
        self.population_view.update(population)


    # Special methods for vivarium.
    @property
    def name(self):
        return "no_replenishment"


    def __repr__(self):
        return "NoReplenishment()"
