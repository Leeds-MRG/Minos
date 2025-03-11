"""
File for adding new cohorts from Understanding Society data to the population
"""

import sys
import os
from os.path import dirname as up
import pandas as pd
import numpy as np
import logging
from minos.modules.base_module import Base
import minos.data_generation.generate_repl_pop as grp
import minos.data_generation.US_utils as uut

PERSISTENT_DIR = os.path.join(up(up(up(__file__))), 'persistent_data')
PROJECTIONS_DEFAULT = 'age-sex-ethnic_projections_2008-2061.csv'
REPL_AGE_DEFAULT = 16
SAMPLE_AGES_DEFAULT = [16, 17, 18]
DATA_PATH = os.path.join(up(up(up(__file__))), 'data')
TRANSITIONS_PATH = os.path.join(DATA_PATH, 'transitions')

# suppressing a warning that isn't a problem
# pd.options.mode.chained_assignment = None  # default='warn' #supress SettingWithCopyWarning


class Replenishment(Base):

    # Special methods for vivarium.
    @property
    def name(self):
        return "Replenishment"

    def __repr__(self):
        return "Replenishment()"

    def setup(self, builder):
        """ Method for initialising the depression module.
        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """
        self.current_year = builder.configuration.time.start.year
        self.config = builder.configuration

        # Define which columns are seen in builder.population.get_view calls.
        # Also defines which columns are created by on_initialize_simulants.

        # view_columns = ['pidp',
        #                 'age',
        #                 'sex',
        #                 'education_state',
        #                 'alive',
        #                 'ethnicity',
        #                 'entrance_time',
        #                 'time',
        #                 'exit_time',
        #                 'job_industry',
        #                 'job_occupation',
        #                 'job_sec',
        #                 'job_duration_m',
        #                 'job_duration_y',
        #                 'depression',
        #                 'academic_year',
        #                 'hidp',
        #                 'birth_month',
        #                 'birth_year',
        #                 'nobs',
        #                 'region',
        #                 'SF_12',
        #                 'hh_int_y',
        #                 'hh_int_m',
        #                 'Date',
        #                 'housing_quality',
        #                 'hh_income',
        #                 'neighbourhood_safety',
        #                 'ncigs',
        #                 'alcohol_spending',
        #                 'smoker',
        #                 'loneliness',
        #                 'weight',
        #                 'nkids',
        #                 'nkids_ind',
        #                 'ndrinks',
        #                 'max_educ',
        #                 'yearly_energy',
        #                 'job_sector',
        #                 'SF_12p',
        #                 'gross_pay_se',
        #                 'nutrition_quality',
        #                 'job_hours_se',
        #                 'job_hours',
        #                 'job_inc',
        #                 'jb_inc_per',
        #                 'hourly_wage',
        #                 'gross_paypm',
        #                 'phealth',
        #                 'marital_status',
        #                 'hh_comp',
        #                 #'labour_state',
        #                 'S7_labour_state',
        #                 'S7_housing_quality',
        #                 'S7_neighbourhood_safety',
        #                 'S7_physical_health',
        #                 'S7_mental_health',
        #                 'equivalent_income',
        #                 'heating',
        #                 'hhsize',
        #                 'financial_situation',
        #                 'housing_tenure',
        #                 'urban',
        #                 'SF_12_diff',
        #                 'hh_income_diff',
        #                 'nutrition_quality_diff',
        #                 'job_hours_diff',
        #                 'hourly_wage_diff',
        #                 'child_ages',
        #                 ]

        # view_columns = list(pd.read_csv("data/imputed_final_US/2020_US_cohort.csv").columns)
        # view_columns = list(pd.read_csv("data/scaled_gb_US/2019_US_cohort.csv").columns)

        # HR 24/09/24 Workaround for all cases (US and synthpop): get columns from input data
        column_source = self.config.base_input_data_dir
        latest_file = os.listdir(column_source)[0]
        view_columns = list(pd.read_csv(os.path.join(column_source, latest_file)).columns)

        if self.config.synthetic:  # only have spatial column and new pidp for synthpop.
            try:
                view_columns += self.config.replenishing_columns  # HR 13/09/24 Workaround to reduce data size for GB synthpop
            except:
                view_columns += ["ZoneID",
                                 # "new_pidp",
                                 'local_simd_deciles',
                                 'simd_decile',
                                 # 'cluster'
                                 ]
        columns_created = ['entrance_time']

        # Shorthand methods for readability.
        self.population_view = builder.population.get_view(view_columns + columns_created)  # view simulants
        self.simulant_creater = builder.population.get_simulant_creator()  # create simulants.
        self.register = builder.randomness.register_simulants  # register new simulants to CRN streams (seed them).

        # Defines how this module initialises simulants when self.simulant_creater is called.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=view_columns + columns_created)
        # Register ageing, updating time and replenishment events on time_step.
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
            new_population.loc[new_population.index, "age"] = new_population["age"].astype('Int64')
            logging.info(f"Starting cohort loaded for {self.current_year}.")

        elif pop_data.user_data["cohort_type"] == "replenishment":
            # After setup only load in agents from new cohorts who arent yet in the population frame via ids (PIDPs).
            new_population = pop_data.user_data["new_cohort"]
            new_population.loc[new_population.index, "entrance_time"] = pop_data.user_data["creation_time"]
            new_population.loc[new_population.index, "age"] = new_population["age"].astype("Int64")
            logging.info(f"Replenishing cohort added for {self.current_year}.")

        elif pop_data.user_data["cohort_type"] == "births":
            # If we're adding new births need to generate all US data columns from scratch (yay).
            # This is an empty frame apart from two critical entrance time and age columns.
            # Everything else is added by other modules.
            new_population = pd.DataFrame(index=pop_data.index)
            new_population.loc[new_population.index, "entrance_time"] = pop_data.user_data["creation_time"]
            new_population.loc[new_population.index, "age"] = 0.
            logging.info(f"Births cohort added for {self.current_year}.")

        # Force index of new cohort to align with index of total population data frame
        # otherwise this will overwrite some sims.
        # A new population frame of one sim will overwrite the sim at index 0.
        new_population.index = pop_data.index

        # Register simulants entrance time and age to CRN. I.E keep them seeded.
        # Add new simulants to the overall population frame.
        self.register(new_population[["entrance_time", "age"]])
        np.seterr(invalid='ignore')
        try:  # Deal with missing var if using pared-down variable set
            new_population['S7_neighbourhood_safety'] = new_population['S7_neighbourhood_safety'].astype(str)  # HR 457
        except KeyError:
            print('KeyError for S7_neighbourhood_safety')

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

        logging.info("REPLENISHMENT")

        # Only add new cohorts on the october of each year when the data is taken.
        # If its october update the current year and load in new cohort data.
        # Also update the time variable with the new year for everyone (dead people also)
        pop = self.population_view.get(event.index, query='pidp > 0')
        if event.time.month == 10 and event.time.year == self.current_year + 1:
            self.current_year += 1
            #pop['time'] += 1
            self.population_view.update(pop)
            # Base year for the simulation is 2018, so we'll use this to select our replenishment pop
            if 'run_id' in self.config.keys():
                #new_wave = pd.read_csv(f"{self.replenishing_dir}/{(self.config['run_ID']//10) + 1}_replenishing_pop_2015-2070.csv")
                new_wave = pd.read_csv(f"{self.replenishing_dir}/{((self.config['run_ID']-1)//10) + 1}_replenishing_pop_2015-2070.csv")
            else:
                new_wave = pd.read_csv(f"{self.replenishing_dir}/replenishing_pop_2015-2070.csv")

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
            # logging
            logging.info(f"\tTotal new 16 year olds added to the model: {cohort_size}")


