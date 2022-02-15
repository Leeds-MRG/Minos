"""
Module for implementation of BHPS education data to daedalus frame.
"""

import pandas as pd
from vivarium.framework.utilities import rate_to_probability
from pathlib import Path
import random
import numpy as np
from RateTables.EducationRateTable import EducationRateTable
from transitions.education_transitions_empirical import main


class empiricalEducation:
    """ Main class for application of employment data to BHPS."""

    @property
    def name(self):
        return "education"

    def __repr__(self):
        return "Education()"

    @staticmethod
    def write_config(config):
        """ Update config file with what this module needs to run.

        Parameters
        ----------
            config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob.
        Returns
        -------
           config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob with added items needed for this module to run.
        """
        # load in all possible education levels to config
        # need subdictionaries in the future to give each category further attributes e.g. training time.
        education_levels = pd.read_csv("persistent_data/education_levels.csv")
        config.update({
            "education_levels": education_levels
        },
            source=str(Path(__file__).resolve()))

        return config

    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        #asfr_education = EducationRateTable(configuration=config)
        # asfr_mortality.rate_table = asfr_mortality.rate_table.loc["location" == config.location]
        # asfr_education.set_rate_table()
        # simulation._data.write("education_enrollment_rate",
        #                       asfr_education.rate_table)

        return simulation

    def setup(self, builder):
        """ Method for initialising the education module.

        Parameters
        ----------
        builder : vivarium.builder
            `builder` class that coordinates the vivarium microsim.
        Returns
        -------
        None
        """

        # load in any data
        self.builder = builder
        self.config = builder.configuration

        # Reformat education levels csv into a dictionary for easier generation of transition matrices.
        education_levels = self.config.education_levels
        education_levels = education_levels.T
        education_levels.columns = education_levels.loc["name"]
        education_levels = education_levels.drop("name", 0)
        education_levels = education_levels.to_dict()
        self.education_levels = education_levels

        """
        Create new columns to be added by this module. These are columns for:
        - is_student : are they a student?
        - student_duration : How long have they been a student?
        - education_target : What education are they studying for?
        - education_duration : How long does the education they are pursuing take?
        - graduation_month : If their education is time sensitive, which month would they graduate?
          For example, GCSE students will leave school in (roughly) August of their 15/16th year dependent of their 
          birthday / enrollment time.
          Just use modular arithmetic to check if they've been in school for the minimum time required to graduate.
          I.E if they've been in school for at least 15 years from birth then they graduate.
          This is  generally much easier than calculating how many months exactly each simulant will be in school for. 
        """

        columns_created = ["is_student",
                           "student_duration",
                           "education_target",
                           "education_duration",
                           "graduation_month",
                           "graduation_time"]
        # columns viewed in self.population_view later. What is needed in on_time_step to calcuate transitions.
        view_columns = columns_created + ['pidp',
                                        'alive',
                                        'age',
                                        'sex',
                                        'ethnicity',
                                        'education_state',
                                        'labour_state', ]

        self.population_view = builder.population.get_view(view_columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)
        # register value rate producers.
        # one for redeployment and role change.
        self.student_change_rate_producer = builder.value.register_rate_producer('student_enrollment_rate',
                                                                             source=self.calculate_student_change_rate)

        #enrollment lookup table
        #enrollment_data = builder.data.load("education_enrollment_rate")
        #self.enrollment_lookup = builder.lookup.build_table(enrollment_data,
        #                                                           key_columns=['sex', 'ethnicity','education_state'],
        #                                                           parameter_columns=['age', 'year'])


        # CRN stream.
        self.random = builder.randomness.get_stream('education_handler')

        # registering any modifiers.
        # adjusting role and job opportunities depending on education status.
        self.job_change_modifier = builder.value.register_value_modifier("job_change_rate",
                                                                         self.education_job_modifier)
        self.role_change_modifier = builder.value.register_value_modifier("role_change_rate",
                                                                         self.education_role_modifier)
        # register event listeners.
        # same priority as employment. need to consider both at the same time.
        education_time_step = builder.event.register_listener("time_step", self.on_time_step, priority=1)

        # load in any other required components

    def on_initialize_simulants(self, pop_data):
        """ Module for when the vivarium builder.initializes_simulants() is run.

        Parameters
        ----------
        pop_data: vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).

        Returns
        -------
        pop_update : pd.DataFrame
            While not strictly return `pop_update` is the new population of simulants added to the main population
            frame.
        """
        # Fill in placeholder frame with default values.
        pop_update = pd.DataFrame({"is_student" : False,
                                   "student_duration" : 0.,
                                   "education_target" : None,
                                   "education_duration" : 0.,
                                   "graduation_month" : 0,
                                   "graduation_time" : None},
                                  index=pop_data.index)

        # Initiate these columns for when real data is added (I.E. replenishment from US cohorts.).
        if pop_data.user_data["sim_state"] in ["setup", "replenishment"]:

            # Get real cohort data and assign pre-existing students to is_student = True
            pop = self.population_view.get(pop_data.index, "pidp>0")
            is_student = pop.loc[pop["labour_state"] == "Student"].index
            pop.loc[is_student, "is_student"] = True
            student_update = pop_update.loc[is_student]

            # Assign students education targets. What are they studying for?
            # TODO lots of potentially interesting work here in estimating sims education targets better.
            # For now use relatively naive assignment (see self.assign_new_students).
            student_update["education_target"] = self.assign_new_students(pop.loc[is_student])

            # Calculate the length of each persons education target and if they would graduate in a specific month.
            student_update["education_duration"] = student_update["education_target"].apply(lambda x: self.education_levels[x]["education_duration"])
            student_update["graduation_month"] = student_update["education_target"].apply(lambda x: self.education_levels[x]["graduation_month"])

            # Calculate the date each sim will graduate.
            # Some educations are time dependent (e.g. degrees graduate in June)
            # Some are not time dependent (e.g. can graduate with a higher diploma at any point)

            # Calculate naive enrollment date.
            # This is just the event time step.
            # Isn't given on the simulation setup step so use the start time based on the YAML config.
            if pop_data.user_data["sim_state"] == "setup":
                creation_time =  self.config.time.start
                creation_time = pd.to_datetime({"year":[creation_time.year],
                                                "month":[creation_time.month],
                                                "day":[creation_time.day]})
                student_update["graduation_time"] = creation_time[
                    0]  # 0 index here required or values are assigned NaT.

            # Otherwise the simulants creaetion time is given to calculate a rough graduation time from.
            else:
                student_update["graduation_time"] = pop_data.user_data["creation_time"]

            # Given their enrollment data calculate a more precise graduation time.
            # This will assign students to graduate in a specific month if required and remove some of the time required
            # for an agent if they are say 18 and obviously most of the way through their A-levels.
            student_update["graduation_time"] += student_update["education_duration"].values.astype("timedelta64[M]")
            student_update["graduation_time"] = self.calculate_graduation_time(student_update)

            # TODO Naively assign students to the start of their education. Can be done better.
            student_update["student_duration"] = 0
            student_update["student_duration"] = self.calculate_student_duration_time(student_update, creation_time,
                                                                                      pop.loc[is_student])
            # Put the updated students back into the main population update frame.
            pop_update.loc[is_student] = student_update

        # Initiate these columns for new births.
        # Default newborns to students with no education working towards GCSEs.
        elif pop_data.user_data["cohort_type"] == "births":

            # Assign newborns to automatically enroll in GCSEs.
            pop_update["is_student"] = True
            pop_update["education_state"] = "Less than GCSE"
            pop_update["student_duration"] = pop_data.user_data["creation_time"]

            # Update their eduation target (GCSE) and associated parameters for what month they graduate and the
            # number of months the course takes.
            pop_update["education_target"] = "GCSE"
            pop_update["graduation_month"] = 8.
            pop_update["education_duration"] = 16*12.

            # Calculate time they graduate. I.E. roughly 16 years after GCSE
            birth_time = pop_data.user_data["creation_time"]
            # Calculate graduation time for GCSE
            graduation_time = birth_time + pd.offsets.DateOffset(years=16)

            # They've been a student for 0 months.
            pop_update["student_duration"] = 0
            # Naively assume it takes exactly 16 years to graduate.
            pop_update["graduation_time"] = graduation_time
            # Update the naive assumption such that they graduate in July in 15-16 years time.
            pop_update["graduation_time"] = self.calculate_graduation_time(pop_update)

        # Add new cohort to population frame.
        self.population_view.update(pop_update)

        # No longer needed. Bug was occuring in that this data couldnt be loaded.
        # Now replenishment module runs on_initialize_simulants first this isnt a problem.

        # if pop_data.user_data["sim_state"] == "setup":
        #     # Update any dummy columns with real data if applicable.
        #     # I cannot for the life of me figure out why they wont just be added normally in pop_view.update.
        #     self.update_real_columns(pop_data)

    def calculate_graduation_time(self, pop):
        """ A function for calculating the time in months until a simulant graduates from birth.

        For example assume all GCSE students graduate in August.
        If a person was born in August it would take them 16 years 0 months to graduate.
        This function should then output exactly 16*12 months.
        Likewise if a person is born in September then it would take them 16 years and 11 months to graduate.

        Parameters
        ----------
        pop : pandas.DataFrane
            The `pop` of simulants for the main population frame
            to calculate the time until graduation for.

        Returns
        -------
        grad_times : pd.Series
            `grad_times` A series of graduation times for the specified population.
        """
        # Get the naive graduation time and the time specific graduation months (if any).
        grad_times = pop["graduation_time"]
        grad_month = pop["graduation_month"]

        # Has anyone enrolled after the annual graduation time?
        # E.G. GCSEs graduate in August so anyone born after September will graduate next year

        enroll_after_time_grad = grad_times.dt.month > grad_month
        # Set the graduation months. E.g. GCSEs graduate in August.
        grad_times_fixed = pd.to_datetime(
        {'year': grad_times.dt.year,
         'month': grad_month,
         'day': 1})

        # If born after the graduate date then push back a year later. E.G. GCSE born after september 2000 graduates
        # in August 2017 between 16 years 9 months and 17 years of age.
        grad_times.loc[enroll_after_time_grad] = grad_times_fixed
        grad_times.loc[enroll_after_time_grad] += pd.offsets.DateOffset(years=1)
        # Return new grad times to attach to update frame.
        return grad_times

    def calculate_student_duration_time(self, pop_update, creation_time, pop = None):
        """ Calculate how long the sims have been in education.

        For births all sims have the same student duration of 0.

        For replenishment some students may be already some way through
        their education. Since there is no information on this in the US
        dataset have to assume most people start at 0.
        However, this can be inferred for some students.
        For example, GCSE students are aged 15-16 in the US dataset.
        A 16 year old is clearly going to graduate within the year and
        so their student duration must be reflected to update this.
        The proximity to the maximum age of their respective education is used
        to estimate this. Someone who is 16 is within a year of the absolute
        maximum age of 17 for GCSE graduation so must be at least 15 years
        (from birth) into their GCSEs.

        Parameters
        ----------
        pop_update, pop : pandas.DataFrame
            The new columns added to the population data frame `pop_update`.
            If adding in real data also include the real `pop` data to use their ages.

        Returns
        -------

        """
        education_levels = self.education_levels # dict of education tiers
        ages = pop["age"] # get ages from real population data (if any).
        # get the maximum age of students for their respective education targets
        max_ages = pop_update["education_target"].apply(lambda x: education_levels[x]["age_max"])
        min_ages = pop_update["education_target"].apply(lambda x: education_levels[x]["age_min"])
        education_duration = pop_update["education_target"].apply(lambda x: education_levels[x]["education_duration"])

        # How many years until they hit the upper age bound for their education target.
        # If they're close to the bound it suggests they're part way through the education already.
        age_diffs = max_ages - ages

        # Has a sim already started their education? I.E. can they not complete their education before reaching the
        # maximum age?
        must_started = (12 * age_diffs) < education_duration

        # Calculate how many months into studies if they've already started.
        must_started_years_diff = (education_duration - (age_diffs * 12)).loc[must_started]


        graduation_times = pop_update["graduation_time"]
        duration_times = pd.DataFrame(index=pop_update.index)
        duration_times.loc[must_started, "duration_times"] = graduation_times.loc[must_started] + must_started_years_diff.subtract(1).values.astype('timedelta64[Y]')

        #
        duration_times.loc[~must_started, "duration_times"] = 0
        return duration_times

    def on_time_step(self, event):
        """ What happens in the employment module on every simulation timestep.

        Parameters
        ----------
        event : vivarium.builder.event
            The time_step `event` is used here. I.E whenever the simulation is stepped forwards.
        Returns
        -------

        """

        # First update the non_students.
        # Test if they enter education or stay put.
        # TODO separate pops for labour state change and job change
        pop = self.population_view.get(event.index, query="alive =='alive'")

        # Calculate probabilities of enrolling as a student using rate producer
        # Choose to enroll or not using vivarium's generalised multinomial randomg generator vivarium.random.choice.
        student_change_df = pd.DataFrame(index=pop.index)
        student_change_df["change"] = rate_to_probability(pd.DataFrame(self.student_change_rate_producer(pop.index)))
        student_change_df["no_change"] = 1 - student_change_df["change"]
        student_change_df["choice"] = self.random.choice(student_change_df.index, student_change_df.columns, student_change_df)

        # Subset of population who enroll.
        new_students = student_change_df.loc[student_change_df["choice"]=="change"]

        # Assign new education as necessary.
        # Will change their student status to true and determine their new status when they graduate.
        pop.loc[new_students.index, "is_student"] = True
        pop.loc[new_students.index, "education_target"] = self.assign_new_students(pop.loc[new_students.index])
        pop["education_duration"] = pop.loc[new_students.index, "education_target"].apply(lambda x:
                                                                                          self.education_levels[x]["education_duration"])
        # Update change in student status.
        self.population_view.update(pop[['is_student', "student_duration", "education_target", "education_duration"]])

        # Now the students. add one month to their student duration.
        # TODO add dropouts?
        pop = self.population_view.get(event.index, query="alive =='alive' and age > 16 and education_duration>0")
        # Add another time step to current students or graduate them if they've reached their education duration.
        # TODO make student duration work.
        #pop["student_duration"] = pop["student_duration"] + 1
        #graduates = self.graduate_students(event, pop)
        graduates = pop.loc[pop["student_duration"]==pop["education_duration"]]
        # Graduate anyone. update their education level and reset student counters
        if len(graduates.index) > 0:
            pop.loc[graduates.index, "education_state"] = pop.loc[graduates.index, "education_target"]
            pop.loc[graduates.index, "education_target"] = None
            pop.loc[graduates.index, "is_student"] = False
            pop.loc[graduates.index, "education_duration"] = 0.
            pop.loc[graduates.index, "student_duration"] = 0.

        # Update pop with student progression and new graduates.
        self.population_view.update(pop[["education_state", "student_duration", "education_target", "is_student",
                                         "education_duration"]])

    def calculate_student_change_rate(self, index):
        """ Calculate probabilities of moving to new job sector.

        Parameters
        ----------
        index : pandas.DataFrame.index
            `index` series indicating which agents to calculate the death rates of.
        Returns
        -------
        job_change_rates: pd.DataFrame
            `job_change_rates` indicates the probability of changing job sectors. 1 is change 0 is stay put.
        """
        student_change_rates = pd.DataFrame({"student_state": 0.5}, index=index)
        return student_change_rates

    def education_job_modifier(self, index, values):
        """ Adjust depression tier1 rates based on employment states

        Note this function requires arguments that match those of mortality.calculate_mortality_rate
        and an addition values argument (not name dependent) that gives the current values
        output by the mortality rate producer.

        Parameters
        ----------
        index : pandas.core.indexes.numeric.Int64Index
            `index` which rows of population frame apply rate modification to.
        values : pandas.core.frame.DataFrame

            the previous `values` output by the mortality_rate value producer.
            More generally the producer defined in the register_value_modifier
            method with this as its minos.

        Returns
        -------
        values : pandas.core.frame.DataFrame
            The modified `values` handed back to the builder for application in
            mortality's on_time_step. In theory, those with higher depression states are
            at higher risk of dying.
        """

        return values

    def education_role_modifier(self, index, values):
        """ Adjust employment role rates based on education status

        Note this function requires arguments that match those of the producer it is modifying
        (employment role producer)
        and an addition values argument (not name dependent) that gives the current values
        output said rate producer.

        Parameters
        ----------
        index : pandas.core.indexes.numeric.Int64Index
            `index` which rows of population frame apply rate modification to.
        values : pandas.core.frame.DataFrame

            the previous `values` output by the value producer.

        Returns
        -------
        values : pandas.core.frame.DataFrame
            The modified `values` handed back to the builder for application in
            its rate_producer in on_time_step. In theory, those with higher education states
            get access to more job sectors.
        """
        return values

    def assign_new_students(self, new_students):
        """ Assign new student education target based on some transition matrix

        Parameters
        ----------
        new_students : pd.DataFrame
            `new_students` population to decide changes in educatio target for.

        Returns
        -------
        new_educations: pd.DataFrame
            `new_educations` a vector of pop.index length assigning each person to a student state.
        """
        # Load in attributes for each education type.
        education_levels = self.education_levels
        # Shorthand name for current education states of enrolling students.
        current_levels = new_students["education_state"]

        # TODO this dummy frame does not encorporate age/sex/ethnicity properly. For now this is just a framework for
        #  better calibrated transitions in the future.

        # Placeholder frame for education transitions generated in generate_education_target_rates.py
        transition_dict = pd.read_csv("persistent_data/education_enrollment_rate_table.csv", index_col=[0, 1])
        #transition_dict = transition_dict.to_dict("split")
        #transition_dict = dict(zip(transition_dict["index"], transition_dict["data"]))

        # Loop over each simulant. Assign 1 if they have the required education to pursure each possible education
        # state.

        def grab_transition_row(x, transition_dict):
            row = transition_dict.loc[x["ethnicity"]].loc[x["sex"]].iloc[int(x["age"])]
            return np.fromstring(row[1:-1], sep=',')

        transition_matrix_rows = new_students.apply(lambda x: grab_transition_row(x,
                                                                                  transition_dict), axis=1)
        transition_matrix_rows = np.vstack(transition_matrix_rows)
        transition_matrix = pd.DataFrame(transition_matrix_rows, index = new_students.index, columns=education_levels.keys())

        required_qual_levels = current_levels.apply(lambda x: education_levels[x]["required_level"])
        qual_levels = current_levels.apply(lambda x: education_levels[x]["education_level"])

        for column in transition_matrix.columns:
            # Make sure nobody enrolls into no education.
            if column == "Less than GCSE":
                continue

            # required qualification and qualifaction level on graduation for each given education state.
            required_qual_level = education_levels[column]["required_level"]
            qual_level = education_levels[column]["education_level"]

            # Check who does not have the required qualifications to enroll.
            # Set it so they cannot enroll in that which they are not qualified for.
            who_unqualified = qual_levels < required_qual_level

            # Make sure noone can repeat their previous education again.
            # TODO slightly naive as people can have two degrees.
            # This is more specifically for values up to A-level.
            who_repeating = current_levels == column

            # Make sure people dont go too far back in the qualifications.
            # This stops degree grads from retaking A-levels.
            # This is only necessary if the who_unqualified uses <= rather than !=.
            # For now only using != as it is simpler but future requires relaxing of this condition so
            # say a degree grad can change careers into teaching.
            # TODO better conditioning for graduation under 18 vs over 18.
            # GCSE -> A-level -> degree is very linear and age dependent vs
            # getting a higher diploma at 35.
            # Part of a better transition matrix would incorporate this.

            #who_overqualified = required_qual_levels <= required_qual_level
            # dummy values that lets everyone past for testing.
            who_overqualified = required_qual_levels >= required_qual_level

            # Who is unqualified, over qualified, or would be repeating the same education again.
            who_ineligible = who_unqualified * who_repeating
            who_ineligible *= who_overqualified
            # Set anyone ineligible to study for a qualification unable to move to it.
            transition_matrix.loc[who_ineligible, column] *= 0

        new_targets = self.random.choice(transition_matrix.index, transition_matrix.columns, transition_matrix)
        new_educations = pd.DataFrame({'education_target': new_targets},
                                  index=new_students.index)
        return new_educations

