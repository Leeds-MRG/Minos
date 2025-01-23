import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import logging
from datetime import datetime as dt


class behindOnBills(Base):


    # Special methods used by vivarium.
    @property
    def name(self):
        return 'behind_on_bills'

    def __repr__(self):
        return "behindOnBills()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().
        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for income
        - Add required columns to population data frame
        - Update other required items such as randomness stream.
        Parameters
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """

        # Load in inputs from pre-setup.
        # self.transition_model = builder.data.load("income_transition")
        self.rpy2_modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        # self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ["age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        "housing_quality",
                        "neighbourhood_safety",
                        "loneliness",
                        "nutrition_quality",
                        "ncigs",
                        'job_sec',
                        'hh_income',
                        'marital_status',
                        'housing_tenure',
                        "behind_on_bills",
                        "SF_12_MCS",
                        'yearly_energy',
                        'financial_situation'
                        ]
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=3)

    def on_time_step(self, event):
        """ Predicts the ability to pay bills for the next point in time.
        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        self.year = event.time.year

        nextWaveBills = self.calculate_behind_on_bills(pop)
        nextWaveBills["behind_on_bills"] = self.random.choice(nextWaveBills.index,
                                                                  list(nextWaveBills.columns+1),
                                                                  nextWaveBills)#.astype(float)
        nextWaveBills.index = pop.index
        # Update population with new BOB values.
        self.population_view.update(nextWaveBills['behind_on_bills'])

    def calculate_behind_on_bills(self, pop):
        year = 2019
        transition_model = r_utils.load_transitions(f"behind_on_bills/clm/behind_on_bills_{year}_{year + 1}", self.rpy2_modules)
        nextWaveBills = r_utils.predict_next_timestep_clm(transition_model, self.rpy2_modules, pop, dependent='behind_on_bills')
        return nextWaveBills