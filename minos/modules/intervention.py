"""Module for applying any interventions to the base population from replenishment."""
import itertools
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from minos.modules.base_module import Base

from minos.outcomes.aggregate_subset_functions import dynamic_subset_function


def get_monthly_boost_amount(data, boost_amount):
    """Calculate monthly uplift for eligible households. number of children * 30.436875/7 weeks * boost amount
    """
    return boost_amount * 30.436875 * data['nkids'] / 7


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
        if self.uplift_condition == "who_below_poverty_line_and_kids":
            pop['hh_income'] -= pop['boost_amount']  # reset boost if people move out of bottom decile. only do this for relative poverty uplift.
        else:
            pop['income_boosted'] = False
        uplifted_households = np.unique(dynamic_subset_function(pop, self.uplift_condition)['hidp'])
        pop.loc[pop['hidp'].isin(uplifted_households) ,'income_boosted'] = True # set everyone who satisfies uplift condition to true.
        pop['boost_amount'] = pop['income_boosted'] * get_monthly_boost_amount(pop, self.uplift_amount) # £25 per week * 30.463/7 weeks per average month * nkids.
        #pop['income_boosted'] = (pop['boost_amount'] != 0)
        pop['hh_income'] += pop['boost_amount']
        # print(np.mean(pop['hh_income'])) # for debugging.
        # TODO some kind of heterogeneity for people in the same household..? general inclusion of houshold compositon.
        self.population_view.update(pop[['hh_income', 'income_boosted', 'boost_amount']])

        logging.info(f"\tNumber of people uplifted: {sum(pop['income_boosted'])}")
        logging.info(f"\t...which is {(sum(pop['income_boosted']) / len(pop)) * 100}% of the total population.")
        logging.info(f"\tTotal boost amount: {pop['boost_amount'].sum()}")
        logging.info(f"\tMean boost amount: {pop['boost_amount'][pop['income_boosted']].mean()}")



