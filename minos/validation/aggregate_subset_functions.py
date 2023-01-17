"""Functions for subsetting minos output data in aggregates and plots"""

import numpy as np
import pandas as pd

def find_subset_function(function_string):

    subset_functions = {
        "none": None,
        "who_alive": who_alive,
        "who_boosted": who_boosted,
        "who_below_living_wage": who_below_living_wage,
        "who_kids": who_kids,
        "who_below_poverty_line_and_kids": who_below_poverty_line_and_kids,
        "who_bottom_income_quintile": who_bottom_income_quintile
        "who_scottish": ,

    }
    if function_string in subset_functions.keys():
        subset_function = subset_functions[function_string]
    else:
        print("no subset_function defined. Defaulting to anyone alive.")
        subset_function = who_alive
    return subset_function

def who_alive(df):
    """ Get who is alive.

    Parameters
    ----------
    df

    Returns
    -------

    """
    return df.loc[df['alive'] == 'alive', ]

def who_boosted(df):
    """ Get who is alive and who has received boost/intervention

    Parameters
    ----------
    df

    Returns
    -------

    """
    df = who_alive(df)
    return df.loc[df['income_boosted'], ]

def who_kids(df):
    "who alive and has kids?"
    df = who_alive(df)
    return df.loc[df['nkids']>0]

def who_below_poverty_line_and_kids(df):
    "who alive and below poverty line and has kids?. Defined as 60% of national median hh income."
    df = who_alive(df)
    df = who_kids(df)
    return df.loc[df['hh_income'] <= (np.nanmedian(df['hh_income']) * 0.6), ]

def who_below_living_wage(df):
    df = who_alive(df)
    "who earns below the living wage?"
    who_uplifted_London = df['hourly_wage'] > 0
    who_uplifted_London *= df['region'] == 'London'
    who_uplifted_London *= df['hourly_wage'] < 11.95
    who_uplifted_notLondon = df['hourly_wage'] > 0
    who_uplifted_notLondon *= df['region'] != 'London'
    who_uplifted_notLondon *= df['hourly_wage'] < 10.90
    return df.loc[who_uplifted_notLondon | who_uplifted_London, ] # get anyone from either group.


def who_bottom_income_quintile(df, k=1):
    df = who_alive(df)
    split = pd.qcut(df['hh_income'], q=5, labels=[1, 2, 3, 4, 5])
    return df.loc[split == k, ]

def who_scotland(df):
    return df.loc[df["region"]=="Scotland", ]

def who_disabled(df):
    return df.loc[df["labour_state"]=="Sick/Disabled", ]

def who_ethnic_minority(df):
    return df.loc[df["ethnicity"] != "WBI", ]

def who_three_kids(df):
    return df.loc[df["nkids"] >= 3, ]
def who_young_mother(df):
    who_kids = df["nkids"] >= 1
    who_mother = df["sex"] == "female"
    who_under_twenty_five = df["age"] <= 25
    who_eligible = who_kids * who_mother * who_under_twenty_five
    return df.loc[who_eligible, ]

def who_young_adults(df):
    return df.loc[df["age"] <= 25, ]

def who_unemployed_adults(df):
    return df.loc[df["labour_state"] == "Unemployed", ]

def who_no_formal_education(df):
    return df.loc[df["education_state"] == 0, ]


# TODO lone parent families, people with complex needs, babies under 1, income related benefits., no recourse to public funds.
# TODO interventions suggested here. briding payment to £50 per week per child, fuel insecurity fund to £20m, flexible LA funding, moratorium on rent, debt releif for financially vulnerable, island household fund.