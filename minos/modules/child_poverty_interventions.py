"""Module for applying any interventions to the base population from replenishment."""
import itertools
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from math import ceil

from minos.modules.base_module import Base
from minos.outcomes.aggregate_subset_functions import dynamic_subset_function


def get_monthly_boost_amount(data, boost_amount):
    """Calculate monthly uplift for eligible households. number of children * 30.436875/7 weeks * boost amount
    """
    return boost_amount * 30.436875 * data['nkids'] / 7


class ChildPovertyReductionRELATIVE(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_relative"

    def __repr__(self):
        return "ChildPovertyReductionRELATIVE"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income", 'nkids', 'pidp', 'hidp']
        columns_created = ["income_boosted", "boost_amount"]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child poverty reduction intervention in year {event.time.year}...")

        # This intervention will reduce the % of children living in families in relative poverty to a defined proportion
        # by a set end year. As a first attempt, we will reduce the numbers to fewer than 10% of children living in
        # relative poverty by 2030

        # STEPS;
        # 1. Calculate median hh_income over all households
        # 2. Calculate total kids in sample
        # 3. Find all households in relative poverty
        # 4. Calculate the proportion of children in relative poverty (hh_income < 60% of median hh_income in that year)
        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        # 7. Profit

        # set parameters
        end_year = 2030
        target_pov_prop = 0.1

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print(f"Number of people already boosted: {full_pop['income_boosted'].sum()}")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        # full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        self.population_view.update(full_pop[['boost_amount']])
        # LA 22/1/24 median income now calculated by household instead of individual
        median_income = full_pop.groupby('hidp').first()['hh_income'].median()

        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        #nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        relative_poverty_threshold = median_income * 0.6
        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['hh_income'] < relative_poverty_threshold)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['boost_amount'][(target_pop['income_boosted'] is True) &  # previously uplifted
                                   (target_pop['hh_income'] < relative_poverty_threshold)] = (  # in relative poverty
                relative_poverty_threshold - target_pop['hh_income'] + 1)  # boost is difference between income and threshold (+1 to guarantee above threshold)

        target_pop['hh_income'] = target_pop['hh_income'] + target_pop['boost_amount']  # apply the boost

        # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        for index, row in target_pop.iterrows():
            pidp = row['pidp']
            if pidp in full_pop['pidp'].values:
                full_pop.loc[full_pop['pidp'] == pidp, 'hh_income'] = row['hh_income']
                full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
                full_pop.loc[full_pop['pidp'] == pidp, 'income_boosted'] = row['income_boosted']

        #self.population_view.update(target_pop[['hh_income', 'boost_amount']])
        #target_pop = self.population_view.get(event.index,
        #                                      query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                            f"{relative_poverty_threshold}")

        # 4. Calculate the proportion of children in relative poverty
        target_pop_nkids = target_pop.groupby('hidp').first()['nkids'].sum()
        prop_in_poverty = target_pop_nkids / nkids_total
        print(f"Percentage of children in poverty: {prop_in_poverty * 100}")

        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # we need to reduce this proportion down to 10% by 2030, so we can calculate the number of years we have left
        # and then the proportion to reduce in that year
        years_remaining = end_year - event.time.year

        if prop_in_poverty > target_pov_prop:
            prop_above_target = prop_in_poverty - target_pov_prop
        else:
            prop_above_target = 0

        if years_remaining > 0:  # before 2030
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 0:  # in 2030
            proportion_to_uplift = prop_above_target
        elif years_remaining < 0:  # after 2030, fix to target level
            proportion_to_uplift = prop_above_target
        print(f"Proportion to uplift by {end_year}: {prop_above_target}")
        print(f"Proportion to uplift this year: {proportion_to_uplift}")

        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        nkids_to_uplift = ceil(nkids_total * proportion_to_uplift)

        # 7. Randomly select households by hidp until we hit the nkids_to_uplift target
        # first get a dataframe of just one person per household
        target_pop_hh_representative = target_pop.groupby('hidp').first().reset_index()
        target_hidps = []
        kids = 0
        for i in target_pop_hh_representative.sample(frac=1).iterrows():
            if (kids + i[1]['nkids']) <= nkids_to_uplift:
                kids += i[1]['nkids']
                target_hidps.append(i[1]['hidp'])
            if kids >= nkids_to_uplift:
                break

        print(f"Number of households to uplift: {len(target_hidps)}")
        #print(f"Number of children to uplift: {target_pop[target_pop['hidp'].isin(target_hidps)]['nkids'].sum()}")
        target_pop_hhs = target_pop[target_pop['hidp'].isin(target_hidps)]
        target_pop_hhs_kids = target_pop_hhs.groupby('hidp').first()['nkids'].sum()
        print(f"Number of children to uplift: {target_pop_hhs_kids}")

        # 8. Calculate boost amount for each household and apply
        # uplift_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & hidp.isin({target_hidps})")
        uplift_pop = target_pop[target_pop['hidp'].isin(target_hidps)]

        # boost is amount to take them above poverty threshold (+1 to guarantee above threshold and not equal to)
        uplift_pop['boost_amount'] = relative_poverty_threshold - uplift_pop['hh_income'] + 1
        # assign income_boosted == True if previously True or uplifted in current wave
        uplift_pop['income_boosted'] = True
        uplift_pop['hh_income'] += uplift_pop['boost_amount']

        # 9. Update original population with uplifted values
        # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        for index, row in uplift_pop.iterrows():
            pidp = row['pidp']
            if pidp in full_pop['pidp'].values:
                full_pop.loc[full_pop['pidp'] == pidp, 'hh_income'] = row['hh_income']
                full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
                full_pop.loc[full_pop['pidp'] == pidp, 'income_boosted'] = row['income_boosted']

        # Convert 'income_boosted' column back to boolean type
        full_pop['income_boosted'] = full_pop['income_boosted'].astype(bool)

        self.population_view.update(full_pop[['hh_income', 'income_boosted', 'boost_amount']])

        # Check the population still in poverty
        # target_pop2 = self.population_view.get(event.index,
        #                                        query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                              f"{relative_poverty_threshold}")
        still_in_pov = full_pop[(full_pop['nkids'] > 0) & (full_pop['hh_income'] < relative_poverty_threshold)]

        print(f"Proportion of children in poverty AFTER intervention: {still_in_pov.groupby('hidp').first()['nkids'].sum() / nkids_total}")

        # 10. Logging
        #TODO: Change these to household calculations
        logging.info(f"\tNumber of people uplifted: {sum(uplift_pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(uplift_pop['income_boosted']) / len(full_pop)) * 100}% of the total "
                     f"population.")
        logging.info(f"\t...and {(sum(uplift_pop['income_boosted']) / len(target_pop)) * 100}% of the population in"
                     f"poverty.")
        logging.info(f"\tTotal boost amount: {uplift_pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount across households in poverty: "
                     f"{uplift_pop['boost_amount'][uplift_pop['income_boosted']].mean()}")