class NoReplenishment(Base):

    def setup(self, builder):
        """ Method for initialising the depression module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """
        self.current_year = builder.configuration.time.start.year
        config = builder.configuration

        # Define which columns are seen in builder.population.get_view calls.
        # Also defines which columns are created by on_initialize_simulants.
        # view_columns = ['pidp',
        #                 'age',
        #                 'sex',
        #                 'education_state',
        #                 'alive',
        #                 'ethnicity',
        #                 'entrance_time',
        #                 'time',
        #                 'exit_time',
        #                 'job_industry',
        #                 'job_occupation',
        #                 'job_sec',
        #                 'job_duration_m',
        #                 'job_duration_y',
        #                 'depression',
        #                 'academic_year',
        #                 'hidp',
        #                 'birth_month',
        #                 'birth_year',
        #                 'nobs',
        #                 'region',
        #                 'SF_12',
        #                 'hh_int_y',
        #                 'hh_int_m',
        #                 'Date',
        #                 'housing_quality',
        #                 'hh_income',
        #                 'neighbourhood_safety',
        #                 'ncigs',
        #                 'alcohol_spending',
        #                 'smoker',
        #                 'loneliness',
        #                 'weight',
        #                 'ndrinks',
        #                 'nkids',
        #                 'max_educ',
        #                 'yearly_energy',
        #                 'job_sector',
        #                 'SF_12p',
        #                 'gross_pay_se',
        #                 'nutrition_quality',
        #                 'job_hours_se',
        #                 'job_hours',
        #                 'job_inc',
        #                 'jb_inc_per',
        #                 'hourly_wage',
        #                 'gross_paypm',
        #                 'marital_status',
        #                 'phealth',
        #                 'hh_comp',
        #                 'S7_labour_state',
        #                 'S7_housing_quality',
        #                 'S7_neighbourhood_safety',
        #                 'S7_physical_health',
        #                 'S7_mental_health',
        #                 'job_hours_diff',
        #                 ]

        view_columns = list(pd.read_csv("data/imputed_final_US/2020_US_cohort.csv").columns)

        if config.synthetic:  # only have spatial column and new pidp for synthpop.
            view_columns += ["ZoneID",
                             # "new_pidp",
                             'local_simd_deciles',
                             'simd_decile',
                             # 'cluster'
                             ]

        columns_created = ['entrance_time']

        # Shorthand methods for readability.
        self.population_view = builder.population.get_view(view_columns + columns_created)  # view simulants
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
                                                 creates_columns=view_columns + columns_created)
        # Register ageing, updating time and replenishment events on time_step.
        #builder.event.register_listener('time_step', self.age_simulants)
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
            # # After setup only load in 16 year old agents from the 2018 datafile at each wave
            # #new_population = pd.read_csv(f"data/final_US/2018_US_cohort.csv")
            # #new_population = new_population[(new_population['age'] == 16)]
            #
            # # After setup only load in agents from new cohorts who arent yet in the population frame via ids (PIDPs).
            # #new_population = pd.DataFrame(columns=["entrance_time", "age"])
            # new_population = pop_data.user_data["new_cohort"]
            # new_population.loc[new_population.index, "entrance_time"] = pop_data.user_data["creation_time"]
            # new_population.loc[new_population.index, "age"] = new_population["age"].astype(float)
            pass

        elif pop_data.user_data["cohort_type"] == "births":
            # If we're adding new births need to generate all US data columns from scratch (yay).
            # This is an empty frame apart from two critical entrance time and age columns.
            # Everything else is added by other modules.
            new_population = pd.DataFrame(index=pop_data.index)
            new_population.loc[new_population.index, "entrance_time"] = pop_data.user_data["creation_time"]
            new_population.loc[new_population.index, "age"] = 0.
            logging.info(f"Births cohort added for {self.current_year}.")

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
        population['time'] += int(event.step_size / pd.Timedelta(days=365.25))
        self.population_view.update(population)

    # Special methods for vivarium.
    @property
    def name(self):
        return "no_replenishment"

    def __repr__(self):
        return "NoReplenishment()"


