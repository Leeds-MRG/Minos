"""
Module for S7_labour_state in Minos.
"""

import pandas as pd
from pathlib import Path
from minos.modules import r_utils
import random
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import catplot

class MaritalStatus(Base):
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'marital_status'

    def __repr__(self):
        return "MaritalStatus()"

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

        # Load in any inputs from pre-setup.
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.

        # Assign randomness streams. Keeps aspects of the msim the same on repeat runs to reduce uncertainty.
        # same CRN seed for every run.
        #self.random = builder.randomness.get_stream(f"labour")
        # random CRN seed for every run.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ["sex",
                        "SF_12",
                        "ethnicity",
                        "age",
                        'region',
                        "hh_income",
                        "education_state",
                        "urban",
                        'housing_tenure',
                        'financial_situation',
                        'marital_status']

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

        # TODO: Handle students properly now that max education is predicted.
        # Separate the population into current students and everyone else. Then see if students max_educ is larger than
        # current education_state, if yes maintain student, if no predict new labour_state

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        mstat_prob_df = self.calculate_mstat(pop)

        mstat_prob_df["marital_status"] = self.random.choice(mstat_prob_df.index, list(mstat_prob_df.columns), mstat_prob_df)
        mstat_prob_df.index = mstat_prob_df.index.astype(int)

        self.population_view.update(mstat_prob_df["marital_status"])

    def calculate_mstat(self, pop):
        """Calculate labour transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # set up list of columns
        cols = ['Single', 'Partnered', 'Separated', 'Widowed']

        # load transition model based on year.
        #year = min(self.year, 2018) # TODO just use latest model for now. Needs some kind of reweighting if extrapolating later.
        if self.cross_validation:
            # if cross-val, fix year to final year model
            year = 2019
        else:
            year = min(self.year, 2019)

        transition_model = r_utils.load_transitions(f"marital_status/nnet/marital_status_{year}_{year+1}", self.rpy2Modules, path=self.transition_dir)
        # returns probability matrix (9xn) of next ordinal state.
        prob_df = r_utils.predict_nnet(transition_model, self.rpy2Modules, pop, cols)
        return prob_df

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"marital_status_barplot_{self.year}.pdf"
        densities = pd.DataFrame(pop['marital_status'].value_counts(normalize=True))
        densities.columns = ['densities']
        densities['marital_status'] = densities.index
        f = plt.figure()
        cat = catplot(data=densities, y='marital_status', x='densities', kind='bar', orient='h')
        plt.savefig(file_name)
        plt.close()