class Education:
    """ Main class for application of employment data to BHPS."""

    @property
    def name(self):
        return "education"

    def __repr__(self):
        return "Education()"

    @staticmethod
    def write_config(config):
        """ Update config file with what this module needs to run.

        Parameters
        ----------
            config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob.
        Returns
        -------
           config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob with added items needed for this module to run.
        """
        # load in all possible education levels to config
        # need subdictionaries in the future to give each category further attributes e.g. training time.
        education_levels = pd.read_csv("persistent_data/education_levels.csv")
        config.update({
            "education_levels": education_levels
        },
            source=str(Path(__file__).resolve()))

        return config

    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        #asfr_education = EducationRateTable(configuration=config)
        # asfr_mortality.rate_table = asfr_mortality.rate_table.loc["location" == config.location]
        # asfr_education.set_rate_table()
        # simulation._data.write("education_enrollment_rate",
        #                       asfr_education.rate_table)

        return simulation

    def setup(self, builder):
        """ Method for initialising the education module.

        Parameters
        ----------
        builder : vivarium.builder
            `builder` class that coordinates the vivarium microsim.
        Returns
        -------
        None
        """

        # load in any data
        self.builder = builder
        self.config = builder.configuration

        # Reformat education levels csv into a dictionary for easier generation of transition matrices.
        education_levels = self.config.education_levels
        education_levels = education_levels.T
        education_levels.columns = education_levels.loc["name"]
        education_levels = education_levels.drop("name", 0)
        education_levels = education_levels.to_dict()
        self.education_levels = education_levels

        """
        Create new columns to be added by this module. These are columns for:
        - is_student : are they a student?
        - student_duration : How long have they been a student?
        - education_target : What education are they studying for?
        - education_duration : How long does the education they are pursuing take?
        - graduation_month : If their education is time sensitive, which month would they graduate?
          For example, GCSE students will leave school in (roughly) August of their 15/16th year dependent of their 
          birthday / enrollment time.
          Just use modular arithmetic to check if they've been in school for the minimum time required to graduate.
          I.E if they've been in school for at least 15 years from birth then they graduate.
          This is  generally much easier than calculating how many months exactly each simulant will be in school for. 
        """

        columns_created = ["is_student",
                           "student_duration",
                           "education_target",
                           "education_duration",
                           "graduation_month",
                           "graduation_time"]
        # columns viewed in self.population_view later. What is needed in on_time_step to calcuate transitions.
        view_columns = columns_created + ['pidp',
                                        'alive',
                                        'age',
                                        'sex',
                                        'ethnicity',
                                        'education_state',
                                        'labour_state', ]

        self.population_view = builder.population.get_view(view_columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)
        # register value rate producers.
        # one for redeployment and role change.
        self.student_change_rate_producer = builder.value.register_rate_producer('student_enrollment_rate',
                                                                             source=self.calculate_student_change_rate)

        #enrollment lookup table
        #enrollment_data = builder.data.load("education_enrollment_rate")
        #self.enrollment_lookup = builder.lookup.build_table(enrollment_data,
        #                                                           key_columns=['sex', 'ethnicity','education_state'],
        #                                                           parameter_columns=['age', 'year'])


        # CRN stream for the module. may be worth disabling later for "true" random employment.
        self.random = builder.randomness.get_stream('education_handler')
        # registering any modifiers.
        # adjusting role and job opportunities depending on education status.
        #
        self.job_change_modifier = builder.value.register_value_modifier("job_change_rate",
                                                                         self.education_job_modifier)
        self.role_change_modifier = builder.value.register_value_modifier("role_change_rate",
                                                                         self.education_role_modifier)
        # register event listeners.
        # same priority as employment. need to consider both at the same time.
        employment_time_step = builder.event.register_listener("time_step", self.on_time_step, priority=1)

        # load in any other required components

    def on_initialize_simulants(self, pop_data):
        """ Module for when the vivarium builder.initializes_simulants() is run.

        Parameters
        ----------
        pop_data: vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).

        Returns
        -------
        pop_update : pd.DataFrame
            While not strictly return `pop_update` is the new population of simulants added to the main population
            frame.
        """
        # Fill in placeholder frame with default values.
        pop_update = pd.DataFrame({"is_student" : False,
                                   "student_duration" : 0.,
                                   "education_target" : None,
                                   "education_duration" : 0.,
                                   "graduation_month" : 0,
                                   "graduation_time" : None},
                                  index=pop_data.index)

        # Initiate these columns for when real data is added (I.E. replenishment from US cohorts.).
        if pop_data.user_data["sim_state"] == "setup" or pop_data.user_data["cohort_type"] == "replenishment":

            # Get real cohort data and assign pre-existing students to is_student = True
            pop = self.population_view.get(pop_data.index, "pidp>0")
            is_student = pop.loc[pop["labour_state"] == "Student"].index
            pop.loc[is_student, "is_student"] = True
            student_update = pop_update.loc[is_student]

            # Assign students education targets. What are they studying for?
            # TODO lots of potentially interesting work here in estimating sims education targets better.
            # For now use relatively naive assignment (see self.assign_new_students).
            student_update["education_target"] = self.assign_new_students(pop.loc[is_student])

            # Calculate the length of each persons education target and if they would graduate in a specific month.
            student_update["education_duration"] = student_update["education_target"].apply(lambda x: self.education_levels[x]["education_duration"])
            student_update["graduation_month"] = student_update["education_target"].apply(lambda x: self.education_levels[x]["graduation_month"])

            # Calculate the date each sim will graduate.
            # Some educations are time dependent (e.g. degrees graduate in June)
            # Some are not time dependent (e.g. can graduate with a higher diploma at any point)

            # Calculate naive enrollment date.
            # This is just the event time step.
            # Isn't given on the simulation setup step so use the start time based on the YAML config.
            if pop_data.user_data["sim_state"] == "setup":
                creation_time =  self.config.time.start
                creation_time = pd.to_datetime({"year":[creation_time.year],
                                                "month":[creation_time.month],
                                                "day":[creation_time.day]})
                student_update["graduation_time"] = creation_time[
                    0]  # 0 index here required or values are assigned NaT.

            # Otherwise the simulants creaetion time is given to calculate a rough graduation time from.
            else:
                student_update["graduation_time"] = pop_data.user_data["creation_time"]

            # Given their enrollment data calculate a more precise graduation time.
            # This will assign students to graduate in a specific month if required and remove some of the time required
            # for an agent if they are say 18 and obviously most of the way through their A-levels.
            student_update["graduation_time"] += student_update["education_duration"].values.astype("timedelta64[M]")
            student_update["graduation_time"] = self.calculate_graduation_time(student_update)

            # TODO Naively assign students to the start of their education. Can be done better.
            student_update["student_duration"] = 0
            student_update["student_duration"] = self.calculate_student_duration_time(student_update, creation_time,
                                                                                      pop.loc[is_student])
            # Put the updated students back into the main population update frame.
            pop_update.loc[is_student] = student_update

        # Initiate these columns for new births.
        # Default newborns to students with no education working towards GCSEs.
        elif pop_data.user_data["cohort_type"] == "births":

            # Assign newborns to automatically enroll in GCSEs.
            pop_update["is_student"] = True
            pop_update["education_state"] = "Less than GCSE"
            pop_update["student_duration"] = pop_data.user_data["creation_time"]

            # Update their eduation target (GCSE) and associated parameters for what month they graduate and the
            # number of months the course takes.
            pop_update["education_target"] = "GCSE"
            pop_update["graduation_month"] = 8.
            pop_update["education_duration"] = 16*12.

            # Calculate time they graduate. I.E. roughly 16 years after GCSE
            birth_time = pop_data.user_data["creation_time"]
            # Calculate graduation time for GCSE
            graduation_time = birth_time + pd.offsets.DateOffset(years=16)

            # They've been a student for 0 months.
            pop_update["student_duration"] = 0
            # Naively assume it takes exactly 16 years to graduate.
            pop_update["graduation_time"] = graduation_time
            # Update the naive assumption such that they graduate in July in 15-16 years time.
            pop_update["graduation_time"] = self.calculate_graduation_time(pop_update)

        # Add new cohort to population frame.
        self.population_view.update(pop_update)

        # No longer needed. Bug was occuring in that this data couldnt be loaded.
        # Now replenishment module runs on_initialize_simulants first this isnt a problem.

        # if pop_data.user_data["sim_state"] == "setup":
        #     # Update any dummy columns with real data if applicable.
        #     # I cannot for the life of me figure out why they wont just be added normally in pop_view.update.
        #     self.update_real_columns(pop_data)

    def calculate_graduation_time(self, pop):
        """ A function for calculating the time in months until a simulant graduates from birth.

        For example assume all GCSE students graduate in August.
        If a person was born in August it would take them 16 years 0 months to graduate.
        This function should then output exactly 16*12 months.
        Likewise if a person is born in September then it would take them 16 years and 11 months to graduate.

        Parameters
        ----------
        pop : pandas.DataFrane
            The `pop` of simulants for the main population frame
            to calculate the time until graduation for.

        Returns
        -------
        grad_times : pd.Series
            `grad_times` A series of graduation times for the specified population.
        """
        # Get the naive graduation time and the time specific graduation months (if any).
        grad_times = pop["graduation_time"]
        grad_month = pop["graduation_month"]

        # Has anyone enrolled after the annual graduation time?
        # E.G. GCSEs graduate in August so anyone born after September will graduate next year

        enroll_after_time_grad = grad_times.dt.month > grad_month
        # Set the graduation months. E.g. GCSEs graduate in August.
        grad_times_fixed = pd.to_datetime(
        {'year': grad_times.dt.year,
         'month': grad_month,
         'day': 1})

        # If born after the graduate date then push back a year later. E.G. GCSE born after september 2000 graduates
        # in August 2017 between 16 years 9 months and 17 years of age.
        grad_times.loc[enroll_after_time_grad] = grad_times_fixed
        grad_times.loc[enroll_after_time_grad] += pd.offsets.DateOffset(years=1)
        # Return new grad times to attach to update frame.
        return grad_times

    def calculate_student_duration_time(self, pop_update, creation_time, pop = None):
        """ Calculate how long the sims have been in education.

        For births all sims have the same student duration of 0.

        For replenishment some students may be already some way through
        their education. Since there is no information on this in the US
        dataset have to assume most people start at 0.
        However, this can be inferred for some students.
        For example, GCSE students are aged 15-16 in the US dataset.
        A 16 year old is clearly going to graduate within the year and
        so their student duration must be reflected to update this.
        The proximity to the maximum age of their respective education is used
        to estimate this. Someone who is 16 is within a year of the absolute
        maximum age of 17 for GCSE graduation so must be at least 15 years
        (from birth) into their GCSEs.

        Parameters
        ----------
        pop_update, pop : pandas.DataFrame
            The new columns added to the population data frame `pop_update`.
            If adding in real data also include the real `pop` data to use their ages.

        Returns
        -------

        """
        education_levels = self.education_levels # dict of education tiers
        ages = pop["age"] # get ages from real population data (if any).
        # get the maximum age of students for their respective education targets
        max_ages = pop_update["education_target"].apply(lambda x: education_levels[x]["age_max"])
        min_ages = pop_update["education_target"].apply(lambda x: education_levels[x]["age_min"])
        education_duration = pop_update["education_target"].apply(lambda x: education_levels[x]["education_duration"])

        # How many years until they hit the upper age bound for their education target.
        # If they're close to the bound it suggests they're part way through the education already.
        age_diffs = max_ages - ages

        # Has a sim already started their education? I.E. can they not complete their education before reaching the
        # maximum age?
        must_started = (12 * age_diffs) < education_duration

        # Calculate how many months into studies if they've already started.
        must_started_years_diff = (education_duration - (age_diffs * 12)).loc[must_started]


        graduation_times = pop_update["graduation_time"]
        duration_times = pd.DataFrame(index=pop_update.index)
        duration_times.loc[must_started, "duration_times"] = graduation_times.loc[must_started] + must_started_years_diff.subtract(1).values.astype('timedelta64[Y]')

        #
        duration_times.loc[~must_started, "duration_times"] = 0
        return duration_times

    def on_time_step(self, event):
        """ What happens in the employment module on every simulation timestep.

        Parameters
        ----------
        event : vivarium.builder.event
            The time_step `event` is used here. I.E whenever the simulation is stepped forwards.
        Returns
        -------

        """

        # First update the non_students.
        # Test if they enter education or stay put.
        # TODO separate pops for labour state change and job change
        pop = self.population_view.get(event.index, query="alive =='alive'")

        # Calculate probabilities of enrolling as a student using rate producer
        # Choose to enroll or not using vivarium's generalised multinomial randomg generator vivarium.random.choice.
        student_change_df = pd.DataFrame(index=pop.index)
        student_change_df["change"] = rate_to_probability(pd.DataFrame(self.student_change_rate_producer(pop.index)))
        student_change_df["no_change"] = 1 - student_change_df["change"]
        student_change_df["choice"] = self.random.choice(student_change_df.index, student_change_df.columns, student_change_df)

        # Subset of population who enroll.
        new_students = student_change_df.loc[student_change_df["choice"]=="change"]

        # Assign new education as necessary.
        # Will change their student status to true and determine their new status when they graduate.
        pop.loc[new_students.index, "is_student"] = True
        pop.loc[new_students.index, "education_target"] = self.assign_new_students(pop.loc[new_students.index])
        pop["education_duration"] = pop.loc[new_students.index, "education_target"].apply(lambda x:
                                                                                          self.education_levels[x]["education_duration"])
        # Update change in student status.
        self.population_view.update(pop[['is_student', "student_duration", "education_target", "education_duration"]])

        # Now the students. add one month to their student duration.
        # TODO add dropouts?
        pop = self.population_view.get(event.index, query="alive =='alive' and age > 16 and education_duration>0")
        # Add another time step to current students or graduate them if they've reached their education duration.
        # TODO make student duration work.
        #pop["student_duration"] = pop["student_duration"] + 1
        #graduates = self.graduate_students(event, pop)
        graduates = pop.loc[pop["student_duration"]==pop["education_duration"]]
        # Graduate anyone. update their education level and reset student counters
        if len(graduates.index) > 0:
            pop.loc[graduates.index, "education_state"] = pop.loc[graduates.index, "education_target"]
            pop.loc[graduates.index, "education_target"] = None
            pop.loc[graduates.index, "is_student"] = False
            pop.loc[graduates.index, "education_duration"] = 0.
            pop.loc[graduates.index, "student_duration"] = 0.

        # Update pop with student progression and new graduates.
        self.population_view.update(pop[["education_state", "student_duration", "education_target", "is_student",
                                         "education_duration"]])

    def calculate_student_change_rate(self, index):
        """ Calculate probabilities of moving to new job sector.

        Parameters
        ----------
        index : pandas.DataFrame.index
            `index` series indicating which agents to calculate the death rates of.
        Returns
        -------
        job_change_rates: pd.DataFrame
            `job_change_rates` indicates the probability of changing job sectors. 1 is change 0 is stay put.
        """
        student_change_rates = pd.DataFrame({"student_state": 0.5}, index=index)
        return student_change_rates

    def education_job_modifier(self, index, values):
        """ Adjust depression tier1 rates based on employment states

        Note this function requires arguments that match those of mortality.calculate_mortality_rate
        and an addition values argument (not name dependent) that gives the current values
        output by the mortality rate producer.

        Parameters
        ----------
        index : pandas.core.indexes.numeric.Int64Index
            `index` which rows of population frame apply rate modification to.
        values : pandas.core.frame.DataFrame

            the previous `values` output by the mortality_rate value producer.
            More generally the producer defined in the register_value_modifier
            method with this as its minos.

        Returns
        -------
        values : pandas.core.frame.DataFrame
            The modified `values` handed back to the builder for application in
            mortality's on_time_step. In theory, those with higher depression states are
            at higher risk of dying.
        """

        return values

    def education_role_modifier(self, index, values):
        """ Adjust employment role rates based on education status

        Note this function requires arguments that match those of the producer it is modifying
        (employment role producer)
        and an addition values argument (not name dependent) that gives the current values
        output said rate producer.

        Parameters
        ----------
        index : pandas.core.indexes.numeric.Int64Index
            `index` which rows of population frame apply rate modification to.
        values : pandas.core.frame.DataFrame

            the previous `values` output by the value producer.

        Returns
        -------
        values : pandas.core.frame.DataFrame
            The modified `values` handed back to the builder for application in
            its rate_producer in on_time_step. In theory, those with higher education states
            get access to more job sectors.
        """
        return values

    def assign_new_students(self, new_students):
        """ Assign new student education target based on some transition matrix

        Parameters
        ----------
        new_students : pd.DataFrame
            `new_students` population to decide changes in educatio target for.

        Returns
        -------
        new_educations: pd.DataFrame
            `new_educations` a vector of pop.index length assigning each person to a student state.
        """
        # Load in attributes for each education type.
        education_levels = self.education_levels
        # Shorthand name for current education states of enrolling students.
        current_levels = new_students["education_state"]

        # TODO this dummy frame does not encorporate age/sex/ethnicity properly. For now this is just a framework for
        #  better calibrated transitions in the future.

        # Placeholder frame for education transitions generated in generate_education_target_rates.py
        transition_dict = pd.read_csv("persistent_data/education_enrollment_rate_table.csv", index_col=[0, 1])
        #transition_dict = transition_dict.to_dict("split")
        #transition_dict = dict(zip(transition_dict["index"], transition_dict["data"]))

        # Loop over each simulant. Assign 1 if they have the required education to pursure each possible education
        # state.

        def grab_transition_row(x, transition_dict):
            row = transition_dict.loc[x["ethnicity"]].loc[x["sex"]].iloc[int(x["age"])]
            return np.fromstring(row[1:-1], sep=',')

        transition_matrix_rows = new_students.apply(lambda x: grab_transition_row(x,
                                                                                  transition_dict), axis=1)
        transition_matrix_rows = np.vstack(transition_matrix_rows)
        transition_matrix = pd.DataFrame(transition_matrix_rows, index = new_students.index, columns=education_levels.keys())

        required_qual_levels = current_levels.apply(lambda x: education_levels[x]["required_level"])
        qual_levels = current_levels.apply(lambda x: education_levels[x]["education_level"])

        for column in transition_matrix.columns:
            # Make sure nobody enrolls into no education.
            if column == "Less than GCSE":
                continue

            # required qualification and qualifaction level on graduation for each given education state.
            required_qual_level = education_levels[column]["required_level"]
            qual_level = education_levels[column]["education_level"]

            # Check who does not have the required qualifications to enroll.
            # Set it so they cannot enroll in that which they are not qualified for.
            who_unqualified = qual_levels < required_qual_level

            # Make sure noone can repeat their previous education again.
            # TODO slightly naive as people can have two degrees.
            # This is more specifically for values up to A-level.
            who_repeating = current_levels == column

            # Make sure people dont go too far back in the qualifications.
            # This stops degree grads from retaking A-levels.
            # This is only necessary if the who_unqualified uses <= rather than !=.
            # For now only using != as it is simpler but future requires relaxing of this condition so
            # say a degree grad can change careers into teaching.
            # TODO better conditioning for graduation under 18 vs over 18.
            # GCSE -> A-level -> degree is very linear and age dependent vs
            # getting a higher diploma at 35.
            # Part of a better transition matrix would incorporate this.

            #who_overqualified = required_qual_levels <= required_qual_level
            # dummy values that lets everyone past for testing.
            who_overqualified = required_qual_levels >= required_qual_level

            # Who is unqualified, over qualified, or would be repeating the same education again.
            who_ineligible = who_unqualified * who_repeating
            who_ineligible *= who_overqualified
            # Set anyone ineligible to study for a qualification unable to move to it.
            transition_matrix.loc[who_ineligible, column] *= 0

        new_targets = self.random.choice(transition_matrix.index, transition_matrix.columns, transition_matrix)
        new_educations = pd.DataFrame({'education_target': new_targets},
                                  index=new_students.index)
        return new_educations