class childUplift(Base):

    @property
    def name(self):
        return "child_uplift"

    def __repr__(self):
        return "childUplift()"

    def pre_setup(self, config, simulation):
        self.uplift_condition = config['intervention_parameters']['uplift_condition']
        self.uplift_amount = config['intervention_parameters']['uplift_amount']
        print(f"Running child uplift with condition {self.uplift_condition} and uplift amount {self.uplift_amount}.")
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

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income",
                        'nkids',
                        'alive',
                        'universal_credit',
                        'hidp',
                        "S7_labour_state",
                        "marital_status",
                        'age',
                        'ethnicity']
        columns_created = ["income_boosted", "boost_amount"]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the hh_income child uplift intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # print(np.mean(pop['hh_income'])) # for debugging purposes.
        # TODO probably a faster way to do this than resetting the whole column.
        # if self.uplift_condition == "who_below_poverty_line_and_kids":
        #     pop['hh_income'] -= pop['boost_amount']  # reset boost if people move out of bottom decile. only do this for relative poverty uplift.
        # else:
        #     pop['income_boosted'] = False

        # Reset boost vars in preparation for the new wave intervention
        pop['income_boosted'] = False
        pop['boost_amount'] = 0

        # Find households to uplift from the uplift condition supplied
        uplifted_households = np.unique(dynamic_subset_function(pop, self.uplift_condition)['hidp'])
        # Households on universal credit and legacy benefits are already receiving £10 SCP in our input population
        # (2020) start. Therefore we need to reduce the intervention by £10 for these people
        uc_households = np.unique(dynamic_subset_function(pop, 'who_universal_credit_and_kids')['hidp'])

        pop.loc[pop['hidp'].isin(uplifted_households), 'income_boosted'] = True  # set everyone who satisfies uplift condition to true.
        pop['boost_amount'] = pop['income_boosted'] * get_monthly_boost_amount(pop, self.uplift_amount)  # £25 per week * 30.463/7 weeks per average month * nkids.


        ###### LA 18/4/24 WE HAVE DECIDED AGAINST DOING THIS #####
        # We cannot know who has and has not already received the SCP intervention in our data, so we cannot be sure if
        # we are taking money away from someone who never received it in the first place. Also only Scottish
        # recipients would be receiving the SCP in the first place, which make up only a fraction of the population,
        # so we would be removing money from more people than received it in the first place.
        #
        # # Universal Credit recipients were receiving a £10 SCP in 2020, which increased to £25 in 2021
        # # Therefore we need to reduce the intervention received by these amounts in these years to make it fully accurate
        # if event.time.year == 2020:
        #     pop.loc[pop['hidp'].isin(
        #         uc_households), 'boost_amount'] = pop['boost_amount'] - 10
        # if event.time.year == 2021:
        #     pop.loc[pop['hidp'].isin(
        #         uc_households), 'boost_amount'] = pop['boost_amount'] - 25

        # pop['income_boosted'] = (pop['boost_amount'] != 0)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(pop['income_boosted']) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'][pop['income_boosted']].mean()}")


