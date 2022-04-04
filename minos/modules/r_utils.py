"""
R utility functions. These are currently all related to the use of transition models.
"""

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr



def load_transitions(component, path = '../data/transitions/'):
    """

    Parameters
    ----------
    path : String
        Path to transitions folder
    component : String
        Component to load transition for, as string

    Returns:
    -------
    An RDS object containing a fitted model for prediction.
    """
    base = importr('base')

    #filename = path + component + '.rds'
    filename = f"{path}{component}.rds"


    model = base.readRDS(filename)

    return model