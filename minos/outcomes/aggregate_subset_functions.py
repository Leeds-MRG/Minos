"""Functions for subsetting minos output data in aggregates and plots"""

import numpy as np
import pandas as pd


def dynamic_subset_function(data, subset_chain_string=None, mode='default_config'):
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
                     "who_universal_credit_and_kids": [who_alive, who_kids, who_universal_credit],
                     "who_scottish": [who_alive, who_scottish],
                    "who_uses_energy": [who_alive, who_uses_energy],



                     # Scottish gov sgugested priort subgroups.
                     "who_disabled": [who_alive, who_kids, who_disabled],
                     "who_ethnic_minority": [who_alive, who_kids, who_ethnic_minority],
                     "who_three_kids": [who_alive, who_three_kids],
                     "who_young_mother": [who_alive, who_young_adults, who_female, who_kids],
                     "who_young_adults": [who_alive, who_kids, who_young_adults],
                     "who_unemployed_adults": [who_alive, who_adult, who_kids, who_unemployed],
                     "who_no_formal_education": [who_alive, who_kids, who_no_formal_education],
                     "who_newborn": [who_alive, who_kids, who_has_newborn],
                     # Not sure about this one? single parent may not be primrary caregiver. e.g. divorced dad without custody.
                     "who_lone_parent_families": [who_alive, who_single, who_kids],
                     # NOT IMPLEMENTED BELOW HERE YET. NO SUFFICIENT DATA IN UNDERSTANDING SOCIETY.
                     # "who_complex_needs": None,
                     # "who_income_benefits": None,
                     # "who_no_public_funds_recourse": None,
                    "who_lone_parent_families": [who_alive, who_single, who_kids],

                    'who_priority_subgroups': [who_alive, who_kids, who_priority_subgroups],
                    'who_priority_subgroups_and_kids': [who_alive, who_kids, who_priority_subgroups],
                    'who_multiple_priority_subgroups': [who_alive, who_kids, who_multiple_priority_subgroups],
                    'who_multiple_priority_subgroups_and_kids': [who_alive, who_kids, who_multiple_priority_subgroups],

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

                     "who_boosted_first_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [1]]],
                     "who_boosted_second_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [2]]],
                     "who_boosted_third_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [3]]],
                     "who_boosted_fourth_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [4]]],
                     "who_boosted_fifth_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [5]]],
                     "who_boosted_sixth_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [6]]],
                     "who_boosted_seventh_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [7]]],
                     "who_boosted_eighth_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [8]]],
                     "who_boosted_ninth_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [9]]],
                     "who_boosted_tenth_simd_decile": [who_alive, who_boosted, [who_kth_simd_decile, [10]]],

                     "who_kids_first_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [1]]],
                     "who_kids_second_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [2]]],
                     "who_kids_third_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [3]]],
                     "who_kids_fourth_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [4]]],
                     "who_kids_fifth_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [5]]],
                     "who_kids_sixth_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [6]]],
                     "who_kids_seventh_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [7]]],
                     "who_kids_eighth_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [8]]],
                     "who_kids_ninth_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [9]]],
                     "who_kids_tenth_simd_decile": [who_alive, who_kids, [who_kth_simd_decile, [10]]],

                     "who_below_poverty_line_and_kids_first_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [1]]],
                     "who_below_poverty_line_and_kids_second_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [2]]],
                     "who_below_poverty_line_and_kids_third_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [3]]],
                     "who_below_poverty_line_and_kids_fourth_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [4]]],
                     "who_below_poverty_line_and_kids_fifth_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [5]]],
                     "who_below_poverty_line_and_kids_sixth_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [6]]],
                     "who_below_poverty_line_and_kids_seventh_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [7]]],
                     "who_below_poverty_line_and_kids_eighth_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [8]]],
                     "who_below_poverty_line_and_kids_ninth_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [9]]],
                     "who_below_poverty_line_and_kids_tenth_simd_decile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_decile, [10]]],

                     "who_universal_credit_and_kids_first_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [1]]],
                     "who_universal_credit_and_kids_second_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [2]]],
                     "who_universal_credit_and_kids_third_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [3]]],
                     "who_universal_credit_and_kids_fourth_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [4]]],
                     "who_universal_credit_and_kids_fifth_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [5]]],
                     "who_universal_credit_and_kids_sixth_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [6]]],
                     "who_universal_credit_and_kids_seventh_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [7]]],
                     "who_universal_credit_and_kids_eighth_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [8]]],
                     "who_universal_credit_and_kids_ninth_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [9]]],
                     "who_universal_credit_and_kids_tenth_simd_decile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_decile, [10]]],

                     "who_priority_subgroups_first_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [1]]],
                     "who_priority_subgroups_second_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [2]]],
                     "who_priority_subgroups_third_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [3]]],
                     "who_priority_subgroups_fourth_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [4]]],
                     "who_priority_subgroups_fifth_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [5]]],
                     "who_priority_subgroups_sixth_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [6]]],
                     "who_priority_subgroups_seventh_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [7]]],
                     "who_priority_subgroups_eighth_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [8]]],
                     "who_priority_subgroups_ninth_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [9]]],
                     "who_priority_subgroups_tenth_simd_decile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_decile, [10]]],

                     "who_first_simd_quintile": [who_alive, [who_kth_simd_quintile, [1]]],
                     "who_second_simd_quintile": [who_alive, [who_kth_simd_quintile, [2]]],
                     "who_third_simd_quintile": [who_alive, [who_kth_simd_quintile, [3]]],
                     "who_fourth_simd_quintile": [who_alive, [who_kth_simd_quintile, [4]]],
                     "who_fifth_simd_quintile": [who_alive, [who_kth_simd_quintile, [5]]],

                     "who_priority_subgroups_first_simd_quintile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_quintile, [1]]],
                     "who_priority_subgroups_second_simd_quintile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_quintile, [2]]],
                     "who_priority_subgroups_third_simd_quintile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_quintile, [3]]],
                     "who_priority_subgroups_fourth_simd_quintile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_quintile, [4]]],
                     "who_priority_subgroups_fifth_simd_quintile": [who_alive, who_kids, who_priority_subgroups, [who_kth_simd_quintile, [5]]],

                     "who_below_poverty_line_and_kids_first_simd_quintile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_quintile, [1]]],
                     "who_below_poverty_line_and_kids_second_simd_quintile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_quintile, [2]]],
                     "who_below_poverty_line_and_kids_third_simd_quintile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_quintile, [3]]],
                     "who_below_poverty_line_and_kids_fourth_simd_quintile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_quintile, [4]]],
                     "who_below_poverty_line_and_kids_fifth_simd_quintile": [who_alive, who_kids, who_below_poverty_line, [who_kth_simd_quintile, [5]]],

                     "who_universal_credit_and_kids_first_simd_quintile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_quintile, [1]]],
                     "who_universal_credit_and_kids_second_simd_quintile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_quintile, [2]]],
                     "who_universal_credit_and_kids_third_simd_quintile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_quintile, [3]]],
                     "who_universal_credit_and_kids_fourth_simd_quintile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_quintile, [4]]],
                     "who_universal_credit_and_kids_fifth_simd_quintile": [who_alive, who_kids, who_universal_credit, [who_kth_simd_quintile, [5]]],

                     "who_boosted_first_simd_quintile": [who_alive, who_boosted, [who_kth_simd_quintile, [1]]],
                     "who_boosted_second_simd_quintile": [who_alive, who_boosted, [who_kth_simd_quintile, [2]]],
                     "who_boosted_third_simd_quintile": [who_alive, who_boosted, [who_kth_simd_quintile, [3]]],
                     "who_boosted_fourth_simd_quintile": [who_alive, who_boosted, [who_kth_simd_quintile, [4]]],
                     "who_boosted_fifth_simd_quintile": [who_alive, who_boosted, [who_kth_simd_quintile, [5]]],


                     "who_uses_energy_first_simd_quintile": [who_alive, [who_kth_simd_quintile, [1]]],
                     "who_uses_energy_second_simd_quintile": [who_alive, [who_kth_simd_quintile, [2]]],
                     "who_uses_energy_third_simd_quintile": [who_alive, [who_kth_simd_quintile, [3]]],
                     "who_uses_energy_fourth_simd_quintile": [who_alive, [who_kth_simd_quintile, [4]]],
                     "who_uses_energy_fifth_simd_quintile": [who_alive, [who_kth_simd_quintile, [5]]],

                     }

    subset_chain = subset_chains[subset_chain_string]

    if "glasgow" in subset_chain_string:
        subset_chain.append(who_glasgow)

    if "edinburgh" in subset_chain_string:
        subset_chain.append(who_edinburgh)


    if mode == 'scotland_mode':  # if in scotland mode add it to the .
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
    default_variables = ["weight", "pidp", "hidp", "alive", "SF_12", 'time', "housing_quality", "hh_income", "neighbourhood_safety", "loneliness", "ZoneID"]

    if "boosted" in subset_function_string:
        default_variables.append("who_boosted")

    if "decile" or "quintile" in subset_function_string:
        default_variables += ["ZoneID", "simd_decile"]

    if "kids" in subset_function_string:
        default_variables.append("nkids")

    if "universal_credit" in subset_function_string:
        default_variables.append("universal_credit")
    
    if "priority_subgroups" in subset_function_string:
        default_variables += ["nkids", "age", "ethnicity", "marital_status", "S7_labour_state", 'simd_decile', 'has_newborn']

    if "energy" in subset_function_string:
        default_variables.append("yearly_energy")

    if "living_wage" in subset_function_string:
        default_variables += ["region", "hourly_wage"]

    required_variables_dict = {        
        # priority subgroups for scotgov. single groups, all groups together, and multiple groups.
        # plus some very custom functions for mapping specific quintiles. 
        "who_newborn": ['nkids', "has_newborn"],
        "who_young_mother": ['nkids', "age", "sex"],
        "who_disabled":  ['nkids', "S7_labour_state"],
        "who_ethnic_minority":  ['nkids', "ethnicity"],
        "who_three_kids":  ['nkids'],
        "who_young_mother":  ['nkids', "age", "sex"],
        "who_young_adults":  ['nkids', "age"],
        "who_unemployed_adults": ['nkids', "age", "S7_labour_state"],
        "who_no_formal_education":  ['nkids', "education_state"],
    }
    if subset_function_string in required_variables_dict:
        default_variables += required_variables_dict[subset_function_string]
    return default_variables

