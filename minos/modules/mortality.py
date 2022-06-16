"""
========================
The Core Mortality Model
========================

This module contains tools modeling all cause mortality.

"""
import pandas as pd
from pathlib import Path

# Required rate conversion and rate table creation functions.
from vivarium.framework.utilities import rate_to_probability
from minos.RateTables.MortalityRateTable import MortalityRateTable


class Mortality:

    @staticmethod
    def write_config(config):
        """ Update config file with what this module needs to run.
        Parameters
        ----------
            config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob.
        Returns
        -------
           config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob with added items needed for this module to run.
        """
        config.update({
            'path_to_mortality_file': "{}/{}".format(config.persistent_data_dir, config.mortality_file)
        }, source=str(Path(__file__).resolve()))
        return config


    # vivarium does allow for use of __init__ so use pre_setup instead.
    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run into the config and simulation object.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run.

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        # Define path to mortality rate data.
        config.update({
            'path_to_mortality_file': "{}/{}".format(config.persistent_data_dir, config.mortality_file)
        }, source=str(Path(__file__).resolve()))

        # Load in mortality rate table data and append it to the simulation object.
        asfr_mortality = MortalityRateTable(configuration=config)
        asfr_mortality.set_rate_table()
        simulation._data.write("cause.all_causes.cause_specific_mortality_rate",
                               asfr_mortality.rate_table)
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

        Parameters
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Load in rate table data from pre-setup.
        all_cause_mortality_data = builder.data.load("cause.all_causes.cause_specific_mortality_rate")
        self.all_cause_mortality_rate = builder.lookup.build_table(all_cause_mortality_data,
                                                                   key_columns=["sex", "region", "ethnicity"],
                                                                   parameter_columns=['age', 'year'])
        # Build mortality rate producer. When called it will give a rate of death for each alive individual.
        self.mortality_rate = builder.value.register_rate_producer('mortality_rate',
                                                                   source=self.calculate_mortality_rate,
                                                                   requires_columns=['sex', 'region', 'ethnicity'])
        # Uniform life expectancy for all simulants. Used to calculate expected years of life lost when dead.
        life_expectancy_data = 81.16  # based on data
        self.life_expectancy = builder.lookup.build_table(life_expectancy_data, parameter_columns=['age'])

        # Assign mortality a common random number stream.
        self.random = builder.randomness.get_stream('mortality_handler')

        # Which columns are created by this module in on_initialize_simulants.
        columns_created = ['cause_of_death', 'years_of_life_lost']
        # Which columns are shown from the population frame when self.population_view is called.
        # I.E. which columns are required to calculate transition probabilities or to be updated at each on_time_step.
        view_columns = columns_created + ['alive', 'exit_time', 'age', 'sex', 'region']
        self.population_view = builder.population.get_view(view_columns)
        # When any new agents are added the columns_created for this module are initiated using this function.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)
        # Add an event every simulation time_step increment to see if anyone dies.
        # Priority 0/10 so simulants make this transition first.
        # No point becoming depressed if you're dead.
        builder.event.register_listener('time_step', self.on_time_step, priority=0)


    def on_initialize_simulants(self, pop_data):
        """  Initiate columns for mortality when new simulants are added.

        Parameters
        ----------
            pop_data: vivarium.framework.population.SimulantData
            Custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """
        # Create frame with new 3 columns and add it to the main population frame.
        # This is the same for both new cohorts and newborn babies.
        # Neither should be dead yet.
        pop_update = pd.DataFrame({'alive': "alive",
                                   'cause_of_death': 'not_dead',
                                   'years_of_life_lost': 0.,
                                   'exit_time': pd.NaT},
                                  index=pop_data.index)
        self.population_view.update(pop_update)


    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get everyone who is alive and calculate their rate of death.
        pop = self.population_view.get(event.index, query="alive =='alive' and sex != 'nan'")
        # Convert these rates to probabilities of death or not death.
        prob_df = rate_to_probability(pd.DataFrame(self.mortality_rate(pop.index)))
        prob_df['no_death'] = 1 - prob_df.sum(axis=1)
        # Each simulant draw a uniform random variable and dies if this value is less than their probability of death.
        # E.g. if an individual has a 0.2 probability of dying and they draw 0.1 then they die.
        # If they draw 0.3 then they live.
        # The "cause_of_death" notation allows for more descriptive deaths.
        # Useful later when dying naturally vs due to mental health issues.
        prob_df['cause_of_death'] = self.random.choice(prob_df.index, list(prob_df.columns), prob_df)
        # prob_df['cause_of_death'] = self.random.choice(prob_df.index, prob_df.columns, prob_df)
        dead_pop = prob_df.query('cause_of_death != "no_death"').copy()

        if not dead_pop.empty:
            # If anyone dies, kill them.
            # Update their alive status, exit time, and expected life lost to the main population frame.
            dead_pop['alive'] = pd.Series('dead', index=dead_pop.index)
            dead_pop['exit_time'] = event.time
            dead_pop['years_of_life_lost'] = self.life_expectancy(dead_pop.index) - pop.loc[dead_pop.index]['age']
            self.population_view.update(dead_pop[['alive', 'exit_time', 'cause_of_death', 'years_of_life_lost']])


    def calculate_mortality_rate(self, index):
        """ Calculate the rate of death for each individual.

        Parameters
        ----------
        index : pandas.DataFrame.index
            Series indicating which agents to calculate the death rates for.
        Returns
        -------
        final_mortality_rates: pd.DataFrame
            Vector of death rates for the specified agents.
        """
        # Use the lookup table to calculate mortality rates and put them in a pandas frame for use in on_time_step.
        mortality_rate = self.all_cause_mortality_rate(index)
        final_mortality_rates = pd.DataFrame({'all_causes': mortality_rate})
        return final_mortality_rates


    # Special methods used by vivarium.
    @property
    def name(self):
        return 'mortality'


    def __repr__(self):
        return "Mortality()"