class hhIncomeIntervention():

    @property
    def name(self):
        return "hh_income_intervention"

    def __repr__(self):
        return "hhIncomeIntervention"

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
        # nothing done here yet. transition models specified by year later.
        print("print sys argv")
        print(sys.argv)
        print(config.keys())
        uplift = [0, 1000, 10000]  # uplift amount
        percentage_uplift = [10, 25, 75]  # uplift proportion.
        run_id = np.arange(1, 50 + 1, 1)  # 50 repeats for each combination of the above parameters
        parameter_lists = list(itertools.product(*[uplift, percentage_uplift, run_id]))
        if 'run_id' in config.keys():
            # Pick a set of parameters according to task_id arg from batch run.
            run_id = config['run_id']
        else:
            # If no task id specified (you should) choose the first task as a test.
            run_id = 1
        parameters = parameter_lists[run_id]
        config.update({'experiment_parameters': parameters}, source=str(Path(__file__).resolve()))
        config.update({'experiment_parameters_names': ['uplift', 'prop', 'id']}, source=str(Path(__file__).resolve()))

        self.uplift = parameters[0]
        self.prop = parameters[1]

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

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income"]
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the hh_income intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= (self.uplift * pop["income_boosted"])  # reset boost if people move out of bottom decile.
        # Reset boost amount to 0
        pop['boost_amount'] = 0
        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        who_uplifted = pop['hh_income'] <= pop['hh_income'].quantile(self.prop / 100)
        pop['income_boosted'] = who_uplifted
        pop['boost_amount'] = (self.uplift * pop["income_boosted"])
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) for debugging. to ensure mean value is feasible. errors can hugely inflate it.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(who_uplifted)}")
        logging.info(f"\t...which is {(sum(who_uplifted) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'].mean()}")


