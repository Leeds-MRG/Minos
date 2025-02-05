
from minos.modules.base_module import Base
import pandas as pd
import logging
import numpy as np


class Ageing(Base):

    def setup(self, builder):
        """ Method for initialising the ageing module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """

        # get model starting year.
        self.current_year = builder.configuration.time.start.year

        # Define which columns are seen in builder.population.get_view calls.
        # Also defines which columns are created by on_initialize_simulants.
        view_columns = ['pidp', 'hidp', 'age', 'time',
                        'nkids', 'nkids_ind',
                        'child_ages', 'child_ages_ind']

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
        #population['age'] += event.step_size / pd.Timedelta(days=365.25)
        population['age'] += 1

        # add one to current year
        #population['time'] += int(event.step_size / pd.Timedelta(days=365.25))
        population['time'] += 1

        # realign children age chains for new repl population. They don't have unique hidps yet.
        # TODO remove this if/when we update household ids in repl.
        # do this by getting the oldest ALIVE member of a household and give everyone in the household that age chain.
        population['child_ages'] = population.groupby('hidp')['child_ages'].transform("first")
        # update children age chains.
        population = self.update_binary_child_ages(population)
        population = self.update_binary_child_ages_ind(population)

        # update new population.
        logging.info(f"Aged population to year {event.time.year}")
        self.population_view.update(population[['age', 'time',
                                                'nkids', 'nkids_ind',
                                                'child_ages', 'child_ages_ind']])

    def update_child_ages(self, pop):
        """ Update age chains for all households with alive individuals.

        Parameters
        ----------
        pop: pd.DataFrame

        Returns
        -------
        pop: pd.DataFrame
        """
        pop['age_nkids_tuple'] = pop['child_ages'].apply(lambda x: self.increment_age_chains(x))
                                                    #pd.DataFrame(.to_list(), index=pop.index)

        pop[['child_ages', 'nkids']] = pop['age_nkids_tuple'].tolist()
        pop['nkids'] = pop['nkids'].astype(float)
        return pop

    def increment_age_chains(self, age_chain):
        """ update the ages of children in the age chains

        Returns
        -------
        age_chain: string
            List of ages of children in the household in descending order separated by dashes -. e.g. 12-4-3-2.
        """

        if age_chain is None:
            age_chain = "childless"
        new_nkids = 0 #  default if no age chain found. assume no children.

        # if household has no children nothing to do.
        if age_chain != "childless" and age_chain != "-9":
            # split age chain into list of strings of ages ['1', '2', '15'] etc.
            age_chain = age_chain.split("_")
            # incerment all child ages by one year. remove them if they hit 16 years old.
            age_chain = [str(int(item) + 1) for item in age_chain if int(item) < 15]

            # get new nkids in household under 16.
            new_nkids = len(age_chain)
            # If household still has children update age_chain. Otherwise set age chain to childless (None) again.
            if new_nkids > 0:

                age_chain = "_".join(age_chain)
            else:
                age_chain = "childless"

        return age_chain, new_nkids

    def update_binary_child_ages(self, pop):
        """ Update age chains for all households with alive individuals.

        Parameters
        ----------
        pop: pd.DataFrame

        Returns
        -------
        pop: pd.DataFrame
        """

        pop['child_ages'] = pop['child_ages'].astype('int64')
        updated_ages = pop['child_ages'].apply(lambda x: self.increment_binary_age_chains(x))
                                                    #pd.DataFrame(.to_list(), index=pop.index)

        pop[['child_ages', 'nkids_delta']] = updated_ages.tolist()
        pop['nkids'] -= pop['nkids_delta']
        pop['child_ages'] = pop['child_ages'].astype('int64')
        pop['nkids'] = pop['nkids'].astype('float64')
        return pop

    def update_binary_child_ages_ind(self, pop):
        """ Update age chains for all individuals

        Parameters
        ----------
        pop: pd.DataFrame

        Returns
        -------
        pop: pd.DataFrame
        """

        pop['child_ages_ind'] = pop['child_ages_ind'].astype('int64')  # Why, Pandas, why?

        updated_ages = pop['child_ages_ind'].apply(lambda x: self.increment_binary_age_chains(x))
        pop[['child_ages_ind', 'nkids_ind_delta']] = updated_ages.tolist()
        # pop['nkids_ind'] -= pop['nkids_ind_delta']  # No! nkids_ind is children *ever* had, so must never be decremented

        pop['child_ages_ind'] = pop['child_ages_ind'].astype('float64')
        # pop['nkids_ind'] = pop['nkids_ind'].astype('float64')
        return pop

    def increment_binary_age_chains(self, age_chain):
        """ update the ages of children in the age chains

        Returns
        -------
        age_chain: string
            Integer-form variable of children in household in descending order; four bits per age bucket
        """

        if age_chain == 0:
            return (0, 0)

        # calculate exiting 16 year olds to calculate nkids change.
        exiting_kids = age_chain >> 60
        # cut 15 year olds off bit shifting left 4.
        # resetting back to 64 bits. kinda ugly mask. 0xFFFFFFFF is the biggest int64 in hex for readability. 2**63.
        #TODO BUG IS HERE SOMEWHERE? not counting values above 8 properly.

        # 0xFFFFFFFF is the biggest number possible for int 64 as a hexadecimal.
        # This is just a bit mask cutting the first four bits off
        mask = (1 << 15*4) - 1
        age_chain = mask & (age_chain) #0xFFFFFFFF &
        age_chain = age_chain << 4
        return age_chain, exiting_kids

    # Special methods for vivarium.
    @property
    def name(self):
        return "ageing"

    def __repr__(self):
        return "Ageing()"