class Education:
    """ Main class for application of employment data to BHPS."""

    @property
    def name(self):
        return "education"

    def __repr__(self):
        return "Education()"

    @staticmethod
    def write_config(config):
        """ Update config file with what this module needs to run.

        Parameters
        ----------
            config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob.
        Returns
        -------
           config : vivarium.config_tree.ConfigTree
            Config yaml tree for AngryMob with added items needed for this module to run.
        """
        # load in all possible education levels to config
        # need subdictionaries in the future to give each category further attributes e.g. training time.
        education_levels = pd.read_csv("persistent_data/education_levels.csv")
        config.update({
            "education_levels": education_levels
        },
            source=str(Path(__file__).resolve()))

        return config

    def pre_setup(self, config, simulation):
        """ Load in anything required for the module to run.

        Parameters
        ----------
        config : vivarium.config_tree.ConfigTree
            Config yaml tree for vivarium with the items needed for this module to run

        simulation : vivarium.interface.interactive.InteractiveContext
            The initiated vivarium simulation object before simulation.setup() is run.

        Returns
        -------
            simulation : vivarium.interface.interactive.InteractiveContext
                The initiated vivarium simulation object with anything needed to run the module.
                E.g. rate tables.
        """
        #asfr_education = EducationRateTable(configuration=config)
        # asfr_mortality.rate_table = asfr_mortality.rate_table.loc["location" == config.location]
        # asfr_education.set_rate_table()
        # simulation._data.write("education_enrollment_rate",
        #                       asfr_education.rate_table)

        return simulation

    def setup(self, builder):
        """ Method for initialising the education module.

        Parameters
        ----------
        builder : vivarium.builder
            `builder` class that coordinates the vivarium microsim.
        Returns
        -------
        None
        """

        # load in any data
        self.builder = builder
        self.config = builder.configuration

        # Reformat education levels csv into a dictionary for easier generation of transition matrices.
        education_levels = self.config.education_levels
        education_levels = education_levels.T
        education_levels.columns = education_levels.loc["name"]
        education_levels = education_levels.drop("name", 0)
        education_levels = education_levels.to_dict()
        self.education_levels = education_levels

        """
        Create new columns to be added by this module. These are columns for:
        - is_student : are they a student?
        - student_duration : How long have they been a student?
        - education_target : What education are they studying for?
        - education_duration : How long does the education they are pursuing take?
        - graduation_month : If their education is time sensitive, which month would they graduate?
          For example, GCSE students will leave school in (roughly) August of their 15/16th year dependent of their 
          birthday / enrollment time.
          Just use modular arithmetic to check if they've been in school for the minimum time required to graduate.
          I.E if they've been in school for at least 15 years from birth then they graduate.
          This is  generally much easier than calculating how many months exactly each simulant will be in school for. 
        """

        columns_created = ["is_student",
                           "student_duration",
                           "education_target",
                           "education_duration",
                           "graduation_month",
                           "graduation_time"]
        # columns viewed in self.population_view later. What is needed in on_time_step to calcuate transitions.
        view_columns = columns_created + ['pidp',
                                        'alive',
                                        'age',
                                        'sex',
                                        'ethnicity',
                                        'education_state',
                                        'labour_state', ]

        self.population_view = builder.population.get_view(view_columns)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)
        # register value rate producers.
        # one for redeployment and role change.
        self.student_change_rate_producer = builder.value.register_rate_producer('student_enrollment_rate',
                                                                             source=self.calculate_student_change_rate)

        #enrollment lookup table
        #enrollment_data = builder.data.load("education_enrollment_rate")
        #self.enrollment_lookup = builder.lookup.build_table(enrollment_data,
        #                                                           key_columns=['sex', 'ethnicity','education_state'],
        #                                                           parameter_columns=['age', 'year'])


        # CRN stream for the module. may be worth disabling later for "true" random employment.
        self.random = builder.randomness.get_stream('education_handler')
        # registering any modifiers.
        # adjusting role and job opportunities depending on education status.
        #
        self.job_change_modifier = builder.value.register_value_modifier("job_change_rate",
                                                                         self.education_job_modifier)
        self.role_change_modifier = builder.value.register_value_modifier("role_change_rate",
                                                                         self.education_role_modifier)
        # register event listeners.
        # same priority as employment. need to consider both at the same time.
        employment_time_step = builder.event.register_listener("time_step", self.on_time_step, priority=1)

        # load in any other required components

    def on_initialize_simulants(self, pop_data):
        """ Module for when the vivarium builder.initializes_simulants() is run.

        Parameters
        ----------
        pop_data: vivarium.framework.population.SimulantData
            `pop_data` is a custom vivarium class for interacting with the population data frame.
            It is essentially a pandas DataFrame with a few extra attributes such as the creation_time,
            creation_window, and current simulation state (setup/running/etc.).

        Returns
        -------
        pop_update : pd.DataFrame
            While not strictly return `pop_update` is the new population of simulants added to the main population
            frame.
        """
        # Fill in placeholder frame with default values.
        pop_update = pd.DataFrame({"is_student" : False,
                                   "student_duration" : 0.,
                                   "education_target" : None,
                                   "education_duration" : 0.,
                                   "graduation_month" : 0,
                                   "graduation_time" : None},
                                  index=pop_data.index)

        # Initiate these columns for when real data is added (I.E. replenishment from US cohorts.).
        if pop_data.user_data["sim_state"] == "setup" or pop_data.user_data["cohort_type"] == "replenishment":

            # Get real cohort data and assign pre-existing students to is_student = True
            pop = self.population_view.get(pop_data.index, "pidp>0")
            is_student = pop.loc[pop["labour_state"] == "Student"].index
            pop.loc[is_student, "is_student"] = True
            student_update = pop_update.loc[is_student]

            # Assign students education targets. What are they studying for?
            # TODO lots of potentially interesting work here in estimating sims education targets better.
            # For now use relatively naive assignment (see self.assign_new_students).
            student_update["education_target"] = self.assign_new_students(pop.loc[is_student])

            # Calculate the length of each persons education target and if they would graduate in a specific month.
            student_update["education_duration"] = student_update["education_target"].apply(lambda x: self.education_levels[x]["education_duration"])
            student_update["graduation_month"] = student_update["education_target"].apply(lambda x: self.education_levels[x]["graduation_month"])

            # Calculate the date each sim will graduate.
            # Some educations are time dependent (e.g. degrees graduate in June)
            # Some are not time dependent (e.g. can graduate with a higher diploma at any point)

            # Calculate naive enrollment date.
            # This is just the event time step.
            # Isn't given on the simulation setup step so use the start time based on the YAML config.
            if pop_data.user_data["sim_state"] == "setup":
                creation_time =  self.config.time.start
                creation_time = pd.to_datetime({"year":[creation_time.year],
                                                "month":[creation_time.month],
                                                "day":[creation_time.day]})
                student_update["graduation_time"] = creation_time[
                    0]  # 0 index here required or values are assigned NaT.

            # Otherwise the simulants creaetion time is given to calculate a rough graduation time from.
            else:
                student_update["graduation_time"] = pop_data.user_data["creation_time"]

            # Given their enrollment data calculate a more precise graduation time.
            # This will assign students to graduate in a specific month if required and remove some of the time required
            # for an agent if they are say 18 and obviously most of the way through their A-levels.
            student_update["graduation_time"] += student_update["education_duration"].values.astype("timedelta64[M]")
            student_update["graduation_time"] = self.calculate_graduation_time(student_update)

            # TODO Naively assign students to the start of their education. Can be done better.
            student_update["student_duration"] = 0
            student_update["student_duration"] = self.calculate_student_duration_time(student_update, creation_time,
                                                                                      pop.loc[is_student])
            # Put the updated students back into the main population update frame.
            pop_update.loc[is_student] = student_update

        # Initiate these columns for new births.
        # Default newborns to students with no education working towards GCSEs.
        elif pop_data.user_data["cohort_type"] == "births":

            # Assign newborns to automatically enroll in GCSEs.
            pop_update["is_student"] = True
            pop_update["education_state"] = "Less than GCSE"
            pop_update["student_duration"] = pop_data.user_data["creation_time"]

            # Update their eduation target (GCSE) and associated parameters for what month they graduate and the
            # number of months the course takes.
            pop_update["education_target"] = "GCSE"
            pop_update["graduation_month"] = 8.
            pop_update["education_duration"] = 16*12.

            # Calculate time they graduate. I.E. roughly 16 years after GCSE
            birth_time = pop_data.user_data["creation_time"]
            # Calculate graduation time for GCSE
            graduation_time = birth_time + pd.offsets.DateOffset(years=16)

            # They've been a student for 0 months.
            pop_update["student_duration"] = 0
            # Naively assume it takes exactly 16 years to graduate.
            pop_update["graduation_time"] = graduation_time
            # Update the naive assumption such that they graduate in July in 15-16 years time.
            pop_update["graduation_time"] = self.calculate_graduation_time(pop_update)

        # Add new cohort to population frame.
        self.population_view.update(pop_update)

        # No longer needed. Bug was occuring in that this data couldnt be loaded.
        # Now replenishment module runs on_initialize_simulants first this isnt a problem.

        # if pop_data.user_data["sim_state"] == "setup":
        #     # Update any dummy columns with real data if applicable.
        #     # I cannot for the life of me figure out why they wont just be added normally in pop_view.update.
        #     self.update_real_columns(pop_data)

    def calculate_graduation_time(self, pop):
        """ A function for calculating the time in months until a simulant graduates from birth.

        For example assume all GCSE students graduate in August.
        If a person was born in August it would take them 16 years 0 months to graduate.
        This function should then output exactly 16*12 months.
        Likewise if a person is born in September then it would take them 16 years and 11 months to graduate.

        Parameters
        ----------
        pop : pandas.DataFrane
            The `pop` of simulants for the main population frame
            to calculate the time until graduation for.

        Returns
        -------
        grad_times : pd.Series
            `grad_times` A series of graduation times for the specified population.
        """
        # Get the naive graduation time and the time specific graduation months (if any).
        grad_times = pop["graduation_time"]
        grad_month = pop["graduation_month"]

        # Has anyone enrolled after the annual graduation time?
        # E.G. GCSEs graduate in August so anyone born after September will graduate next year

        enroll_after_time_grad = grad_times.dt.month > grad_month
        # Set the graduation months. E.g. GCSEs graduate in August.
        grad_times_fixed = pd.to_datetime(
        {'year': grad_times.dt.year,
         'month': grad_month,
         'day': 1})

        # If born after the graduate date then push back a year later. E.G. GCSE born after september 2000 graduates
        # in August 2017 between 16 years 9 months and 17 years of age.
        grad_times.loc[enroll_after_time_grad] = grad_times_fixed
        grad_times.loc[enroll_after_time_grad] += pd.offsets.DateOffset(years=1)
        # Return new grad times to attach to update frame.
        return grad_times

    def calculate_student_duration_time(self, pop_update, creation_time, pop = None):
        """ Calculate how long the sims have been in education.

        For births all sims have the same student duration of 0.

        For replenishment some students may be already some way through
        their education. Since there is no information on this in the US
        dataset have to assume most people start at 0.
        However, this can be inferred for some students.
        For example, GCSE students are aged 15-16 in the US dataset.
        A 16 year old is clearly going to graduate within the year and
        so their student duration must be reflected to update this.
        The proximity to the maximum age of their respective education is used
        to estimate this. Someone who is 16 is within a year of the absolute
        maximum age of 17 for GCSE graduation so must be at least 15 years
        (from birth) into their GCSEs.

        Parameters
        ----------
        pop_update, pop : pandas.DataFrame
            The new columns added to the population data frame `pop_update`.
            If adding in real data also include the real `pop` data to use their ages.

        Returns
        -------

        """
        education_levels = self.education_levels # dict of education tiers
        ages = pop["age"] # get ages from real population data (if any).
        # get the maximum age of students for their respective education targets
        max_ages = pop_update["education_target"].apply(lambda x: education_levels[x]["age_max"])
        min_ages = pop_update["education_target"].apply(lambda x: education_levels[x]["age_min"])
        education_duration = pop_update["education_target"].apply(lambda x: education_levels[x]["education_duration"])

        # How many years until they hit the upper age bound for their education target.
        # If they're close to the bound it suggests they're part way through the education already.
        age_diffs = max_ages - ages

        # Has a sim already started their education? I.E. can they not complete their education before reaching the
        # maximum age?
        must_started = (12 * age_diffs) < education_duration

        # Calculate how many months into studies if they've already started.
        must_started_years_diff = (education_duration - (age_diffs * 12)).loc[must_started]


        graduation_times = pop_update["graduation_time"]
        duration_times = pd.DataFrame(index=pop_update.index)
        duration_times.loc[must_started, "duration_times"] = graduation_times.loc[must_started] + must_started_years_diff.subtract(1).values.astype('timedelta64[Y]')

        #
        duration_times.loc[~must_started, "duration_times"] = 0
        return duration_times

    def on_time_step(self, event):
        """ What happens in the employment module on every simulation timestep.

        Parameters
        ----------
        event : vivarium.builder.event
            The time_step `event` is used here. I.E whenever the simulation is stepped forwards.
        Returns
        -------

        """

        # First update the non_students.
        # Test if they enter education or stay put.
        # TODO separate pops for labour state change and job change
        pop = self.population_view.get(event.index, query="alive =='alive'")

        # Calculate probabilities of enrolling as a student using rate producer
        # Choose to enroll or not using vivarium's generalised multinomial randomg generator vivarium.random.choice.
        student_change_df = pd.DataFrame(index=pop.index)
        student_change_df["change"] = rate_to_probability(pd.DataFrame(self.student_change_rate_producer(pop.index)))
        student_change_df["no_change"] = 1 - student_change_df["change"]
        student_change_df["choice"] = self.random.choice(student_change_df.index, student_change_df.columns, student_change_df)

        # Subset of population who enroll.
        new_students = student_change_df.loc[student_change_df["choice"]=="change"]

        # Assign new education as necessary.
        # Will change their student status to true and determine their new status when they graduate.
        pop.loc[new_students.index, "is_student"] = True
        pop.loc[new_students.index, "education_target"] = self.assign_new_students(pop.loc[new_students.index])
        pop["education_duration"] = pop.loc[new_students.index, "education_target"].apply(lambda x:
                                                                                          self.education_levels[x]["education_duration"])
        # Update change in student status.
        self.population_view.update(pop[['is_student', "student_duration", "education_target", "education_duration"]])

        # Now the students. add one month to their student duration.
        # TODO add dropouts?
        pop = self.population_view.get(event.index, query="alive =='alive' and age > 16 and education_duration>0")
        # Add another time step to current students or graduate them if they've reached their education duration.
        # TODO make student duration work.
        #pop["student_duration"] = pop["student_duration"] + 1
        #graduates = self.graduate_students(event, pop)
        graduates = pop.loc[pop["student_duration"]==pop["education_duration"]]
        # Graduate anyone. update their education level and reset student counters
        if len(graduates.index) > 0:
            pop.loc[graduates.index, "education_state"] = pop.loc[graduates.index, "education_target"]
            pop.loc[graduates.index, "education_target"] = None
            pop.loc[graduates.index, "is_student"] = False
            pop.loc[graduates.index, "education_duration"] = 0.
            pop.loc[graduates.index, "student_duration"] = 0.

        # Update pop with student progression and new graduates.
        self.population_view.update(pop[["education_state", "student_duration", "education_target", "is_student",
                                         "education_duration"]])

    def calculate_student_change_rate(self, index):
        """ Calculate probabilities of moving to new job sector.

        Parameters
        ----------
        index : pandas.DataFrame.index
            `index` series indicating which agents to calculate the death rates of.
        Returns
        -------
        job_change_rates: pd.DataFrame
            `job_change_rates` indicates the probability of changing job sectors. 1 is change 0 is stay put.
        """
        student_change_rates = pd.DataFrame({"student_state": 0.5}, index=index)
        return student_change_rates

    def education_job_modifier(self, index, values):
        """ Adjust depression tier1 rates based on employment states

        Note this function requires arguments that match those of mortality.calculate_mortality_rate
        and an addition values argument (not name dependent) that gives the current values
        output by the mortality rate producer.

        Parameters
        ----------
        index : pandas.core.indexes.numeric.Int64Index
            `index` which rows of population frame apply rate modification to.
        values : pandas.core.frame.DataFrame

            the previous `values` output by the mortality_rate value producer.
            More generally the producer defined in the register_value_modifier
            method with this as its minos.

        Returns
        -------
        values : pandas.core.frame.DataFrame
            The modified `values` handed back to the builder for application in
            mortality's on_time_step. In theory, those with higher depression states are
            at higher risk of dying.
        """

        return values

    def education_role_modifier(self, index, values):
        """ Adjust employment role rates based on education status

        Note this function requires arguments that match those of the producer it is modifying
        (employment role producer)
        and an addition values argument (not name dependent) that gives the current values
        output said rate producer.

        Parameters
        ----------
        index : pandas.core.indexes.numeric.Int64Index
            `index` which rows of population frame apply rate modification to.
        values : pandas.core.frame.DataFrame

            the previous `values` output by the value producer.

        Returns
        -------
        values : pandas.core.frame.DataFrame
            The modified `values` handed back to the builder for application in
            its rate_producer in on_time_step. In theory, those with higher education states
            get access to more job sectors.
        """
        return values

    def assign_new_students(self, new_students):
        """ Assign new student education target based on some transition matrix

        Parameters
        ----------
        new_students : pd.DataFrame
            `new_students` population to decide changes in educatio target for.

        Returns
        -------
        new_educations: pd.DataFrame
            `new_educations` a vector of pop.index length assigning each person to a student state.
        """
        # Load in attributes for each education type.
        education_levels = self.education_levels
        # Shorthand name for current education states of enrolling students.
        current_levels = new_students["education_state"]

        # TODO this dummy frame does not encorporate age/sex/ethnicity properly. For now this is just a framework for
        #  better calibrated transitions in the future.

        # Placeholder frame for education transitions generated in generate_education_target_rates.py
        transition_dict = pd.read_csv("persistent_data/education_enrollment_rate_table.csv", index_col=[0, 1])
        #transition_dict = transition_dict.to_dict("split")
        #transition_dict = dict(zip(transition_dict["index"], transition_dict["data"]))

        # Loop over each simulant. Assign 1 if they have the required education to pursure each possible education
        # state.

        def grab_transition_row(x, transition_dict):
            row = transition_dict.loc[x["ethnicity"]].loc[x["sex"]].iloc[int(x["age"])]
            return np.fromstring(row[1:-1], sep=',')

        transition_matrix_rows = new_students.apply(lambda x: grab_transition_row(x,
                                                                                  transition_dict), axis=1)
        transition_matrix_rows = np.vstack(transition_matrix_rows)
        transition_matrix = pd.DataFrame(transition_matrix_rows, index = new_students.index, columns=education_levels.keys())

        required_qual_levels = current_levels.apply(lambda x: education_levels[x]["required_level"])
        qual_levels = current_levels.apply(lambda x: education_levels[x]["education_level"])

        for column in transition_matrix.columns:
            # Make sure nobody enrolls into no education.
            if column == "Less than GCSE":
                continue

            # required qualification and qualifaction level on graduation for each given education state.
            required_qual_level = education_levels[column]["required_level"]
            qual_level = education_levels[column]["education_level"]

            # Check who does not have the required qualifications to enroll.
            # Set it so they cannot enroll in that which they are not qualified for.
            who_unqualified = qual_levels < required_qual_level

            # Make sure noone can repeat their previous education again.
            # TODO slightly naive as people can have two degrees.
            # This is more specifically for values up to A-level.
            who_repeating = current_levels == column

            # Make sure people dont go too far back in the qualifications.
            # This stops degree grads from retaking A-levels.
            # This is only necessary if the who_unqualified uses <= rather than !=.
            # For now only using != as it is simpler but future requires relaxing of this condition so
            # say a degree grad can change careers into teaching.
            # TODO better conditioning for graduation under 18 vs over 18.
            # GCSE -> A-level -> degree is very linear and age dependent vs
            # getting a higher diploma at 35.
            # Part of a better transition matrix would incorporate this.

            #who_overqualified = required_qual_levels <= required_qual_level
            # dummy values that lets everyone past for testing.
            who_overqualified = required_qual_levels >= required_qual_level

            # Who is unqualified, over qualified, or would be repeating the same education again.
            who_ineligible = who_unqualified * who_repeating
            who_ineligible *= who_overqualified
            # Set anyone ineligible to study for a qualification unable to move to it.
            transition_matrix.loc[who_ineligible, column] *= 0

        new_targets = self.random.choice(transition_matrix.index, transition_matrix.columns, transition_matrix)
        new_educations = pd.DataFrame({'education_target': new_targets},
                                  index=new_students.index)
        return new_educations