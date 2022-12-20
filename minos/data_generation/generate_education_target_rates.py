"""First effort at generating a rough transition matrix for education states.

This is a very naive approach but is a useful stopgap.
Will generate a lookup table over

"""

import pandas as pd
import itertools
import numpy as np

def format_education_levels(file_name):
    education_levels = pd.read_csv(file_name)
    education_levels = education_levels.T
    education_levels.columns = education_levels.loc["name"]
    education_levels = education_levels.drop("name", 0)
    education_levels = education_levels.to_dict()
    education_levels = education_levels
    return education_levels

# def generate_matrix_columns():
#     """Generate columns for transition matrix.
#
#     Parameters
#     ----------
#     None
#
#     Returns
#     -------
#     columns : list
#         A list of dataframe `columns` for the transition matrix.
#     """
#     columns = ["ETH", "EDU"]
#     for gender in ["M", "F"]:
#         for i in range(102):
#             if i == 0:
#                 new_column = f"{gender}B.0"
#             elif i > 100:
#                 new_column = f"{gender}100.101p"
#             else:
#                 new_column = f"{gender}{i - 1}.{i}"
#             columns.append(new_column)
#     return columns

# def generate_base_transition_frame(education_levels):
#     """build a lookup table for next education targets
#
#     Example frame looks like..
#
#     ETH.group,MB.0,M0.1,M1.2,...,M98.99,M99.100,M100.101p,FB.0,F0.1,F1.2,...F98.99,F99.100,F100.101p
#     BAN,Less than GCSE,
#     BAN,GCSE,
#     BAN,CSE,
#     BAN,Standard/Lower,
#     ...
#     BLA,
#     ...
#     BLC,
#     ...
#     CHI,
#     ...
#     IND,
#     ...
#     MIX,
#     ...
#     OAS,
#     ...
#     OBL,
#     ...
#     OTH,
#     ...
#     PAK,
#     ...
#     WBI,
#     ...
#     11,WHO,Medical Education,...
#     Parameters
#     ----------
#     education_levels
#
#     Returns
#     -------
#     transition_frame
#     """
#     # creation base transition frame.
#     # loop over ages, ethnicity, gender and current education state
#
#     # define education states and ethnicities
#     edus = education_levels.keys()
#     ets = ["BAN", "BLA", "BLC", "CHI", "IND", "MIX", "OAS", "OBL", "OTH", "PAK", "WBI"]
#     #Generate data frame columns and create all combinations of eth/edu for their columns.
#     columns = generate_matrix_columns()
#     eth_edu_columns = pd.DataFrame(itertools.product(ets, edus))
#
#     # Initial placeholder frame with eth/edu columns added to fill the index.
#     transition_frame = pd.DataFrame(0, index = eth_edu_columns.index, columns = columns)
#     transition_frame[["ETH", "EDU"]] = eth_edu_columns
#
#     return transition_frame

def generate_age_columns():
    """Generate 102 string for the age brackets between birth and 101+ years old.

    Parameters
    ----------
    Returns
    -------

    columns : list
        A list of strings for the age `column`.
    """
    columns = []
    for i in range(102):
        if i == 0:
            new_column = f"B.0"
        elif i > 100:
            new_column = f"100.101p"
        else:
            new_column = f"{i - 1}.{i}"
        columns.append(new_column)
    return columns

def generate_transitions_dictionary(education_levels):
    """build a lookup table for next education targets

    Example frame looks like..

    ETH.group,MB.0,M0.1,M1.2,...,M98.99,M99.100,M100.101p,FB.0,F0.1,F1.2,...F98.99,F99.100,F100.101p
    BAN,Less than GCSE,
    BAN,GCSE,
    BAN,CSE,
    BAN,Standard/Lower,
    ...
    BLA,
    ...
    BLC,
    ...
    CHI,
    ...
    IND,
    ...
    MIX,
    ...
    OAS,
    ...
    OBL,
    ...
    OTH,
    ...
    PAK,
    ...
    WBI,
    ...
    11,WHO,Medical Education,...
    Parameters
    ----------
    education_levels

    Returns
    -------
    transition_frame
    """
    # creation base transition frame.
    # loop over ages, ethnicity, gender and current education state

    # define education states and ethnicities
    edus = education_levels.keys()
    eths = ["BAN", "BLA", "BLC", "CHI", "IND", "MIX", "OAS", "OBL", "OTH", "PAK", "WBI", "WHO"]
    gens = ["Male", "Female"]
    #ages = generate_age_columns()
    ages = np.arange(0, 101)
    columns = itertools.product(eths, gens, ages)

    transition_dict = {}
    # Add in placeholder keys for each combination of ethnicity, gender, and age.
    for eth in eths:
        transition_dict[eth] = {}
        for gen in gens:
            transition_dict[eth][gen] = {}
            for age in ages:
                transition_dict[eth][gen][age] = {}
    transition_dict = generate_education_rates_dict(transition_dict, columns, education_levels)

    return transition_dict

