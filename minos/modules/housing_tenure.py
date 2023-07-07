"""
Module for housing tenure in Minos.
Type of housing i.e. social rented, private rented, owned with mortgage, owned outright etc.
Possible future work for moving households and changing household composition (e.g. marrying/births)
"""

import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import catplot
import logging
from datetime import datetime as dt


class HousingTenure(Base):

    @property
    def name(self):
        return "housing_tenure"

    def __repr__(self):
        return "HousingTenure()"

    # In Daedalus pre_setup was done in the run_pipeline file. This way is tidier and more modular in my opinion.

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

        # Load in inputs from pre-setup.
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.

        # Assign randomness streams if necessary. Only useful if seeding counterfactuals.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["sex",
                        "ethnicity",
                        "age",
                        "hh_income",
                        'housing_tenure',
                        'urban',
                        'financial_situation']
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=5)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        logging.info("HOUSING TENURE")

        # Construct transition probability distributions.
        # Draw individuals next states randomly from this distribution.
        # Adjust other variables according to changes in state. E.g. a birth would increase child counter by one.

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        housing_tenure_prob_df = self.calculate_housing_tenure(pop)

        housing_tenure_prob_df["housing_tenure"] = self.random.choice(housing_tenure_prob_df.index,
                                                                      list(housing_tenure_prob_df.columns),
                                                                      housing_tenure_prob_df)

        housing_tenure_prob_df.index = housing_tenure_prob_df.index.astype(int)

        # convert numeric prediction into string factors (low, medium, high)
        #housing_tenure_factor_dict = {}
        #housing_tenure_prob_df.replace({'housing_tenure': housing_tenure_factor_dict},
        #                        inplace=True)

        self.population_view.update(housing_tenure_prob_df["housing_tenure"])

    def calculate_housing_tenure(self, pop):
        """Calculate housing tenure transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # load transition model based on year.
        if self.cross_validation:
            # if cross-val, fix year to final year model
            year = 2019
        else:
            year = min(self.year, 2019)

        # 2019 model doesn't have the 'Rented private furnished' category. Set differently for years before this
        if year == 2019:
            cols = ['Owned outright', 'Owned with mortgage', 'Local authority rent', 'Housing assoc rented',
                    'Rented from employer', 'Rented private unfurnished', 'Other']
        elif year < 2019:
            cols = ['Owned outright', 'Owned with mortgage', 'Local authority rent', 'Housing assoc rented',
                    'Rented from employer', 'Rented private unfurnished', 'Rented private furnished', 'Other']

        transition_model = r_utils.load_transitions(f"housing_tenure/nnet/housing_tenure_{year}_{year+1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)
        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_nnet(transition_model,
                                       self.rpy2Modules,
                                       pop,
                                       cols)
        return prob_df

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"housing_tenure_barplot_{self.year}.pdf"
        densities = pd.DataFrame(pop['housing_tenure'].value_counts(normalize=True))
        densities.columns = ['densities']
        densities['housing_tenure'] = densities.index
        f = plt.figure()
        cat = catplot(data=densities, y='housing_tenure', x='densities', kind='bar', orient='h')
        plt.savefig(file_name)
        plt.close()