# HR 09/02/25 Return Euclidean distance between two vectors
def euclidean(v1, v2):
    d = np.sqrt(np.sum((v1 - v2) ** 2))
    return d


# HR 09/02/25 Objective function for simulated annealing function - used as measure of convergence
def objective_function(df, target_dict):

    PENALTY_VALUE = 10.0  # Setting this >0 avoids samples with empty categories being produced

    obj = 0.0
    for v, t in target_dict.items():
        if isinstance(t, (int, float)):  # For int/float
            m = df[v].mean()
            new_val = euclidean(m, t)
        elif isinstance(t, dict):  # For categoricals

            vc = df[v].value_counts(normalize=True)

            # Must check all categories in target are present; if not, add zero value to avoid ValueError
            if set(t) != set(df[v]):
                not_present = set(t) - set(df[v])
                for _np in not_present:
                    vc.loc[_np] = PENALTY_VALUE

            vec = np.array(vc.sort_index())
            t_sorted = ([v for (k, v) in sorted(t.items())])

            new_val = euclidean(vec, t_sorted)
        else:
            new_val = PENALTY_VALUE
        obj += new_val
    return obj


def sample_with_constraints(df,
                            target_dict,
                            frac=0.1,
                            n=None,
                            delta_threshold=0.002,  # Convergence threshold
                            subfrac=0.005,  # Relative size of subsample to replace
                            T_0=1000.0,  # Initial temperature
                            alpha=0.99,  # Cooling rate
                            ):
    """
    Returns a fractional sample of the input dataframe with a set of values close to the target set.
    Uses simulated annealing to find the sample.

    Parameters:
    df (pandas.DataFrame): The input dataframe
    target_dict (dict): The target set of values
    frac (float): The size of the sample to be returned, expressed as a fraction of the input dataframe

    Returns:
    pandas.DataFrame: A fractional sample of the input dataframe with a mean value close to the target values
    """
    # Get size of sample to create -> this prioritises n if it is specified
    if n is not None and isinstance(n, (int, float, )):
        frac = n / len(df)

    # Initialise variables
    oversample = frac > 1.0  # Only allow for duplicates per sample if requested size bigger than repl source pop
    current_sample = df.sample(frac=frac, replace=oversample)
    current_obj = objective_function(current_sample, target_dict)  # Objective of current sample
    T = T_0

    # Run simulated annealing loop
    i = 0

    # while T > 1.0:
    while current_obj > delta_threshold:

        # 1. Get subsample to be used as replacement
        n_replace = int(subfrac * frac * len(df))
        to_replace = df.sample(n=n_replace)

        # 2. Replace random rows in current sample with subsample
        new_sample = current_sample.sample(frac=1)[:-n_replace]  # Shuffle then drop last n rows
        new_sample = pd.concat([new_sample, to_replace])

        # 3. Calculate objective of proposed sample
        new_obj = objective_function(new_sample, target_dict)
        diff = new_obj - current_obj

        # 4. If proposed sample better than current sample, keep it; otherwise discard
        # Accept or reject the new sample based on the Metropolis criterion
        # if diff < 0 or np.exp(-diff / T) > np.random.rand():
        if diff < 0:
            current_sample = new_sample
            current_obj = new_obj

        # Cool down the system
        T *= alpha
        sys.stdout.write('\rIteration no. {} (obj: {:.6f}), N = {}'.format(i, current_obj, len(current_sample)))

        # # Check if the current sample is close enough to the target mean
        # if abs(current_obj - target) < delta_threshold:
        #     break

        i += 1

    print('\r')
    return current_sample, current_obj