####################################################################################################################

class hhIncomeChildUplift(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "hh_income_20_uplift"

    def __repr__(self):
        return "hhIncomeChildUplift"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income", 'nkids']
        columns_created = ["income_boosted", "boost_amount"]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the hh_income child uplift intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # print(np.mean(pop['hh_income'])) # for debugging purposes.
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']  # reset boost if people move out of bottom decile.
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0
        pop['boost_amount'] = (25 * 30.436875 * pop['nkids'] / 7) # £25 per week * 30.463/7 weeks per average month * nkids.
        pop['income_boosted'] = (pop['boost_amount'] != 0)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(pop['income_boosted']) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'][pop['income_boosted']].mean()}")


########################################################################################################################
class hhIncomePovertyLineChildUplift(Base):
    """uplift intervention module. £20 uplift per child for households below the poverty line."""

    @property
    def name(self):
        return "hh_income_poverty_live_20_uplift"

    def __repr__(self):
        return "hhIncomePovertyLineChildUplift"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for death rate
        - Add required columns to population data frame
        - Add listener event to check if people die on each time step.
        - Update other required items such as randomness stream.

        Parameter
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["hh_income"]
        columns_created = ["income_boosted", 'boost_amount']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False, # who boosted?
                                   'boost_amount': 0.}, # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the hh_income poverty line child uplift intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive'")
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0
        # Poverty is defined as having (equivalised) disposable hh income <= 60% of national median.
        # About £800 as of 2020 + adjustment for inflation.
        # Subset everyone who is under poverty line.
        # TODO sheffield median not necessarily national average. need some work to store national macro estimates from somewhere?
        who_uplifted = (pop['hh_income'] <= np.nanmedian(pop['hh_income']) * 0.6) #
        pop['boost_amount'] = (who_uplifted * 25 * 30.436875 / 7) # £20 per child per week uplift for everyone under poverty line.

        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        pop['income_boosted'] = who_uplifted
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(pop['income_boosted']) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'][pop['income_boosted']].mean()}")



### some test on time steps for variious scotland interventions
#scotland only.
# pop = self.population_view.get(event.index, query="alive =='alive' and region=='Scotland'")

#disabled people. labour state.
# pop = self.population_view.get(event.index, query="alive =='alive' and labour_state=='Sick/Disabled'")
#unemployed adults. unemployed labour state.
# pop = self.population_view.get(event.index, query="alive =='alive' and labour_state=='Unemployed'")

#minority ethnic households
# pop = pop.loc[pop['ethnicity'].isin(minorities) # BAN,BLA,BLC,CHI,IND,OBL,WHO,OAS,PAK any others?

#child poverty priority groups (3+ children, mother under 25). nkids >3/ nkids >0 and female and under 25. further groups depend on data.)
# pop = self.population_view.get(event.index, query="alive =='alive' and nkids>=3")
# pop = self.population_view.get(event.index, query="alive =='alive' and age<=25 and nkids>0")

#young adults (under 25). obvious.
# pop = self.population_view.get(event.index, query="alive =='alive' and age<=25")

#those with no formal qualifications. Education level 0.
# pop = self.population_view.get(event.index, query="alive =='alive' and education_state==0")


# Doubling briding payment from 130 to 260 per month per child. analogous to child uplift.

# fuel insecurity fund to 20 million.
# constraining scotland to only use 20 million for energy expenditure.
# requires full scale population or reduction of money to be proportional.

#funding to Local authorities for more flexible management of energy bills. seems idealistic and hard to implement without extensive data on how each LA would react. needs much more research.
# again needs full spatial population as MINOS input.

#moratorium on rent/evictions. not sure how easy this would be. can freeze rents but no eviction variables.

# debt relief on most financially vulnerable. (again no debt variables.) have financial condition variables which may be useful instead?

# island households fund. spatial policy should be easy to cut by island super outputs but need a list of them from somewhere (spatial policy...).


