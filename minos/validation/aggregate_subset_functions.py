"""Functions for subsetting minos output data in aggregates and plots"""

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
    df = df.loc[df['alive'] == 'alive', ]
    return df.loc[df['income_boosted'], ]