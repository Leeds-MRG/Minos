"""
Module for implementation of BHPS education data to daedalus frame.
"""

import pandas as pd
from vivarium.framework.utilities import rate_to_probability
from pathlib import Path
import random
import os
import subprocess # For running R scripts in shell.

class Employment:
    """ Main class for application of employment data to BHPS."""

    @property
    def name(self):
        return "employment"

    def __repr__(self):
        return "Employment()"

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
        # load in all possible job sectors to config
        job_sectors = pd.read_csv("modules/job_sector_levels.csv")
        job_roles = pd.read_csv("modules/job_role_levels.csv")
        config.update({
            "job_sectors": job_sectors,
            "job_roles": job_roles
        },
            source=str(Path(__file__).resolve()))
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
        """ Method for initialising the employment module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # load in any data
        self.builder = builder
        self.config = builder.configuration
        self.job_sectors = self.config.job_sectors
        self.job_roles = self.config.job_roles
        # create new columns to be added by this module
        columns_created = ["labour_duration", "job_duration", "role_duration"]
        view_columns = columns_created +['pidp',
                   'age',
                   'sex',
                   'education_state',
                   'ethnicity',
                   'alive',
                   'time',
                   'depression_state',
                   'labour_state',
                   'job_industry',
                   'job_occupation',
                   'job_sec',
                   'job_duration_m',
                   'job_duration_y']

        self.population_view = builder.population.get_view(view_columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)
        # register value rate producers.
        # one for redeployment and role change.
        #self.labour_change_rate_producer = builder.value.register_rate_producer('labour_change_rate',
        #                                                                     source=self.calculate_labour_change_rate)
        self.job_change_rate_producer = builder.value.register_rate_producer('job_change_rate',
                                                                             source=self.calculate_job_change_rate)
        self.role_change_rate_producer = builder.value.register_rate_producer('role_change_rate',
                                                                              source=self.calculate_role_change_rate)

        # priority 1 below death. not much point changing jobs if you're dead.

        # CRN stream for the module. may be worth disabling later for "true" random employment.
        self.random = builder.randomness.get_stream('employment_handler')
        # registering any modifiers.
        # depression modifier changes rate according to current employment
        # the unemployed/ high level jobs are more likely to induce depression etc.
        # adjusting so higher depression under certain employment circumstances.
        self.employment_modifier1 = builder.value.register_value_modifier("depression_tier1_rate",
                                                                         self.employment_depression_modifier)
        self.employment_modifier0 = builder.value.register_value_modifier("depression_tier0_rate",
                                                                         self.employment_depression_modifier)
        # register event listeners.
        # priority 1 below death.
        employment_time_step = builder.event.register_listener("time_step", self.on_time_step, priority=1)

        # load in any other required components

    def on_initialize_simulants(self, pop_data):
        """ Module for when the vivarium builder.randomness.register_simulants() is run.

        Parameters
        ----------
        pop_data: vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).

        Returns
        -------
        None.
        """
        job_sectors = self.job_sectors["job_sectors"]
        job_roles = self.job_roles["job_roles"]
        n = len(pop_data.index)
        pop_update = pd.DataFrame({"labour_duration": 0.,
                                   "role_duration": 0.},
                                  index=pop_data.index)
        if pop_data.user_data["sim_state"] == "setup":
            #TODO initate labour state duration properly.
            pass
        elif pop_data.user_data["cohort_type"] == "replenishment":
            pass
        elif pop_data.user_data["cohort_type"] == "births":
            # Default newborns to students with no labour state history.
            # These are filler for US variables.
            # 
            pop_update["labour_state"] = "Student"
            pop_update["job_sec"] = 0
            pop_update["job_industry"] = 0
            pop_update["job_occupation"] = 0
            pop_update["job_duration_m"] = 0
            pop_update["job_duration_y"] = 0

        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ What happens in the employment module on every simulation timestep.

        Parameters
        ----------
        event : vivarium.builder.event
            The time_step `event` is used here. I.E whenever the simulation is stepped forwards.
        Returns
        -------

        """

        # Grab anyone alive of working age.
        pop = self.population_view.get(event.index, query="alive =='alive' and age >= 16")
        self.current_year = event.time.year

        # Changing labour state.
        labour_change_df = self.labour_state_probabilities(pop.index)

        # calculate probabilities of changing role/job sector.
        job_change_df = pd.DataFrame(index=pop.index)
        job_change_df["change"] = rate_to_probability(pd.DataFrame(self.job_change_rate_producer(pop.index)))
        job_change_df["no_change"] = 1 - job_change_df["change"]

        role_change_df = pd.DataFrame(index=pop.index)
        role_change_df["change"] = rate_to_probability(pd.DataFrame(self.role_change_rate_producer(pop.index)))
        role_change_df["no_change"] = 1 - role_change_df["change"]



        #job_change = self.random.choice(job_change_df.index, job_change_df.columns, job_change_df)
        #role_change = self.random.choice(role_change_df.index, role_change_df.columns, role_change_df)
        labour_change = self.random.choice(labour_change_df.index, labour_change_df.columns, labour_change_df)
        # Keep or assign new job/role as necessary.
        # Idea is to have the assign functions do all the work as to be flexible. should just output a list of job/role
        # strings.

        labour_change_df["labour_state"] = labour_change
        #which_labour_failed = labour_change.loc[labour_change["labour_state"] == "Unnamed: 0"].index

        #job_change_df["labour_state"] = self.assign_new_jobs(pop, job_change)
        #role_change_df["role_state"] = self.assign_new_roles(pop, role_change)

        # Update change in jobs/roles. add 1 step to duration if keeps same job/role.
        #different_job_index = pop.loc[pop["job_state"] != job_change_df["job_state"]].index
        #pop["job_duration"] += 1
        #pop.loc[different_job_index, "job_duration"] = 0

        labour_change_df.index = pop.index
        different_labour_index = pop.loc[pop["labour_state"] != labour_change_df["labour_state"]].index
        pop["labour_duration"] += 1
        pop.loc[different_labour_index, "job_duration"] = 0

        #different_role_index = pop.loc[pop["role_state"] != role_change_df["role_state"]].index
        #pop["role_duration"] += 1
        #pop.loc[different_role_index, "role_duration"] = 0

        # Update main population frame with new jobs/roles.
        pop[["labour_state"]] = labour_change_df["labour_state"]
        #pop[["role_state"]] = role_change_df["role_state"]

        self.population_view.update(pop[['labour_state', "job_duration", "role_duration"]])

    def labour_state_probabilities(self, index):
        """ Calculate labour change rates of population using R script.

        Parameters
        ----------
        index: pd.Series
            `index` of which sims in population are changing states.

        Returns
        -------
        None
        """
        # Save current population frame to csv for handling by the R script.
        pop = self.population_view.get(index, "alive=='alive' and age>=16")
        pop_file_name = "data/labour_change_frame.csv"
        transitions_file_name = "data/labour_state_transitions.csv"
        pop.to_csv(pop_file_name, index=False)

        # input arguments for labour transitions R file.
        arg1 = self.current_year
        arg2 = "multinom"
        arg3 = pop_file_name
        # Run R script with given parameters. Will return labour transition probabilities for each sim.
        # Return this to a csv for on_time_step to use random.choice and choose the new labour state.
        process = subprocess.call(f'Rscript transitions/labour_in_python.R {arg1} {arg2} {arg3}', shell=True)

        # Pull labour transition probabilities from the csv and delete the csv for privacy/storage reasons.
        labour_probabilities = pd.read_csv(transitions_file_name)
        labour_probabilities.index = index # replace index to align with main population dataframe.
        os.remove(pop_file_name)
        os.remove(transitions_file_name)
        return labour_probabilities

    def calculate_job_change_rate(self, index):
        """ Calculate probabilities of moving to new job sector.

        Parameters
        ----------
        index : pandas.DataFrame.index
            `index` series indicating which agents to calculate the death rates of.
        Returns
        -------
        job_change_rates: pd.DataFrame
            `job_change_rates` indicates the probability of changing job sectors. 1 is change 0 is stay put.
        """

        pop = self.population_view.get(index, "pidp>0")
        pop.to_csv("data/job_change_frame.csv")
        job_change_rates = pd.DataFrame({"labour_state": 0.1}, index=index)
        return job_change_rates

    def calculate_role_change_rate(self, index):
        """ Calculate probability of transitioning to a new role within work whether promotion/demotion/firing etc.

        Parameters
        ----------
        index : pandas.DataFrame.index
            `index` series indicating which agents to calculate the death rates of.
        Returns
        -------
        role_change_rates: pd.DataFrame
            `role_change_rates` indicates the probability of changing roles within a job. 1 is change 0 is stay put.
        """
        role_change_rates = pd.DataFrame({"role_state": 0.1}, index=index)
        return role_change_rates

    def employment_depression_modifier(self, index, values):
        """ Adjust depression tier1 rates based on employment states

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
        return values

    def assign_new_roles(self, pop, role_change):
        """ Assign new job based on some transition probabilities.

        Parameters
        ----------
        pop : pd.DataFrame
            `pop` population to decide changes in role for.
        role_change : pd.DataFrame
            `role_change` bool vector giving whether a sim is moving or not 0 it yes 1 if no.
            Can probably remove this by only feeding in pop that are changing.
        Returns
        -------
        new_roles
            `new_roles` a vector of pop.index length assigning each person to a job. May be their old job.
        """

        job_roles = self.job_roles["job_roles"]
        n = len(pop.index)
        new_roles = pd.DataFrame({'role_state': random.choices(job_roles, k=n)},
                                  index=pop.index)
        return new_roles

    def assign_new_jobs(self, pop, job_change):
        """ Assign new job based on some transition matrix

        Parameters
        ----------
        pop
        job_change

        Returns
        -------
        new_jobs
            `new_jobs` a vector of pop.index length
        """
        job_sectors = self.job_sectors["job_sectors"]
        n = len(pop.index)
        new_jobs = pd.DataFrame({'job_state': random.choices(job_sectors, k=n)},
                                  index=pop.index)
        return new_jobs