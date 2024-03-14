
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
                        'child_ages',
                        'oecd_equiv']

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

        logging.info(f"Aged population to year {event.time.year}")
        self.population_view.update(population[['age', 'time']])

        child_population = self.population_view.get(event.index, query="child_ages!='childless'")

        # realign children age chains for new repl population. They don't have unique hidps yet.
        # TODO remove this if/when we update household ids in repl.
        # do this by getting the oldest ALIVE member of a household and give everyone in the household that age chain.
        child_population['child_ages'] = child_population.groupby('hidp')['child_ages'].transform("first")
        child_population['oecd_equiv'] = child_population.groupby('hidp')['oecd_equiv'].transform("max")

        # update children age chains.
        newChildAges = self.update_child_ages(child_population)

        # When a child reaches 16 years old and is then removed from the child_ages and nkids columns, the
        # child_ages column is filled with a nan value instead of 'None'
        # Doing this cleanup here because this is causing a mixed type column (strings for age_chains and float for nan)
        #population['child_ages'][population['child_ages'].isna()] = None

        newChildAges['nkids'] = newChildAges['nkids'].astype(float)
        newChildAges['oecd_equiv'] = population['oecd_equiv'] + newChildAges['oecd_change']
        newChildAges['oecd_equiv'] = newChildAges['oecd_equiv'].astype(float)
        # oecd has to be at least 1.
        newChildAges['oecd_equiv'] = newChildAges["oecd_equiv"].clip(lower=1.0)

        # update new population.
        logging.info(f"Aged children for population to year {event.time.year}")
        self.population_view.update(newChildAges[['child_ages', 'nkids', 'oecd_equiv']])


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



        pop[['child_ages', 'nkids', 'oecd_change']] = pop['age_nkids_tuple'].tolist()
        pop['nkids'] = pop['nkids'].astype(float)
        return pop

    def increment_age_chains(self, age_chain):
        """ update the ages of children in the age chains

        Returns
        -------
        age_chain: string
            List of ages of children in the household in descending order seperated by dashes -. e.g. 12-4-3-2.
        """

        if age_chain is None:
            age_chain = "childless"
        new_nkids = 0 #  default if no age chain found. assume no children.
        oecd_change = 0

        # if household has no children nothing to do.
        if age_chain != "childless" and age_chain != "-9":
            # split age chain into list of strings of ages ['1', '2', '15'] etc.
            age_chain = age_chain.split("_")
            # incerment all child ages by one year. remove them if they hit 16 years old.
            new_age_chain = []
            for age in age_chain:
                age = str(int(age) + 1)
                if age == "14":
                    oecd_change += 0.2 # change oecd contribution from 0.3 to 0.5.
                    new_age_chain.append(age)
                elif age == "16":
                    oecd_change -= 0.5 # leaving model. remove oecd contribution of 0.5.
                else:
                    new_age_chain.append(age) # no oecd contribution change. just add back in.


            # get new nkids in household under 16.
            new_nkids = len(new_age_chain)
            # If household still has children update age_chain. Otherwise set age chain to childless (None) again.
            if new_nkids > 0:
                age_chain = "_".join(new_age_chain)
            else:
                age_chain = "childless"

        return age_chain, new_nkids, oecd_change

    # Special methods for vivarium.
    @property
    def name(self):
        return "ageing"

    def __repr__(self):
        return "Ageing()"