def get_age_fraction_by_year_newethpop(_path, _file, ages):
    if isinstance(ages, (int, )):
        ages = [ages]
    pop = pd.read_csv(os.path.join(_path, _file))

    age_frac_by_year = {}
    for age in ages:
        age_frac_by_year[age] = pop.groupby('year').apply(
            lambda x: x.loc[x['age'] == age]['count'].sum() / x['count'].sum()).to_dict()
    return age_frac_by_year


def get_ethnicity_by_year_newethpop(_path, _file, ages):
    if isinstance(ages, (int, )):
        ages = [ages]
    pop = pd.read_csv(os.path.join(_path, _file))

    eth_by_year = {}
    for age in ages:
        sub = pop.loc[pop['age'] == age]
        eth_by_year[age] = sub.groupby('year').apply(
            lambda x: x.groupby('ethnicity')['count'].sum() / x['count'].sum()).T.to_dict()
    return eth_by_year


def get_sex_by_year_newethpop(_path, _file, ages):
    if isinstance(ages, (int, )):
        ages = [ages]
    pop = pd.read_csv(os.path.join(_path, _file))

    eth_by_year = {}
    for age in ages:
        sub = pop.loc[pop['age'] == age]
        eth_by_year[age] = sub.groupby('year').apply(
            lambda x: x.groupby('sex')['count'].sum() / x['count'].sum()).T.to_dict()
    return eth_by_year