def who_alive(df):
    """ Get who is alive.
    Parameters
    ----------
    df
    Returns
    -------
    """
    return df.loc[df['alive'] == 'alive',]

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
    return df.loc[who_uplifted_notLondon | who_uplifted_London,]  # get anyone from either group.


def who_bottom_income_quintile(df, k=1):
    df = who_alive(df)
    split = pd.qcut(df['hh_income'], q=5, labels=[1, 2, 3, 4, 5])
    return df.loc[split == k, ]


def who_below_poverty_line(df):
    "who below poverty line?. Defined as 60% of national median hh income."
    return df.loc[df['hh_income'] <= (np.nanmedian(df['hh_income']) * 0.6),]


def who_boosted(df):
    # Get anyone who receives an income boost..
    return df.query("`income_boosted` == True")


def who_disabled(df):
    return df.query("`S7_labour_state` == 'Sick/Disabled'")


def who_has_newborn(df):
    return df.query("`has_newborn` == True")


def who_ethnic_minority(df):
    # Who is not White British (ethnic minority)?
    df = df.query("ethnicity != 'WBI'")
    df = df.query("ethnicity != 'WHO'")
    return df


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
    return df.query("marital_status != 'Partnered'")


def who_three_kids(df):
    # Who has three or more children.
    return df.loc[df["nkids"] >= 3,]


