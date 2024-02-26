"""
================
Fertility Models
================

This module contains several different models of fertility.

"""
from pathlib import Path
import numpy as np
import pandas as pd
import minos.utils as utilities
from os.path import dirname as up

from minos.RateTables.FertilityRateTable import FertilityRateTable
from minos.modules.base_module import Base

PREGNANCY_DURATION = pd.Timedelta(days=9 * utilities.DAYS_PER_MONTH)


class FertilityAgeSpecificRates(Base):
    """
    A simulant-specific model for fertility and pregnancies.
    """

    @property
    def name(self):
        return 'age_specific_fertility'

    @staticmethod
    def pre_setup(config, simulation):
        """ Load in anything required for the module to run.

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
        # produce rate table from minos file path in config and save it to the simulation.
        config.update({
            'path_to_fertility_file': "{}/{}".format(config.persistent_data_dir, config.fertility_file)
        }, source=str(Path(__file__).resolve()))
        asfr_fertility = FertilityRateTable(configuration=config)
        asfr_fertility.set_rate_table()
        simulation._data.write("covariate.age_specific_fertility_rate.estimate",
                               asfr_fertility.rate_table)

        return simulation

    def setup(self, builder):
        """ Initialise the module within the vivarium simulation.

        - load in data from pre_setup
        - register any value producers/modifiers for birth rate
        - add required columns to population data frame
        - add listener event to check if people are born on each time step.
        - update other required items such as random and clock.

        Parameters
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """
        # Load in birth rate lookup table data and build lookup table.
        age_specific_fertility_rate = builder.data.load("covariate.age_specific_fertility_rate.estimate")
        fertility_rate = builder.lookup.build_table(age_specific_fertility_rate,
                                                    key_columns=['sex', 'region', 'ethnicity'],
                                                    parameter_columns=['age', 'year'])
        # Register rate producer for birth rates by
        # This determines the rates at which sims give birth over the simulation time step.
        self.fertility_rate = builder.value.register_rate_producer('fertility rate',
                                                                   source=fertility_rate,
                                                                   requires_columns=['sex', 'ethnicity'])

        # CRN stream for seeding births.
        self.randomness = builder.randomness.get_stream('fertility')

        # Add new columns to population required for module using build in sim creator.
        self.population_view = builder.population.get_view(
            ['last_birth_time', 'sex', 'parent_id', 'ethnicity', 'age'])
        self.simulant_creator = builder.population.get_simulant_creator()
        # Initiate these columns using on_initialize_simulants below.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=['last_birth_time', 'parent_id'],
                                                 requires_columns=['sex'])
        # Add listener event to check who has given birth on each time step using the on_time_step function below.
        # builder.event.register_listener('time_step', self.on_time_step, priority=self.priority)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        """ Adds the required columns for the module to run to the population data frame.

        Parameters
        --------
            pop_data: vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """
        # give indices of all women in population. (men cant give birth)
        pop = self.population_view.subview(['sex', 'age']).get(pop_data.index)
        women = pop.loc[pop.sex == "Female"].index

        # if the simulation is already running use pre-existing parent data. else give them all -1 (N/A) parents.
        # if pop_data.user_data['sim_state'] == 'time_step':
        # Changed from above due to addition of new cohorts.
        if np.sum(pop["age"]) == 0:
            parent_id = pop_data.user_data['parent_ids']
            self.new_babies_index = pop_data.index
        else:
            parent_id = -1
        # Generate columns for last birth time and parent IDs for the pop_data frame.
        pop_update = pd.DataFrame({'last_birth_time': pd.NaT, 'parent_id': parent_id}, index=pop_data.index)
        # FIXME: This is a misuse of the column and makes it invalid for
        #    tracking metrics.
        # Do the naive thing, set so all women can have children
        # and none of them have had a child in the last year.
        # TODO: alter this so newborns cant have children. It's weird.
        pop_update.loc[women, 'last_birth_time'] = pop_data.creation_time - pd.Timedelta(days=utilities.DAYS_PER_YEAR)
        # add new columns to population frame.
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get a view on all living women who haven't had a child in at least nine months.
        # TODO needs to find a way to update event.index.
        # Currently people who are just added to the population arent in this index and wont be considered for births.

        nine_months_ago = pd.Timestamp(event.time - PREGNANCY_DURATION)
        population = self.population_view.get(event.index, query='alive == "alive" and sex == "Female"')
        can_have_children = population.last_birth_time < nine_months_ago
        eligible_women = population[can_have_children]
        # calculate rates of having children and randomly draw births
        # filter_for_rate simply takes the subset of women who have given birth generated via the CRN stream.
        rate_series = self.fertility_rate(eligible_women.index)
        had_children = self.randomness.filter_for_rate(eligible_women, rate_series).copy()
        # Set new last birth times and update the population frame.
        had_children.loc[:, 'last_birth_time'] = event.time
        self.population_view.update(had_children['last_birth_time'])

        # If children were born, add them to the population table and record
        # who their mother was.
        num_babies = len(had_children)
        if num_babies:
            self.simulant_creator(num_babies,
                                  population_configuration={
                                      'age_start': 0.,
                                      'age_end': 0.,
                                      'sim_state': 'time_step',
                                      'creation_time': event.time,
                                      'cohort_type': 'births',
                                      'num_babies': num_babies,
                                      'parent_ids': had_children.index,
                                  })

            # Get all new borns back from the population to add remaining information.
            # I changed it to this from VPH because its less messing around when adding new cohorts.
            new_babies = self.population_view.get(self.new_babies_index,
                                                  query='alive == "alive" and parent_id != -1')

            # Assign age, sex, ethnicity to newborns and update the population frame again.
            # Need to Assign other attributes too such as unemployment.
            # Better to be done in the other modules.
            if new_babies.shape[0] != 0:
                new_babies['ethnicity'] = self.population_view.get(event.index).iloc[new_babies['parent_id']][
                    'ethnicity'].values
                new_babies['sex'] = self.randomness.choice(new_babies.index, ["Male", "Female"],
                                                           additional_key='sex_choice')

                self.population_view.update(new_babies[['ethnicity', 'sex', 'age']])

    @staticmethod
    def load_age_specific_fertility_rate_data(builder):
        """I have no idea what this is. loads in rate table taking subset for women and specific columns.
        I think its been deprecated by the Ratetables.FertilityRateTable file."""
        asfr_data = builder.data.load("covariate.age_specific_fertility_rate.estimate")
        columns = ['year_start', 'year_end', 'ethnicity', 'age_start', 'age_end', 'mean_value']
        asfr_data = asfr_data.loc[asfr_data.sex == 2][columns]
        return asfr_data

    def __repr__(self):
        return "FertilityAgeSpecificRates()"




class nkidsFertilityAgeSpecificRates(Base):
    """
    A simulant-specific model for fertility and pregnancies.
    """
    # @staticmethod
    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run.

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
        # produce rate table from minos file path in config and save it to the simulation.
        config.update({
            'path_to_fertility_file': "{}/{}".format(config.persistent_data_dir, config.fertility_file)
        }, source=str(Path(__file__).resolve()))
        asfr_fertility = FertilityRateTable(configuration=config)
        asfr_fertility.set_rate_table()
        simulation._data.write("covariate.age_specific_fertility_rate.estimate",
                               asfr_fertility.rate_table)
        simulation._data.write("parity_max", asfr_fertility.parity_max)
        print("Max. parity successfully passed to ANBC:", asfr_fertility.parity_max)

        return simulation

    def setup(self, builder):
        """ Initialise the module within the vivarium simulation.

        - load in data from pre_setup
        - register any value producers/modifiers for birth rate
        - add required columns to population data frame
        - add listener event to check if people are born on each time step.
        - update other required items such as random and clock.

        Parameters
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """
        # Load in birth rate lookup table data and build lookup table.
        self.parity_max = builder.data.load("parity_max")
        age_specific_fertility_rate = builder.data.load("covariate.age_specific_fertility_rate.estimate")
        fertility_rate = builder.lookup.build_table(age_specific_fertility_rate,
                                                    key_columns=['sex', 'region', 'ethnicity', 'nkids_ind'],
                                                    parameter_columns=['age', 'year'])
        # Register rate producer for birth rates by
        # This determines the rates at which sims give birth over the simulation time step.
        self.fertility_rate = builder.value.register_rate_producer('fertility rate',
                                                                   source=fertility_rate,
                                                                   requires_columns=['sex', 'ethnicity', 'nkids_ind'])

        # CRN stream for seeding births.
        self.randomness = builder.randomness.get_stream('fertility')

        view_columns = ['sex', 'ethnicity', 'age', 'nkids', 'nkids_ind', 'hidp', 'pidp', "child_ages"]

        columns_created = ['has_newborn']

        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Add new columns to population required for module using build in sim creator.
        self.population_view = builder.population.get_view(view_columns + columns_created)

        # Add listener event to check who has given birth on each time step using the on_time_step function below.
        # builder.event.register_listener('time_step', self.on_time_step, priority=self.priority)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        """ Adds the required columns for the module to run to the population data frame.

        Parameters
        --------
            pop_data: vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """
        # One new column for whether a household has any newborn children.
        pop_update = pd.DataFrame({'has_newborn': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)



    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get a view on all living people.
        population = self.population_view.get(event.index, query='alive == "alive"')
        population['has_newborn'] = False
        # resetting nkids in repl populations.
        population['nkids'] = population.groupby('hidp')['nkids'].transform("max")

        # not needed due to yearly increments.
        #nine_months_ago = pd.Timestamp(event.time - PREGNANCY_DURATION)
        #can_have_children = population.last_birth_time < nine_months_ago
        #eligible_women = population[can_have_children]
        # calculate rates of having children and randomly draw births
        # filter_for_rate simply takes the subset of women who have given birth generated via the CRN stream.
        who_women = population.loc[population['sex']=='Female',].index
        rate_series = self.fertility_rate(who_women)

        # get women who had children.
        had_children = self.randomness.filter_for_rate(who_women, rate_series).copy()

        # 1. Find everyone in a household who has had children by hidp and increment nkids by 1
        had_children_hidps = population.loc[had_children, 'hidp'] # Get all HIDPs of people who've had children
        who_had_children_households = population.loc[population['hidp'].isin(had_children_hidps),].index # Get all HIDPs who live in HH that has had a child
        population.loc[who_had_children_households, 'nkids'] += 1
        population.loc[who_had_children_households, 'has_newborn'] = True
        population.loc[who_had_children_households, 'child_ages'] = population.loc[who_had_children_households, 'child_ages'].apply(lambda x: self.add_new_child_to_chain(x))  # add new child to children ages chain.

        # LA 26/2/24
        # Problem when adding new babies to childless households
        # Results in a string with structure '0_None'
        # Therefore we need to remove the 'None' part of the string
        #population['child_ages'] = population['child_ages'].str.replace('0_None', '0')
        # Spotted the add_new_child_to_chain() function below and fixed it there instead.

        # 2. Find individuals who have had children by pidp and increment nkids_ind by 1
        #TODO future differentiation within a household of which kids belong to who in child age chains.
        who_had_children_individuals = population.loc[had_children, 'pidp'].index
        population.loc[who_had_children_individuals, 'nkids_ind'] += 1
        self.population_view.update(population[['nkids_ind', 'child_ages', 'nkids', 'has_newborn']])

    @staticmethod
    def add_new_child_to_chain(age_chain):

        value = age_chain#.values[0]
        if type(value) == float or value is None or value == 'None':
            return "0"
        else:
            return "0_" + age_chain

    @staticmethod
    def load_age_specific_fertility_rate_data(builder):
        """I have no idea what this is. loads in rate table taking subset for women and specific columns.
        I think its been deprecated by the Ratetables.FertilityRateTable file."""
        asfr_data = builder.data.load("covariate.age_specific_fertility_rate.estimate")
        columns = ['year_start', 'year_end', 'ethnicity', 'age_start', 'age_end', 'mean_value']
        asfr_data = asfr_data.loc[asfr_data.sex == 2][columns]
        return asfr_data


    @property
    def name(self):
        return 'nkids_age_specific_fertility'

    def __repr__(self):
        return "nkidsFertilityAgeSpecificRates()"
