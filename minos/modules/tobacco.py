"""
Module for tobacco in Minos.
Calculation of monthly household tobacco
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import histplot
import numpy as np
import logging

class Tobacco(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'tobacco'

    def __repr__(self):
        return "Tobacco()"

    def setup(self, builder):
        """ Initialise the module during simulation.setup().

        Notes
        -----
        - Load in data from pre_setup
        - Register any value producers/modifiers for tobacco
        - Add required columns to population data frame
        - Update other required items such as randomness stream.

        Parameters
        ----------
        builder : vivarium.engine.Builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.

        """

        # Load in inputs from pre-setup.
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_run_crn_key())

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
                        'SF_12',
                        'behind_on_bills',
                        'financial_situation'
                        ]
        #view_columns += self.transition_model.rx2('model').names
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
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        logging.info("TOBACCO")

        # Get living people to update their tobacco
        pop = self.population_view.get(event.index, query="alive =='alive'")
        self.year = event.time.year

        # Predict next tobacco value
        newWaveTobacco = pd.DataFrame(self.calculate_tobacco(pop))
        newWaveTobacco.columns = ['ncigs']
        newWaveTobacco.index = pop.index
        newWaveTobacco["ncigs"] = newWaveTobacco["ncigs"].astype(int)
        # Draw individuals next states randomly from this distribution.
        # Update population with new tobacco
        newWaveTobacco["ncigs"] = np.clip(newWaveTobacco['ncigs'], 0, 300)
        self.population_view.update(newWaveTobacco["ncigs"])

    def calculate_tobacco(self, pop):
        """Calculate tobacco transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # load transition model based on year.
        if self.cross_validation:
            # if cross-val, fix year to final year model
            year = 2020
        else:
            year = max(self.year, 2014)
            year = min(year, 2020)

        # if simulation goes beyond real data in 2020 dont load the transition model again.
        if not self.transition_model or year <= 2020:
            self.transition_model = r_utils.load_transitions(f"ncigs/zip/ncigs_{year}_{year + 1}", self.rpy2Modules, path=self.transition_dir)
            self.transition_model = r_utils.randomise_fixed_effects(self.transition_model,
                                                                    self.rpy2Modules,
                                                                    "zip",
                                                                    seed=self.run_seed)

        # The calculation relies on the R predict method and the model that has already been specified
        nextWaveTobacco = r_utils.predict_next_timestep_zip(model=self.transition_model,
                                                            rpy2Modules=self.rpy2Modules,
                                                            current=pop,
                                                            seed=self.run_seed)
        return nextWaveTobacco

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"tobacco_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="ncigs", stat='density')
        plt.savefig(file_name)
        plt.close()