def who_unemployed(df):
    # who unemployed
    return df.loc[df["S7_labour_state"] == "Unemployed",]


def who_young_adults(df):
    # who aged between 16 and 25.
    df = df.loc[df["age"] <= 25,]
    df = df.loc[df["age"] >= 16,]
    #return df.loc[df['sex']=="Female", ]
    return df

def who_has_newborn(df):
    # get all households with newborns
    return df.loc[df['has_newborn'] == True, ]

def who_universal_credit(df):
    # whos on universal credit.
    # TODO extend to other legacy benefits at some point?
    return df.loc[df['universal_credit'] == 1, ]


def who_uses_energy(df):
    return df.loc[df['yearly_energy'] > 0]


def who_priority_subgroups(df):
    # get individual in all priority subgroups.
    # subgroups defined as per
    # Tackling child poverty delivery plan 2022-2026 - annex 2: child poverty evaluation strategy
    # - updated - gov.scot (www.gov.scot)
    subset_functions = [who_single, who_three_kids, who_young_adults, who_ethnic_minority, who_disabled, who_has_newborn]
    df['who_boosted'] = False
    for subset_function in subset_functions:
        search_index = subset_function(df).index
        df.loc[search_index,"who_boosted"] = True
    who_subsetted = np.unique(df.query('who_boosted == True')['hidp'])
    df.loc[df['hidp'].isin(who_subsetted) ,'who_boosted'] = True # set everyone who satisfies uplift condition to true.
    return df.loc[df['who_boosted'], ]


