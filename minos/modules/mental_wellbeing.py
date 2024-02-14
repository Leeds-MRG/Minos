"""
Module for SF_12_MCS in Minos.
Calculation of next mental wellbeing state
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
from seaborn import histplot
import matplotlib.pyplot as plt
import numpy as np
import logging


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
                        'SF_12_MCS',
                        'housing_quality',
                        'phealth',
                        'ncigs',
                        'nutrition_quality',
                        'neighbourhood_safety',
                        'loneliness',
                        'SF_12_diff',
                        'financial_situation',
                        'active']

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
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=["SF_12_MCS"])
        # newWaveMWB = newWaveMWB.rename(columns={"new_dependent": "SF_12_MCS",
        #                                         "predicted": "SF_12_MCS_diff"})
        # newWaveMWB = newWaveMWB.to_frame(name='SF_12_MCS')
        # Set index type to int (instead of object as previous)
        newWaveMWB.index = pop.index
        SF_12sd = np.std(newWaveMWB["SF_12"])
        #add noise to force variance to 100.
        newWaveMWB['SF_12'] += self.generate_gaussian_noise(newWaveMWB.index, 0, 10/SF_12sd)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveMWB['SF_12_MCS'])

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
        transition_model = r_utils.load_transitions(f"SF_12_MCS/ols/SF_12_MCS_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)

        return r_utils.predict_next_timestep_ols(transition_model,
                                                      self.rpy2Modules,
                                                      pop,
                                                      'SF_12_MCS')

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
        transition_model = r_utils.load_transitions(f"SF_12_MCS/ols_diff/SF_12_MCS_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)

        return r_utils.predict_next_timestep_ols_diff(transition_model,
                                                      self.rpy2Modules,
                                                      pop,
                                                      'SF_12_MCS',
                                                      year=self.year)

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"mwb_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="SF_12_MCS", stat='density')
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
        self.gee_transition_model = r_utils.load_transitions(f"SF_12_MCS/gee/SF_12_MCS_GEE", self.rpy2_modules)

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
        if self.max_sf12_MCS == None:
            self.max_sf12_MCS = np.max(pop["SF_12_MCS"])
            self.SF12_MCS_std = np.std(pop["SF_12_MCS"])

        ## Predict next income value
        newWaveMWB = self.calculate_mwb(pop)
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=["SF_12_MCS"])
        # Set index type to int (instead of object as previous)
        newWaveMWB.index = pop.index

        SF12_MCS_mean = np.mean(newWaveMWB["SF_12_MCS"])
        # scale SF12 to have standard deviation 10.
        newWaveMWB['SF_12_MCS'] += self.generate_gaussian_noise(newWaveMWB.index, 0, (self.SF12_MCS_std/np.std(newWaveMWB["SF_12_MCS"]))**2)

        #print(np.mean(newWaveMWB["SF_12_MCS"]))
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveMWB['SF_12_MCS'])


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
        return self.max_sf12_MCS - r_utils.predict_next_timestep_gee(self.gee_transition_model, self.rpy2_modules, pop, 'SF_12_MCS')



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
                        #'education_state',
                        'labour_state',
                        #'job_sec',
                        'hh_income',
                        'SF_12_MCS',
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
        self.gee_transition_model = r_utils.load_transitions(f"SF_12_MCS/gee_yj/SF_12_MCS_GEE_YJ", self.rpy2_modules, path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj_gamma/SF_12_GEE_YJ_GAMMA", self.rpy2_modules, path=self.transition_dir)
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
        newWaveMWB = pd.DataFrame(newWaveMWB, columns=["SF_12_MCS"])
        newWaveMWB.index = pop.index # aligning index to vivarium builder dataframe. ensures assignment of new values to correct individuals.
        #newWaveMWB["SF_12_MCS"] -= 2
        newWaveMWB["SF_12_MCS"] = np.clip(newWaveMWB["SF_12_MCS"], 0, 100) # keep within [0, 100] bounds of SF12.
        #newWaveMWB.sort_index(inplace=True)
        print(np.mean(newWaveMWB["SF_12_MCS"]))

        # Update population with new income
        self.population_view.update(newWaveMWB['SF_12_MCS'])


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
                                                                 self.rpy2_modules,
                                                                 current=self.history_data,
                                                                 dependent='SF_12_MCS',
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
                        'SF_12_MCS',
                        'SF_12_MCS_diff',
                        'pidp',
                        'hh_income',
                        'time'
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

        #only need to load this once for now.
        self.lmm_transition_model = r_utils.load_transitions(f"SF_12_MCS/lmm/SF_12_MCS_LMM", self.rpy2_modules, path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12_MCS/glmm/SF_12_MCS_GLMM", self.rpy2_modules, path=self.transition_dir)

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
        pop["SF_12_MCS_last"] = pop["SF_12_MCS"]

        # Predict next mwb value
        newWaveMWB = pd.DataFrame(columns=['SF_12_MCS'])
        newWaveMWB['SF_12_MCS'] = self.calculate_mwb(pop)
        newWaveMWB.index = pop.index
        #newWaveMWB["SF_12"] -= 1

        sf12_mean = np.mean(newWaveMWB["SF_12_MCS"])
        std_ratio = (11/np.std(newWaveMWB["SF_12_MCS"]))
        newWaveMWB["SF_12_MCS"] *= (11/np.std(newWaveMWB["SF_12_MCS"]))
        newWaveMWB["SF_12_MCS"] -= ((std_ratio-1)*sf12_mean)
        #newWaveMWB["SF_12_MCS"] -= 1.5
        #newWaveMWB["SF_12_MCS"] += (50 - np.mean(newWaveMWB["SF_12_MCS"]))
        #newWaveMWB["SF_12_MCS"] = np.clip(newWaveMWB["SF_12_MCS"], 0, 100) # keep within [0, 100] bounds of SF12.
        newWaveMWB["SF_12_MCS_diff"] = newWaveMWB["SF_12_MCS"] - pop["SF_12_MCS"]
        # Update population with new SF12_MCS
        #print(np.mean(newWaveMWB["SF_12_MCS"]))
        #print(np.std(newWaveMWB["SF_12_MCS"]))
        self.population_view.update(newWaveMWB[['SF_12_MCS', "SF_12_MCS_diff"]])


    def calculate_mwb(self, pop):
        """Calculate SF_12 transition distribution based on provided people/indices
        Parameters
        ----------
            index : pd.Index
                Which individuals to calculate transitions for.
        Returns
        -------
        """
        # nextWaveMWB = r_utils.predict_next_timestep_yj_gamma_glmm(self.gee_transition_model,
        #                                                        self.rpy2_modules,
        #                                                        current= pop,
        #                                                        dependent='SF_12_MCS',
        #                                                        reflect=True,
        #                                                        yeo_johnson= True,
        #                                                        noise_std= 0.1)  # 5 for non yj, 0.35 for yj

        nextWaveMWB = r_utils.predict_next_timestep_yj_gaussian_lmm(self.lmm_transition_model,
                                                                    self.rpy2_modules,
                                                                    pop,
                                                                    dependent='SF_12_MCS',
                                                                    log_transform=True,
                                                                    noise_std=0.025)  #

        return nextWaveMWB


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
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj/SF_12_GEE_YJ", self.rpy2_modules, path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"SF_12/gee_yj_gamma/SF_12_GEE_YJ_GAMMA", self.rpy2_modules, path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"SF_12/lmm_diff/SF_12_LMM_DIFF", self.rpy2_modules, path=self.transition_dir)
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
                                                                 self.rpy2_modules,
                                                                 current= pop,
                                                                 dependent='SF_12_diff',
                                                                 reflect=False,
                                                                 yeo_johnson=True,
                                                                 noise_std= 0.35)#1
        #return out_data.iloc[self.history_data.loc[self.history_data['time'] == self.year].index]
        return out_data