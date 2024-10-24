""" File for adding new cohorts from Understanding Society data to the population"""

import pandas as pd
from minos.modules.base_module import Base

# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning


class ReplenishmentNowcast(Base):


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
        # builder.event.register_listener('time_step', self.on_time_step, priority=self.priority)
        super().setup(builder)

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
            new_population = pd.read_csv(f"{self.input_data_dir}/{self.current_year}_US_cohort.csv")
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
            new_wave = pd.read_csv(f"{self.input_data_dir}/{self.current_year}_US_cohort.csv")
        else:
            # otherwise dont load anyone in.
            new_wave = pd.DataFrame()
        # Get alive population.
        pop = self.population_view.get(event.index, query='pidp > 0 and alive == "alive"')
        # Check new data has any simulants in it before adding to frame.
        if new_wave.shape[0] > 0:
            new_cohort = new_wave.loc[~new_wave["pidp"].isin(pop["pidp"])]

            # How many agents to add.
            cohort_size = new_cohort.shape[0]
            # This dictionary appears again in generate_initial_population later.
            # It is the user_data attribute of pop_data. It can be empty if you want but anything needed to initalise
            # simulants is required here. For now, its only the creation time.
            # This is a remnant from daedalus that needs simplifying.
            new_cohort_config = {'sim_state': 'time_step',
                                 'creation_time': event.time,
                                 'new_cohort': new_cohort,
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
        return "replenishmentNowcast"


    def __repr__(self):
        return "ReplenishmentNowcast()"
