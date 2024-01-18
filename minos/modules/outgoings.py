"""
Module for estimating household outgoings (rent, council tax, and mortgages) (and yearly energy?)
"""

import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import histplot
import numpy as np
import logging



"""
Module for net income in Minos.
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

class lmmYJOutgoings(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'lmmYJ_outgoings'

    def __repr__(self):
        return "lmmYJOutgoings()"

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
        # view_columns = ['pidp',
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
                        "net_hh_income",
                        "outgoings",
                        "oecd_equiv",
                        "hh_rent",
                        "hh_mortgage",
                        "council_tax",
                        'net_hh_income_diff',
                        "yearly_energy",
                        'hh_int_m',
                        'housing_tenure',
                        'time'
                        ]

        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)  # + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        #builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=2)

        # just load this once.
        # self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_yj/hh_income_GEE_YJ", self.rpy2Modules,
        #                                             path=self.transition_dir)
        # self.gee_transition_model = r_utils.load_transitions(f"hh_income/gee_diff/hh_income_GEE_DIFF", self.rpy2Modules,
        #                                                     path=self.transition_dir)
        self.rent_transition_model = r_utils.load_transitions(f"hh_rent/glmm/hh_rent_GLMM", self.rpy2Modules,
                                                             path=self.transition_dir)
        self.mortgage_transition_model = r_utils.load_transitions(f"hh_mortgage/glmm/hh_mortgage_GLMM", self.rpy2Modules,
                                                              path=self.transition_dir)
        # self.history_data = self.generate_history_dataframe("final_US", [2018, 2019], view_columns)
        # self.history_data["hh_income_diff"] = self.history_data['hh_income'] - self.history_data.groupby(['pidp'])['hh_income'].shift(1)

    def on_time_step(self, event):
        """ Predicts the hh_income for the next timestep.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """
        # Get living people to update their income
        # various renters.
        # TODO investigate specific renting categories heterogeneity. E.g. renting from local authority?
        pop = self.population_view.get(event.index, query="alive =='alive' & housing_tenure >= 3")
        self.year = event.time.year
        pop['hh_rent_last'] = pop['hh_rent']
        ## Predict next income value

        newWaveRent = pd.DataFrame(columns=['hh_rent'])
        newWaveRent['hh_rent'] = self.calculate_hh_rent(pop)
        newWaveRent.index = pop.index
        newWaveRent['hh_rent'] = newWaveRent['hh_rent'].clip(0, 4000)
        self.population_view.update(newWaveRent[['hh_rent']])

        #mortgagers
        pop = self.population_view.get(event.index, query="alive =='alive' & housing_tenure == 2")
        pop['hh_mortgage_last'] = pop['hh_mortgage']

        newWaveMortgage = pd.DataFrame(columns=['hh_mortgage'])
        newWaveMortgage['hh_mortgage'] = self.calculate_hh_mortgage(pop)
        newWaveMortgage.index = pop.index
        newWaveMortgage['hh_mortgage'] = newWaveMortgage['hh_mortgage'].clip(0, 15000)
        self.population_view.update(newWaveMortgage[['hh_mortgage']])

        # property owners
        pop = self.population_view.get(event.index, query="alive =='alive' & housing_tenure == 1")
        pop['hh_rent'] = 0.
        pop['hh_mortgage'] = 0.
        self.population_view.update(pop[['hh_mortgage', 'hh_rent']])



    def calculate_hh_rent(self, pop):
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
        nextWavenetIncome = r_utils.predict_next_timestep_yj_gamma_glmm(self.rent_transition_model,
                                                                        self.rpy2Modules,
                                                                        pop,
                                                                        dependent='hh_rent_new',
                                                                        yeo_johnson=False,
                                                                        reflect=False,
                                                                        noise_std=10)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWavenetIncome

    def calculate_hh_mortgage(self, pop):
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
        nextWavenetIncome = r_utils.predict_next_timestep_yj_gamma_glmm(self.mortgage_transition_model,
                                                                        self.rpy2Modules,
                                                                        pop,
                                                                        dependent='hh_mortgage_new',
                                                                        yeo_johnson=False,
                                                                        reflect=False,
                                                                        noise_std=10)  # 0.45 for yj. 100? for non yj.
        # get new hh income diffs and update them into history_data.
        # self.update_history_dataframe(pop, self.year-1)
        # new_history_data = self.history_data.loc[self.history_data['time']==self.year].index # who in current_year
        # next_diffs = nextWaveIncome.iloc[new_history_data]
        return nextWavenetIncome


    def plot(self, pop, config):
        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()