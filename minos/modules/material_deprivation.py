"""
Module for material deprivation in Minos.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
from seaborn import histplot
import matplotlib.pyplot as plt
import numpy as np
import logging


class MaterialDeprivation(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'material_deprivation'

    def __repr__(self):
        return "MaterialDeprivation()"

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
        self.rpy2_modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ['pidp',
                        'sex',
                        'ethnicity',
                        'age',
                        'time',
                        'region',
                        'education_state',
                        'hh_income',
                        'SF_12_MCS',
                        'SF_12_MCS_diff',
                        'SF_12_PCS',
                        'SF_12_PCS_diff',
                        'marital_status',
                        'hhsize',
                        'housing_tenure',
                        'urban',
                        'financial_situation',
                        'matdep',
                        'matdep_diff',
                        'weight']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=5)

        #only need to load this once for now.
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/lmm/SF_12_LMM", self.rpy2_modules, path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"matdep/glmmb/matdep_GLMMB", self.rpy2_modules, path=self.transition_dir)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.
        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        self.year = event.time.year
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop = pop.sort_values('pidp') #sorting aligns index to make sure individual gets their correct prediction.
        pop["matdep_last"] = pop["matdep"]

        # Predict next mwb value
        newWaveMatdep = pd.DataFrame(columns=['matdep'])
        newWaveMatdep['matdep'] = self.calculate_mwb(pop)
        newWaveMatdep.index = pop.index
        #newWaveMatdep["matdep"] -= 1

        sf12_mean = np.mean(newWaveMatdep["matdep"])
        std_ratio = (11/np.std(newWaveMatdep["matdep"]))
        newWaveMatdep["matdep"] *= (11/np.std(newWaveMatdep["matdep"]))
        newWaveMatdep["matdep"] -= ((std_ratio-1)*sf12_mean)
        newWaveMatdep["matdep"] -= 1.5
        #newWaveMatdep["matdep"] += (50 - np.mean(newWaveMatdep["SF_12_MCS"]))
        newWaveMatdep["matdep"] = np.clip(newWaveMatdep["matdep"], 0, 1) # keep within [0, 100] bounds of SF12.
        newWaveMatdep["matdep_diff"] = newWaveMatdep["matdep"] - pop["matdep"]
        # Update population with new SF12_MCS
        #print(np.mean(newWaveMatdep["matdep"]))
        #print(np.std(newWaveMatdep["matdep"]))
        self.population_view.update(newWaveMatdep[['matdep', "matdep_diff"]])


    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        out_data = r_utils.predict_next_timestep_yj_gamma_glmm(self.gee_transition_model,
                                                               self.rpy2_modules,
                                                               current= pop,
                                                               dependent='matdep',
                                                               reflect=False,
                                                               yeo_johnson= False,
                                                               mod_type='beta',
                                                               noise_std= 5)  # 5 for non yj, 0.35 for yj
        return out_data