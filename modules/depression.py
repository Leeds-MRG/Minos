"""
Module for implementation of BHPS depression data to daedalus frame.
"""

import pandas as pd
import numpy as np
import subprocess
import os
from pathlib import Path

from vivarium.framework.utilities import rate_to_probability

from RateTables.DepressionRateTable import DepressionRateTable

class Depression:
    """ Main class for application of depression data to BHPS."""

    @property
    def name(self):
        return "depression"

    def __repr__(self):
        return "Depression()"

    def write_config(self, config):
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
        # config.update({
        #     "path_to_depression_files": {
        #         "tier0": "{}/{}".format(config.persistent_data_dir, config.depression_files.tier0),
        #     },
        # },
        #    source=str(Path(__file__).resolve()))
        return config

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
        return simulation

    def setup(self, builder):
        """ Method for initialising the depression module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """
        # Rate producer for individual states. Given a population calculate depression probabilities using
        # self.calculate_depression_transitions.
        # Name depre
        #self.depression_tier0_rate_producer = builder.value.register_rate_producer('depression_transitions',
        #                                                                     source=self.calculate_depression_transitions,
        #                                                                   requires_columns=['sex', 'ethnicity'])

        # CRN stream for depression states. maybe need one per state?
        self.random = builder.randomness.get_stream('depression_handler')

        # Add columns for depression module to alter to population data frame.
        columns_created = ["depression_duration"]
        view_columns = columns_created + ['alive',
                                          'age',
                                          'sex',
                                          'ethnicity',
                                          'labour_state',
                                          "depression_state",
                                          "education_state",
                                          "pidp"]
        self.population_view = builder.population.get_view(view_columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Register modifier for mortality based on depression state.
        # Adjust death rate dependent on self.depression_mortality_modifier function.
        # TODO: how to adjust rates?
        mortality_modifier = builder.value.register_value_modifier("mortality_rate", self.depression_mortality_modifier)

        # Register time step event for transition of depression on time_step.
        # Priority 1 due so no action if a patient dies on priority 0. Can't be anxious if you're dead.
        # TODO: more formal definition of priority. Ordering of the modules..
        depression_time_step = builder.event.register_listener("time_step", self.on_time_step, priority=1)

        # Load in vivarium clock.
        self.clock = builder.time.clock()

    def on_initialize_simulants(self, pop_data):
        """ Module for adding required module columns to population data frame when vivarium simulation.setup() is run.

        Parameters
        ----------
        pop_data: vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """
        # Create new columns and add them to the population frame.
        # Default states here are simply the 0 state.
        # Default depression columns across all 3 init types.
        # TODO naive depression duration. No data in US? not sure what else can be done.
        pop_update = pd.DataFrame({'depression_duration': 0.},
                                  index=pop_data.index)
        # On initial wave do nothing. Depression state already in data.
        if pop_data.user_data["sim_state"] == "setup":
            pass
        # On replenishment also do nothing.
        elif pop_data.user_data["cohort_type"] == "replenishment":
            # For initial and cohorts import depression state.
            pass
        elif pop_data.user_data["cohort_type"] == "births":
            # Default newborns to have normal levels of depression.
            # Assuming babies cant be depressed.
            pop_update["depression_state"] = 2.
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ What happens in the depression module on every simulation timestep.

        Parameters
        ----------
        event : vivarium.builder.event
            The event time_step that called this function.
        """

        # Get anyone alive.
        pop = self.population_view.get(event.index, query="alive =='alive'")

        prob_df = pd.DataFrame(index = pop.index)
        prob_df["increase"] = rate_to_probability(pd.DataFrame(self.calculate_depression_transitions(pop.index)))
        prob_df["decrease"] = 1 - prob_df["increase"]
        # Choose a new state with bernoulli variables. Probs dont need normalising to 1 which is nice.
        prob_df['depression_state'] = self.random.choice(prob_df.index, prob_df.columns, prob_df)

        # Map states to 0/1 to match existing states.
        # TODO fix this dumb approach so empoyment nnet works properly. Should be true and false.
        prob_df["depression_state"] = prob_df["depression_state"].map({"increase":1., "decrease":0.})
        # Add 1 to duration if they remain in their previous state. Otherwise reset to 0.
        same_state_index = pop.loc[pop["depression_state"] == prob_df["depression_state"]].index
        not_same_state_index = set(pop.index) - set(same_state_index)
        pop.loc[same_state_index, "depression_duration"] += 1.
        pop.loc[not_same_state_index, "depression_duration"] = 0.
        pop["depression_state"] = prob_df["depression_state"]

        self.population_view.update(pop[['depression_state', "depression_duration"]])

    def calculate_depression_transitions(self, index):
        """ Calculate rates of transition between depression into state 0.

        Parameters
        ----------
        index : pandas.DataFrame.index
            `index` series indicating which agents to calculate the death rates of.
        Returns
        -------
        depression_transitions: pd.DataFrame
            `final_mortality_rates` indicates the rate of death for each agent specified in index
            between the previous and current time step events.
        """
        pop = self.population_view.get(index, "alive=='alive'")
        pop_file_name = "data/depression_transition_frame.csv"
        pop.to_csv(pop_file_name, index=False)

        # input arguments for depression transitions R file.
        arg1 = "logistic_normal"
        arg2 = pop_file_name
        # Run R script with given parameters. Will return labour transition probabilities for each sim.
        # Return this to a csv for on_time_step to use random.choice and choose the new labour state.
        process = subprocess.call(f'Rscript transitions/depression_in_python.R {arg1} {arg2}', shell=True)

        # Pull labour transition probabilities from the csv and delete the csv for privacy/storage reasons.
        depression_transitions = pd.read_csv("data/depression_state_transitions.csv")
        depression_transitions.index = index # replace index to align with main population dataframe.
        os.remove(pop_file_name)
        os.remove("data/depression_state_transitions.csv")
        # Dummy safety for debugging. Set all to 0.1 prob.
        # depression_transitions = pd.DataFrame({'all_causes': 0.1}, index=index)
        return depression_transitions

    def depression_mortality_modifier(self, index, values):
        """ Adjust mortality rate based on depression states

        Note this function requires arguments that match those of mortality.calculate_mortality_rate
        and an addition values argument (not name dependent) that gives the current values
        output by the mortality rate producer.

        Parameters
        ----------
        index : pandas.core.indexes.numeric.Int64Index
            `index` which rows of population frame apply rate modification to.
        values : pandas.core.frame.DataFrame

            the previous `values` output by the mortality_rate value producer.
            More generally the producer defined in the register_value_modifier
            method with this as its source.

        Returns
        -------
        values : pandas.core.frame.DataFrame
            The modified `values` handed back to the builder for application in
            mortality's on_time_step. In theory, those with higher depression states are
            at higher risk of dying.
        """

        # get depression states from population.
        pop = self.population_view.get(index, query="alive =='alive' and sex != 'nan'")
        # Adjust depression rates accordingly.
        # TODO: actual values for these.
        values.loc[pop["depression_state"] == 1] *= 0.5
        values.loc[pop["depression_state"] == 2] *= 1
        values.loc[pop["depression_state"] == 3] *= 2
        values.loc[pop["depression_state"] == 4] *= 10
        return values