# HR 10/02/25 Get size of cohort required to give certain proportion of total population
def get_cohort_size_by_proportion(target_proportion, pop_size):
    cohort_size = pop_size / ((1.0 / target_proportion) - 1.0)
    return cohort_size


# HR 13/02/25 Correct all time variables in repl cohort; this reproduces functionality in generate_repl_pop.expand_repl
def correct_temporal_variables(pop, repl_year, current_year):

    year_increment = current_year - repl_year
    pop['time'] = current_year
    pop['birth_year'] = pop['birth_year'] + year_increment
    pop['hh_int_y'] = pop['hh_int_y'].astype(int) + year_increment
    pop = uut.generate_interview_date_var(pop)

    return pop


# HR 12/02/25 Wrapper for creating repl pop at runtime or offline
def create_replenishing_population(pop_size,
                                   target_year,
                                   repl_year=2019,
                                   source_pop=None,
                                   sample_ages=SAMPLE_AGES_DEFAULT,
                                   repl_age=REPL_AGE_DEFAULT,
                                   delta_threshold=0.02,
                                   ):

    if source_pop is None:
        source_path = os.path.join(DATA_PATH, 'scaled_gb_US')
        source_file = f'{repl_year}_US_cohort.csv'
        source_pop = pd.read_csv(os.path.join(source_path, source_file))

    # Get reference values to match
    ref_deets = (PERSISTENT_DIR, PROJECTIONS_DEFAULT)
    afrac = get_age_fraction_by_year_newethpop(*ref_deets, ages=16)
    aeth = get_ethnicity_by_year_newethpop(*ref_deets, ages=16)
    asex = get_sex_by_year_newethpop(*ref_deets, ages=16)

    # Get sex and ethnicity fractions to be used as targets in simulated annealing algorithm + sample size
    sex_target = asex[repl_age][target_year]
    eth_target = aeth[repl_age][target_year]
    af = afrac[repl_age][target_year]
    repl_size = get_cohort_size_by_proportion(af, pop_size)

    # Filter source population for valid values only; avoids missing value issues during simulated annealing
    source_filtered = source_pop.loc[(source_pop['sex'].isin(sex_target)) &
                                     (source_pop['ethnicity'].isin(eth_target)) &
                                     (source_pop['age'].isin(sample_ages)),
    ]

    repl_pop, obj = sample_with_constraints(source_filtered,
                                            target_dict={'sex': sex_target,
                                                         'ethnicity': eth_target,
                                                         },
                                            delta_threshold=delta_threshold,
                                            n=repl_size,
                                            )

    # 1. Correct ages and times/dates; need to do [age, birth_year, hh_int_y, time]; function for Date is in US_utils
    repl_pop.loc[repl_pop['age'] != REPL_AGE_DEFAULT, 'age'] = REPL_AGE_DEFAULT  # Accounts for possibility of drawing repl from ages other than 16yos
    repl_pop = correct_temporal_variables(repl_pop, repl_year=2019, current_year=target_year)

    # 2. Predict max_educ variable (uses transition model); function is in generate_repl_pop
    repl_pop.loc[repl_pop['education_state'] > 2, 'education_state'] = 2
    repl_pop.reset_index(drop=True, inplace=True)  # Avoids issue with transition model (duplicate index values)
    repl_pop = grp.predict_education(repl_pop, TRANSITIONS_PATH)

    return repl_pop