# def generate_exponential_rates(transition_frame, min_age, max_age, education_level, scale):
#     """ Generate a decreasing exponential probability of enrolling in an education as a sim gets older.
#
#     Parameters
#     ----------
#     transition_frame: pandas.DataFrame
#         The `transition_frame` to adjust the
#     min_age, max_age : int
#         `min_age` `max_age` The minimum and maximum ages to enroll in an education.
#     education_level : string
#         The specific `education_level` to be modified.
#     scale : float
#         The positive `scale` of the exponential distribution determines how quickly it drops off.
#         A higher scale gives a sharper curve. E.g. A-levels only have around 3 years of enrollment where as a degree
#         can start anywhere from 18 until death. A-levels will be given a much larger scale value.
#     Returns
#     -------
#
#     """
#     # Grab the specific sub frame for the adjusted education level.
#     sub_frame = transition_frame.loc[transition_frame["EDU"] == education_level]
#
#     row_values = []
#     age_range = np.arange(0, 101)
#     # generate exponential probabilities between min_age and max_age with the given scale.
#
#
#     for i in age_range:
#         if min_age<=i and i<=max_age:
#             # Note division by 100 here so epxonential decay is much slower.
#             # Otherwise would need huge rate values that dont behave as intended.
#             probability = scale * np.exp(-scale * (i-min_age)/20)
#         else:
#             probability = 0
#         row_values.append(probability)
#     #update male and female age rows with these new values
#     male_columns = sub_frame.columns[2: (3+101-1)]
#     female_columns = sub_frame.columns[-(101):]
#     sub_frame.loc[sub_frame.index, male_columns] = row_values
#     sub_frame.loc[sub_frame.index, female_columns] = row_values
#
#     transition_frame.loc[sub_frame.index] = sub_frame
#     return transition_frame

def generate_education_rates_dict(transition_dict, columns, education_levels):
    # loop over each combination of ethnicity gender and age.
    for item in columns:

        age = item[2]

        # Calculate their probability of transitions for each education given their attributes.
        # Rate of decline about an education level's minimum age.
        edu_scales = [0, 1, 1, 1, 1, 2, 0.5, 5, 5, 0.5, 0.5, 1.75, 1.75, 1.5, 1.5, 1.5]
        # Placeholder entry for given key.
        row_values = []

        for i, edu in enumerate(education_levels.keys()):
            # List of transitions for each state.
            if edu == "Less than GCSE":
                row_values.append(0)
                continue
            min_age = education_levels[edu]["age_min"]
            max_age = education_levels[edu]["age_max"]
            range = max_age - min_age
            # allow for GCSE case of assignment at birth.
            if range == 0:
                range = 1
            scale = edu_scales[i]
            age = item[2]
            if item[2] == 0 and edu == "GCSE":
                probability = 1
            # TODO Maybe need a case for 101p here.
            elif min_age<= age and age <= max_age:
                # IF a sim in the required age range to study something then assign a probability to it
                # based on their distance from the minimum age.
                # Note division by 20 here so exponential decay is much slower.
                # Otherwise would need huge rate values that dont behave as intended.
                probability = scale * np.exp(-scale * (i-min_age)/range)
            else:
                # If not in the eligible age range assign 0.
                probability = 0
            row_values.append(probability)
        transition_dict[item[0]][item[1]][item[2]] = row_values
    return transition_dict

# def apply_exponential_transitions(transition_frame, education_levels):
#     """Apply dummy exponential distributions
#
#     Parameters
#     ----------
#     transition_frame : pd.DataFrame
#     education_states : dict
#
#     Returns
#     -------
#     transition_frame : pd.DataFrame
#     """
#     scales = [0, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 1.75, 1.75, 1.5, 1.5, 1.5]
#     for i, item in enumerate(education_levels.keys()):
#         if item == "Less than GCSE":
#             continue
#         min_age = education_levels[item]["age_min"]
#         max_age = education_levels[item]["age_max"]
#         scale = scales[i]
#         transition_frame = generate_exponential_rates(transition_frame, min_age, max_age, item, scale)
#
#     return transition_frame

# def save_frame(transition_frame):
#     """ Save education transitions to csv.
#
#     Parameters
#     ----------
#     transition_frame : pd.DataFrame
#         The `transition_frame` to save to a csv.
#
#     Returns
#     -------
#
#     """
#     file_name = "../persistent_data/education_enrollment_rate_table.csv"
#     transition_frame.to_csv(file_name)
#     print(f"File saved to: {file_name}")

def save_dict(transition_dict):
    """ Save education transitions to csv.

    Parameters
    ----------
    transition_frame : pd.DataFrame
        The `transition_frame` to save to a csv.

    Returns
    -------

    """
    file_name = "../persistent_data/education_enrollment_rate_table.csv"
    transition_frame = pd.DataFrame.from_dict({(i,j): transition_dict[i][j]
                           for i in transition_dict.keys()
                           for j in transition_dict[i].keys()
                           for k in transition_dict[i][j].keys()},
                       orient='index')


    transition_frame.to_csv(file_name)
    print(f"File saved to: {file_name}")

def main():
    file_name = "../persistent_data/education_levels.csv"
    education_levels = format_education_levels(file_name)
    # transition_frame = generate_base_transition_frame(education_levels)
    # transition_frame = apply_exponential_transitions(transition_frame, education_levels)
    # save_frame(transition_frame)
    transition_dict = generate_transitions_dictionary(education_levels)
    save_dict(transition_dict)

if __name__ == "__main__":
    main()