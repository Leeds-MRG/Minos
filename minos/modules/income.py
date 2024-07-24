"""
Module for income in Minos.
Calculation of monthly household income
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import histplot
import numpy as np
import logging
from scipy.stats import skew


class Income(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'income'

    def __repr__(self):
        return "Income()"

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
        view_columns = ['pidp',
                        'age',
                        'sex',
                        'ethnicity',
                        'region',
                        'hh_income',
                        'job_sec',
                        'S7_labour_state',
                        'education_state',
                        'SF_12',
                        'housing_quality',
                        'job_sector']
        # view_columns += self.transition_model.rx2('model').names
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
        pop_update = pd.DataFrame({'hh_income_diff': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        logging.info("INCOME")

        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        self.year = event.time.year

        ## Predict next income value
        newWaveIncome = self.calculate_income(pop)
        newWaveIncome = pd.DataFrame(newWaveIncome, columns=['hh_income'])
        # newWaveIncome = newWaveIncome.rename(columns={"new_dependent": "hh_income",
        #                                               "predicted": "hh_income_diff"})
        # newWaveIncome = newWaveIncome.to_frame(name='hh_income')
        # Set index back to population of interest.
        newWaveIncome.index = pop.index

        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveIncome['hh_income'])

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        year = min(self.year, 2019)
        transition_model = r_utils.load_transitions(f"hh_income/ols/hh_income_{year}_{year + 1}", self.rpy2Modules,
                                                   path=self.transition_dir)
        nextWaveIncome = r_utils.predict_next_timestep_ols(transition_model,
                                                           self.rpy2Modules,
                                                           pop,
                                                           dependent='hh_income')
        return nextWaveIncome

    def calculate_income_rateofchange(self, pop):
        """Calculate income transition with rate of change (diff) models

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Dataframe
            Dataframe of new predicted hh_income value and difference from previous year.
        """
        # load transition model based on year.
        if self.cross_validation:
            # if cross-val, fix year to final year model
            year = 2019
        else:
            year = min(self.year, 2019)

        transition_model = r_utils.load_transitions(f"hh_income/ols_diff/hh_income_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)
        # The calculation relies on the R predict method and the model that has already been specified
        nextWaveIncome = r_utils.predict_next_timestep_ols(transition_model,
                                                                self.rpy2Modules,
                                                                pop,
                                                                dependent='hh_income',
                                                                year=self.year)
        return nextWaveIncome

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()


class geeIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'geeIncome'

    def __repr__(self):
        return "geeIncome()"

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
        view_columns = ['pidp',
                        'weight',
                        'age',
                        'sex',
                        'ethnicity',
                        'region',
                        'hh_income',
                        'job_sec',
                        'labour_state',
                        'education_state',
                        'SF_12',
                        'housing_quality',
                        'job_sector']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        # builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee/hh_income_GEE", self.rpy2Modules,
                                                         path=self.transition_dir)
        self.min_hh_income = None

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
            pop_update = pd.DataFrame({'hh_income_diff': 0},
                                      index=pop_data.index)
            self.population_view.update(pop_update)

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
        if self.min_hh_income == None:
            self.min_hh_income = np.min(pop["hh_income"])
            self.income_std = np.std(pop["hh_income"])

        ## Predict next income value
        newWaveIncome = self.calculate_income(pop)
        newWaveIncome = pd.DataFrame(newWaveIncome, columns=['hh_income'])
        # newWaveIncome = newWaveIncome.rename(columns={"new_dependent": "hh_income",
        #                                               "predicted": "hh_income_diff"})
        # newWaveIncome = newWaveIncome.to_frame(name='hh_income')
        # Set index back to population of interest.
        newWaveIncome.index = pop.index

        newWaveIncome['hh_income'] += self.generate_gaussian_noise(pop.index, 0, 1000)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveIncome['hh_income'])

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.

        nextWaveIncome = r_utils.predict_next_timestep_gee(self.gee_transition_model,
                                                           self.rpy2Modules,
                                                           pop,
                                                           dependent='hh_income')
        return nextWaveIncome + self.min_hh_income
    def calculate_income_rateofchange(self, pop):
        """Calculate income transition with rate of change (diff) models

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Dataframe
            Dataframe of new predicted hh_income value and difference from previous year.
        """
        # load transition model based on year.
        year = min(self.year, 2019)
        transition_model = r_utils.load_transitions(f"hh_income/ols/hh_income_{year}_{year + 1}",
                                                    self.rpy2Modules,
                                                    path=self.transition_dir)
        # The calculation relies on the R predict method and the model that has already been specified
        nextWaveIncome = r_utils.predict_next_timestep_ols(transition_model,
                                                           self.rpy2Modules,
                                                           pop,
                                                           dependent='hh_income',
                                                           year=self.year)
        return nextWaveIncome

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()


class geeYJIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'geeYJIncome'

    def __repr__(self):
        return "geeYJIncome()"

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
        #view_columns = ['pidp',
        #                'age',
        #                'sex',
        #                'ethnicity',
        #                'region',
        #                'hh_income',
        #                'job_sec',
        #                #'labour_state',
        #                'education_state',
        #                'SF_12',
        #                'weight',
        #                #'housing_quality',
        #                'job_sector']
        view_columns = [
            'hh_income',
            'age',
            'sex',
            'ethnicity',
            'region',
            'education_state',
            'job_sec',
            'job_sector',
            'time',
            'pidp',
            'weight'
        ]
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        # builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        #self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj/hh_income_GEE_YJ", self.rpy2Modules,
        #                                             path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj_gamma/hh_income_GEE_YJ_GAMMA", self.rpy2Modules,
                                                             path=self.transition_dir)
        self.history_data = self.generate_history_dataframe("final_US", [2018, 2019, 2020], view_columns)

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
        pop_update = pd.DataFrame({'hh_income_diff': 0},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop = pop.sort_values('pidp')
        self.year = event.time.year

        ## Predict next income value
        newWaveIncome = self.calculate_income(pop)
        newWaveIncome = pd.DataFrame(newWaveIncome, columns=['hh_income'])
        # newWaveIncome = newWaveIncome.rename(columns={"new_dependent": "hh_income",
        #                                               "predicted": "hh_income_diff"})
        # newWaveIncome = newWaveIncome.to_frame(name='hh_income')
        # Set index back to population of interest.
        newWaveIncome.index = pop.index

        #newWaveIncome['hh_income'] += self.generate_gaussian_noise(pop.index, 0, 1000)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveIncome['hh_income'])

    # def calculate_income(self, pop):
    #     """Calculate income transition distribution based on provided people/indices
    #
    #     Parameters
    #     ----------
    #         pop: PopulationView
    #             Population from MINOS to calculate next income for.
    #     Returns
    #     -------
    #     nextWaveIncome: pd.Series
    #         Vector of new household incomes from OLS prediction.
    #     """
    #     # load transition model based on year.
    #     #if self.year != 2020:
    #     self.update_history_dataframe(pop, self.year)
    #     nextWaveIncome = r_utils.predict_next_timestep_yj_gaussian_gee(self.gee_transition_model,
    #                                                        self.rpy2Modules,
    #                                                        self.history_data,
    #                                                        dependent='hh_income',
    #                                                        noise_std=1)#2
    #
    #     return nextWaveIncome.iloc[self.history_data.loc[self.history_data['time']==self.year].index]

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        #if self.year != 2020:
        self.update_history_dataframe(pop, self.year)
        nextWaveIncome = r_utils.predict_next_timestep_yj_gamma_gee(self.gee_transition_model,
                                                                       self.rpy2Modules,
                                                                       self.history_data,
                                                                       dependent='hh_income',
                                                                       reflect=False,
                                                                       noise_std=0.5)#2

        return nextWaveIncome.iloc[self.history_data.loc[self.history_data['time']==self.year].index]

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()