# HR 13/02/25 Class specifically for use with individual-level GB synthpop
# Main difference to Replenishment (from which it inherits) are:
# 1. Replenishing population is created at runtime from the synthpop; this uses the same projections as Replenishment
# but repl pop size is specified explicitly, rather than through weights
# 2. As a result, the on_time_step method is vastly simpler
class ReplenishmentIndividual(Replenishment):

    @property
    def name(self):
        return "ReplenishmentIndividual"

    def __repr__(self):
        return "ReplenishmentIndividual()"

    def on_time_step(self, event):
        """ On time step add new simulants to the module.
        New simulants to be added must be 16 years old, the number and ethnicity/sex distribution matched to
        population projections

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The `event` that triggered the function call.
        """

        logging.info("REPLENISHMENT (INDIVIDUAL LEVEL FOR GB SYNTHPOP)")
        print('Running replenishment for GB synthpop...')

        population = self.population_view.get(event.index, query="alive == 'alive'")
        print('Pop. size:', len(population))
        current_year = event.time.year
        new_wave = create_replenishing_population(pop_size=len(population),
                                                  target_year=current_year,
                                                  )
        cohort_size = len(new_wave)
        print('Repl cohort size:', cohort_size)

        # 3. Reset index to avoid Pandas ValueErrors due to duplicate indices in current and repl pops
        m = max(population.index)
        new_wave.index = range(m, m + cohort_size)

        # Populate repl config, to be passed to simulant_creater
        new_cohort_config = {'sim_state': 'time_step',
                             'creation_time': event.time,
                             'new_cohort': new_wave,
                             'cohort_type': "replenishment",
                             'cohort_size': cohort_size}

        # Create simulants, which adds repl pop to population
        self.simulant_creater(cohort_size, population_configuration=new_cohort_config)
        logging.info(f"\tTotal new 16 year olds added to the model: {cohort_size}")


