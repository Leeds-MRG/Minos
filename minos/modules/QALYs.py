"""
Module for housing in Minos.
Upgrade of household appliances
Possible future work for moving households and changing household composition (e.g. marrying/births)
"""

import pandas as pd
from minos.modules import r_utils
from minos.modules.base_module import Base
import matplotlib.pyplot as plt
from seaborn import catplot
import logging

class QALYs(Base):

    @property
    def name(self):
        return "QALY"

    def __repr__(self):
        return "QALYs()"

    # In Daedalus pre_setup was done in the run_pipeline file. This way is tidier and more modular in my opinion.

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

        # Determine which subset of the main population is used in this module.
        # columns_created is the columns created by this module.
        # view_columns is the columns from the main population used in this module. essentially what is needed for
        # transition models and any outputs.
        view_columns = ['SF_12_MCS',
                        'SF_12_PCS']
        columns_created = ["QALYs"]
        # view_columns += self.transition_model.rx2('model').names
        self.population_view = builder.population.get_view(columns=view_columns + columns_created)  # + columns_created)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        # builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)
        super().setup(builder)


    def on_initialize_simulants(self, pop_data):
        """  Initiate columns for QALYs when new simulants are added.
        Only column needed is the QALYs column itself.
        Parameters
        ----------
            pop_data: vivarium.framework.population.SimulantData
            Custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        """

        pop_update = pd.DataFrame({"QALYs": 0.,}, index=pop_data.index)
        self.population_view.update(pop_update)

    def on_time_step(self, event):
        """Produces new children and updates parent status on time steps.

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The event time_step that called this function.
        """

        logging.info("HOUSING QUALITY")

        # Construct transition probability distributions.
        # Draw individuals next states randomly from this distribution.
        # Adjust other variables according to changes in state. E.g. a birth would increase child counter by one.

        # setting qalys of dead people to 0.
        dead_pop = self.population_view.get(event.index, query="alive=='dead'")
        dead_pop['QALYs'] = 0.
        self.population_view.update(dead_pop["QALYs"])

        n_dead = dead_pop.shape[0]

        # alive people calculate qalys using lawrence/fleischmann formula.
        alive_pop = self.population_view.get(event.index, query="alive=='alive'")
        n_alive = alive_pop.shape[0]
        proportion_pop_alive = (n_alive / (n_dead + n_alive))
        alive_pop = self.calculate_two_term_qaly(alive_pop, proportion_pop_alive)

        self.population_view.update(alive_pop[["QALYs"]])


    def calculate_two_term_qaly(self, df, proportion_pop_alive):
        """
        QALY calculation comes from Lawrence and Fleishman (2004) - https://pubmed.ncbi.nlm.nih.gov/15090102/

        In table 4 of the above paper, regression model coefficients were presented which allow the mapping of MCS and PCS
        scores onto EQ-5D, from which we can calculate utility scores.

        From the utility scores we can calculate QALYs by multiplying the utility score by the population size (alive).

        NB the larger six variable QALY formula is also provided below. Provides slightly better performance but can
        only be calculated for the entire population at once due to non-linearity from higher order terms.
        https://www.ncbi.nlm.nih.gov/books/NBK562431/

        MEAN OF THIS VECTOR WILL GIVE YEARLY QALY
        Parameters
        ----------
        df

        Returns
        -------

        """

        # Run without any subpopulations to worry about

        # First calculate utility score using values table 4 from Lawrence and Fleishman (2004)
        df['eq5d_utility'] = -0.3720 + (df['SF_12_PCS'] * 0.01411) + (df['SF_12_MCS'] * 0.02859)
        # Now calculate QALYs by multiplying utility score by pop_size
        df['QALYs'] = (df['eq5d_utility'] * proportion_pop_alive)

        return df


    def calculate_six_term_qaly(self, df, alive_pop):
        """
        QALY calculation comes from Lawrence and Fleishman (2004) - https://pubmed.ncbi.nlm.nih.gov/15090102/

        In table 4 of the above paper, regression model coefficients were presented which allow the mapping of MCS and PCS
        scores onto EQ-5D, from which we can calculate utility scores.

        From the utility scores we can calculate QALYs by multiplying the utility score by the population size (alive).

        Parameters
        ----------
        df

        Returns
        -------

        """

        # Run without any subpopulations to worry about

        # First calculate utility score using values table 4 from Lawrence and Fleishman (2004)
        df['utility'] = -1.6984 + \
                        (df['SF_12_PCS'] * 0.07927) + \
                        (df['SF_12_MCS'] * 0.02859) + \
                        ((df['SF_12_PCS'] * df['SF_12_MCS']) * -0.000126) + \
                        ((df['SF_12_PCS'] * df['SF_12_PCS']) * -0.00141) + \
                        ((df['SF_12_MCS'] * df['SF_12_MCS']) * -0.00014) + \
                        ((df['SF_12_PCS'] * df['SF_12_PCS'] * df['SF_12_PCS']) * 0.0000107)

        # Now calculate QALYs by multiplying utility score by pop_size
        df['QALYs'] = df['utility'] * df['alive_pop']

        return df