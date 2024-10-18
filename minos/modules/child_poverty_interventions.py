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


def get_weighted_median(data):
    """
    Calculate weighted median for relative poverty intervention.

    Solution from here: https://stackoverflow.com/questions/26102867/python-weighted-median-algorithm-with-pandas

    Returns
    -------

    """
    data.sort_values(by='hh_income', ascending=True, inplace=True)
    cumsum = data['weight'].cumsum()
    cutoff = data['weight'].sum() / 2.0
    median = data['weight'][cumsum >= cutoff].iloc[0]
    return median


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
        view_columns = ["hh_income", 'nkids', 'pidp', 'hidp', 'weight', "income_boosted", "boost_amount"]
        columns_created = ['income_boosted_this_wave']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Some interventions require us to remove the boost amount from hh_income before calculating the next hh_income
        self.reset_intervention = True

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted_this_wave': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child relative poverty reduction intervention in year {event.time.year}...")

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
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        #self.population_view.update(full_pop[['boost_amount']])

        # LA 22/1/24 median income now calculated by household instead of individual
        median_income = full_pop.groupby('hidp').first()['hh_income'].median()
        # LA 14/5/24 median calculation now weighted median over households
        #full_pop_hh_rep = full_pop.groupby('hidp').first()
        #median_income = get_weighted_median(full_pop_hh_rep)

        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        #nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        relative_poverty_threshold = median_income * 0.6

        print(f"Median income: {median_income}")
        print(f"Relative Poverty Threshold: {relative_poverty_threshold}")

        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['hh_income'] < relative_poverty_threshold)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['boost_amount'][(target_pop['income_boosted'] is True) &  # previously uplifted
                                   (target_pop['hh_income'] < relative_poverty_threshold)] = (  # in relative poverty
                relative_poverty_threshold - target_pop['hh_income'] + 1)  # boost is difference between income and threshold (+1 to guarantee above threshold)

        target_pop[target_pop['boost_amount'] < 0]['boost_amount'] = 0

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

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
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
        for i in target_pop_hh_representative.sample(frac=1, random_state=self.run_seed).iterrows():
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
        uplift_pop['income_boosted_this_wave'] = True
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