# HR 14/02/25 All examples below are tested and show various ways to use simulated annealing algorithm
if __name__ == "__main__":

    # # 1. Simple mean value example using 2019 US data
    # y = 2019
    # pathy = os.path.join(DATA_PATH, f"final_US/{y}_US_cohort.csv")
    # dy = pd.read_csv(pathy)
    # # samp, mu = sample_with_constraints(dy, target_dict={'age': 40})
    #
    # # 2. Second simple example with mean-value target and distribution-type target
    # sex_target = {'Female': 0.55, 'Male': 0.45}
    # dy_filt = dy.loc[dy['sex'].isin(sex_target)]
    # # samp, mu = sample_with_constraints(dy_filt, target_dict={'sex': sex_target, 'age': 48})
    #
    # # 3. Another distribution example... ethnicity simplified
    # eth_dist = {'WBI': 0.8, 'WHO': 0.1, 'BAN': 0.05, 'BLA': 0.05}
    # deth = dy.loc[(dy['ethnicity'].isin(eth_dist)) & (dy['sex'].isin(sex_target))]
    #
    # # samp, obj = sample_with_constraints(deth, target_dict={'ethnicity': eth_dist,
    # #                                                        # 'sex': sex_target,
    # #                                                        },
    # #                                     delta_threshold=0.01)
    #
    # # 4. Full runtime-equivalent example using wrapper function, as at runtime, for one year (2015 but can be anything)
    # s15 = create_replenishing_population(pop_size=500000, target_year=2015, delta_threshold=0.03)
    #
    # # 5. Code for offline generation of repl using GB synthpop - not used now but leaving here for posterity
    # # However! The repl cohort sizes are only approximately correct as they don't account for mortality and fertility
    # sp_path = os.path.join(DATA_PATH, 'scaled_gb_US')
    # sp_file = '2019_US_cohort.csv'
    # sp_data = pd.read_csv(os.path.join(sp_path, sp_file))
    #
    # repl_path = os.path.join(DATA_PATH, 'replenishing_scaled_GB')
    # if not os.path.isdir(repl_path):
    #     os.makedirs(repl_path)
    #
    # repl_pop = {}
    # for y in range(2015, 2019+1):  # Example range; can be anything
    #     repl_pop[y] = create_replenishing_population(pop_size=len(sp_data),
    #                                                  target_year=y,
    #                                                  source_pop=sp_data,
    #                                                  delta_threshold=0.03,
    #                                                  )
    #
    #     # Save for runtime
    #     repl_out = os.path.join(repl_path, f'{y}_repl_GB_cohort.csv')
    #     print('Saving to: {}'.format(repl_out))
    #     repl_pop[y].to_csv(repl_out)

    # # 6. Example to look at degree of convergence between repl pop and target distributions
    # # Get reference values to match
    # repl_age = 16
    # sample_ages = [16, 17, 18]
    # ref_deets = (PERSISTENT_DIR, PROJECTIONS_DEFAULT)
    # afrac = get_age_fraction_by_year_newethpop(*ref_deets, ages = repl_age)
    # aeth = get_ethnicity_by_year_newethpop(*ref_deets, ages = repl_age)
    # asex = get_sex_by_year_newethpop(*ref_deets, ages = repl_age)
    #
    # years = [2015, 2025, 2035]
    # thres = 0.02
    # for y in years:
    #
    #     # Get sex and ethnicity fractions to be used as targets in simulated annealing algorithm + sample size
    #     sex_target = asex[repl_age][y]
    #     eth_target = aeth[repl_age][y]
    #     af = afrac[repl_age][y]
    #     repl_size = get_cohort_size_by_proportion(af, len(sp_data))
    #
    #     sp_filtered = sp_data.loc[(sp_data['sex'].isin(sex_target)) &
    #                               (sp_data['ethnicity'].isin(eth_target)) &
    #                               (sp_data['age'].isin(sample_ages)),
    #     ]
    #     samp, obj = sample_with_constraints(sp_filtered,
    #                                         target_dict={'ethnicity': eth_target,
    #                                                      'sex': sex_target,
    #                                                      },
    #                                         delta_threshold=thres)
    #
    #     print('## Running for year {} with convergence threshold {}'.format(y, thres))
    #
    #     comparison_sex = pd.concat([samp['sex'].value_counts(normalize=True).to_frame(), pd.Series(sex_target)], axis=1)
    #     comparison_sex.columns = ['target', 'sample']
    #     comparison_sex['relative diff'] = np.sqrt(np.abs(comparison_sex['target']**2 - comparison_sex['sample']**2)) / comparison_sex['target']
    #     print(comparison_sex)
    #     print('Mean relative difference in sex: {}'.format(comparison_sex['relative diff'].mean()))
    #
    #     comparison_eth = pd.concat([samp['ethnicity'].value_counts(normalize=True).to_frame(), pd.Series(eth_target)], axis=1)
    #     comparison_eth.columns = ['target', 'sample']
    #     comparison_eth['relative diff'] = np.sqrt(np.abs(comparison_eth['target']**2 - comparison_eth['sample']**2)) / comparison_eth['target']
    #     print(comparison_eth)
    #     print('Mean relative difference in ethnicity: {}'.format(comparison_eth['relative diff'].mean()))

    pass
