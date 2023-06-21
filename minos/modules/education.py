""" File for adding new cohorts from Understanding Society data to the population"""

import pandas as pd
from minos.modules.base_module import Base

# suppressing a warning that isn't a problem
pd.options.mode.chained_assignment = None # default='warn' #supress SettingWithCopyWarning
import matplotlib.pyplot as plt
from seaborn import catplot
import logging

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
        builder.event.register_listener("time_step", self.on_time_step, priority=2)

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

        #### NOTE ####
        # The age that these qualifications are achieved varies quite a lot in Understanding Society data, but trying
        # to include that variance here would add a level of complexity that is probably not worth the hassle (we're
        # assuming that the long term effects of education on health are more important than if an individual achieved
        # e.g. a level 7 qualification later in life).
        # Therefore, we are making a couple of assumptions on when to transition based on either knowledge of the
        # UK education system, or the average age at which these levels are achieved in the underlying data. Note that
        # the age achieved is 1 year after the qualifications are held to account for the range of dates that
        # individuals answer the survey. These are:
        # Level 1 and 2 - Age 17
        #   1 & 2 are equivalent to GCSEs at different grades, and because young people are required to be in full-time
        #   education until 16 it seems reasonable to assume that everyone will achieve this level.
        # Level 3 - Age 19
        #   Level 3 is equivalent to A-levels, advanced apprenticeships, and baccalaureate's. Government guidelines do
        #   require young people to be in FT education, apprenticeship, or combination of volunteering and PT education,
        #   but there is no guarantee that they will achieve these levels so this is not guaranteed like level 1 or 2.
        # Level 5 - Age 30
        #   Nursing or med quals are a weird one, so this is based on the average age achieve in US as there is large
        #   variance in the data.
        # Level 6 - Age 27
        #   Again basing this on US data as it covers first class degrees but also a range of other qualifications.
        # Level 7 - Age 30
        #   This is an unfortunately difficult decision, and is a bit of a balance between the mean age in US data and
        #   a 'want' to not have respondents in full time education for too long in the model. The mean age this level
        #   is achieved is 32 in the data, but that would mean these people are in FT education from 16-32 which is
        #   not realistic. I think these individuals would most likely have some time in employment between these ages
        #   but that would be very complex to implement.

        # First make sure those who are not at max_educ are still in education in S7_labour_state
        pop = self.population_view.get(event.index, query="alive=='alive' and education_state!=max_educ")
        pop['S7_labour_state'] = 'FT Education'

        # Level 1 is equivalent to GCSEs with grades 3,2,1 (D,E,F,G)
        level1 = self.population_view.get(event.index,
                                          query="alive=='alive' and age >= 17 and S7_labour_state=='FT Education' and max_educ == 1")
        # Update education state and apply back to population view
        level1['education_state'][level1['education_state'] < 1] = 1
        self.population_view.update(level1['education_state'])

        # Level 2 is equivalent to GCSEs with grades 9,8,7,6,5,4 (A*,A,B,C)
        # No need to test max_educ for this one, everyone stays in education to 16 now minimum
        level2 = self.population_view.get(event.index,
                                          query="alive=='alive' and age >= 17 and S7_labour_state=='FT Education' and max_educ >= 2")
        # Update education state and apply back to population view
        level2['education_state'][level2['education_state'] < 2] = 2
        self.population_view.update(level2['education_state'])

        # Level 3 is equivalent to A-level, so make this change by age 19 if max_educ is 3 or larger
        level3 = self.population_view.get(event.index,
                                          query="alive=='alive' and age >= 19 and S7_labour_state=='FT Education' and max_educ >= 3")
        level3['education_state'][level3['education_state'] < 3] = 3
        self.population_view.update(level3['education_state'])

        # Level 6 is 1st degree or teaching qual (not PGCE), so make this change by age 26 if max_educ is 6 or larger
        level6 = self.population_view.get(event.index,
                                          query="alive=='alive' and age >= 26 and S7_labour_state=='FT Education' and max_educ >= 6")
        level6['education_state'][level6['education_state'] < 6] = 6
        self.population_view.update(level6['education_state'])

        # Level 5 is nursing/medical and HE diploma, so make this change by age 30 if max_educ is 5
        level5 = self.population_view.get(event.index,
                                          query="alive=='alive' and age >= 30 and S7_labour_state=='FT Education' and max_educ == 5")
        level5['education_state'][level5['education_state'] < 5] = 5
        self.population_view.update(level5['education_state'])

        # Level 7 is higher degree (masters/PhD), so make this change by age 30 if max_educ is 7
        level7 = self.population_view.get(event.index,
                                          query="alive=='alive' and age >= 30 and S7_labour_state=='FT Education' and max_educ == 7")
        level7['education_state'][level7['education_state'] < 7] = 7
        self.population_view.update(level7['education_state'])

    def plot(self, pop, config):

        file_name = config.output_plots_dir + f"education_barplot_{self.year}.pdf"
        densities = pd.DataFrame(pop['education_state'].value_counts(normalize=True))
        densities.columns = ['densities']
        densities['education_state'] = densities.index
        f = plt.figure()
        cat = catplot(data=densities, y='education_state', x='densities', kind='bar', orient='h')
        plt.savefig(file_name)
        plt.close()