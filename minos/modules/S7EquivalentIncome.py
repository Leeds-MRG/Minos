"""
Module for income in Minos.
Calculation of monthly household income
Possible extension to interaction with employment/education and any spatial/interaction effects.
"""
import numpy as np
import pandas as pd
import minos.modules.r_utils as r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import histplot


class S7EquivalentIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 's7equivalentincome'

    def __repr__(self):
        return "S7EquivalentIncome()"


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
                        'S7_physical_health',
                        'S7_mental_health',
                        'S7_labour_state',
                        'S7_housing_quality',
                        'S7_neighbourhood_safety',
                        'loneliness',
                        'equivalent_income']
        #view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=6)

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

        ## Predict next income value
        newWaveIncome = self.calculate_income(pop)
        newWaveIncome = pd.DataFrame(newWaveIncome, columns=["equivalent_income"])
        # Set index type to int (instead of object as previous)
        newWaveIncome.index = newWaveIncome.index.astype(int)

        # Draw individuals next states randomly from this distribution.
        # Update population with new income
        self.population_view.update(newWaveIncome['equivalent_income'])

    def calculate_income(self, pop):
        """Calculate equivalent income based on provided SIPHER 7 variables

        Parameters
        ----------
            pop: PopulationView
                Population from MINOS to calculate next income for.
        Returns
        -------
        nextWaveIncome: pd.Series
            Vector of new household incomes from OLS prediction.
        """
        # This is a deterministic calculation based on the values from each of the SIPHER7 variables
        # Each level of each variable is assigned a weight, which are then used to modify the value for disposable
        # income to generate a value that is based on both the income and characteristics of a persons life

        # This was first done by one-hot encoding each of the S7 variables, but this would be clunky and inefficient
        # I'm going to try and do it slightly more efficiently

        # The goal here is to calculate an exponent term for modifying income to equivalent income:
        #   EquivalentIncome = Income*EXP(X)
        # Each weighting applies to the level

        # First set up dictionaries for each variable to hold its factor weights
        phys_health_dict = {
            5: 0,
            4: -0.116/1.282,
            3: -0.135/1.282,
            2: -0.479/1.282,
            1: -0.837/1.282
        }
        men_health_dict = {
            5: 0,
            4: -0.14/1.282,
            3: -0.215/1.282,
            2: -0.656/1.282,
            1: -0.877/1.282
        }
        loneliness_dict = {
            1: 0,
            2: -0.186/1.282,
            3: -0.591/1.282
        }
        employment_dict = {
            'FT Employed': 0,
            'PT Employed': 0.033/1.282,
            'Job Seeking': -0.283/1.282,
            'FT Education': -0.184/1.282,
            'Family Care': -0.755/1.282,
            'Not Working': -0.221/1.282
        }
        housing_dict = {
            'Yes to all': 0,
            'Yes to some': -0.235/1.282,
            'No to all': -0.696/1.282
        }
        nh_safety_dict = {
            'Hardly ever': 0,
            'Some of the time': -0.291/1.282,
            'Often': -0.599/1.282
        }

        ### REMOVE THIS PROPERLY SOON!
        # We have a single value of -2 for S7_physical_health which doesn't fit the bill, I'm just replacing it for
        # now but should handle this properly soon in either complete_case or imputation
        #pop['S7_physical_health'][pop['S7_physical_health'] == -2] = 1

        # Now we add together weights for each factor level to generate the exponent term
        pop['EI_exp_term'] = 0
        #pop['EI_exp_term'] = pop['EI_exp_term'] + phys_health_dict.get(pop['S7_physical_health'])
        pop['EI_exp_term'] = pop['EI_exp_term'] + pop.apply(lambda x: phys_health_dict[x['S7_physical_health']], axis=1)
        pop['EI_exp_term'] = pop['EI_exp_term'] + pop.apply(lambda x: men_health_dict[x['S7_mental_health']], axis=1)
        pop['EI_exp_term'] = pop['EI_exp_term'] + pop.apply(lambda x: loneliness_dict[x['loneliness']], axis=1)
        pop['EI_exp_term'] = pop['EI_exp_term'] + pop.apply(lambda x: employment_dict[x['S7_labour_state']], axis=1)
        pop['EI_exp_term'] = pop['EI_exp_term'] + pop.apply(lambda x: housing_dict[x['S7_housing_quality']], axis=1)
        pop['EI_exp_term'] = pop['EI_exp_term'] + pop.apply(lambda x: nh_safety_dict[x['S7_neighbourhood_safety']], axis=1)

        # finally do the calculation for equivalent income (EI = income^EI_exp_term)
        pop['equivalent_income'] = pop['hh_income'] * np.exp(pop['EI_exp_term'])

        return pop['equivalent_income']

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"equivalent_income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="equivalent_income", stat='density')
        plt.savefig(file_name)
        plt.close()
