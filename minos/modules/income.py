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

# Annual average inflation based on CPI index.
# https://www.statista.com/statistics/270384/inflation-rate-in-the-united-kingdom/
annual_cpi_rates = {
    2017: 2.68,
    2018: 2.48,
    2019: 1.79,
    2020: 0.85,
    2021: 2.59,
    2022: 9.12,
    2023: 8.99,
    2024: 3.73,
    2025: 1.82,
    2026: 2.00,
    # Stabilises to 2% because they can't predict this far ahead.. All years beyond have this value.
    # This is a Bank of England target and is highly optimistic..
}

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
                        'labour_state',
                        'education_state',
                        'SF_12',
                        'housing_quality',
                        'job_sector']
        #view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=2)

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
        newWaveIncome = pd.DataFrame(newWaveIncome, columns=["hh_income"])
        # Set index type to int (instead of object as previous)
        newWaveIncome.index = newWaveIncome.index.astype(int)

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
        year = min(self.year, 2018)
        transition_model = r_utils.load_transitions(f"hh_income/ols/hh_income_{year}_{year + 1}")
        # The calculation relies on the R predict method and the model that has already been specified
        nextWaveIncome = r_utils.predict_next_timestep_ols(transition_model, pop, dependent='hh_income')
        return nextWaveIncome

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"income_hist_{self.year}.pdf"
        f = plt.figure()
        histplot(pop, x="hh_income", stat='density')
        plt.savefig(file_name)
        plt.close()


class grossIncome(Base):

    # Special methods used by vivarium.
    @property
    def name(self):
        return 'gross_income'

    def __repr__(self):
        return "grossIncome()"

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
                        'net_hh_income',
                        'job_sec',
                        'labour_state',
                        'education_state',
                        'SF_12',
                        'housing_quality',
                        'job_sector',
                        'gross_hh_income',
                        'oecd_equiv',
                        'outgoings',
                        'tenure',
                        'yearly_energy',
                        'financial_situation',
                        'marital_status',
                        'hhsize',
                        'FP10']
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=2)

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
        newWaveGrossIncome = self.calculate_income(pop)
        newWaveGrossIncome = pd.DataFrame(newWaveGrossIncome, columns=["gross_hh_income"])
        # Set index type to int (instead of object as previous)
        newWaveGrossIncome.index = newWaveGrossIncome.index.astype(int)
        # adjust for inflation
        newWaveGrossIncome['gross_hh_income'] = self.adjust_inflation(newWaveGrossIncome['gross_hh_income'], self.year)
        # calculate net (disposable) income based on overheads and house size.
        newWaveGrossIncome['net_hh_income'] = self.transform_gross_to_net_income(newWaveGrossIncome['gross_hh_income'],
                                                                                 pop['outgoings'],
                                                                                 pop['oecd_equiv'])

        nextWaveFinancialSituation = self.calculate_financial_situation(pop)
        nextWaveFinancialSituation["financial_situation"] = self.random.choice(nextWaveFinancialSituation.index, list(nextWaveFinancialSituation.columns+1),
                                                                nextWaveFinancialSituation).astype(float)
        nextWaveFinancialSituation.index = newWaveGrossIncome.index
        newWaveGrossIncome['financial_situation'] = nextWaveFinancialSituation['financial_situation']
        # calculate FP10 based on energy usage and gross income
        newWaveGrossIncome['FP10'] = self.calculate_fp10(newWaveGrossIncome['gross_hh_income'], pop['yearly_energy'])

        # Draw individuals next states randomly from this distribution.
        # Update population with new income.
        self.population_view.update(newWaveGrossIncome[['gross_hh_income', 'net_hh_income', 'FP10', 'financial_situation']])

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
        year = min(self.year, 2018)
        transition_model = r_utils.load_transitions(f"gross_hh_income/ols/gross_hh_income_{year}_{year + 1}")
        # The calculation relies on the R predict method and the model that has already been specified
        nextWaveGrossIncome = r_utils.predict_next_timestep_ols(transition_model, pop, dependent='gross_hh_income')
        return nextWaveGrossIncome

    def calculate_financial_situation(self, pop):
        year = min(self.year, 2018)
        transition_model = r_utils.load_transitions(f"financial_situation/clm/financial_situation_{year}_{year + 1}")
        nextWaveFinancialPerception = r_utils.predict_next_timestep_clm(transition_model, pop, dependent='financial_situation')
        return nextWaveFinancialPerception

    def transform_gross_to_net_income(self, gross_income, outgoings, oecd_equiv):
        return (gross_income - outgoings)/ oecd_equiv

    def calculate_fp10(self, gross_income, energy_use):
        # Is 10% of gross income spent on fuel?
        return (10 * energy_use) >= gross_income

    def adjust_inflation(self, gross_income, year):
        """ Adjust gross income according to yearly inflation."""
        if year >= 2026:
            yearly_inf_rate = 1.02
        else:
            yearly_inf_rate = 1 + (annual_cpi_rates[year] / 100)  # Get forecasted inflation rate due to CPI.

            # Widely assumed to be 2% after 2026 for UK.
        return gross_income / yearly_inf_rate