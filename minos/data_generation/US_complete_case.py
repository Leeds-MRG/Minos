"""Functions for applying complete case missingness correction to
Understanding Society data."""

import numpy as np

def complete_case(data):
    """ main function for complete case.

    Parameters
    ----------
    data : pd.DataFrame
        US data to perform complete case correction on.
    Returns
    -------
    data : pd.DataFrame
        Corrected data.
    """
    data = data.replace([-1, -2, -7, -8, -9,
                         "-1", "-2", "-7", "-8", "-9",
                         "-1.0", "-2.0", "-7.0", "-8.0", "-9.0"], np.nan)
    data = data.dropna(0)
    return data