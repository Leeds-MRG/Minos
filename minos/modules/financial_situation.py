import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import logging
from datetime import datetime as dt


class financialSituation(Base):


    # Special methods used by vivarium.
    @property
    def name(self):
        return 'financial_situation'

    def __repr__(self):
        return "financialSituation()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

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
                        "financial_situation",
                        ]
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        self.year = event.time.year

        nextWaveFinancialPerception = self.calculate_financial_situation(pop)
        nextWaveFinancialPerception["financial_situation"] = self.random.choice(nextWaveFinancialPerception.index,
                                                                list(nextWaveFinancialPerception.columns+1),
                                                                nextWaveFinancialPerception).astype(float)
        nextWaveFinancialPerception.index = pop.index
        #nextWaveFinancialPerception["financial_situation"] = nextWaveFinancialPerception["financial_situation"].astype(int)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income.
        self.population_view.update(nextWaveFinancialPerception['financial_situation'])

    def calculate_financial_situation(self, pop):
        year = 2020
        # if simulation goes beyond real data in 2020 dont load the transition model again.
        if not self.transition_model or year <= 2020:
            self.transition_model = r_utils.load_transitions(f"financial_situation/clm/financial_situation_{year}_{year + 1}",
                                                             self.rpy2Modules, path=self.transition_dir)
            self.transition_model = r_utils.randomise_fixed_effects(self.transition_model, self.rpy2Modules, "clm")

        #transition_model = r_utils.load_transitions(f"financial_situation/clm/financial_situation_{year}_{year + 1}", self.rpy2Modules)
        nextWaveFinancialPerception = r_utils.predict_next_timestep_clm(self.transition_model, self.rpy2Modules, pop,
                                                                        dependent='financial_situation')
        return nextWaveFinancialPerception
