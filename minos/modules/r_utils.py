"""
R utility functions. These are currently all related to the use of transition models.
"""
import os
os.environ['R_HOME'] = "/Library/Frameworks/R.framework/Resources" # path to R depends on user.

import rpy2.robjects as ro
from rpy2.robjects import IntVector, StrVector, pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter
import pandas as pd

def load_transitions(component, path = 'data/transitions/'):
    """
    This function will load transition models that have been generated in R and saved as .rds files.
    
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
    # import base R package
    base = importr('base')

    # generate filename from arguments and load model
    filename = f"{path}{component}.rds"
    model = base.readRDS(filename)

    return model


def predict_next_timestep(model, current, independant):
    """
    This function will take the transition model loaded in load_transitions() and use it to predict the next timestep
    for a module.

    Parameters
    ----------
    Model : R rds object
        Fitted model loaded in from .rds file
    current : vivarium.framework.population.PopulationView
        View including columns that are required for prediction

    Returns:
    -------
    A prediction of the information for next timestep
    """
    # import R packages
    base = importr('base')
    stats = importr('stats')

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    prediction = stats.predict(model, currentRDF)
    newRPopDF = base.cbind(currentRDF, hh_income = prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    #newPandasPopDF[[independant]] = newPandasPopDF[['predicted']]
    #newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    return newPandasPopDF[["hh_income"]]

def predict_next_timestep_clm(model, current):
    """
    This function will take the transition model loaded in load_transitions() and use it to predict the next timestep
    for a module.
    Parameters
    ----------
    Model : R rds object
        Fitted model loaded in from .rds file
    Returns:
    -------
    A prediction of the information for next timestep
    """
    # import R packages
    base = importr('base')
    stats = importr('stats')
    ordinal = importr('ordinal')

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # NOTE clm package predict function is a bit wierdly written. The predict type "prob" gives the probability of an
    # individual belonging to each possible next state. If there are 4 states this is a 4xn matrix.
    # If the response variable (y in this case/ next housing state) is specific it ONLY gives the probability of being
    # in next true state (1xn matrix). Not an issue here as next housing state y isn't in the vivarium population.

    # R predict.clm method returns a matrix of probabilities of beloning in each state.
    prediction = stats.predict(model, currentRDF, type="prob")

    # Convert prob matrix back to pandas.
    with localconverter(ro.default_converter + pandas2ri.converter):
        prediction_matrix_list = ro.conversion.rpy2py(prediction[0])
    predictionDF = pd.DataFrame(prediction_matrix_list)
    return predictionDF
  
