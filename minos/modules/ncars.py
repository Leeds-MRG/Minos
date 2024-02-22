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

class nCars(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'ncars'

    def __repr__(self):
        return "nCars()"

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
        self.random = builder.randomness.get_stream("ncars")

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
                        'job_sec',
                        'hh_income',
                        'SF_12',
                        "ncars",
                        "S7_labour_state",
                        'pidp',
                        'hidp'
                        ]
        #view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=6)
        self.transition_model = r_utils.load_transitions(f"ncars/mzip/ncars_new_MZIP", self.rpy2Modules, path=self.transition_dir)


    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        logging.info("ncars")

        # Get living people to update their tobacco
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop['ncars'] = pop['ncars'].clip(0, 10)
        pop['ncars_new'] = pop['ncars'] #dummy column
        self.year = event.time.year
        print(f"before ncars: {np.mean(pop['ncars'])}")

        # Predict next tobacco value
        newWaveNCars = pd.DataFrame(self.calculate_n_cars(pop))
        newWaveNCars.columns = ['ncars']
        newWaveNCars.index = pop.index

        non_zero_ncars = newWaveNCars.loc[newWaveNCars['ncars']>0, ]
        ncars_mean = np.mean(non_zero_ncars["ncars"])
        std_ratio = (np.std(pop.loc[pop['ncars']>0, 'ncars'])/np.std(non_zero_ncars['ncars']))
        non_zero_ncars["ncars"] *= std_ratio
        non_zero_ncars["ncars"] -= ((std_ratio-1)*ncars_mean)
        non_zero_ncars['ncars'] += 0.175
        newWaveNCars.loc[newWaveNCars['ncars']>0, 'ncars'] = non_zero_ncars['ncars']

        newWaveNCars['ncars'] = newWaveNCars['ncars'].clip(0, 10)
        newWaveNCars['hidp'] = pop['hidp']
        newWaveNCars['ncars'] = newWaveNCars.groupby(by=['hidp'])['ncars'].transform('mean')
        newWaveNCars['ncars'] = np.round(newWaveNCars['ncars']).astype(int) # switch back to ints. viv column takes float though..
        newWaveNCars['ncars'] = newWaveNCars['ncars'].astype(float)

        #newWaveNCars["ncars"] = newWaveNCars["ncars"].astype(int)
        # Draw individuals next states randomly from this distribution.
        # Update population with new tobacco
        print(f"ncars: {np.mean(newWaveNCars['ncars'])}")
        self.population_view.update(newWaveNCars["ncars"])

    def calculate_n_cars(self, pop):
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

        # The calculation relies on the R predict method and the model that has already been specified
        # nextWaveNCars = r_utils.predict_next_timestep_zip(model=transition_model,
        #                                                     rpy2Modules= self.rpy2Modules,
        #                                                     current=pop,
        #                                                     dependent='ncars_next')
        nextWaveNCars = r_utils.predict_next_timestep_mixed_zip(model=self.transition_model,
                                                          rpy2Modules= self.rpy2Modules,
                                                          current=pop,
                                                          dependent='ncars_new',
                                                          noise_std=0.25)
        return nextWaveNCars

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"ncars_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="ncigs", stat='density')
        plt.savefig(file_name)
        plt.close()
