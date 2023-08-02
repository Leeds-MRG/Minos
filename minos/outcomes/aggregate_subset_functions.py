"""Functions for subsetting minos output data in aggregates and plots"""

import numpy as np
import pandas as pd

def dynamic_subset_function(data, subset_chain_string=None, mode = 'default_config'):

    if subset_chain_string == None:
        function_string = "who_alive"
        print("No subset defined. Defaulting to who_alive..")

    subset_chains = {"who": [],
                     # Original intervention subgroups.
                    "who_alive": [who_alive],
                    "who_boosted": [who_alive, who_boosted],
                    "who_below_living_wage": [who_alive, who_below_living_wage],
                    "who_kids": [who_alive, who_kids],
                    "who_below_poverty_line_and_kids": [who_alive, who_kids, who_below_poverty_line],
                    "who_scottish": [who_alive, who_scottish],
                    #"who_bottom_income_quintile": who_bottom_income_quintile,
                    # Scottish gov sgugested vulnerable subgroups.
                    "who_disabled": [who_alive, who_kids, who_disabled],
                    "who_ethnic_minority": [who_alive, who_kids, who_ethnic_minority],
                    "who_three_kids": [who_alive, who_three_kids],
                    "who_young_mother": [who_alive, who_young_adults, who_female, who_kids],
                    "who_young_adults": [who_alive, who_kids, who_young_adults],
                    "who_unemployed_adults": [who_alive, who_adult, who_kids, who_unemployed],
                    "who_no_formal_education": [who_alive, who_kids, who_no_formal_education],
                     # Not sure about this one? single parent may not be primrary caregiver. e.g. divorced dad without custody.
                    "who_lone_parent_families": [who_alive, who_single, who_kids],
                    "who_uses_energy": [who_alive, who_uses_energy],
                    # NOT IMPLEMENTED BELOW HERE YET. NO SUFFICIENT DATA IN UNDERSTANDING SOCIETY.
                    #"who_complex_needs": None,
                    #"who_babies_under_one": None,
                    #"who_income_benefits": None,
                    #"who_no_public_funds_recourse": None,
                    "who_first_simd_decile": [who_alive, [who_kth_simd_decile, [1]]],
                    "who_second_simd_decile": [who_alive, [who_kth_simd_decile, [2]]],
                    "who_third_simd_decile": [who_alive, [who_kth_simd_decile, [3]]],
                    "who_fourth_simd_decile": [who_alive, [who_kth_simd_decile, [4]]],
                    "who_fifth_simd_decile": [who_alive, [who_kth_simd_decile, [5]]],
                    "who_sixth_simd_decile": [who_alive, [who_kth_simd_decile, [6]]],
                    "who_seventh_simd_decile": [who_alive, [who_kth_simd_decile, [7]]],
                    "who_eighth_simd_decile": [who_alive, [who_kth_simd_decile, [8]]],
                    "who_ninth_simd_decile": [who_alive, [who_kth_simd_decile, [9]]],
                    "who_tenth_simd_decile": [who_alive, [who_kth_simd_decile, [10]]],

                     }

    subset_chain = subset_chains[subset_chain_string]

    if mode == 'scotland_mode': # if in scotland mode add it to the .
        subset_chain.append(who_scottish)

    for subset_function in subset_chain:
        if type(subset_function) == list:
            subset_function, subset_args = subset_function
            data = subset_function(data, subset_args)
        else:
            data = subset_function(data)

    return data


def get_required_intervention_variables(subset_function_string):
    # get required variables for intervention used in aggregate_subset_function. makes csvs load much faster.
    default_variables = ["pidp", "alive", "SF_12", 'time']
    required_variables_dict = {
        "who_alive": default_variables,
        "who_boosted":  default_variables + ["income_boosted"],
        "who_below_living_wage": default_variables + ["region", "hourly_wage"],
        "who_kids": default_variables + ["nkids"],
        "who_below_poverty_line_and_kids": default_variables + ["hh_income", "nkids"],
        "who_uses_energy": default_variables + ['yearly_energy'],
        "who_first_simd_decile": default_variables + ['simd_decile'],
        "who_second_simd_decile": default_variables + ['simd_decile'],
        "who_third_simd_decile": default_variables + ['simd_decile'],
        "who_fourth_simd_decile": default_variables + ['simd_decile'],
        "who_fifth_simd_decile": default_variables + ['simd_decile'],
        "who_sixth_simd_decile": default_variables + ['simd_decile'],
        "who_seventh_simd_decile": default_variables + ['simd_decile'],
        "who_eighth_simd_decile": default_variables + ['simd_decile'],
        "who_ninth_simd_decile": default_variables + ['simd_decile'],
        "who_tenth_simd_decile": default_variables + ['simd_decile'],
    }
    return required_variables_dict[subset_function_string]

def who_alive(df):
    """ Get who is alive.
    Parameters
    ----------
    df
    Returns
    -------
    """
    return df.loc[df['alive'] == 'alive', ]

def who_uses_energy(df):
    # who spends money on energy. fuel bills > 0.
    return df.loc[df['yearly_energy']>=0,]

def who_adult(df):
    return df.query("age >= 16")


def who_below_living_wage(df):
    # Who earns below the living wage?
    who_uplifted_London = df['hourly_wage'] > 0
    who_uplifted_London *= df['region'] == 'London'
    who_uplifted_London *= df['hourly_wage'] < 11.95
    who_uplifted_notLondon = df['hourly_wage'] > 0
    who_uplifted_notLondon *= df['region'] != 'London'
    who_uplifted_notLondon *= df['hourly_wage'] < 10.90
    return df.loc[who_uplifted_notLondon | who_uplifted_London, ] # get anyone from either group.


#def who_bottom_income_quintile(df, k=1):
#    df = who_alive(df)
#    split = pd.qcut(df['hh_income'], q=5, labels=[1, 2, 3, 4, 5])
#    return df.loc[split == k, ]


def who_below_poverty_line(df):
    "who below poverty line?. Defined as 60% of national median hh income."
    return df.loc[df['hh_income'] <= (np.nanmedian(df['hh_income']) * 0.6), ]


def who_boosted(df):
    # Get anyone who receives an income boost..
    return df.query("`income_boosted` == True")


def who_disabled(df):
    return df.query("`labour_state` == 'Sick/Disabled'")


def who_ethnic_minority(df):
    # Who is not White British (ethnic minority)?
    return df.query("ethnicity != 'WBI'")


def who_female(df):
    return df.query("sex == 'female'")


def who_kids(df):
    "who alive and has kids?"
    return df.query("nkids > 0")


def who_no_formal_education(df):
    # Lowest education tier.
    return df.query("`education_state` == 0")


def who_scottish(df):
    # Who Scottish?
    return df.query("region == 'Scotland'")


def who_single(df):
    # who not married. E.g. single/diuorced/widowed etc.
    return df.query("marstat != 'Married'")


def who_three_kids(df):
    # Who has three or more children.
    return df.loc[df["nkids"] >= 3, ]


def who_unemployed(df):
    # who unemployed
    return df.loc[df["labour_state"] == "Unemployed", ]


def who_young_adults(df):
    # who aged between 16 and 25.
    df =  df.loc[df["age"] <= 25, ]
    return df.loc[df["age"] >= 16, ]

def who_kth_simd_decile(df, *args):
    k = args[0][0]
    return df.loc[df["simd_decile"] == k]