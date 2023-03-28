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

class Labour(Base):
    # Special methods used by vivarium.
    @property
    def name(self):
        return 's7labour'

    def __repr__(self):
        return "S7Labour()"

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
                        "S7_labour_state",
                        "ethnicity",
                        "age",
                        'region',
                        "hh_income",
                        "education_state",
                        "S7_physical_health",
                        'S7_mental_health']

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

        #TODO: Handle students properly now that max education is predicted.
        # Separate the population into current students and everyone else. Then see if students max_educ is larger than
        # current education_state, if yes maintain student, if no predict new labour_state

        pop = self.population_view.get(event.index, query="alive=='alive'")
        self.year = event.time.year

        labour_prob_df = self.calculate_labour(pop)

        labour_prob_df["S7_labour_state"] = self.random.choice(labour_prob_df.index, list(labour_prob_df.columns), labour_prob_df)
        labour_prob_df.index = labour_prob_df.index.astype(int)

        self.population_view.update(labour_prob_df["S7_labour_state"])


    def calculate_labour(self, pop):
        """Calculate labour transition distribution based on provided people/indices.

        Parameters
        ----------
            pop : pd.DataFrame
                The population dataframe.
        Returns
        -------
        """
        # set up list of columns
        cols = ['FT Employed', 'PT Employed', 'Job Seeking', 'FT Education', 'Family Care', 'Not Working']

        # load transition model based on year.
        year = min(self.year, 2018) # TODO just use latest model for now. Needs some kind of reweighting if extrapolating later.
        transition_model = r_utils.load_transitions(f"S7_labour_state/nnet/S7_labour_state_nnet_{year}_{year+1}", self.rpy2Modules, path=self.transition_dir)
        # returns probability matrix (9xn) of next ordinal state.
        prob_df = r_utils.predict_nnet(transition_model, self.rpy2Modules, pop, cols)
        return prob_df

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"S7_labour_state_barplot_{self.year}.pdf"
        densities = pd.DataFrame(pop['S7_labour_state'].value_counts(normalize=True))
        densities.columns = ['densities']
        densities['S7_labour_state'] = densities.index
        f = plt.figure()
        cat = catplot(data=densities, y='S7_labour_state', x='densities', kind='bar', orient='h')
        plt.savefig(file_name)
        plt.close()
