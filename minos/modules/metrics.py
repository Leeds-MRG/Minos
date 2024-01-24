"""Module for updating amy useful deterministic variables that happen not to be updated anywhere"""

import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import logging
from datetime import datetime as dt
from minos.data_generation import generate_composite_vars as gcv
from minos.data_generation import US_utils


''' All metrics related to child poverty '''
class ChildPovertyMetrics(Base):
    @property
    def name(self):
        return "child_poverty_metrics"

    def __repr__(self):
        return "ChildPovertyMetrics()"

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
        view_columns = ['hidp',
                        'hh_income',
                        'relative_poverty',
                        # 'relative_poverty_percentile',
                        'absolute_poverty',
                        # 'absolute_poverty_percentile',
                        'matdep_child',
                        # 'low_income',
                        'low_income_matdep_child',
                        'relative_poverty_history',
                        'persistent_poverty',
                        ]
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=6)

        # Grab reference year hh income for absolute poverty calculations; saved recalculating at each timestep
        # self.median_reference = US_utils.get_equivalised_income_uk()  # 1. Using ONS/external data
        self.median_reference = US_utils.get_equivalised_income_internal()  # 2. Using US/internal data

    def on_time_step(self, event):
        """Produces poverty variables on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        ''' 1. Household-level poverty variables '''
        pop = gcv.update_poverty_vars_hh(pop,
                                         year=self.year,
                                         median_reference=self.median_reference)  # Passing 2010/11 median here saves recalculating at each time step

        ''' 2. Individual-level poverty variables '''
        pop = gcv.update_poverty_vars_ind(pop)

        ''' 3. Update master population with all poverty variables '''
        updated_vars = ['relative_poverty',
                        # 'relative_poverty_percentile',
                        'absolute_poverty',
                        # 'absolute_poverty_percentile',
                        # 'low_income',
                        'low_income_matdep_child',
                        'relative_poverty_history',
                        'persistent_poverty',
                        ]

        # 06/12/23 Bodge to avoid Vivarium type error (actually PopulationError)
        vars_to_cast = {'relative_poverty': int,
                        'absolute_poverty': int,
                        # 'low_income': int,
                        'low_income_matdep_child': int,
                        'relative_poverty_history': int,
                        'persistent_poverty': int,
                        }

        for var, _type in vars_to_cast.items():
            pop[var] = pop[var].astype(_type)

        self.population_view.update(pop[updated_vars])
