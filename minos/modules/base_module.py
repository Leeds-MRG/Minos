"""
Superclass for MINOS modules to try and reduce a lot of boilerplate. Removes a lot of repetition and makes modules
easier to build.


"""

from datetime import datetime as dt
from scipy.special import ndtri  # very fast standard normal sampler.
from minos.data_generation.US_utils import load_multiple_data
import pandas as pd

PRIORITY_DEFAULT = 10


class Base():

    @property
    def name(self):
        return "base"

    def __repr__(self):
        return "Base()"

    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run into the config and simulation object.

        This default does nothing. If any further setup is required it is done in each module.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run.

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run with updated config/inputs.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        # Use transition directory specified in config file
        self.transition_dir = config.transition_dir
        # Use data directory from config file
        self.input_data_dir = config.input_data_dir
        # replenishing directory
        self.replenishing_dir = config.replenishing_dir
        # mode
        self.cross_validation = config.cross_validation

        # # Grab module priority
        # self.priority = simulation.component_priority_map.get(self.__repr__(), PRIORITY_DEFAULT)
        # print("Priority for {} set to {}".format(self.__repr__(), self.priority))

        return simulation

    def setup(self, builder):
        component_priority_map = builder.data.load("component_priority_map")
        self.priority = component_priority_map.get(self.__repr__(), PRIORITY_DEFAULT)
        # print("Priority for {} set to {}".format(self.__repr__(), self.priority))
        builder.event.register_listener("time_step", self.on_time_step, priority=self.priority)

    def on_time_step(self, event):
        pass

    def on_initialize_simulants(self, pop_data):
        """  Initiate columns for mortality when new simulants are added. By default adds no columns.

        Parameters
        ----------
        pop_data: vivarium.framework.population.SimulantData
            Custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).
        Returns
        -------
        None
        """
        # Initiate any columns created by this module and add them to the main population.
        # No synthetic columns for housing currently. Maybe housing history variables added here.
        return pop_data

    def generate_fixed_crn_key(self):
        "CRN randomness streams in vivarium use hash some input string key as the seed for RNG."
        "If we want a fixed seed for each vivarium run just use the name of the module."
        "Useful if trying to reduce variance. Or for non-random models e.g. OLS."
        return f"{self.name}"

    def generate_random_crn_key(self):
        "Provides random hash for each minos run using date time."
        "Provides more stochasticity in random models e.g. binomial/clm"
        "Seems like vivarium uses a 10 digit congruency generator to produces hashes."
        "Very unlikely to repeat but even then doesn't matter.."
        return f"{self.name}{dt.now()}"

    def plot(self, pop_data, config):
        """ Default plot method for modules. Does nothing.

        Modules can specify another plot object that saves distributions of state.

        Parameters
        ----------
        pop_data: population data from vivarium. Whatever columns needs plotting.

        config: vivarium.configTree

            Config yaml for any needed plot parameters.

        Returns
        -------
        None
        """
        pass

    def generate_gaussian_noise(self, index, mu=0, sigma=1):
        """ Generate Gaussian noise for continuous variables in MINOS
        Parameters
        ----------
        index: pandas.Index
            How many observations to generate. should match number of rows from minos dataframe
        mu, sigma: float
            Mean and standard deviation of desired Gaussian data. Defaults to 0 and 1 (I.E. the standard Normal distribution).
        Returns
        -------
        data: np.array
            1xn vector of n samples from the Gaussian distribution N(mu, sigma^2).
        """

        u = self.random.get_draw(index)
        return (sigma*ndtri(u)) + mu


    def generate_history_dataframe(self, source, years, variables):
        file_names = [f"data/{source}/{year}_US_cohort.csv" for year in years]
        if file_names:
            data = load_multiple_data(file_names)
            data = data[variables]
            data = data.sort_values(by=["pidp", "time"])
        else:
            data = pd.DataFrame()
        return data

    def update_history_dataframe(self, new_data, year, lag=5):
        self.history_data = pd.concat([self.history_data, new_data])
        self.history_data = self.history_data.loc[self.history_data["time"] > year-lag]
        self.history_data = self.history_data.sort_values(by=['pidp', 'time'])
        self.history_data.reset_index(inplace=True, drop=True)


class Intervention:

    # Generic intervention class to reduce boilerplate.

    #presetup
    #setup
    #ontimestep
    #plot

    def on_initialize_simulants(self, pop_data):
        pop_update = pd.DataFrame({'income_boosted': False,
                                   'boost_amount': 0.},
                                  index=pop_data.index)
        self.population_view.update(pop_update)


    def plot(self, pop_data, config):
        """ Default plot method for modules. Does nothing.

        Modules can specify another plot object that saves distributions of state.

        Parameters
        ----------
        pop_data: population data from vivarium. Whatever columns needs plotting.

        config: vivarium.configTree

            Config yaml for any needed plot parameters.

        Returns
        -------
        None
        """
        pass

