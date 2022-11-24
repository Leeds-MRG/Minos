"""Functions for subsetting minos output data in aggregates and plots"""

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