"""
Module for housing in Minos.
Upgrade of household appliances
Possible future work for moving households and changing household composition (e.g. marrying/births)
"""

import pandas as pd
from pathlib import Path
from minos.modules import r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import catplot
from datetime import datetime as dt

class Housing(Base):

    @property
    def name(self):
        return "housing"

    def __repr__(self):
        return "Housing()"

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
                        "labour_state",
                        "SF_12",
                        "job_sec",
                        "ethnicity",
                        "age",
                        "housing_quality",
                        "hh_income",]
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=4)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Construct transition probability distributions.
        # Draw individuals next states randomly from this distribution.
        # Adjust other variables according to changes in state. E.g. a birth would increase child counter by one.

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        housing_prob_df = self.calculate_housing(pop)

        housing_prob_df["housing_quality"] = self.random.choice(housing_prob_df.index,
                                                                list(housing_prob_df.columns),
                                                                housing_prob_df) + 1

        housing_prob_df.index = housing_prob_df.index.astype(int)

        # convert numeric prediction into string factors (low, medium, high)
        housing_factor_dict = {1: 'Low',
                               2: 'Medium',
                               3: 'High'}
        housing_prob_df.replace({'housing_quality': housing_factor_dict},
                                inplace=True)


        self.population_view.update(housing_prob_df["housing_quality"])

    def calculate_housing(self, pop):
        """Calculate housing transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # load transition model based on year.
        year = min(self.year, 2019)
        transition_model = r_utils.load_transitions(f"housing_quality/clm/housing_quality_{year}_{year+1}", self.rpy2Modules, path=self.transition_dir)
        # returns probability matrix (3xn) of next ordinal state.
        prob_df = r_utils.predict_next_timestep_clm(transition_model, self.rpy2Modules, pop, 'housing_quality')
        return prob_df

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"housing_barplot_{self.year}.pdf"
        densities = pd.DataFrame(pop['housing_quality'].value_counts(normalize=True))
        densities.columns = ['densities']
        densities['housing_quality'] = densities.index
        f = plt.figure()
        cat = catplot(data=densities, y='housing_quality', x='densities', kind='bar', orient='h')
        plt.savefig(file_name)
        plt.close()