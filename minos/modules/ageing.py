
from minos.modules.base_module import Base
import pandas as pd
import logging

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
                        'time']

        # Shorthand methods for readability.
        self.population_view = builder.population.get_view(view_columns)  # view simulants

        # Register ageing, updating time and replenishment events on time_step.
        builder.event.register_listener('time_step', self.on_time_step, priority=0)


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
        population['time'] += int(event.step_size / pd.Timedelta(days=365.25))

        # update new population.
        logging.info(f"Aged population to year {event.time.year}")
        self.population_view.update(population)

    # Special methods for vivarium.
    @property
    def name(self):
        return "ageing"

    def __repr__(self):
        return "Ageing()"
