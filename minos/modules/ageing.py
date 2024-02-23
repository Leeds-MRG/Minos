
from minos.modules.base_module import Base
import pandas as pd
import logging
import numpy as np

class Ageing(Base):

    def setup(self, builder):
        """ Method for initialising the depression module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """

        # get model starting year.
        self.current_year = builder.configuration.time.start.year

        # Define which columns are seen in builder.population.get_view calls.
        # Also defines which columns are created by on_initialize_simulants.
        view_columns = ['pidp',
                        'hidp',
                        'age',
                        'nkids',
                        'time',
                        'child_ages']

        # Shorthand methods for readability.
        self.population_view = builder.population.get_view(view_columns)  # view simulants

        # Register ageing, updating time and replenishment events on time_step.
        # builder.event.register_listener('time_step', self.on_time_step, priority=self.priority)
        super().setup(builder)

    def on_time_step(self, event):
        """ Age everyone by the length of the simulation time step in days
        Parameters
        ----------
        event : builder.event
            some time point at which to run the method.
        """
        # get alive people and add time in years to their age.
        population = self.population_view.get(event.index, query="alive == 'alive'")
        population['age'] += event.step_size / pd.Timedelta(days=365.25)


        # add one to current year
        #population['time'] += int(event.step_size / pd.Timedelta(days=365.25))
        population['time'] += 1

        # realign children age chains for new repl population. They don't have unique hidps yet.
        # TODO remove this if/when we update household ids in repl.
        # do this by getting the oldest ALIVE member of a household and give everyone in the household that age chain.
        population['child_ages'] = population.groupby('hidp')['child_ages'].transform("first")
        # update children age chains.
        population = self.update_child_ages(population)

        # When a child reaches 16 years old and is then removed from the child_ages and nkids columns, the
        # child_ages column is filled with a nan value instead of 'None'
        # Doing this cleanup here because this is causing a mixed type column (strings for age_chains and float for nan)
        #population['child_ages'][population['child_ages'].isna()] = None

        population['nkids'] = population['nkids'].astype(float)

        # update new population.
        logging.info(f"Aged population to year {event.time.year}")
        self.population_view.update(population[['age', 'time', 'child_ages', 'nkids']])


    def update_child_ages(self, pop):
        """ Update age chains for all households with alive individuals.

        Parameters
        ----------
        pop: pd.DataFrame

        Returns
        -------
        pop: pd.DataFrame
        """
        pop['child_ages'] = pop['child_ages'].astype(str)
        pop['age_nkids_tuple'] = pop['child_ages'].apply(lambda x: self.increment_age_chains(x))
                                                    #pd.DataFrame(.to_list(), index=pop.index)



        pop[['child_ages', 'nkids']] = pop['age_nkids_tuple'].tolist()
        pop['nkids'] = pop['nkids'].astype(float)
        return pop

    def increment_age_chains(self, age_chain):
        """

        Returns
        -------
        age_chain: string
            List of ages of children in the household in descending order seperated by dashes -. e.g. 12-4-3-2.
        """
        # split age chain into list
        new_nkids = 0  # default if no age chain found. assume no children.
        value = age_chain  # .values[0]
        if value != 'None' and value is not None:

            assert value is not None, f"Value is None, this should not happen. value: {value}"
            assert value != 'None', f"Value is 'None', this should not happen. value: {value}"
            assert isinstance(value, str), f"Value is not str, this should not happen. value: {value}"

            # Split delimited string to list of ages
            age_chain = value.split("_")
            # # If only one child the above line doesn't do anything, so need to encapsulate those in a list
            # if age_chain:

            assert isinstance(age_chain, list), f"age_chain is not list when it should be. age_chain: {age_chain}, type: {type(age_chain)}"
            assert age_chain != [], f"age_chain is an empty list when it should not be. age_chain: {age_chain}, type: {type(age_chain)}"

            assert age_chain is not None, f"age_chain is None, this should not happen. age_chain: {age_chain}"
            assert age_chain != 'None', f"age_chain is 'None', this should not happen. age_chain: {age_chain}"
            assert age_chain != '', f"age_chain is '', this should not happen. age_chain: {age_chain}"

            assert not isinstance(age_chain, int), f"age_chain is int, this should not be. age_chain: {age_chain}, type: {type(age_chain)}"

            # increment each item by one
            # remove item if item is over 16.
            try:
                age_chain = [str(int(item) + 1) for item in age_chain if int(item) < 15]
            except ValueError as verror:
                print(verror)
                print(f"age_chain is an invalid value, this should not happen. age_chain: {age_chain}, type: {type(age_chain)}")
                exit("Please address the problem with child ages and try again")

            # If there are no more children, explicitly replace with None
            # This is identified when age_chain == nan, and is therefore not a list
            # if age_chain.isna():
            #if not type(age_chain).isinstance(list):
            if not isinstance(age_chain, list):
                age_chain = None

            #age_chain = np.sort(age_chain, ascending=True)
            # return child ages chain and length of list.
            if age_chain:
                new_nkids = len(age_chain)
                age_chain = "_".join(age_chain)
            else:
                new_nkids = 0
                age_chain = np.nan
        else:
            age_chain = value
        return age_chain, new_nkids


    # Special methods for vivarium.
    @property
    def name(self):
        return "ageing"

    def __repr__(self):
        return "Ageing()"
