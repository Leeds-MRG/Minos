"""Functions for subsetting minos output data in aggregates and plots"""

import numpy as np
import pandas as pd

def find_subset_function(function_string):
    if function_string == "none":
        subset_function = None
    elif function_string == "who_alive":
        subset_function = who_alive
    elif function_string == "who_boosted":
        subset_function = who_boosted
    else:
        print("no subset_function defined. Defaulting to None")
        subset_function = None
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
    "who has kids?"
    df = who_alive(df)
    return df.loc[df['nkids']>0]

def who_below_poverty_line(df):
    "who below poverty line?. Defined as 60% of national median hh income."
    df = who_alive(df)
    return df.loc[(df['hh_income'] <= np.nanmedian(df['hh_income']) * 0.6),]

def who_living_wage(df):
    df = who_alive(df)
    "who earns below the living wage?"
    who_uplifted_London = df['hourly_wage'] > 0
    who_uplifted_London *= df['region'] == 'London'
    who_uplifted_London *= df['hourly_wage'] < 11.95
    who_uplifted_notLondon = df['hourly_wage'] > 0
    who_uplifted_notLondon *= df['region'] != 'London'
    who_uplifted_notLondon *= df['hourly_wage'] < 10.90
    return df.loc[df[who_uplifted_notLondon | who_uplifted_London], ]