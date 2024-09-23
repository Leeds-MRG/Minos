"""
Module for mwb in Minos.
Calculation of change in SF12
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
from seaborn import histplot
import matplotlib.pyplot as plt
import numpy as np
import logging
from scipy.stats import skew


class MWB(Base):
    """Mental Well-Being Module"""

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'mwb'

    def __repr__(self):
        return "MWB()"

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
        view_columns = ['pidp',
                        'sex',
                        'ethnicity',
                        'age',
                        'education_state',
                        'S7_labour_state',
                        'job_sec',
                        'hh_income',
                        'SF_12',
                        'housing_quality',
                        'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness',
                        'SF_12_diff']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        # builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

    def on_initialize_simulants(self, pop_data):
        """  Initiate columns for SF_12 when new simulants are added.
        Only column needed is the diff column for rate of change model predictions.

        Parameters
        ----------
            pop_data: vivarium.framework.population.SimulantData
            Custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """
        # Create frame with new 3 columns and add it to the main population frame.
        # This is the same for both new cohorts and newborn babies.
        # Neither should be dead yet.
        pop_update = pd.DataFrame({'SF_12_diff': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        logging.info("MENTAL WELLBEING (SF12 MCS)")

        self.year = event.time.year

        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")

        ## Predict next income value
        newWaveMWB = self.calculate_mwb(pop)
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=['SF_12'])
        # newWaveMWB = newWaveMWB.rename(columns={"new_dependent": "SF_12",
        #                                         "predicted": "SF_12_diff"})
        # newWaveMWB = newWaveMWB.to_frame(name='SF_12')
        # Set index type to int (instead of object as previous)
        newWaveMWB.index = pop.index
        SF_12sd = np.std(newWaveMWB["SF_12"])
        #add noise to force variance to 100.
        newWaveMWB['SF_12'] += self.generate_gaussian_noise(newWaveMWB.index, 0, 10/SF_12sd)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income

        self.population_view.update(newWaveMWB['SF_12'])

    def calculate_mwb(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # year can only be 2017 as its the only year with data for all vars
        year = 2017
        transition_model = r_utils.load_transitions(f"SF_12/ols/SF_12_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)

        return r_utils.predict_next_timestep_ols(transition_model,
                                                      self.rpy2Modules,
                                                      pop,
                                                      'SF_12')

    def calculate_mwb_rateofchange(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # year can only be 2017 as its the only year with data for all vars
        year = 2017
        transition_model = r_utils.load_transitions(f"SF_12/ols_diff/SF_12_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)

        return r_utils.predict_next_timestep_ols_diff(transition_model,
                                                 self.rpy2Modules,
                                                 pop,
                                                 'SF_12',
                                                 year=self.year)

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"mwb_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="SF_12", stat='density')
        plt.savefig(file_name)
        plt.close('all')


class geeMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'geeMWB'

    def __repr__(self):
        return "geeMWB()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

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
                        'education_state',
                        'labour_state',
                        'job_sec',
                        'hh_income',
                        'SF_12',
                        'housing_quality',
                        'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        self.max_sf12 = None
        #only need to load this once for now.
        self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee/SF_12_GEE", self.rpy2Modules)

    def update_prediction_population(self, current_pop):
        """ Update longitudinal data frame of past observations with current information.

        Remove those not alive and sort by pidp and time so gee R model can read it.

        Parameters
        ----------
        current_pop

        Returns
        -------

        """
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
        if self.max_sf12 == None:
            self.max_sf12 = np.max(pop["SF_12"])
            self.SF12_std = np.std(pop["SF_12"])

        ## Predict next income value
        newWaveMWB = self.calculate_mwb(pop)
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=["SF_12"])
        # Set index type to int (instead of object as previous)
        newWaveMWB.index = pop.index

        SF12_mean = np.mean(newWaveMWB["SF_12"])
        # scale SF12 to have standard deviation 10.
        newWaveMWB['SF_12'] += self.generate_gaussian_noise(newWaveMWB.index, 0, (self.SF12_std/np.std(newWaveMWB["SF_12"]))**2)

        #print(np.mean(newWaveMWB["SF_12"]))
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveMWB['SF_12'])


    def calculate_mwb(self, pop):
        """Calculate income transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        year = min(self.year, 2018)
        return self.max_sf12 - r_utils.predict_next_timestep_gee(self.gee_transition_model, self.rpy2Modules, pop, 'SF_12')



class geeYJMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'gee_yj_mwb'

    def __repr__(self):
        return "geeYJMWB()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

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
                        #'education_state',
                        'labour_state',
                        #'job_sec',
                        'hh_income',
                        'SF_12',
                        'housing_quality',
                        #'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness']

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        #only need to load this once for now.
        self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj/SF_12_GEE_YJ", self.rpy2Modules, path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj_gamma/SF_12_GEE_YJ_GAMMA", self.rpy2Modules, path=self.transition_dir)
        self.history_data = self.generate_history_dataframe("final_US", [2014, 2017, 2020], view_columns)

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

        # Predict next mwb value
        newWaveMWB = self.calculate_mwb(pop)
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=["SF_12"])
        newWaveMWB.index = pop.index # aligning index to vivarium builder dataframe. ensures assignment of new values to correct individuals.
        #newWaveMWB["SF_12"] -= 2
        newWaveMWB["SF_12"] = np.clip(newWaveMWB["SF_12"], 0, 100) # keep within [0, 100] bounds of SF12.
        #newWaveMWB.sort_index(inplace=True)
        print(np.mean(newWaveMWB["SF_12"]))

        # Update population with new income
        self.population_view.update(newWaveMWB['SF_12'])


    def calculate_mwb(self, pop):
        """Calculate income transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        self.update_history_dataframe(pop, self.year, lag=10)
        out_data = r_utils.predict_next_timestep_yj_gaussian_gee(self.gee_transition_model,
                                                                 self.rpy2Modules,
                                                                 current=self.history_data,
                                                                 dependent='SF_12',
                                                                 reflect=True,
                                                                 noise_std= 0.85)#1
        return out_data.iloc[self.history_data.loc[self.history_data['time'] == self.year].index]


class lmmYJMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmm_yj_mwb'

    def __repr__(self):
        return "lmmYJMWB()"

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
        view_columns = ["time",
                        "age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        "housing_quality",
                        "neighbourhood_safety",
                        "loneliness",
                        "nutrition_quality",
                        "ncigs",
                        'SF_12',
                        'SF_12_diff',
                        'pidp',
                        'hh_income'
                        ]

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # only need to load this once for now.
        self.lmm_transition_model = r_utils.load_transitions(f"SF_12/lmm/SF_12_LMM",
                                                             self.rpy2Modules,
                                                             path=self.transition_dir)
        self.lmm_transition_model = r_utils.randomise_fixed_effects(self.lmm_transition_model,
                                                                    self.rpy2Modules,
                                                                    "lmm",
                                                                    seed=self.run_seed)
        # self.gee_transition_model = r_utils.load_transitions(f"SF_12_MCS/glmm/SF_12_MCS_GLMM", self.rpy2_modules, path=self.transition_dir)

        # LA 24/6/24
        # self.rf_transition_model = r_utils.load_transitions(f"SF_12/rf/SF_12_RF",
        #                                                     self.rpy2Modules,
        #                                                     path=self.transition_dir)

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
        pop = pop.sort_values('pidp')  # sorting aligns index to make sure individual gets their correct prediction.
        pop["SF_12_last"] = pop["SF_12"]

        # Predict next mwb value
        newWaveMWB = pd.DataFrame(columns=['SF_12'])
        newWaveMWB['SF_12'] = self.calculate_mwb(pop)
        newWaveMWB.index = pop.index
        # newWaveMWB["SF_12"] -= 1

        sf12_mean_old = np.mean(pop['SF_12_last'])
        sf12_mean_new = np.mean(newWaveMWB["SF_12"])
        std_ratio = (np.std(pop['SF_12']) / np.std(newWaveMWB["SF_12"]))
        newWaveMWB["SF_12"] *= std_ratio
        newWaveMWB["SF_12"] -= ((std_ratio - 1) * sf12_mean_new)

        # newWaveMWB["SF_12"] -= 1.5
        #newWaveMWB["SF_12"] += (47.6 - np.mean(newWaveMWB["SF_12"]))
        newWaveMWB["SF_12"] += (sf12_mean_old - np.mean(newWaveMWB["SF_12"]))
        newWaveMWB["SF_12"] = np.clip(newWaveMWB["SF_12"], 0, 100)  # keep within [0, 100] bounds of SF12.

        newWaveMWB["SF_12_diff"] = newWaveMWB["SF_12"] - pop["SF_12"]

        self.population_view.update(newWaveMWB[['SF_12', "SF_12_diff"]])

    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # out_data = r_utils.predict_next_timestep_yj_gamma_glmm(self.transition_model,
        #                                                        self.rpy2Modules,
        #                                                        current= pop,
        #                                                        dependent='SF_12',
        #                                                        reflect=True,
        #                                                        yeo_johnson= True,
        #                                                        noise_std= 0.1)# 5 for non yj, 0.35 for yj

        nextWaveMWB = r_utils.predict_next_timestep_yj_gaussian_lmm(self.lmm_transition_model,
                                                                    self.rpy2Modules,
                                                                    pop,
                                                                    dependent='SF_12',
                                                                    reflect=True,
                                                                    log_transform=True,
                                                                    noise_std=3,
                                                                    seed=self.run_seed)  #

        # nextWaveMWB = r_utils.predict_next_rf(self.rf_transition_model,
        #                                       self.rpy2Modules,
        #                                       pop,
        #                                       dependent='SF_12',
        #                                       seed=self.run_seed)

        return nextWaveMWB


class RFDiffMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'rf_diff_mwb'

    def __repr__(self):
        return "RFDiffMWB()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ["time",
                        "age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        "housing_quality",
                        "neighbourhood_safety",
                        "loneliness",
                        "nutrition_quality",
                        "ncigs",
                        'SF_12',
                        'SF_12_diff',
                        'pidp',
                        'hh_income'
                        ]

        #columns_created = ["SF_12_diff"]
        self.population_view = builder.population.get_view(columns=view_columns)  # columns_created

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants)  # , creates_columns=columns_created

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # only need to load this once for now.
        self.rf_transition_model = r_utils.load_transitions(f"SF_12/rf_diff/SF_12_diff_RF_DIFF", self.rpy2Modules, path=self.transition_dir)

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

        pop['SF_12_last'] = pop['SF_12']
        pop['SF_12_diff_last'] = pop['SF_12_diff']

        # Predict next mwb value
        newWaveMWB = pd.DataFrame(columns=['SF_12', 'SF_12_diff'])
        newWaveMWB['SF_12_diff'] = self.calculate_mwb(pop)
        newWaveMWB.index = pop.index
        newWaveMWB['SF_12'] = pop['SF_12'] + newWaveMWB['SF_12_diff']

        # clip to reasonable bounds
        newWaveMWB["SF_12"] = np.clip(newWaveMWB["SF_12"], 0, 80)  # keep within [0, 100] bounds of SF12.
        # Recalculate SF_12_diff after clipping
        newWaveMWB["SF_12_diff"] = newWaveMWB["SF_12"] - pop["SF_12"]

        # Update population with new SF12
        print(np.mean(newWaveMWB["SF_12"]))
        self.population_view.update(newWaveMWB[['SF_12', 'SF_12_diff']])

    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        #self.update_history_dataframe(pop, self.year, lag=10)
        # out_data = r_utils.predict_next_timestep_yj_gaussian_lmm(self.gee_transition_model,
        #                                                          self.rpy2Modules,
        #                                                          current= pop,
        #                                                          dependent='SF_12_diff',
        #                                                          reflect=False,
        #                                                          yeo_johnson=True,
        #                                                          noise_std= 0.35)#1

        out_data = r_utils.predict_next_rf(self.rf_transition_model,
                                           self.rpy2Modules,
                                           pop,
                                           dependent='SF_12_diff',
                                           seed=self.run_seed,
                                           noise=5)

        #return out_data.iloc[self.history_data.loc[self.history_data['time'] == self.year].index]
        return out_data


class lmmDiffMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmm_diff_mwb'

    def __repr__(self):
        return "lmmDiffMWB()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

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
                        #'education_state',
                        'labour_state',
                        #'job_sec',
                        'hh_income',
                        'SF_12',
                        'housing_quality',
                        #'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness']

        columns_created = ["SF_12_diff"]
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        #only need to load this once for now.
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj/SF_12_GEE_YJ", self.rpy2Modules, path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj_gamma/SF_12_GEE_YJ_GAMMA", self.rpy2Modules, path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"SF_12/lmm_diff/SF_12_LMM_DIFF", self.rpy2Modules, path=self.transition_dir)
        #self.history_data = self.generate_history_dataframe("final_US", [2014, 2017, 2020], view_columns)

    def on_initialize_simulants(self, pop_data):
        """  Initiate columns for hh_income when new simulants are added.
        Only column needed is the diff column for rate of change model predictions.

        Parameters
        ----------
            pop_data: vivarium.framework.population.SimulantData
            Custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """
        # Create frame with new 3 columns and add it to the main population frame.
        # This is the same for both new cohorts and newborn babies.
        # Neither should be dead yet.
        pop_update = pd.DataFrame({'SF_12_diff': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

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

        # Predict next mwb value
        newWaveMWB = pd.DataFrame(columns=['SF_12', 'SF_12_diff'])
        newWaveMWB['SF_12_diff'] = self.calculate_mwb(pop)
        newWaveMWB.index = pop.index
        newWaveMWB['SF_12'] = pop['SF_12'] + newWaveMWB['SF_12_diff']

        # newWaveMWB = newWaveMWB.rename(columns={"new_dependent": "SF_12",
        #                                               "predicted": "SF_12_diff"})
        # newWaveMWB = newWaveMWB.to_frame(name='SF_12')
        # Set index back to population of interest.

        # Update population with new SF12
        print(np.mean(newWaveMWB["SF_12"]))
        self.population_view.update(newWaveMWB[['SF_12', 'SF_12_diff']])


    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        #self.update_history_dataframe(pop, self.year, lag=10)
        out_data = r_utils.predict_next_timestep_yj_gaussian_lmm(self.gee_transition_model,
                                                                 self.rpy2Modules,
                                                                 current= pop,
                                                                 dependent='SF_12_diff',
                                                                 reflect=False,
                                                                 yeo_johnson=True,
                                                                 noise_std= 0.35)#1
        #return out_data.iloc[self.history_data.loc[self.history_data['time'] == self.year].index]
        return out_data


class MarsMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'mars_mwb'

    def __repr__(self):
        return "MarsMWB()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ["time",
                        "age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        "housing_quality",
                        "neighbourhood_safety",
                        "loneliness",
                        "nutrition_quality",
                        "ncigs",
                        'SF_12',
                        'SF_12_diff',
                        'pidp',
                        'hh_income'
                        ]

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # only need to load this once for now.
        self.transition_model = r_utils.load_transitions(f"SF_12/mars/SF_12_MARS",
                                                         self.rpy2Modules,
                                                         path=self.transition_dir)

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
        pop = pop.sort_values('pidp')  # sorting aligns index to make sure individual gets their correct prediction.
        pop["SF_12_last"] = pop["SF_12"]

        # Predict next mwb value
        newWaveMWB = pd.DataFrame(columns=['SF_12'])
        newWaveMWB['SF_12'] = self.calculate_mwb(pop)
        newWaveMWB.index = pop.index

        newWaveMWB["SF_12"] = np.clip(newWaveMWB["SF_12"], 0, 100)  # keep within [0, 100] bounds of SF12.

        newWaveMWB["SF_12_diff"] = newWaveMWB["SF_12"] - pop["SF_12"]

        self.population_view.update(newWaveMWB[['SF_12', "SF_12_diff"]])

    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        nextWaveMWB = r_utils.predict_next_MARS(model=self.transition_model,
                                                rpy2_modules=self.rpy2Modules,
                                                current=pop,
                                                dependent='SF_12',
                                                seed=self.run_seed,
                                                noise_gauss=3,
                                                noise_cauchy=0.3)

        return nextWaveMWB


class RFMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'rf_mwb'

    def __repr__(self):
        return "RFMWB()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ["time",
                        "age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        "housing_quality",
                        "neighbourhood_safety",
                        "loneliness",
                        "nutrition_quality",
                        "ncigs",
                        'SF_12',
                        'SF_12_diff',
                        'pidp',
                        'hh_income'
                        ]

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # only need to load this once for now.
        self.transition_model = r_utils.load_transitions(f"SF_12/rf/SF_12_RF",
                                                         self.rpy2Modules,
                                                         path=self.transition_dir)

    def on_time_step(self, event):
        """
        Produces new children and updates parent status on time steps.
        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        self.year = event.time.year
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop = pop.sort_values('pidp')  # sorting aligns index to make sure individual gets their correct prediction.
        pop["SF_12_last"] = pop["SF_12"]

        # Predict next mwb value
        newWaveMWB = pd.DataFrame(columns=['SF_12'])
        newWaveMWB['SF_12'] = self.calculate_mwb(pop)
        newWaveMWB.index = pop.index

        newWaveMWB["SF_12"] = np.clip(newWaveMWB["SF_12"], 0, 100)  # keep within [0, 100] bounds of SF12.

        newWaveMWB["SF_12_diff"] = newWaveMWB["SF_12"] - pop["SF_12"]

        self.population_view.update(newWaveMWB[['SF_12', "SF_12_diff"]])

    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            pop :
        Returns
        -------
        """
        nextWaveMWB = r_utils.predict_next_rf(self.transition_model,
                                                 self.rpy2Modules,
                                                 pop,
                                                 dependent='SF_12',
                                                 seed=self.run_seed,
                                                 noise_gauss=0,
                                                 noise_cauchy=0)

        return nextWaveMWB


# Define the function to adjust skewness
def adjust_skewness(new_wave_data, target_skew):
    current_skew = skew(new_wave_data)
    std_dev = np.std(new_wave_data)
    mean_income = np.mean(new_wave_data)

    # Calculate beta for cubic transformation
    beta = (target_skew - current_skew) / (3 * (std_dev ** 3))

    # Apply cubic transformation
    adjusted_income = new_wave_data + beta * (new_wave_data - mean_income) ** 3

    return adjusted_income


# Function to scale variance by quintile
# def scale_variance_by_quintile(new_data, old_data, column_name):
#     # Create a column for quintile labels
#     new_data['quintile'] = pd.qcut(new_data[column_name], q=5, labels=False)
#
#     old_var_name = column_name + '_last'
#
#     # Process each quintile separately
#     for quintile in range(5):
#         # Get current quintile's data
#         current_quintile_data = new_data[new_data['quintile'] == quintile]
#         old_quintile_data = old_data[old_data[old_var_name].between(
#             old_data[old_var_name].quantile(quintile * 0.2),
#             old_data[old_var_name].quantile((quintile + 1) * 0.2),
#             inclusive='left'  # 'left' to match the behavior of qcut
#         )]
#
#         # If there's no data in this quintile in the old data, skip
#         if old_quintile_data.empty:
#             continue
#
#         # Calculate income mean for the current quintile
#         income_mean = np.mean(current_quintile_data[column_name])
#
#         # Calculate change in standard deviation between waves for the current quintile
#         std_ratio = np.std(old_quintile_data[old_var_name]) / np.std(current_quintile_data[column_name])
#
#         # Rescale income to have the new mean but keep the old standard deviation
#         new_data.loc[new_data['quintile'] == quintile, column_name] *= std_ratio
#         new_data.loc[new_data['quintile'] == quintile, column_name] -= ((std_ratio - 1) * income_mean)
#
#     # Drop the quintile column
#     new_data.drop(columns=['quintile'], inplace=True)
#
#     return new_data


# Function to scale variance by quintile
def scale_variance_by_quintile(new_data, old_data, column_name, old_column_name):
    # Create quintile labels for both new and old datasets
    new_data['quintile'] = pd.qcut(new_data[column_name], q=5, labels=False)
    old_data['quintile'] = pd.qcut(old_data[old_column_name], q=5, labels=False)

    # Process each quintile separately
    for quintile in range(5):
        # Get current quintile's data for both new and old datasets
        current_quintile_data = new_data[new_data['quintile'] == quintile][column_name]
        old_quintile_data = old_data[old_data['quintile'] == quintile][old_column_name]

        # Calculate income mean for the current quintile
        income_mean = np.mean(current_quintile_data)

        # Calculate change in standard deviation between waves for the current quintile
        std_ratio = np.std(old_quintile_data) / np.std(current_quintile_data)

        # Rescale income to have the new mean but keep the old standard deviation
        new_data.loc[new_data['quintile'] == quintile, column_name] *= std_ratio
        new_data.loc[new_data['quintile'] == quintile, column_name] -= ((std_ratio - 1) * income_mean)

    # Drop the quintile column
    new_data.drop(columns=['quintile'], inplace=True)
    old_data.drop(columns=['quintile'], inplace=True)

    return new_data


class XGBMWB(Base):
    """Mental Well-Being Module"""
    # Special methods used by vivarium.
    @property
    def name(self):
        return 'xgb_mwb'

    def __repr__(self):
        return "XGBMWB()"

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
        self.rpy2Modules = builder.data.load("rpy2_modules")

        # Build vivarium objects for calculating transition probabilities.
        # Typically this is registering rate/lookup tables. See vivarium docs/other modules for examples.
        #self.transition_coefficients = builder.

        # Assign randomness streams if necessary.
        self.random = builder.randomness.get_stream(self.generate_random_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        view_columns = ["time",
                        "age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        "housing_quality",
                        "neighbourhood_safety",
                        "loneliness",
                        "nutrition_quality",
                        "ncigs",
                        'SF_12',
                        'SF_12_diff',
                        'pidp',
                        'hh_income'
                        ]

        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # only need to load this once for now.
        self.transition_model = r_utils.load_transitions(f"SF_12/xgb/SF_12_XGB",
                                                         self.rpy2Modules,
                                                         path=self.transition_dir)

    def on_time_step(self, event):
        """
        Produces new children and updates parent status on time steps.
        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        self.year = event.time.year
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop = pop.sort_values('pidp')  # sorting aligns index to make sure individual gets their correct prediction.
        pop["SF_12_last"] = pop["SF_12"]

        # Predict next mwb value
        newWaveMWB = pd.DataFrame(columns=['SF_12'])
        newWaveMWB['SF_12'] = self.calculate_mwb(pop)
        newWaveMWB.index = pop.index

        ## SCALING FIX FOR CHILD POV INTERVENTIONS??
        # Instead of scaling the whole pop at once, lets scale by quintile to maintain the variance of higher quintiles
        # This is especially important in interventions that target small groups, and especially especially so in
        # interventions that have fixed thresholds (like child pov reduction)

        # Apply the scaling function
        #newWaveMWB = scale_variance_by_quintile(newWaveMWB, pop, 'SF_12')

        # scaling
        #sf12_mean_old = np.mean(pop['SF_12_last'])
        sf12_mean_new = np.mean(newWaveMWB["SF_12"])
        std_ratio = (np.std(pop['SF_12']) / np.std(newWaveMWB["SF_12"]))
        #std_ratio = (10.9 / np.std(newWaveMWB["SF_12"]))
        #std_ratio = (11 / np.std(newWaveMWB["SF_12"]))
        newWaveMWB["SF_12"] *= std_ratio
        newWaveMWB["SF_12"] -= ((std_ratio - 1) * sf12_mean_new)
        # newWaveMWB["SF_12"] += (sf12_mean_old - np.mean(newWaveMWB["SF_12"]))

        newWaveMWB["SF_12"] = np.clip(newWaveMWB["SF_12"], 0, 100)  # keep within [0, 100] bounds of SF12.

        newWaveMWB["SF_12_diff"] = newWaveMWB["SF_12"] - pop["SF_12"]

        self.population_view.update(newWaveMWB[['SF_12', "SF_12_diff"]])

    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            pop :
        Returns
        -------
        """
        nextWaveMWB = r_utils.predict_next_xgb(self.transition_model,
                                               self.rpy2Modules,
                                               pop,
                                               dependent='SF_12',
                                               seed=self.run_seed,
                                               log_transform=False,
                                               reflect=False,
                                               noise_gauss=0,
                                               noise_cauchy=0)

        return nextWaveMWB
