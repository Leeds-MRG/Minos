"""
R utility functions. These are currently all related to the use of transition models.
"""
# TODO figure out scaling of variables in Rpy2. makes models more stable.
# TODO: Rewrite all these functions to generalise more. Lots of duplicated code

import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, r
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.vectors import FactorVector, FloatVector
from rpy2.robjects import numpy2ri
import pandas as pd
import numpy as np
#import matplotlib.pyplot as pl


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
    #print(filename)
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
    if dependent in ['loneliness', 'neighbourhood_safety', 'housing_quality', 'auditc', 'financial_situation',
                     'chron_disease', 'matdep']:
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
        zeros = ro.conversion.rpy2py(zeros)

    # draw randomly if a person drinks
    # if they drink assign them their predicted value from count.
    # otherwise assign 0 (no spending).
    preds = (np.random.uniform(size=zeros.shape) >= zeros) * counts
    return np.ceil(preds)


def predict_next_timestep_logit(model, rpy2_modules, current, dependent):
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
    prediction = stats.predict(model, currentRDF, type='response')
    newRPopDF = base.cbind(currentRDF, predicted = prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    newPandasPopDF[[dependent]] = newPandasPopDF[['predicted']]
    newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    return newPandasPopDF[[dependent]]


def predict_next_timestep_gee(model, rpy2_modules, current, dependent, noise_std):
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

    current["pidp"] = -current["pidp"]

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    prediction = stats.predict(model, currentRDF, type='response', allow_new_levels=True)

    if noise_std:
        VGAM = rpy2_modules["VGAM"]
        prediction = prediction.ro + VGAM.rlaplace(current.shape[0], 0, noise_std) # add gaussian noise.

    newRPopDF = base.cbind(currentRDF, predicted = prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    newPandasPopDF[[dependent]] = newPandasPopDF[['predicted']]
    newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    return newPandasPopDF[[dependent]]


def predict_next_timestep_yj_gaussian_lmm(model, rpy2_modules, current, dependent, log_transform, noise_std = 0):
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
    #geepack = rpy2_modules['geepack']
    stats = rpy2_modules['stats']
    bestNormalize = rpy2_modules['bestNormalize']
    lme4 = rpy2_modules["lme4"]

    #current = current.drop([dependent, 'time'], axis=1)
    #current["pidp"] = -current["pidp"]

    # need to add tiny value to the 0 MCS values as this causes problems in log transform
    if dependent == "SF_12_MCS":
        current.loc[current[dependent] <= 0.0, dependent] = 0.01


    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    if dependent in ["SF_12_PCS", "SF_12_MCS"]:
        max_value = model.do_slot("max_value")
        min_value = model.do_slot("min_value")

    if log_transform:
        # log transformation currently only for PCS (also testing MCS)
        currentRDF[currentRDF.names.index(dependent)] = base.log(currentRDF.rx2(dependent))

    # explicitly convert to matrix to overcome error in predict_merMod below
    #currentRDF_matrix = matrix.as_matrix(currentRDF)

    prediction = lme4.predict_merMod(model, currentRDF, type='response', allow_new_levels=True)  # estimate next income using OLS.

    # if dependent == "SF_12":
    #     ols_data = ols_data.ro + stats.rnorm(n, 0, noise_std) # add gaussian noise.
    # elif dependent == "nutrition_quality":
    #     ols_data = ols_data.ro + stats.rnorm(n, 0, noise_std) # add gaussian noise.
    # elif dependent == 'hh_income' and noise_std:
    #     #VGAM = rpy2_modules["VGAM"]
    #     #ols_data = ols_data.ro + VGAM.rlaplace(n, 0, noise_std) # add gaussian noise.
    #     #ols_data = ols_data.ro + stats.rcauchy(n, 0, noise_std)
    #     ols_data = ols_data.ro + stats.rnorm(n, 0, noise_std) # add gaussian noise.

    # if dependent == "SF_12_PCS":
    #     dependent_list = list(prediction.rx2(dependent))
    #     print("After noise added:")
    #     print(min(dependent_list))
    #     print(max(dependent_list))

    if log_transform:
        prediction = base.exp(prediction)


    valid_dependents = ['hh_income', 'hh_income_new', 'nutrition_quality_new', 'nutrition_quality',
                        'nutrition_quality_diff', 'SF_12_PCS', 'SF_12_MCS']
    if dependent == "SF_12" and noise_std:
        prediction = prediction.ro + stats.rnorm(current.shape[0], 0, noise_std) # add gaussian noise.
    elif (dependent in valid_dependents) and noise_std:
        VGAM = rpy2_modules["VGAM"]
        prediction = prediction.ro + VGAM.rlaplace(current.shape[0], 0, noise_std)  # add gaussian noise.
    else:
        prediction = prediction # no noise is added.

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        #ols_data = ro.conversion.rpy2py(ols_data)
        prediction = ro.conversion.rpy2py(prediction)

    if dependent in ["SF_12_PCS", "SF_12_MCS"]:
        # Final step is to clip the values to min and max seen in input data
        prediction = np.clip(prediction, min_value, max_value)

    return pd.DataFrame(prediction, columns=[dependent])


def predict_next_timestep_yj_gamma_glmm(model, rpy2_modules, current, dependent, reflect, yeo_johnson, noise_std = 1):
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
    #geepack = rpy2_modules['geepack']
    stats = rpy2_modules['stats']
    bestNormalize = rpy2_modules['bestNormalize']
    lme4 = rpy2_modules["lme4"]
    glmmTMB = rpy2_modules["glmmTMB"]

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # flip left skewed data to right skewed about its maximum.
    if reflect:
        max_value = model.do_slot("max_value")
        currentRDF[currentRDF.names.index(dependent)] = max_value.ro - currentRDF.rx2(dependent)

    # load YJ transform
    if yeo_johnson:
        # stupid workaround to get attributes from R S4 type objects. Replaces rx2.
        yj = model.do_slot("transform")

    # get minimum value to reverse transformatino to strictly positve values.
    min_value = model.do_slot("min_value")

    prediction = lme4.predict_merMod(model, newdata=currentRDF, type='response',
                                        allow_new_levels=True)  # estimate next income using gamma GEE.
    # Inverting transforms to get back to true income values.
    prediction = prediction.ro + (min_value.ro - 0.001)  # invert shift to strictly positive values.



    if dependent == 'nutrition_quality':
        prediction = prediction.ro + stats.rnorm(current.shape[0], 0, noise_std) # add gaussian noise.
    elif dependent in ["SF_12_MCS", "SF_12_PCS"] and noise_std:
        VGAM = rpy2_modules["VGAM"]
        prediction = prediction.ro + VGAM.rlaplace(current.shape[0], 0, noise_std) # add gaussian noise.
        #prediction = prediction.ro + stats.rnorm(current.shape[0], 0, noise_std) # add gaussian noise.
    elif (dependent in ["hh_income_new", 'hourly_wage']) and noise_std:
        #VGAM = rpy2_modules["VGAM"]
        #prediction = prediction.ro + VGAM.rlaplace(current.shape[0], 0, noise_std) # add gaussian noise.
        prediction = prediction.ro + stats.rnorm(current.shape[0], 0, noise_std) # add gaussian noise.
        noise = np.clip(stats.rcauchy(current.shape[0], 0, 0.005), -5, 5) #0.005
        with localconverter(ro.default_converter + numpy2ri.converter):
            Rnoise = ro.conversion.py2rpy(noise)
        prediction = prediction.ro + Rnoise # add gaussian noise.
    else:
        prediction = prediction

    if yeo_johnson:
        prediction = stats.predict(yj, newdata=prediction, inverse=True)  # invert yj transform.

    if reflect:
        prediction = max_value.ro - prediction

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        prediction_output = ro.conversion.rpy2py(prediction)

    return pd.DataFrame(prediction_output, columns=[dependent])


def predict_next_timestep_beta_glmm(model, rpy2_modules, current, dependent, reflect, noise_std = 1):
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
    glmmTMB = rpy2_modules["glmmTMB"]

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # flip left skewed data to right skewed about its maximum.
    if reflect:
        max_value = model.do_slot("max_value")
        max_value = FloatVector(max_value)
        currentRDF[currentRDF.names.index(dependent)] = max_value.ro - currentRDF.rx2(dependent)

    # convert PCS to 0-1 range for beta family
    currentRDF[currentRDF.names.index(dependent)] = currentRDF.rx2(dependent) / FloatVector([100]).ro
    #current[dependent] = current[dependent] / 100

    prediction = stats.predict(model,
                               newdata=currentRDF,
                               type='response',
                               allow_new_levels=True)  # estimate next income using beta GLMM.


    if dependent in ["SF_12_MCS", "SF_12_PCS"] and noise_std:
        VGAM = rpy2_modules["VGAM"]
        prediction = prediction.ro + VGAM.rlaplace(current.shape[0], 0, noise_std)  # add gaussian noise.
    else:
        prediction = prediction

    # convert PCS back to 0-100 range for real values
    #currentRDF[currentRDF.names.index(dependent)] = currentRDF.rx2(dependent) * FloatVector([100]).ro

    if reflect:
        prediction = max_value.ro - prediction

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        prediction_output = ro.conversion.rpy2py(prediction)

    # Convert prediction back to 0-100 scale
    prediction = pd.DataFrame(prediction_output, columns=[dependent])
    prediction[dependent] = prediction[dependent] * 100

    return prediction


def predict_next_rf(model, rpy2_modules, current, dependent, noise_std = 1):

    # import R packages
    base = rpy2_modules['base']
    stats = rpy2_modules['stats']
    rf = rpy2_modules['randomForest']

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    prediction = stats.predict(model, newdata=currentRDF)

    # Add noise to predictions
    if dependent in ["SF_12_MCS", "SF_12_PCS"] and noise_std:
        VGAM = rpy2_modules["VGAM"]
        prediction = prediction.ro + VGAM.rlaplace(current.shape[0], 0, noise_std)  # add laplace noise.


    newRPopDF = base.cbind(currentRDF, predicted=prediction)
    # Convert back to pandas
    with localconverter(ro.default_converter + pandas2ri.converter):
        newPandasPopDF = ro.conversion.rpy2py(newRPopDF)

    # Now rename the predicted var (have to drop original column first)
    newPandasPopDF[[dependent]] = newPandasPopDF[['predicted']]
    newPandasPopDF.drop(labels=['predicted'], axis='columns', inplace=True)

    return newPandasPopDF[[dependent]]
