import itertools
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from minos.modules.base_module import Base

class livingWageIntervention(Base):
    """Living Wage Intervention. Increase hh_income for anyone who doesn't earn a living wage to bridge the gap."""

    @property
    def name(self):
        return "living_wage_intervention"

    def __repr__(self):
        return "livingWageIntervention()"

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
        view_columns = ['hh_income', 'hourly_wage', 'job_hours', 'region', 'sex', 'ethnicity', 'alive', 'job_sector']
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
        """
        Parameters
        ----------
        pop_data
        Returns
        -------
        """
        pop_update = pd.DataFrame({'income_boosted': False, # who boosted?
                                   'boost_amount': 0.}, # hh income boosted by how much?
                                  index=pop_data.index)
        self.population_view.update(pop_update)


    def on_time_step(self, event):
        """
        Parameters
        ----------
        event
        Returns
        -------
        """

        logging.info("INTERVENTION:")
        logging.info(
            f"\tApplying effects of the living wage intervention in year {event.time.year}...")

        pop = self.population_view.get(event.index, query="alive =='alive' and job_sector == 2")
        # TODO probably a faster way to do this than resetting the whole column.
        #pop['hh_income'] -= pop['boost_amount']
        # reset boost amount to 0 before calculating next uplift
        pop['boost_amount'] = 0

        # 03/11/23 - Changing living wage values to match the living wage foundation, recently had an increase
        #            Alongside this we're also rebasing the inflation adjustment to 2023 to match these pounds
        # Now get who gets uplift (different for London/notLondon)
        who_uplifted_London = pop['hourly_wage'] > 0
        who_uplifted_London *= pop['region'] == 'London'
        who_uplifted_London *= pop['hourly_wage'] < 13.15
        who_uplifted_notLondon = pop['hourly_wage'] > 0
        who_uplifted_notLondon *= pop['region'] != 'London'
        who_uplifted_notLondon *= pop['hourly_wage'] < 12.00
        # Calculate boost amount (difference between hourly wage and living wage multiplied by hours worked in a week (extended to month))
        # boost_amount = hourly_wage_diff * hours_worked_monthly
        pop['boost_amount'] = (13.15 - pop['hourly_wage']) * (pop['job_hours'] * 4.2) * who_uplifted_London
        pop['boost_amount'] += (12.00 - pop['hourly_wage']) * (pop['job_hours'] * 4.2) * who_uplifted_notLondon


        # pop['income_deciles'] = pd.qcut(pop["hh_income"], int(100/self.prop), labels=False)
        pop['income_boosted'] = who_uplifted_notLondon | who_uplifted_London
        #pop.drop(labels='who_uplifted', inplace=True)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of household composition.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(who_uplifted_London) + sum(who_uplifted_notLondon)}")
        if who_uplifted_London.sum() > 0:  # if any London individuals in simulation being uplifted (will be not true in some synthetic population runs)
            logging.info(
                f"\t...which is {((sum(who_uplifted_London) + sum(who_uplifted_notLondon)) / len(pop)) * 100}% of the total population.")
            logging.info(f"\t\tLondon n: {sum(who_uplifted_London)}")
            logging.info(f"\t\tLondon %: {(sum(who_uplifted_London) / len(pop[pop['region'] == 'London'])) * 100}")
        logging.info(f"\t\tNot London n: {sum(who_uplifted_notLondon)}")
        logging.info(f"\t\tNot London %: {(sum(who_uplifted_notLondon) / len(pop[pop['region'] != 'London'])) * 100}")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'][pop['income_boosted'] == True].sum()}")
        if who_uplifted_London.sum() > 0:
            logging.info(f"\t\tLondon: {pop[who_uplifted_London]['boost_amount'].sum()}")
        logging.info(f"\t\tNot London: {pop[who_uplifted_notLondon]['boost_amount'].sum()}")
        logging.info(f"\tMean weekly boost amount: {pop['boost_amount'][pop['income_boosted'] == True].mean()}")
        if who_uplifted_London.sum() > 0:
            logging.info(f"\t\tLondon: {pop[who_uplifted_London]['boost_amount'].mean()}")
        logging.info(f"\t\tNot London: {pop[who_uplifted_notLondon]['boost_amount'].mean()}")