class ChildPovertyReductionRELATIVE_2(Base):
    """
    Uplift by £25 per week per child in each household.
    """

    @property
    def name(self):
        return "child_poverty_reduction_relative_2"

    def __repr__(self):
        return "ChildPovertyReductionRELATIVE_2"

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
        view_columns = ["hh_income", 'nkids', 'pidp', 'hidp', "income_boosted", "boost_amount"]
        columns_created = ['income_boosted_this_wave']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Some interventions require us to remove the boost amount from hh_income before calculating the next hh_income
        self.reset_intervention = True

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted_this_wave': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child relative poverty reduction intervention in year {event.time.year}...")

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
        #relative_poverty_threshold = 1247.71
        #relative_poverty_threshold = 1100.69

        relative_poverty_dict_scot = {2020: 1099.828,
                                      2021: 1150.213,
                                      2022: 1194.458,
                                      2023: 1233.024,
                                      2024: 1266.388,
                                      2025: 1296.189,
                                      2026: 1322.225,
                                      2027: 1346.128,
                                      2028: 1366.740,
                                      2029: 1386.232,
                                      2030: 1402.559,
                                      2031: 1418.178,
                                      2032: 1431.654,
                                      2033: 1444.763,
                                      2034: 1455.863,
                                      2035: 1466.089}

        relative_poverty_threshold = relative_poverty_dict_scot.get(event.time.year)


        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print("\nSTARTING FOR RELATIVE POVERTY...\n")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        #full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        # self.population_view.update(full_pop[['boost_amount']])

        print(f"Number of people already boosted: {full_pop['income_boosted'].sum()}")

        ## ALREADY BOOSTED POPULATION
        # Now get those who have already been boosted and boost again if necessary
        # open a new temporary column so as not to cause issues downstream
        full_pop['boost_amount_sustain'] = 0.
        full_pop['boost_amount_sustain'][
            (full_pop['income_boosted'] is True) &  # already boosted in previous wave
            (full_pop['hh_income'] < relative_poverty_threshold)] = (  # income below threshold
                relative_poverty_threshold - full_pop['hh_income'] + 1)  # boost amount is difference to threshold

        # boost amount should only be positive
        full_pop[full_pop['boost_amount_sustain'] < 0]['boost_amount_sustain'] = 0.
        full_pop['hh_income'] = full_pop['hh_income'] + full_pop['boost_amount_sustain']  # apply the boost

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < relative_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in relative poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in relative poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        # 4. Calculate the proportion of children in relative poverty
        # target_pop_nkids = target_pop.groupby('hidp').first()['nkids'].sum()
        prop_in_poverty = num_kids_in_pov / num_kids
        print(f"Percentage of children in relative poverty: {prop_in_poverty * 100}")

        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # we need to reduce this proportion down to 10% by 2030, so we can calculate the number of years we have left
        # and then the proportion to reduce in that year
        years_remaining = end_year - event.time.year

        if prop_in_poverty > target_pov_prop:
            prop_above_target = prop_in_poverty - target_pov_prop
        else:
            prop_above_target = 0

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
        elif years_remaining == 0:  # in 2030
            proportion_to_uplift = prop_above_target
        elif years_remaining < 0:  # after 2030, fix to target level
            proportion_to_uplift = prop_above_target

        print(f"Proportion to uplift by {end_year}: {prop_above_target}")
        print(f"Proportion to uplift this year: {proportion_to_uplift}")

        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        nkids_to_uplift = ceil(num_kids * proportion_to_uplift)

        # 7. Randomly select households by hidp until we hit the nkids_to_uplift target
        # first get a dataframe of just one person per household
        target_hidps = []
        kids = 0
        for i in pov_pop_children_hh_rep.sample(frac=1, random_state=self.run_seed).iterrows():
            if (kids + i[1]['nkids']) <= nkids_to_uplift:
                kids += i[1]['nkids']
                target_hidps.append(i[1]['hidp'])
            if kids >= nkids_to_uplift:
                break

        print(f"Number of households to uplift: {len(target_hidps)}")
        target_pop_hhs = full_pop[full_pop['hidp'].isin(target_hidps)]
        target_pop_hhs_kids = target_pop_hhs.groupby('hidp').first()['nkids'].sum()
        print(f"Number of children to uplift: {target_pop_hhs_kids}")

        # 8. Calculate boost amount for each household and apply
        full_pop['boost_amount'][full_pop['hidp'].isin(target_hidps)] = (  # in target household
                relative_poverty_threshold - full_pop['hh_income'] + 1)  # boost amount is difference to threshold

        # boost amount should only be positive
        full_pop[full_pop['boost_amount'] < 0]['boost_amount'] = 0.
        full_pop['hh_income'] = full_pop['hh_income'] + full_pop['boost_amount']  # apply the boost

        # Copy the sustain boost from earlier onto boost amount and update some intervention vars
        full_pop['boost_amount'] = full_pop['boost_amount'] + full_pop['boost_amount_sustain']
        full_pop['income_boosted'][full_pop['boost_amount'] > 0] = True
        full_pop['income_boosted_this_wave'][full_pop['boost_amount'] > 0] = True

        self.population_view.update(full_pop[['hh_income',
                                              'income_boosted',
                                              'boost_amount',
                                              'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < relative_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in relative poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")

        # 10. Logging
        #TODO: Change these to household calculations
        logging.info(f"\tNumber of people uplifted: {sum(full_pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(full_pop['income_boosted']) / len(full_pop)) * 100}% of the total "
                     f"population.")
        logging.info(f"\t...and {(sum(full_pop['income_boosted']) / len(full_pop)) * 100}% of the population in"
                     f"poverty.")
        logging.info(f"\tTotal boost amount: {full_pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount across households in poverty: "
                     f"{full_pop['boost_amount'][full_pop['income_boosted']].mean()}")


class ChildPovertyReductionRELATIVE_psub(Base):
    """
    Uplift by £25 per week per child in each household.
    """

    @property
    def name(self):
        return "child_poverty_reduction_relative_psub"

    def __repr__(self):
        return "ChildPovertyReductionRELATIVE_psub"

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
        view_columns = ["hh_income", 'nkids', 'pidp', 'hidp', "income_boosted", "boost_amount"]
        columns_created = ['income_boosted_this_wave']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Some interventions require us to remove the boost amount from hh_income before calculating the next hh_income
        self.reset_intervention = True

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted_this_wave': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child relative poverty reduction intervention in year {event.time.year}...")

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
        target_pov_prop = 0.147
        #relative_poverty_threshold = 1247.71
        #relative_poverty_threshold = 1100.69

        relative_poverty_dict_scot = {2020: 1099.828,
                                      2021: 1150.213,
                                      2022: 1194.458,
                                      2023: 1233.024,
                                      2024: 1266.388,
                                      2025: 1296.189,
                                      2026: 1322.225,
                                      2027: 1346.128,
                                      2028: 1366.740,
                                      2029: 1386.232,
                                      2030: 1402.559,
                                      2031: 1418.178,
                                      2032: 1431.654,
                                      2033: 1444.763,
                                      2034: 1455.863,
                                      2035: 1466.089}

        relative_poverty_threshold = relative_poverty_dict_scot.get(event.time.year)


        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive == 'alive'")

        print(f"Number of people already boosted: {full_pop['income_boosted'].sum()}")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        # full_pop['income_boosted'] = False
        # However we do want to reset boost amount so we can recalculate (and not uplift if not necessary)
        full_pop['boost_amount'] = 0.0
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        #self.population_view.update(full_pop[['boost_amount']])

        # LA 22/1/24 median income now calculated by household instead of individual
        #median_income = full_pop.groupby('hidp').first()['hh_income'].median()
        # LA 14/5/24 median calculation now weighted median over households
        full_pop_hh_rep = full_pop.groupby('hidp').first()
        #median_income = get_weighted_median(full_pop_hh_rep)

        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        #nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        #relative_poverty_threshold = median_income * 0.6
        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['hh_income'] < relative_poverty_threshold)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        #target_pop['boost_amount'][(target_pop['income_boosted'] is True) &  # previously uplifted
        #                           (target_pop['hh_income'] < relative_poverty_threshold)] = (  # in relative poverty
        #        relative_poverty_threshold - target_pop['hh_income'] + 1)  # boost is difference between income and threshold (+1 to guarantee above threshold)

        target_pop.loc[(target_pop['income_boosted'] is True) & (
                    target_pop['hh_income'] < relative_poverty_threshold), 'boost_amount'] = (
                    relative_poverty_threshold - target_pop['hh_income'] + 1)

        # boost amount should only be positive
        target_pop[target_pop['boost_amount'] < 0]['boost_amount'] = 0

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

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
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
        for i in target_pop_hh_representative.sample(frac=1, random_state=self.run_seed).iterrows():
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
        uplift_pop['income_boosted_this_wave'] = True
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

        self.population_view.update(full_pop[['hh_income', 'income_boosted', 'boost_amount', 'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < relative_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in relative poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")

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


class ChildPovertyReductionABSOLUTE(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_absolute"

    def __repr__(self):
        return "ChildPovertyReductionABSOLUTE"

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
        view_columns = ["hh_income", 'nkids', 'pidp', 'hidp', "income_boosted", "boost_amount"]
        columns_created = ['income_boosted_this_wave']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Some interventions require us to remove the boost amount from hh_income before calculating the next hh_income
        self.reset_intervention = True

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted_this_wave': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child absolute poverty reduction intervention in year {event.time.year}...")

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
        target_pov_prop = 0.05
        #absolute_pov_threshold = 955.54
        absolute_pov_threshold = 963.17

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print(f"Number of people already boosted: {full_pop['income_boosted'].sum()}")

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < absolute_pov_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in relative poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        # full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        #self.population_view.update(full_pop[['boost_amount']])


        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        #nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        #relative_poverty_threshold = median_income * 0.6
        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['hh_income'] < absolute_pov_threshold)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['boost_amount'][(target_pop['income_boosted'] is True) &  # previously uplifted
                                   (target_pop['hh_income'] < absolute_pov_threshold)] = (  # in poverty
                absolute_pov_threshold - target_pop['hh_income'] + 1)  # boost is difference between income and threshold (+1 to guarantee above threshold)

        # boost amount should only be positive
        target_pop[target_pop['boost_amount'] < 0]['boost_amount'] = 0
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

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
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
        for i in target_pop_hh_representative.sample(frac=1, random_state=self.run_seed).iterrows():
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
        uplift_pop['boost_amount'] = absolute_pov_threshold - uplift_pop['hh_income'] + 1
        # assign income_boosted == True if previously True or uplifted in current wave
        uplift_pop['income_boosted'] = True
        uplift_pop['income_boosted_this_wave'] = True
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

        self.population_view.update(full_pop[['hh_income', 'income_boosted', 'boost_amount', 'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < absolute_pov_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in absolute poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")

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


class ChildPovertyReductionABSOLUTE_psub(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_absolute_psub"

    def __repr__(self):
        return "ChildPovertyReductionABSOLUTE_psub"

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
        view_columns = ["hh_income", 'nkids', 'pidp', 'hidp', "income_boosted", "boost_amount"]
        columns_created = ['income_boosted_this_wave']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Some interventions require us to remove the boost amount from hh_income before calculating the next hh_income
        self.reset_intervention = True

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted_this_wave': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child absolute poverty reduction intervention in year {event.time.year}...")

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
        target_pov_prop = 0.061
        #absolute_pov_threshold = 955.54
        absolute_pov_threshold = 963.17

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print(f"Number of people already boosted: {full_pop['income_boosted'].sum()}")

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < absolute_pov_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in relative poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        # full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        #self.population_view.update(full_pop[['boost_amount']])


        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        #nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        #relative_poverty_threshold = median_income * 0.6
        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['hh_income'] < absolute_pov_threshold)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['boost_amount'][(target_pop['income_boosted'] is True) &  # previously uplifted
                                   (target_pop['hh_income'] < absolute_pov_threshold)] = (  # in poverty
                absolute_pov_threshold - target_pop['hh_income'] + 1)  # boost is difference between income and threshold (+1 to guarantee above threshold)

        # boost amount should only be positive
        target_pop[target_pop['boost_amount'] < 0]['boost_amount'] = 0
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

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
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
        for i in target_pop_hh_representative.sample(frac=1, random_state=self.run_seed).iterrows():
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
        uplift_pop['boost_amount'] = absolute_pov_threshold - uplift_pop['hh_income'] + 1
        # assign income_boosted == True if previously True or uplifted in current wave
        uplift_pop['income_boosted'] = True
        uplift_pop['income_boosted_this_wave'] = True
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

        self.population_view.update(full_pop[['hh_income', 'income_boosted', 'boost_amount', 'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < absolute_pov_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in absolute poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")

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


class ChildPovertyReduction(Base):

    @property
    def name(self):
        return "child_poverty_reduction"

    def __repr__(self):
        return "ChildPovertyReduction"

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
                        'pidp',
                        'hidp',
                        "boost_amount",
                        "income_boosted"]
        columns_created = ["boost_amount_rel",
                           "boost_amount_abs",
                           "income_boosted_this_wave",
                           "relative_boosted",
                           "absolute_boosted"]

        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'boost_amount_rel': 0.,
                                   'boost_amount_abs': 0.,
                                   'income_boosted_this_wave': False,
                                   "relative_boosted": False,
                                   "absolute_boosted": False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(
            f"\tApplying effects of the child absolute poverty reduction intervention in year {event.time.year}...")

        # This is a (perhaps ambitious) attempt to combine both the relative and absolute poverty reduction interventions
        # into one big intervention. Balancing these 2 interventions might be complicated hence the ambition.

        # set parameters
        end_year = 2030
        target_rel_prop = 0.1
        #relative_poverty_threshold = 1247.71  # US data
        # relative_poverty_threshold = 1100.69  # scottish synthpop

        # relative_poverty_dict_scot = {2020: 1099.828,
        #                               2021: 1150.213,
        #                               2022: 1194.458,
        #                               2023: 1233.024,
        #                               2024: 1266.388,
        #                               2025: 1296.189,
        #                               2026: 1322.225,
        #                               2027: 1346.128,
        #                               2028: 1366.740,
        #                               2029: 1386.232,
        #                               2030: 1402.559,
        #                               2031: 1418.178,
        #                               2032: 1431.654,
        #                               2033: 1444.763,
        #                               2034: 1455.863,
        #                               2035: 1466.089}
        #
        # relative_poverty_threshold = relative_poverty_dict_scot.get(event.time.year)

        # Load population and filter out some important populations
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print("\nSTARTING FOR RELATIVE POVERTY...\n")

        # First calculate threshold for this year
        median_income = full_pop.groupby('hidp').first()['hh_income'].median()
        relative_poverty_threshold = median_income * 0.6

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        #full_pop['relative_boosted'] = False
        full_pop['boost_amount_rel'] = 0.0
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        # self.population_view.update(full_pop[['boost_amount']])

        print(f"Number of people already boosted: {full_pop['relative_boosted'].sum()}")

        ## ALREADY BOOSTED POPULATION
        # Now get those who have already been boosted and boost again if necessary
        # open a new temporary column so as not to cause issues downstream
        full_pop['boost_amount_rel_sustain'] = 0.
        full_pop['boost_amount_rel_sustain'][(full_pop['relative_boosted'] is True) &  # already boosted in previous wave
                (full_pop['hh_income'] < relative_poverty_threshold)] = (  # income below threshold
                relative_poverty_threshold - full_pop['hh_income'] + 1)  # boost amount is difference to threshold

        # boost amount should only be positive
        full_pop[full_pop['boost_amount_rel_sustain'] < 0]['boost_amount_rel_sustain'] = 0.
        full_pop['hh_income'] = full_pop['hh_income'] + full_pop['boost_amount_rel_sustain']  # apply the boost

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < relative_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in relative poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in relative poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        # 4. Calculate the proportion of children in relative poverty
        #target_pop_nkids = target_pop.groupby('hidp').first()['nkids'].sum()
        prop_in_poverty = num_kids_in_pov / num_kids
        print(f"Percentage of children in relative poverty: {prop_in_poverty * 100}")

        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # we need to reduce this proportion down to 10% by 2030, so we can calculate the number of years we have left
        # and then the proportion to reduce in that year
        years_remaining = end_year - event.time.year

        if prop_in_poverty > target_rel_prop:
            prop_above_target = prop_in_poverty - target_rel_prop
        else:
            prop_above_target = 0

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
        elif years_remaining == 0:  # in 2030
            proportion_to_uplift = prop_above_target
        elif years_remaining < 0:  # after 2030, fix to target level
            proportion_to_uplift = prop_above_target

        # UPLIFT EVERYONE UNDER POVERTY THRESHOLD, WHAT DOES IT DO?
        #proportion_to_uplift = prop_in_poverty

        print(f"Proportion to uplift by {end_year}: {prop_above_target}")
        print(f"Proportion to uplift this year: {proportion_to_uplift}")

        # 6. Calculate number of children to elevate out of poverty based on proportion to uplift
        nkids_to_uplift = ceil(num_kids * proportion_to_uplift)

        # 7. Randomly select households by hidp until we hit the nkids_to_uplift target
        # first get a dataframe of just one person per household
        #target_pop_hh_representative = target_pop.groupby('hidp').first().reset_index()
        target_hidps = []
        kids = 0
        for i in pov_pop_children_hh_rep.sample(frac=1, random_state=self.run_seed).iterrows():
            if (kids + i[1]['nkids']) < nkids_to_uplift:
                kids += i[1]['nkids']
                target_hidps.append(i[1]['hidp'])
            if kids >= nkids_to_uplift:
                break

        print(f"Number of households to uplift: {len(target_hidps)}")
        # print(f"Number of children to uplift: {target_pop[target_pop['hidp'].isin(target_hidps)]['nkids'].sum()}")
        target_pop_hhs = full_pop[full_pop['hidp'].isin(target_hidps)]
        target_pop_hhs_kids = target_pop_hhs.groupby('hidp').first()['nkids'].sum()
        print(f"Number of children to uplift: {target_pop_hhs_kids}")

        # 8. Calculate boost amount for each household and apply
        full_pop['boost_amount_rel'][full_pop['hidp'].isin(target_hidps)] = (  # in target household
                relative_poverty_threshold - full_pop['hh_income'] + 1)  # boost amount is difference to threshold

        # boost amount should only be positive
        full_pop[full_pop['boost_amount_rel'] < 0]['boost_amount_rel'] = 0.
        full_pop['hh_income'] = full_pop['hh_income'] + full_pop['boost_amount_rel']  # apply the boost

        # Copy the sustain boost from earlier onto boost amount and update some intervention vars
        full_pop['boost_amount_rel'] = full_pop['boost_amount_rel'] + full_pop['boost_amount_rel_sustain']
        full_pop['relative_boosted'][full_pop['boost_amount_rel'] > 0] = True
        full_pop['income_boosted_this_wave'][full_pop['boost_amount_rel'] > 0] = True

        self.population_view.update(full_pop[['hh_income',
                                              'relative_boosted',
                                              'boost_amount_rel',
                                              'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < relative_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in relative poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")





        ########################## NOW DO ABSOLUTE POVERTY ##########################

        print("\nSTARTING FOR ABSOLUTE POVERTY...\n")

        # set up intervention parameters
        target_abs_prop = 0.05
        absolute_poverty_threshold = 963.17

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print(f"Number of people already boosted: {full_pop['absolute_boosted'].sum()}")

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < absolute_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in absolute poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in absolute poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        # full_pop['income_boosted'] = False
        full_pop['boost_amount_abs'] = 0.0
        # We do however want to reset the boosted this wave tag
        #full_pop['income_boosted_this_wave'] = False
        # self.population_view.update(full_pop[['boost_amount']])

        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        # nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        # relative_poverty_threshold = median_income * 0.6
        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        #target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['hh_income'] < absolute_poverty_threshold)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        full_pop['boost_amount_abs_sustain'] = 0.
        full_pop['boost_amount_abs_sustain'][(full_pop['absolute_boosted'] is True) &  # previously uplifted
                                   (full_pop['hh_income'] < absolute_poverty_threshold)] = (  # in poverty
                absolute_poverty_threshold - full_pop['hh_income'] + 1)  # boost is difference between income and threshold (+1 to guarantee above threshold)

        # boost amount should only be positive
        full_pop[full_pop['boost_amount_abs_sustain'] < 0]['boost_amount_abs_sustain'] = 0
        full_pop['hh_income'] = full_pop['hh_income'] + full_pop['boost_amount_abs_sustain']  # apply the boost

        # # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        # for index, row in target_pop.iterrows():
        #     pidp = row['pidp']
        #     if pidp in full_pop['pidp'].values:
        #         full_pop.loc[full_pop['pidp'] == pidp, 'hh_income'] = row['hh_income']
        #         full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
        #         full_pop.loc[full_pop['pidp'] == pidp, 'income_boosted'] = row['income_boosted']

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < relative_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in absolute poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in absolute poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        # # 4. Calculate the proportion of children in relative poverty
        # target_pop_nkids = target_pop.groupby('hidp').first()['nkids'].sum()
        # prop_in_poverty = target_pop_nkids / nkids_total
        # print(f"Percentage of children in poverty: {prop_in_poverty * 100}")

        # 4. Calculate the proportion of children in relative poverty
        # target_pop_nkids = target_pop.groupby('hidp').first()['nkids'].sum()
        prop_in_poverty = num_kids_in_pov / num_kids
        print(f"Percentage of children in absolute poverty: {prop_in_poverty * 100}")

        # 5. Calculate how many should be uplifted (gradual reduction in child poverty with 2030 as year we hit 10%)
        # we need to reduce this proportion down to 10% by 2030, so we can calculate the number of years we have left
        # and then the proportion to reduce in that year
        years_remaining = end_year - event.time.year

        if prop_in_poverty > target_abs_prop:
            prop_above_target = prop_in_poverty - target_abs_prop
        else:
            prop_above_target = 0

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
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
        #target_pop_hh_representative = target_pop.groupby('hidp').first().reset_index()
        target_hidps = []
        kids = 0
        for i in pov_pop_children_hh_rep.sample(frac=1, random_state=self.run_seed).iterrows():
            if (kids + i[1]['nkids']) <= nkids_to_uplift:
                kids += i[1]['nkids']
                target_hidps.append(i[1]['hidp'])
            if kids >= nkids_to_uplift:
                break

        # print(f"Number of households to uplift: {len(target_hidps)}")
        # # print(f"Number of children to uplift: {target_pop[target_pop['hidp'].isin(target_hidps)]['nkids'].sum()}")
        # target_pop_hhs = target_pop[target_pop['hidp'].isin(target_hidps)]
        # target_pop_hhs_kids = target_pop_hhs.groupby('hidp').first()['nkids'].sum()
        # print(f"Number of children to uplift: {target_pop_hhs_kids}")

        print(f"Number of households to uplift: {len(target_hidps)}")
        # print(f"Number of children to uplift: {target_pop[target_pop['hidp'].isin(target_hidps)]['nkids'].sum()}")
        target_pop_hhs = full_pop[full_pop['hidp'].isin(target_hidps)]
        target_pop_hhs_kids = target_pop_hhs.groupby('hidp').first()['nkids'].sum()
        print(f"Number of children to uplift: {target_pop_hhs_kids}")

        # 8. Calculate boost amount for each household and apply
        full_pop['boost_amount_abs'][full_pop['hidp'].isin(target_hidps)] = (  # in target household
                relative_poverty_threshold - full_pop['hh_income'] + 1)  # boost amount is difference to threshold

        # boost amount should only be positive
        full_pop[full_pop['boost_amount_abs'] < 0]['boost_amount_abs'] = 0.
        full_pop['hh_income'] = full_pop['hh_income'] + full_pop['boost_amount_abs']  # apply the boost

        # Copy the sustain boost from earlier onto boost amount and update some intervention vars
        full_pop['boost_amount_abs'] = full_pop['boost_amount_abs'] + full_pop['boost_amount_abs_sustain']
        full_pop['absolute_boosted'][full_pop['boost_amount_abs'] > 0] = True
        full_pop['income_boosted_this_wave'][full_pop['boost_amount_abs'] > 0] = True

        self.population_view.update(full_pop[['hh_income',
                                              'absolute_boosted',
                                              'boost_amount_abs',
                                              'income_boosted_this_wave']])

        # # 8. Calculate boost amount for each household and apply
        # # uplift_pop = self.population_view.get(event.index,
        # #                                       query=f"alive == 'alive' & hidp.isin({target_hidps})")
        # #uplift_pop = target_pop[target_pop['hidp'].isin(target_hidps)]
        #
        # # boost is amount to take them above poverty threshold (+1 to guarantee above threshold and not equal to)
        # uplift_pop['boost_amount'] = absolute_poverty_threshold - uplift_pop['hh_income'] + 1
        # # assign income_boosted == True if previously True or uplifted in current wave
        # uplift_pop['income_boosted'] = True
        # uplift_pop['income_boosted_this_wave'] = True
        # uplift_pop['hh_income'] += uplift_pop['boost_amount']
        #
        # # 9. Update original population with uplifted values
        # # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        # for index, row in uplift_pop.iterrows():
        #     pidp = row['pidp']
        #     if pidp in full_pop['pidp'].values:
        #         full_pop.loc[full_pop['pidp'] == pidp, 'hh_income'] = row['hh_income']
        #         full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
        #         full_pop.loc[full_pop['pidp'] == pidp, 'income_boosted'] = row['income_boosted']
        #
        # # Convert 'income_boosted' column back to boolean type
        # full_pop['income_boosted'] = full_pop['income_boosted'].astype(bool)
        #
        # self.population_view.update(
        #     full_pop[['hh_income', 'income_boosted', 'boost_amount', 'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['hh_income'] < absolute_poverty_threshold]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in absolute poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in absolute poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")

        # Get the population one last time to update the combined intervention boost variables
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        full_pop['income_boosted'] = full_pop['relative_boosted'] + full_pop['absolute_boosted']
        full_pop['boost_amount'] = full_pop['boost_amount_rel'] + full_pop['boost_amount_abs']

        self.population_view.update(full_pop[['income_boosted', 'boost_amount']])

        # Finally need to combine the specific poverty vars such as relative_boosted and absolute_boosted into

        # 10. Logging
        # TODO: Change these to household calculations
        # logging.info(f"\tNumber of people uplifted: {sum((full_pop['relative_boosted']) | sum(full_pop['absolute_boosted']))}")
        # logging.info(f"\t...which is {(sum((full_pop['relative_boosted']) | sum(full_pop['absolute_boosted'])) / len(full_pop)) * 100}% of the total "
        #              f"population.")
        # logging.info(f"\t...and {(sum((full_pop['relative_boosted']) | sum(full_pop['absolute_boosted'])) / len(full_pop)) * 100}% of the population in"
        #              f"poverty.")
        # logging.info(f"\tTotal boost amount: {full_pop['boost_amount_rel'].sum() + full_pop['boost_amount_abs'].sum()}")
        # logging.info(f"\tMean boost amount across households in poverty: "
        #              f"{full_pop['boost_amount'][full_pop['income_boosted']].mean()}")


class ChildPovertyReductionSUSTAIN(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_sustain"

    def __repr__(self):
        return "ChildPovertyReductionSUSTAIN()"

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
        view_columns = ["hh_income", 'nkids', 'hidp']
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
        relative_poverty_threshold = 1247.71  # US data

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")
        # Reset the previous income_boosted for testing
        # full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        self.population_view.update(full_pop[['boost_amount']])
        # LA 22/1/24 median income now calculated by household instead of individual
        #median_income = full_pop.groupby('hidp').first()['hh_income'].median()
        #median_income = full_pop['hh_income'].median()
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()

        # # HR 07/11/23 Correcting method of calculating total number of kids in full pop
        # Select first instance of each hidp to avoid duplicating nkids
        # nkids_total = full_pop.drop_duplicates(subset=['hidp'], keep='first')['nkids'].sum()
        # full_pop_nodupes = full_pop.drop_duplicates(subset=['hidp'], keep='first')
        # nkids_pop = full_pop_nodupes['nkids'].sum()
        # print('## TOTAL KIDS ## ')
        # print('Method 1 (simple sum): {}'.format(nkids_total))
        # print('Method 2 (unique HHs): {}'.format(nkids_pop))

        # TODO probably a faster way to do this than resetting the whole column.
        # full_pop['hh_income'] -= full_pop['boost_amount']  # reset boost
        # 3. Find all households in relative poverty
        #relative_poverty_threshold = median_income * 0.6
        target_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                    f"{relative_poverty_threshold}")
        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['boost_amount'][(target_pop['income_boosted'] == True) &  # previously uplifted
                                   (target_pop['hh_income'] < relative_poverty_threshold)] = relative_poverty_threshold - target_pop['hh_income']
        target_pop[target_pop['boost_amount'] < 0]['boost_amount'] = 0
        target_pop['hh_income'] = target_pop['hh_income'] + target_pop['boost_amount']
        self.population_view.update(target_pop[['hh_income', 'boost_amount']])
        target_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                    f"{relative_poverty_threshold}")
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
        nkids_to_uplift = round(target_pop_nkids * proportion_to_uplift)
        target_pop_hh_rep = target_pop.groupby('hidp').first().reset_index()

        # 7. Randomly select households by hidp until we hit the nkids_to_uplift target
        target_hidps = []
        kids = 0
        for i in target_pop_hh_rep.sample(frac=1).iterrows():
            if (kids + i[1]['nkids']) <= nkids_to_uplift:
                kids += i[1]['nkids']
                target_hidps.append(i[1]['hidp'])
            if kids >= nkids_to_uplift:
                break

        print(f"Number of households to uplift: {len(target_hidps)}")
        print(f"Number of children to uplift: {target_pop[target_pop['hidp'].isin(target_hidps)]['nkids'].sum()}")

        # 8. Calculate boost amount for each household and apply
        uplift_pop = self.population_view.get(event.index,
                                              query=f"alive == 'alive' & hidp.isin({target_hidps})")
        uplift_pop['boost_amount'] = relative_poverty_threshold - uplift_pop['hh_income']
        uplift_pop['income_boosted'] = (uplift_pop['boost_amount'] != 0)
        uplift_pop['hh_income'] += uplift_pop['boost_amount']

        # 9. Update original population with uplifted values
        self.population_view.update(uplift_pop[['hh_income', 'income_boosted', 'boost_amount']])

        target_pop2 = self.population_view.get(event.index,
                                               query=f"alive == 'alive' & nkids > 0 & hh_income < "
                                                     f"{relative_poverty_threshold}")

        print(f"Proportion of children in poverty AFTER intervention: {target_pop2.groupby('hidp').first()['nkids'].sum() / nkids_total}")

        # 10. Logging
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


class ChildPovertyReductionMatDep(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_matdep"

    def __repr__(self):
        return "ChildPovertyReductionMatDep"

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
                        'pidp',
                        'hidp',
                        "income_boosted",
                        "boost_amount",
                        'matdep_child',
                        'low_income_matdep_child']
        columns_created = ['income_boosted_this_wave']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Some interventions require us to remove the boost amount from hh_income before calculating the next hh_income
        self.reset_intervention = True

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted_this_wave': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child material deprivation intervention in year {event.time.year}...")

        # This intervention will reduce the % of children living in families in combined material deprivation and low income
        # to a defined proportion by a set end year. According to the Scottish Government website (link below), the
        # target for combined material deprivation and low income is 8% by 2030


        # Some information about the child poverty targets here: https://www.gov.scot/news/tackling-child-poverty-delivery-plan-2022-26/

        # set parameters
        end_year = 2030
        target_pov_prop = 0.08
        #absolute_pov_threshold = 955.54
        #absolute_pov_threshold = 963.17

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print(f"Number of people already boosted: {full_pop['income_boosted'].sum()}")

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['low_income_matdep_child'] == 1]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in in low income and child material "
            f"deprivation, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in low income and material deprivation, which is "
            f"{(num_kids_in_pov / num_kids) * 100}% of the total.")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        # full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        #self.population_view.update(full_pop[['boost_amount']])


        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        #nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        #relative_poverty_threshold = median_income * 0.6
        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['low_income_matdep_child'] == 1)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['matdep_child'][(target_pop['income_boosted'] is True) &  # previously uplifted
                                    (target_pop['low_income_matdep_child'] == 1)] = 0

        # boost amount should only be positive
        #target_pop[target_pop['boost_amount'] < 0]['boost_amount'] = 0
        #target_pop['hh_income'] = target_pop['hh_income'] + target_pop['boost_amount']  # apply the boost

        # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        for index, row in target_pop.iterrows():
            pidp = row['pidp']
            if pidp in full_pop['pidp'].values:
                full_pop.loc[full_pop['pidp'] == pidp, 'matdep_child'] = row['matdep_child']
                #full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
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

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
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
        for i in target_pop_hh_representative.sample(frac=1, random_state=self.run_seed).iterrows():
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
        uplift_pop['matdep_child'] = 0
        # assign income_boosted == True if previously True or uplifted in current wave
        uplift_pop['income_boosted'] = True
        uplift_pop['income_boosted_this_wave'] = True
        #uplift_pop['hh_income'] += uplift_pop['boost_amount']

        # 9. Update original population with uplifted values
        # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        for index, row in uplift_pop.iterrows():
            pidp = row['pidp']
            if pidp in full_pop['pidp'].values:
                full_pop.loc[full_pop['pidp'] == pidp, 'hh_income'] = row['metdep_child']
                #full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
                full_pop.loc[full_pop['pidp'] == pidp, 'income_boosted'] = row['income_boosted']

        # Convert 'income_boosted' column back to boolean type
        full_pop['income_boosted'] = full_pop['income_boosted'].astype(bool)

        self.population_view.update(full_pop[['hh_income', 'income_boosted', 'boost_amount', 'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['low_income_matdep_child'] == 1]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in absolute poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")

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


class ChildPovertyReductionMatDepIncome(Base):
    """Uplift by £25 per week per child in each household. """

    @property
    def name(self):
        return "child_poverty_reduction_matdep_income"

    def __repr__(self):
        return "ChildPovertyReductionMatDepIncome"

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
                        'pidp',
                        'hidp',
                        "income_boosted",
                        "boost_amount",
                        'matdep_child',
                        'low_income_matdep_child']
        columns_created = ['income_boosted_this_wave']
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

        # Some interventions require us to remove the boost amount from hh_income before calculating the next hh_income
        self.reset_intervention = True

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        #builder.event.register_listener("time_step", self.on_time_step, priority=4)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted_this_wave': False},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):

        logging.info("INTERVENTION:")
        logging.info(f"\tApplying effects of the child material deprivation and low income intervention in "
                     f"year {event.time.year}...")

        # This intervention will reduce the % of children living in families in combined material deprivation and low income
        # to a defined proportion by a set end year. According to the Scottish Government website (link below), the
        # target for combined material deprivation and low income is 8% by 2030


        # Some information about the child poverty targets here: https://www.gov.scot/news/tackling-child-poverty-delivery-plan-2022-26/

        # set parameters
        end_year = 2030
        target_pov_prop = 0.08
        #absolute_pov_threshold = 955.54
        #absolute_pov_threshold = 963.17

        # 1. Calculate median hh_income over all households
        full_pop = self.population_view.get(event.index, query="alive =='alive'")

        print(f"Number of people already boosted: {full_pop['income_boosted'].sum()}")

        # Calculate threshold for this year
        median_income = full_pop.groupby('hidp').first()['hh_income'].median()
        income_threshold = median_income * 0.7

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['low_income_matdep_child'] == 1]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households in in low income and child material "
            f"deprivation, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children in low income and material deprivation, which is "
            f"{(num_kids_in_pov / num_kids) * 100}% of the total.")

        # DO NOT reset the previous income_boosted for testing
        # We need to track people who have been intervened so we can continue the intervention indefinitely
        # full_pop['income_boosted'] = False
        full_pop['boost_amount'] = 0.0
        # We do however want to reset the boosted this wave tag
        full_pop['income_boosted_this_wave'] = False
        #self.population_view.update(full_pop[['boost_amount']])


        # Number of kids should be calculated by household also
        # 2. Total number of kids
        nkids_total = full_pop.groupby('hidp').first()['nkids'].sum()
        #nkids_total = full_pop['nkids'].sum()

        # 3. Find all households in relative poverty
        #relative_poverty_threshold = median_income * 0.6
        # target_pop = self.population_view.get(event.index,
        #                                       query=f"alive == 'alive' & nkids > 0 & hh_income < "
        #                                             f"{relative_poverty_threshold}")
        target_pop = full_pop[(full_pop['nkids'] > 0) & (full_pop['low_income_matdep_child'] == 1)]

        # 3a. This is the SUSTAIN intervention, so we want to find the households that have previously received the
        # intervention (if any) and uplift them again. This is to simulate ongoing support for a set of families
        target_pop['matdep_child'][(target_pop['income_boosted'] is True) &  # previously uplifted
                                   (target_pop['low_income_matdep_child'] == 1)] = 0  # no longer in material deprivation
        target_pop['boost_amount'][(target_pop['income_boosted'] is True) &
                                   (target_pop['low_income_matdep_child'] == 1)] = (  # income below threshold
                income_threshold - full_pop['hh_income'] + 1)  # boost amount is difference to threshold

        # boost_amount must be positive
        target_pop[target_pop['boost_amount'] < 0]['boost_amount'] = 0.

        # TODO: Add noise with scipy.stats.truncnorm

        # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        for index, row in target_pop.iterrows():
            pidp = row['pidp']
            if pidp in full_pop['pidp'].values:
                full_pop.loc[full_pop['pidp'] == pidp, 'matdep_child'] = row['matdep_child']
                full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
                full_pop.loc[full_pop['pidp'] == pidp, 'income_boosted'] = row['income_boosted']

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

        if (years_remaining > 0) & (years_remaining != 1):  # before 2030 (but not 2029)
            proportion_to_uplift = prop_above_target / years_remaining
        elif years_remaining == 1:  # 2029 - divide by 2 as diving by 1 means meeting target 1 year early
            proportion_to_uplift = prop_above_target / 2
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
        for i in target_pop_hh_representative.sample(frac=1, random_state=self.run_seed).iterrows():
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
        uplift_pop = target_pop[target_pop['hidp'].isin(target_hidps)]

        # boost is amount to take them above poverty threshold (+1 to guarantee above threshold and not equal to)
        uplift_pop['matdep_child'] = 0
        uplift_pop['boost_amount'] = (income_threshold - uplift_pop['hh_income']) + 1
        # boost_amount must be positive
        uplift_pop[uplift_pop['boost_amount'] < 0]['boost_amount'] = 0.
        # assign income_boosted == True if previously True or uplifted in current wave
        uplift_pop['income_boosted'] = True
        uplift_pop['income_boosted_this_wave'] = True
        uplift_pop['hh_income'] += uplift_pop['boost_amount']

        # 9. Update original population with uplifted values
        # Iterate over rows in 'uplift_pop' and update corresponding rows in 'full_pop'
        for index, row in uplift_pop.iterrows():
            pidp = row['pidp']
            if pidp in full_pop['pidp'].values:
                full_pop.loc[full_pop['pidp'] == pidp, 'hh_income'] = row['matdep_child']
                full_pop.loc[full_pop['pidp'] == pidp, 'boost_amount'] = row['boost_amount']
                full_pop.loc[full_pop['pidp'] == pidp, 'income_boosted'] = row['income_boosted']

        # Convert 'income_boosted' column back to boolean type
        full_pop['income_boosted'] = full_pop['income_boosted'].astype(bool)

        self.population_view.update(full_pop[['hh_income', 'income_boosted', 'boost_amount', 'income_boosted_this_wave']])

        # Generate a few important populations to use for reporting / further work
        full_pop_hh_rep = full_pop.groupby('hidp').first().reset_index()  # single representative of each household
        pov_pop_hh_rep = full_pop_hh_rep[full_pop_hh_rep['low_income_matdep_child'] == 1]
        pov_pop_children_hh_rep = pov_pop_hh_rep[pov_pop_hh_rep['nkids'] > 0]

        # Number of children
        num_kids = full_pop_hh_rep['nkids'].sum()
        num_kids_in_pov = pov_pop_children_hh_rep['nkids'].sum()

        print(f"Number of children in the model: {num_kids}")

        print(
            f"There are {len(pov_pop_hh_rep)}/{len(full_pop_hh_rep)} households still in absolute poverty, with {len(pov_pop_children_hh_rep)} containing children.")
        print(
            f"This amounts to {num_kids_in_pov} children still in poverty, which is {(num_kids_in_pov / num_kids) * 100}% of the total.")

        print(
            f"Proportion of children in poverty AFTER intervention: {num_kids_in_pov / num_kids}")

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




class fullScottishPackage(Base):

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
        #TODO hard code this for universal credit uplift
        uplifted_households = np.unique(dynamic_subset_function(pop, self.uplift_condition)['hidp'])
        # Households on universal credit and legacy benefits are already receiving £10 SCP in our input population
        # (2020) start. Therefore we need to reduce the intervention by £10 for these people
        #uc_households = np.unique(dynamic_subset_function(pop, 'who_universal_credit_and_kids')['hidp'])

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

        """
        As per Emma's feedback we have another intervention that roughly implements all of the child poverty action plan on top of the 
        SCP. this intervention is going here. 
    
        going to reuse the generalised child uplift interventoin function. with different subset and uplift requirements. 
    
        - “Best Start Grant Pregnancy and Baby Payment – one off payment of up to £754.65 from 24 weeks in pregnancy up until a 
        baby turns 6 months for families who get certain benefits. 
        we don't have gestation in this model currently. simplified version gives 754.65 if a child is born. 
    
        · Best Start Grant Early Learning Payment – one off payment of £314.45 when a child is between two and three years and 
        six months for families who get certain benefits. 
        # give household 314.45 per newborn in a given year. 
        
        · Best Start Grant School Age Payment – one off payment of £314.45 when a child would normally start primary one for 
        families who get certain benefits.
        # when child is 4 years old give one off bump of 314.45
    
        · Best Start Foods – a pre-paid card from pregnancy up to when a child turns three for families on certain benefits 
         to help buy healthy food 
         does a household have children less than 3? if yes, given them the equivalent money for this card.
          or bump nutrition quality?
        """

        pop = self.population_view.get(event.index, query="alive =='alive'")

        # best start pregnancy grant.
        # get households with newborns. given them 754.65. cant retroactively give them payment here. is this a provlem?
        #households_with_newborn = np.uniquepop.loc[pop['has_newborn']['hidp'])
        # people_in_newborn_households = pop.loc[pop['hidp'].isin(households_with_newborn)].index
        # pop.loc[people_in_newborn_households, 'hh_income'] += 754.65

        # best start foods payment.
        # households with children three and under get money to spend on 'more nutritious' food.
        # More difficult to implement the effects of this. It is not an income boost per se, but it would substantially
        # improve nutrition quality.
        # TODO function to identify households with children of the required ages. im hating the child ages string more with each day.
        #households_with_children_under_4= np.uniquepop.loc[pop['has_newborn']['hidp'])
        # people_in_newborn_households = pop.loc[pop['hidp'].isin(households_with_newborn)].index
        # pop.loc[people_in_newborn_households, 'hh_income'] += 754.65



        # best start early learning payment and  best start grant school age payment.
        # children aged 2,3,4 years old get one off payments of 314.45 for early learning developnment
        # NOTE This is two seperate grants for 2,3 years old and 4 years old but they're virtually identical
        # implementation so combining.
        #households_with_2_3_year_olds = np.uniquepop.loc[pop['has_newborn']['hidp'])
        # people_in_2_3_year_olds_households = pop.loc[pop['hidp'].isin(households_with_2_3_year_olds )].index
        # pop.loc[people_in_2_3_year_olds_households , 'hh_income'] += 314.45


