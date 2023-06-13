"""
R utility functions. These are currently all related to the use of transition models.
"""
# TODO figure out scaling of variables in Rpy2. makes models more stable.
# TODO: Rewrite all these functions to generalise more. Lots of duplicated code

import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.vectors import FactorVector
import pandas as pd
import numpy as np
import matplotlib.pyplot as pl


def load_transitions(component, rpy2_modules, path='data/transitions/'):
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
    base = rpy2_modules['base']

    # generate filename from arguments and load model
    filename = f"{path}/{component}.rds"
    model = base.readRDS(filename)

    return model


def predict_next_timestep_ols(model, rpy2_modules, current, dependent):
    """
    This function will take the transition model loaded in load_transitions() and use it to predict the next timestep
    for a module.

    Parameters
    ----------
    model : R rds object
        Fitted model loaded in from .rds file
    current : vivarium.framework.population.PopulationView
        View including columns that are required for prediction
    dependent : str
        The independent variable we are trying to predict

    Returns:
    -------
    A prediction of the information for next timestep
    """
    # import R packages
    base = rpy2_modules['base']
    stats = rpy2_modules['stats']

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    prediction = stats.predict(model, currentRDF)
    newRPopDF = base.cbind(currentRDF, predicted=prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    newPandasPopDF[[dependent]] = newPandasPopDF[['predicted']]
    newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    return newPandasPopDF[[dependent]]


def predict_next_timestep_ols_diff(model, rpy2_modules, current, dependent, year):
    """
    This function will take the transition model loaded in load_transitions() and use it to predict the next timestep
    for a module.

    Parameters
    ----------
    model : R rds object
        Fitted model loaded in from .rds file
    current : vivarium.framework.population.PopulationView
        View including columns that are required for prediction
    dependent : str
        The independent variable we are trying to predict

    Returns:
    -------
    A prediction of the information for next timestep
    """

    # import R packages
    base = rpy2_modules['base']
    stats = rpy2_modules['stats']

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    prediction = stats.predict(model, currentRDF)
    newRPopDF = base.cbind(currentRDF, predicted=prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    #newPandasPopDF[[dependent]] = newPandasPopDF[['predicted']]
    #newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    # Now add the predicted value to hh_income and drop predicted
    newPandasPopDF['new_dependent'] = newPandasPopDF[[dependent, 'predicted']].sum(axis=1)
    newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    # new_dependent is module var, predicted is module_diff var
    return newPandasPopDF[['new_dependent', 'predicted']]


def predict_next_timestep_clm(model, rpy2modules, current, dependent):
    """
    This function will take the transition model loaded in load_transitions() and use it to predict the next timestep
    for a module.
    Parameters
    ----------
    model : R rds object
        Fitted model loaded in from .rds file
    current : vivarium.framework.population.PopulationView
        View including columns that are required for prediction
    dependent : str
        The dependent variable we are trying to predict
    Returns:
    -------
    A prediction of the information for next timestep
    """
    # import R packages
    base = rpy2modules['base']
    stats = rpy2modules['stats']
    ordinal = rpy2modules['ordinal']

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # need to cast the dependent var to an R FactorVector
    if dependent in ['loneliness', 'neighbourhood_safety', 'housing_quality']:
        dependent_index = list(currentRDF.colnames).index(dependent)
        dependent_col = FactorVector(currentRDF.rx2(dependent))
        currentRDF[dependent_index] = dependent_col

    # NOTE clm package predict function is a bit wierdly written. The predict type "prob" gives the probability of an
    # individual belonging to each possible next state. If there are 4 states this is a 4xn matrix.
    # If the response variable (y in this case/ next housing state) is specific it ONLY gives the probability of being
    # in next true state (1xn matrix). Not an issue here as next housing state y isn't in the vivarium population.

    # R predict.clm method returns a matrix of probabilities of belonging in each state.
    prediction = stats.predict(model, currentRDF, type="prob")

    # Convert prob matrix back to pandas.
    with localconverter(ro.default_converter + pandas2ri.converter):
        prediction_matrix_list = ro.conversion.rpy2py(prediction[0])
    predictionDF = pd.DataFrame(prediction_matrix_list)

    return predictionDF


def predict_nnet(model, rpy2Modules, current, columns):
    """
    Function for predicting next state using nnet models.

    Parameters
    ----------
    model : R rds object
        Fitted model loaded in from .rds file
    current : vivarium.framework.population.PopulationView
        View including columns that are required for prediction
    columns : Iterable[str]
        List of potential output levels that have an associated probability

    Returns
    -------

    """
    # import R packages
    base = rpy2Modules['base']
    stats = rpy2Modules['stats']
    nnet = rpy2Modules['nnet']
    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    prediction = stats.predict(model, currentRDF, type="probs", na_action='na_omit')

    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(prediction)

    return pd.DataFrame(newPandasPopDF, columns=columns)


def predict_next_timestep_zip(model, rpy2Modules, current, dependent):
    """ Get next state for alcohol monthly expenditure using zero inflated poisson models.

    Parameters
    ----------
    model : R rds object
        Fitted model loaded in from .rds file
    current: pd.DataFrame
        current population dataframe.
    dependent : str
        The dependent variable we are trying to predict
    rescale_factor : int
        Value for rescaling the dependent variable

    Returns
    -------

    """

    base = rpy2Modules['base']
    stats = rpy2Modules['stats']
    zeroinfl = rpy2Modules['zeroinfl']

    # grab transition model
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # grab count and zero prediction types
    # count determines values if they actually drink
    # zero determine probability of them not drinking
    counts = stats.predict(model, currentRDF, type="count")
    zeros = stats.predict(model, currentRDF, type="zero")


    with localconverter(ro.default_converter + pandas2ri.converter):
        counts = ro.conversion.rpy2py(counts)
    with localconverter(ro.default_converter + pandas2ri.converter):
        zeros = ro.conversion.rpy2py(zeros)

    # draw randomly if a person drinks
    # if they drink assign them their predicted value from count.
    # otherwise assign 0 (no spending).
    preds = (np.random.uniform(size=zeros.shape) >= zeros) * counts
    return np.ceil(preds)


def predict_next_timestep_gee(model, rpy2_modules, current, dependent):
    """
    This function will take the transition model loaded in load_transitions() and use it to predict the next timestep
    for a module.
    Parameters
    ----------
    model : R rds object
        Fitted model loaded in from .rds file
    current : vivarium.framework.population.PopulationView
        View including columns that are required for prediction
    dependent : str
        The independent variable we are trying to predict
    Returns:
    -------
    A prediction of the information for next timestep
    """
    # import R packages
    base = rpy2_modules['base']
    geepack = rpy2_modules['geepack']
    stats = rpy2_modules['stats']

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    prediction = stats.predict(model, currentRDF, type='response', allow_new_levels=True)
    newRPopDF = base.cbind(currentRDF, predicted = prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    newPandasPopDF[[dependent]] = newPandasPopDF[['predicted']]
    newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    return newPandasPopDF[[dependent]]


def predict_next_timestep_yj_gaussian_gee(model, rpy2_modules, current, dependent, noise_std = 1):
    """
    This function will take the transition model loaded in load_transitions() and use it to predict the next timestep
    for a module.
    Parameters
    ----------
    model : R rds object
        Fitted model loaded in from .rds file
    current : vivarium.framework.population.PopulationView
        View including columns that are required for prediction
    dependent : str
        The independent variable we are trying to predict
    Returns:
    -------
    A prediction of the information for next timestep
    """
    # import R packages
    base = rpy2_modules['base']
    geepack = rpy2_modules['geepack']
    stats = rpy2_modules['stats']
    bestNormalize = rpy2_modules['bestNormalize']
    n = current.shape[0]


    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)


    # Inverse yeojohnson transform.
    # Stored in estimate_transitions.R.
    # Note inverse=True arg is needed to get back to actual gross income.
    yj = model.rx2('transform') # use yj from fitted model for latest year.
    currentRDF[currentRDF.names.index(dependent)] = stats.predict(yj, newdata=currentRDF.rx2(dependent))  # apply yj transform
    ols_data = stats.predict(model, newdata=currentRDF)  # estimate next income using OLS.

    ols_data = ols_data.ro + stats.rnorm(n, 0, noise_std) # add gaussian noise with variance 10.
    prediction = stats.predict(yj, newdata=ols_data, inverse=True)  # invert yj transform.

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    newRPopDF = base.cbind(currentRDF, predicted = prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    newPandasPopDF[[dependent]] = newPandasPopDF[['predicted']]
    newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    return newPandasPopDF[[dependent]]