def who_multiple_priority_subgroups(df):
    # get individual in all priority subgroups.
    # subgroups defined as per
    # Tackling child poverty delivery plan 2022-2026 - annex 2: child poverty evaluation strategy
    # - updated - gov.scot (www.gov.scot)
    subset_functions = [who_single, who_three_kids, who_young_adults, who_ethnic_minority, who_disabled, who_has_newborn]
    df['subgroup_counts'] = 0 # count number of priority subgroups each household is in. 
    for subset_function in subset_functions:
        search_index = subset_function(df).index
        df.loc[search_index,"subgroup_counts"] += 1
    
    # make sure household subgroup count account for everyone in the household. I.E. household with mixed ethnicities may not catch ethnic minority priority subgroup for everyone. 
    # make sure it does. 
    df['subgroup_counts'] = df.groupby("hidp")['subgroup_counts'].transform(max)

    # get all households in more than 1 priority group. 
    df['who_boosted'] = df.loc[df['subgroup_counts']>1, ]
    who_subsetted = np.unique(df.query('who_boosted == True')['hidp'])
    df.loc[df['hidp'].isin(who_subsetted) ,'who_boosted'] = True # set everyone who satisfies uplift condition to true.
    return df.loc[df['who_boosted'], ]



def who_kth_simd_decile(df, *args):
    k = args[0][0]
    return df.loc[df["simd_decile"] == k]


def who_kth_simd_quintile(df, *args):
    k = args[0][0]
    return df.loc[np.ceil(df["simd_decile"]/2) == k]


def who_glasgow(df):
    df.loc[df['ZoneID'].isin(get_region_lsoas("glasgow")), ]

def who_edinburgh(df):
    df.loc[df['ZoneID'].isin(get_region_lsoas("edinburgh")), ]


def get_region_lsoas(region):
    region_file_name_dict = {"manchester": "manchester_lsoas.csv",
                             "scotland": "scotland_data_zones.csv",
                             "sheffield": "sheffield_lsoas.csv",
                             "glasgow": "glasgow_data_zones.csv",
                             "edinburgh": "edinburgh_data_zones.csv"}
    lsoas_file_path = "persistent_data/spatial_data/" + region_file_name_dict[region]
    return pd.read_csv(lsoas_file_path)
