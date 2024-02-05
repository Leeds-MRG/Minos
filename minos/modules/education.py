""" File for adding new cohorts from Understanding Society data to the population"""

import pandas as pd
import logging
import r_utils
from minos.modules.base_module import Base

# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None  # default='warn' #supress SettingWithCopyWarning


class EducationOld(Base):

    # Special methods for vivarium.
    @property
    def name(self):
        return "education"


    def __repr__(self):
        return "Education()"

    def setup(self, builder):
        """ Method for initialising the education module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """

        # Load in inputs from pre-setup.
        self.rpy2Modules = builder.data.load("rpy2_modules")

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
                        'education_state',
                        'max_educ']
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=5)

    def on_time_step(self, event):
        """ On time step check handle various education changes for people aged 16-30.

        Justification for certain age changes:
        - All children must now complete GCSE, so before age 17 must have attained GCSE (level 2)
        - A-levels and equivalent finish at 18, so anyone who achieves this will have it applied before age 19 (level 3)
        -

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The `event` that triggered the function call.
        """

        logging.info("EDUCATION")

        self.year = event.time.year

        # Level 2 is equivalent to GCSE level, which everyone should have achieved by the age of 17
        # No need to test max_educ for this one, everyone stays in education to 16 now minimum
        level2 = self.population_view.get(event.index, query="alive=='alive' and age == 17 and S7_labour_state=='FT Education'")
        # Update education state and apply back to population view
        level2['education_state'][level2['education_state'] < 2] = 2
        self.population_view.update(level2['education_state'])

        # Level 3 is equivalent to A-level, so make this change by age 19 if max_educ is 3 or larger
        level3 = self.population_view.get(event.index, query="alive=='alive' and age == 19 and S7_labour_state=='FT Education' and max_educ >= 3")
        level3['education_state'][level3['education_state'] < 3] = 3
        self.population_view.update(level3['education_state'])

        # Level 5 is nursing/medical and HE diploma, so make this change by age 22 if max_educ is 5
        level5 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 22 and S7_labour_state=='FT Education' and max_educ == 5")
        level5['education_state'][level5['education_state'] < 5] = 5
        self.population_view.update(level5['education_state'])

        # Level 6 is 1st degree or teaching qual (not PGCE), so make this change by age 22 if max_educ is 6 or larger
        level6 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 22 and S7_labour_state=='FT Education' and max_educ >= 6")
        level6['education_state'][level6['education_state'] < 6] = 6
        self.population_view.update(level6['education_state'])

        # Level 7 is higher degree (masters/PhD), so make this change by age 25 if max_educ is 7
        level7 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 26 and S7_labour_state=='FT Education' and max_educ == 7")
        level7['education_state'][level7['education_state'] < 7] = 7
        self.population_view.update(level7['education_state'])


class Education(Base):

    # Special methods for vivarium.
    @property
    def name(self):
        return "education"


    def __repr__(self):
        return "Education()"

    def setup(self, builder):
        """ Method for initialising the education module.

        Parameters
        ----------
        builder : vivarium.builder
            Vivarium's control object. Stores all simulation metadata and allows modules to use it.
        """

        # Load in inputs from pre-setup.
        self.rpy2Modules = builder.data.load("rpy2_modules")

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
                        'education_state']
        self.population_view = builder.population.get_view(columns=view_columns)

        # Population initialiser. When new individuals are added to the microsimulation a constructer is called for each
        # module. Declare what constructer is used. usually on_initialize_simulants method is called. Inidividuals are
        # created at the start of a model "setup" or after some deterministic (add cohorts) or random (births) event.
        builder.population.initializes_simulants(self.on_initialize_simulants)

        # Declare events in the module. At what times do individuals transition states from this module. E.g. when does
        # individual graduate in an education module.
        builder.event.register_listener("time_step", self.on_time_step, priority=5)

        # Load in transition models
        self.start_transition_model = r_utils.load_transitions(f"education_state/mcmcglmm/education_state_MCMCGLMM",
                                                               self.rpy2Modules,
                                                               path=self.transition_dir)
        self.stop_transition_model = r_utils.load_transitions(f"start_educ/logit/start_educ_",
                                                              self.rpy2Modules,
                                                              path=self.transition_dir)
        self.educ_transition_model = r_utils.load_transitions(f"stop_educ/logit/stop_educ_",
                                                              self.rpy2Modules,
                                                              path=self.transition_dir)

    def on_time_step(self, event):
        """ On time step check handle various education changes for people aged 16-30.

        Justification for certain age changes:
        - All children must now complete GCSE, so before age 17 must have attained GCSE (level 2)
        - A-levels and equivalent finish at 18, so anyone who achieves this will have it applied before age 19 (level 3)
        -

        Parameters
        ----------
        event : vivarium.population.PopulationEvent
            The `event` that triggered the function call.
        """

        logging.info("EDUCATION")

        self.year = event.time.year

        # Level 2 is equivalent to GCSE level, which everyone should have achieved by the age of 17
        # No need to test max_educ for this one, everyone stays in education to 16 now minimum
        level2 = self.population_view.get(event.index, query="alive=='alive' and age == 17 and S7_labour_state=='FT Education'")
        # Update education state and apply back to population view
        level2['education_state'][level2['education_state'] < 2] = 2
        self.population_view.update(level2['education_state'])

        # Level 3 is equivalent to A-level, so make this change by age 19 if max_educ is 3 or larger
        level3 = self.population_view.get(event.index, query="alive=='alive' and age == 19 and S7_labour_state=='FT Education' and max_educ >= 3")
        level3['education_state'][level3['education_state'] < 3] = 3
        self.population_view.update(level3['education_state'])

        # Level 5 is nursing/medical and HE diploma, so make this change by age 22 if max_educ is 5
        level5 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 22 and S7_labour_state=='FT Education' and max_educ == 5")
        level5['education_state'][level5['education_state'] < 5] = 5
        self.population_view.update(level5['education_state'])

        # Level 6 is 1st degree or teaching qual (not PGCE), so make this change by age 22 if max_educ is 6 or larger
        level6 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 22 and S7_labour_state=='FT Education' and max_educ >= 6")
        level6['education_state'][level6['education_state'] < 6] = 6
        self.population_view.update(level6['education_state'])

        # Level 7 is higher degree (masters/PhD), so make this change by age 25 if max_educ is 7
        level7 = self.population_view.get(event.index,
                                          query="alive=='alive' and age == 26 and S7_labour_state=='FT Education' and max_educ == 7")
        level7['education_state'][level7['education_state'] < 7] = 7
        self.population_view.update(level7['education_state'])

    def predict_educ_start(self, pop):

        next_wave_start_educ = r_utils.predict_next_timestep_logit(model=self.start_transition_model,
                                                                   rpy2_modules=self.rpy2_modules,
                                                                   current=pop,
                                                                   dependent='education_state')
        return next_wave_start_educ

    def predict_educ_stop(self, pop):

        next_wave_stop_educ = r_utils.predict_next_timestep_logit(model=self.stop_transition_model,
                                                                  rpy2_modules=self.rpy2_modules,
                                                                  current=pop,
                                                                  dependent='education_state')
        return next_wave_stop_educ