def select_random_income(group):
    random_income = np.random.choice(group['hh_income'])
    return group.assign(hh_income=random_income)


class lmmYJIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmYJIncome'

    def __repr__(self):
        return "lmmYJIncome()"

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
        self.random = builder.randomness.get_stream(self.generate_run_crn_key())

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module.
        # In this case, view_columns are taken straight from the transition model
        #view_columns = ['pidp',
        #                'age',
        #                'sex',
        #                'ethnicity',
        #                'region',
        #                'hh_income',
        #                'job_sec',
        #                #'labour_state',
        #                'education_state',
        #                'SF_12',
        #                'weight',
        #                #'housing_quality',
        #                'job_sector']
        view_columns = ["age",
                        "sex",
                        "ethnicity",
                        "region",
                        "education_state",
                        'job_sec',
                        'SF_12',
                        'pidp',
                        'hh_income',
                        'hh_income_diff',
                        'S7_labour_state',
                        'time',
                        'hidp',
                        'boost_amount'
                        ]


        #columns_created = ['hh_income_diff']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)# + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        #self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj/hh_income_GEE_YJ", self.rpy2Modules,
        #                                             path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_diff/hh_income_GEE_DIFF", self.rpy2Modules,
        #                                                     path=self.transition_dir)
        # self.transition_model = r_utils.load_transitions(f"hh_income/glmm/hh_income_GLMM", self.rpy2Modules,
        #                                                     path=self.transition_dir)
        # self.transition_model = r_utils.randomise_fixed_effects(self.transition_model, self.rpy2Modules, "glmm")
        self.transition_model = r_utils.load_transitions(f"hh_income/glmm/hh_income_GLMM", self.rpy2Modules,
                                                         path=self.transition_dir)
        self.transition_model = r_utils.randomise_fixed_effects(self.transition_model,
                                                                self.rpy2Modules,
                                                                "glmm",
                                                                seed=self.run_seed)
        #self.history_data = self.generate_history_dataframe("final_US", [2018, 2019], view_columns)
        #self.history_data["hh_income_diff"] = self.history_data['hh_income'] - self.history_data.groupby(['pidp'])['hh_income'].shift(1)

        # LA 24/6/24
        # self.rf_transition_model = r_utils.load_transitions(f"hh_income/rf/hh_income_RF",
        #                                                     self.rpy2Modules,
        #                                                     path=self.transition_dir)

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
        #pop_update = pd.DataFrame({'hh_income_diff': 0.},
        #                          index=pop_data.index)
        #self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        #pop = pop.sort_values('pidp')
        self.year = event.time.year

        # LA 5/7/24
        # If intervention is a reset intervention, remove boost amount from hh_income before predicting next
        if self.reset_income_intervention:
            pop['hh_income'] = pop['hh_income'] - pop['boost_amount']

        # dummy column to load new prediction into.
        pop['hh_income_last'] = pop['hh_income']

        ## Predict next income values
        newWaveIncome = pd.DataFrame(columns=['hh_income'])
        newWaveIncome['hh_income'] = self.calculate_income(pop)
        newWaveIncome.index = pop.index

        # Ensure whole household has equal hh_income by taking mean after prediction
        newWaveIncome['hidp'] = pop['hidp']
        newWaveIncome = newWaveIncome.groupby('hidp').apply(select_random_income).reset_index(drop=True)

        # calculate household income mean
        income_mean = np.mean(newWaveIncome["hh_income"])
        # calculate change in standard deviation between waves.
        std_ratio = (np.std(pop['hh_income_last'])/np.std(newWaveIncome["hh_income"]))
        # rescale income to have new mean but keep old standard deviation.
        newWaveIncome["hh_income"] *= std_ratio
        newWaveIncome["hh_income"] -= ((std_ratio-1)*income_mean)
        #newWaveIncome["hh_income"] -= 75

        # difference in hh income
        newWaveIncome['hh_income_diff'] = newWaveIncome['hh_income'] - pop['hh_income_last']

        self.population_view.update(newWaveIncome[['hh_income', 'hh_income_diff']])

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        nextWaveIncome = r_utils.predict_next_timestep_yj_gamma_glmm(self.transition_model,
                                                                     self.rpy2Modules,
                                                                     pop,
                                                                     dependent='hh_income',
                                                                     yeo_johnson=True,
                                                                     reflect=False,
                                                                     noise_std=0.175,
                                                                     seed=self.run_seed)  #0.45 for yj. 100? for non yj.

        # nextWaveIncome = r_utils.predict_next_timestep_yj_gaussian_lmm(self.transition_model,
        #                                                                self.rpy2Modules,
        #                                                                pop,
        #                                                                dependent='hh_income',
        #                                                                log_transform=False,
        #                                                                noise_std=100)

        # nextWaveIncome = r_utils.predict_next_rf(self.rf_transition_model,
        #                                          self.rpy2Modules,
        #                                          pop,
        #                                          dependent='hh_income',
        #                                          seed=self.run_seed)

        # get new hh income diffs and update them into history_data.
        #self.update_history_dataframe(pop, self.year-1)
        #new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        #next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveIncome

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()


class RFDiffIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'rfDiffIncome'

    def __repr__(self):
        return "RFDiffIncome()"

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
                        'job_sec',
                        'SF_12',
                        'pidp',
                        'hh_income',
                        'hh_income_diff',
                        'S7_labour_state',
                        'time',
                        'hidp'
                        ]
        #columns_created = ['hh_income_diff']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)  # columns_created

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)  # , creates_columns=columns_created

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        self.rf_transition_model = r_utils.load_transitions(f"hh_income/rf_diff/hh_income_diff_RF_DIFF",
                                                            self.rpy2Modules,
                                                            path=self.transition_dir)

    # def on_initialize_simulants(self, pop_data):
    #     """  Initiate columns for hh_income when new simulants are added.
    #     Only column needed is the diff column for rate of change model predictions.
    #
    #     Parameters
    #     ----------
    #         pop_data: vivarium.framework.population.SimulantData
    #         Custom vivarium class for interacting with the population data frame.
    #         It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
    #         creation_window, and current simulation state (setup/running/etc.).
    #     """
    #     # Create frame with new 3 columns and add it to the main population frame.
    #     # This is the same for both new cohorts and newborn babies.
    #     # Neither should be dead yet.
    #     pop_update = pd.DataFrame({'hh_income_diff': 0.},
    #                               index=pop_data.index)
    #     self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop = pop.sort_values('pidp')
        self.year = event.time.year

        pop['hh_income_last'] = pop['hh_income']
        pop['hh_income_diff_last'] = pop['hh_income_diff']

        #pop['hh_income_diff_last'] = pop['hh_income_diff']
        ## Predict next income value
        newWaveIncome = pd.DataFrame(columns=['hh_income', 'hh_income_diff'])
        newWaveIncome['hh_income_diff'] = self.calculate_income(pop)
        newWaveIncome.index = pop.index
        newWaveIncome['hh_income'] = pop['hh_income'] + newWaveIncome['hh_income_diff']

        # Ensure whole household has equal hh_income by taking mean after prediction
        newWaveIncome['hidp'] = pop['hidp']
        newWaveIncome = newWaveIncome.groupby('hidp').apply(select_random_income).reset_index(drop=True)

        #newWaveIncome['hh_income'] += self.generate_gaussian_noise(pop.index, 0, 1000)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        #print(f"Mean Income: {np.mean(newWaveIncome['hh_income'])}")
        self.population_view.update(newWaveIncome[['hh_income', 'hh_income_diff']])

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        # nextWaveIncome = r_utils.predict_next_timestep_yj_gaussian_lmm(self.gee_transition_model,
        #                                                             self.rpy2Modules,
        #                                                             pop,
        #                                                             dependent='hh_income_diff',
        #                                                             yeo_johnson = True,
        #                                                             reflect=False,
        #                                                             noise_std= 0.05)#0.45

        nextWaveIncome = r_utils.predict_next_rf(self.rf_transition_model,
                                                 self.rpy2Modules,
                                                 pop,
                                                 dependent='hh_income_diff',
                                                 seed=self.run_seed,
                                                 noise=150)

        # get new hh income diffs and update them into history_data.
        #self.update_history_dataframe(pop, self.year-1)
        #new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        #next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveIncome


class lmmDiffIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmDiffIncome'

    def __repr__(self):
        return "lmmDiffIncome()"

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
        #view_columns = ['pidp',
        #                'age',
        #                'sex',
        #                'ethnicity',
        #                'region',
        #                'hh_income',
        #                'job_sec',
        #                #'labour_state',
        #                'education_state',
        #                'SF_12',
        #                'weight',
        #                #'housing_quality',
        #                'job_sector']
        view_columns = [
            'hh_income',
            'age',
            'sex',
            'ethnicity',
            'region',
            'education_state',
            'job_sec',
            #'job_sector',
            'time',
            'pidp',
            'weight',
            #'hh_income_diff'
        ]
        columns_created = ['hh_income_diff']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        #self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj/hh_income_GEE_YJ", self.rpy2Modules,
        #                                             path=self.transition_dir)
        #self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_diff/hh_income_GEE_DIFF", self.rpy2Modules,
        #                                                     path=self.transition_dir)
        self.gee_transition_model = r_utils.load_transitions(f"hh_income/lmm_diff/hh_income_LMM_DIFF", self.rpy2Modules,
                                                             path=self.transition_dir)
        #self.history_data = self.generate_history_dataframe("final_US", [2018, 2019], view_columns)
        #self.history_data["hh_income_diff"] = self.history_data['hh_income'] - self.history_data.groupby(['pidp'])['hh_income'].shift(1)

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
        pop_update = pd.DataFrame({'hh_income_diff': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        pop = self.population_view.get(event.index, query="alive =='alive'")
        pop = pop.sort_values('pidp')
        self.year = event.time.year

        #pop['hh_income_diff_last'] = pop['hh_income_diff']
        ## Predict next income value
        newWaveIncome = pd.DataFrame(columns=['hh_income', 'hh_income_diff'])
        newWaveIncome['hh_income_diff'] = self.calculate_income(pop)
        newWaveIncome.index = pop.index
        newWaveIncome['hh_income'] = pop['hh_income'] + newWaveIncome['hh_income_diff']
        # newWaveIncome = newWaveIncome.rename(columns={"new_dependent": "hh_income",
        #                                               "predicted": "hh_income_diff"})
        # newWaveIncome = newWaveIncome.to_frame(name='hh_income')
        # Set index back to population of interest.

        #newWaveIncome['hh_income'] += self.generate_gaussian_noise(pop.index, 0, 1000)
        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        print("income", np.mean(newWaveIncome['hh_income']))
        self.population_view.update(newWaveIncome[['hh_income', 'hh_income_diff']])

    # def calculate_income(self, pop):
    #     """Calculate income transition distribution based on provided people/indices
    #
    #     Parameters
    #     ----------
    #         pop: PopulationView
    #             Population from MINOS to calculate next income for.
    #     Returns
    #     -------
    #     nextWaveIncome: pd.Series
    #         Vector of new household incomes from OLS prediction.
    #     """
    #     # load transition model based on year.
    #     #if self.year != 2020:
    #     self.update_history_dataframe(pop, self.year)
    #     nextWaveIncome = r_utils.predict_next_timestep_yj_gaussian_gee(self.gee_transition_model,
    #                                                        self.rpy2Modules,
    #                                                        self.history_data,
    #                                                        dependent='hh_income',
    #                                                        noise_std=1)#2
    #
    #     return nextWaveIncome.iloc[self.history_data.loc[self.history_data['time']==self.year].index]

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # load transition model based on year.
        nextWaveIncome = r_utils.predict_next_timestep_yj_gaussian_lmm(self.gee_transition_model,
                                                                    self.rpy2Modules,
                                                                    pop,
                                                                    dependent='hh_income_diff',
                                                                    yeo_johnson = True,
                                                                    reflect=False,
                                                                    noise_std= 0.05)#0.45
        # get new hh income diffs and update them into history_data.
        #self.update_history_dataframe(pop, self.year-1)
        #new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        #next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWaveIncome

    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()


class MarsIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'mars_income'

    def __repr__(self):
        return "MarsIncome()"

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
                        'job_sec',
                        'SF_12',
                        'pidp',
                        'hh_income',
                        'hh_income_diff',
                        'S7_labour_state',
                        'time',
                        'hidp',
                        'boost_amount'
                        ]

        self.population_view = builder.population.get_view(columns=view_columns)# + columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        super().setup(builder)

        # just load this once.
        self.transition_model = r_utils.load_transitions(f"hh_income/mars/hh_income_MARS", self.rpy2Modules,
                                                         path=self.transition_dir)
        # self.transition_model = r_utils.randomise_fixed_effects(self.transition_model,
        #                                                         self.rpy2Modules,
        #                                                         "glmm",
        #                                                         seed=self.run_seed)

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

        # LA 5/7/24
        # If intervention is a reset intervention, remove boost amount from hh_income before predicting next
        if self.reset_income_intervention:
            pop['hh_income'] = pop['hh_income'] - pop['boost_amount']

        # dummy column to load new prediction into.
        pop['hh_income_last'] = pop['hh_income']

        ## Predict next income values
        newWaveIncome = pd.DataFrame(columns=['hh_income'])
        newWaveIncome['hh_income'] = self.calculate_income(pop)
        newWaveIncome.index = pop.index

        # Ensure whole household has equal hh_income by taking mean after prediction
        newWaveIncome['hidp'] = pop['hidp']
        newWaveIncome = newWaveIncome.groupby('hidp').apply(select_random_income).reset_index(drop=True)

        # difference in hh income
        newWaveIncome['hh_income_diff'] = newWaveIncome['hh_income'] - pop['hh_income_last']

        self.population_view.update(newWaveIncome[['hh_income', 'hh_income_diff']])

    def calculate_income(self, pop):
        """
        Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """

        nextWaveIncome = r_utils.predict_next_MARS(model=self.transition_model,
                                                   rpy2_modules=self.rpy2Modules,
                                                   current=pop,
                                                   dependent='hh_income',
                                                   seed=self.run_seed,
                                                   noise_gauss=350,
                                                   noise_cauchy=35)

        return nextWaveIncome


class RFIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'rf_income'

    def __repr__(self):
        return "RFIncome()"

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
                        'job_sec',
                        'SF_12',
                        'pidp',
                        'hh_income',
                        'hh_income_diff',
                        'S7_labour_state',
                        'time',
                        'hidp'
                        ]
        #columns_created = ['hh_income_diff']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)  # columns_created

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants)  # , creates_columns=columns_created

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        self.rf_transition_model = r_utils.load_transitions(f"hh_income/rf/hh_income_RF",
                                                            self.rpy2Modules,
                                                            path=self.transition_dir)

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

        pop['hh_income_last'] = pop['hh_income']

        #pop['hh_income_diff_last'] = pop['hh_income_diff']
        ## Predict next income value
        newWaveIncome = pd.DataFrame(columns=['hh_income'])
        newWaveIncome['hh_income'] = self.calculate_income(pop)
        newWaveIncome.index = pop.index

        # Ensure whole household has equal hh_income by taking mean after prediction
        newWaveIncome['hidp'] = pop['hidp']
        newWaveIncome = newWaveIncome.groupby('hidp').apply(select_random_income).reset_index(drop=True)

        # difference in hh income
        newWaveIncome['hh_income_diff'] = newWaveIncome['hh_income'] - pop['hh_income_last']

        self.population_view.update(newWaveIncome[['hh_income', 'hh_income_diff']])

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        nextWaveIncome = r_utils.predict_next_rf(self.rf_transition_model,
                                                 self.rpy2Modules,
                                                 pop,
                                                 dependent='hh_income',
                                                 seed=self.run_seed,
                                                 noise_gauss=500,
                                                 noise_cauchy=0)

        return nextWaveIncome


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


class XGBIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'xbg_income'

    def __repr__(self):
        return "XGBIncome()"

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
                        'job_sec',
                        'SF_12',
                        'pidp',
                        'hh_income',
                        'hh_income_diff',
                        'S7_labour_state',
                        'time',
                        'hidp'
                        ]
        #columns_created = ['hh_income_diff']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)  # columns_created

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants)  # , creates_columns=columns_created

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)

        # just load this once.
        self.transition_model = r_utils.load_transitions(f"hh_income/xgb/hh_income_XGB",
                                                            self.rpy2Modules,
                                                            path=self.transition_dir)
        # self.preprocessing_recipe = r_utils.load_transitions(f"hh_income/xgb/hh_income_recipe",
        #                                                      self.rpy2Modules,
        #                                                      path=self.transition_dir)

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

        pop['hh_income_last'] = pop['hh_income']

        # prepare pop for xgboost model
        # xgboost requires a numeric matrix, so we can use one-hot encoding for this
        # encoded_pop = pd.get_dummies(pop, columns=['sex',
        #                                            'ethnicity',
        #                                            'region',
        #                                            'education_state',
        #                                            'job_sec',
        #                                            'S7_labour_state'])

        ## Predict next income value
        newWaveIncome = pd.DataFrame(columns=['hh_income'])
        newWaveIncome['hh_income'] = self.calculate_income(pop)
        newWaveIncome.index = pop.index

        # Ensure whole household has equal hh_income by taking mean after prediction
        newWaveIncome['hidp'] = pop['hidp']
        newWaveIncome = newWaveIncome.groupby('hidp').apply(select_random_income)#.reset_index(drop=True)

        ## SCALING FIX FOR CHILD POV INTERVENTIONS??
        # Instead of scaling the whole pop at once, lets scale by quintile to maintain the variance of higher quintiles
        # This is especially important in interventions that target small groups, and especially especially so in
        # interventions that have fixed thresholds (like child pov reduction)

        # Apply the scaling function
        #newWaveIncome = scale_variance_by_quintile(newWaveIncome, pop, 'hh_income')

        # calculate household income mean
        income_mean = np.mean(newWaveIncome["hh_income"])
        # calculate change in standard deviation between waves.
        std_ratio = (np.std(pop['hh_income_last']) / np.std(newWaveIncome["hh_income"]))
        # rescale income to have new mean but keep old standard deviation.
        newWaveIncome["hh_income"] *= std_ratio
        newWaveIncome["hh_income"] -= ((std_ratio - 1) * income_mean)

        # Adjust Skewness
        target_skew = skew(pop["hh_income_last"])
        newWaveIncome["hh_income"] = adjust_skewness(newWaveIncome["hh_income"], target_skew)

        # difference in hh income
        newWaveIncome['hh_income_diff'] = newWaveIncome['hh_income'] - pop['hh_income_last']

        self.population_view.update(newWaveIncome[['hh_income', 'hh_income_diff']])

    def calculate_income(self, pop):
        """Calculate income transition distribution based on provided people/indices

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        nextWaveIncome = r_utils.predict_next_xgb(self.transition_model,
                                                  self.rpy2Modules,
                                                  pop,
                                                  dependent='hh_income',
                                                  seed=self.run_seed,
                                                  log_transform=False,
                                                  reflect=False,
                                                  noise_gauss=0,
                                                  noise_cauchy=0)

        return nextWaveIncome
