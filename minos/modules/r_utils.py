"""
R utility functions. These are currently all related to the use of transition models.
"""
# TODO figure out scaling of variables in Rpy2. makes models more stable.
# TODO: Rewrite all these functions to generalise more. Lots of duplicated code

import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, r
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.vectors import FactorVector
from rpy2.robjects import numpy2ri
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
    return np.array(prediction)


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
    return np.array(prediction)


def predict_next_timestep_logit(model, rpy2modules, current, dependent):
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
    #glm = rpy2modules['glm']

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # NOTE clm package predict function is a bit wierdly written. The predict type "prob" gives the probability of an
    # individual belonging to each possible next state. If there are 4 states this is a 4xn matrix.
    # If the response variable (y in this case/ next housing state) is specific it ONLY gives the probability of being
    # in next true state (1xn matrix). Not an issue here as next housing state y isn't in the vivarium population.

    # R predict.clm method returns a matrix of probabilities of belonging in each state.
    prediction = stats.predict(model, currentRDF, type="response")

    # Convert prob matrix back to pandas.
    return np.array(prediction)


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
    return pd.DataFrame(np.array(prediction)[0])


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

    return pd.DataFrame(np.array(prediction), columns=columns)

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

    # draw randomly if a person drinks
    # if they drink assign them their predicted value from count.
    # otherwise assign 0 (no spending).
    preds = (np.random.uniform(size=len(zeros)) >= zeros) * counts
    return np.ceil(preds)


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

    return np.array(prediction)

def predict_next_timestep_yj_gaussian_lmm(model, rpy2_modules, current, dependent, reflect, log_transform=False, noise_std = 0):
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
    if dependent == "SF_12_MCS_MCS":
        current.loc[current[dependent] <= 0.0, dependent] = 0.01


    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # flip left skewed data to right skewed about its maximum.
    if reflect:
        if dependent in ["SF_12_PCS", "SF_12_MCS_MCS"]:
            max_value = model.do_slot("max_value")
            min_value = model.do_slot("min_value")
        max_value = model.do_slot("max_value")
        currentRDF[currentRDF.names.index(dependent)] = max_value.ro - currentRDF.rx2(dependent) + 10


    if log_transform:
        # log transformation currently only for PCS (also testing MCS)
        currentRDF[currentRDF.names.index(dependent)] = base.log(currentRDF.rx2(dependent))

    # explicitly convert to matrix to overcome error in predict_merMod below
    #currentRDF_matrix = matrix.as_matrix(currentRDF)

    prediction = lme4.predict_merMod(model, currentRDF, type='response', allow_new_levels=True)  # estimate next income using OLS.

    # if dependent == "SF_12_MCS":
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

    # flip left skewed data to right skewed about its maximum.
    if reflect:
        max_value = model.do_slot("max_value")
        currentRDF[currentRDF.names.index(dependent)] = max_value.ro - currentRDF.rx2(dependent)

    if log_transform:
        prediction = base.exp(prediction)


    valid_dependents = ['hh_income', 'hh_income_new', 'nutrition_quality_new', 'nutrition_quality',
                        'nutrition_quality_diff', 'SF_12_PCS', 'SF_12_MCS_MCS']
    if dependent == "SF_12_MCS" and noise_std:
        prediction = prediction.ro + stats.rnorm(current.shape[0], 0, noise_std) # add gaussian noise.
    elif (dependent in valid_dependents) and noise_std:
        VGAM = rpy2_modules["VGAM"]
        prediction = prediction.ro + VGAM.rlaplace(current.shape[0], 0, noise_std)  # add gaussian noise.
    else:
        prediction = prediction # no noise is added.

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    # Convert back to pandas
    return np.array(prediction)

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

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)


    # load YJ transform
    if yeo_johnson:
        # stupid workaround to get attributes from R S4 type objects. Replaces rx2.
        yj = model.do_slot("transform")

    # flip left skewed data to right skewed about its maximum.
    if reflect:
        max_value = model.do_slot("max_value")
        currentRDF[currentRDF.names.index(dependent)] = max_value.ro - currentRDF.rx2(dependent)


    # get minimum value to reverse transformatino to strictly positve values.
    min_value = model.do_slot("min_value")

    prediction = lme4.predict_merMod(model, newdata=currentRDF, type='response', allow_new_levels=True)  # estimate next income using gamma GEE.
    # Inverting transforms to get back to true income values.


    prediction = prediction.ro + (min_value.ro - 0.001) # invert shift to strictly positive values.

    if dependent == 'nutrition_quality':
        prediction = prediction.ro + stats.rnorm(current.shape[0], 0, noise_std) # add gaussian noise.
    elif dependent == "SF_12_MCS" and noise_std:
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
        prediction = max_value.ro - prediction # invert shift to strictly positive values.


    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    # Convert back to pandas
    return np.array(prediction)


def predict_next_rf(model, rpy2_modules, current, dependent):

    # import R packages
    base = rpy2_modules['base']
    stats = rpy2_modules['stats']
    rf = rpy2_modules['randomForest']

    # Convert from pandas to R using package converter
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # R predict method returns a Vector of predicted values, so need to be bound to original df and converter to Pandas
    prediction = stats.predict(model, newdata=currentRDF)
    newRPopDF = base.cbind(currentRDF, predicted=prediction)
    # Convert back to pandas
    return np.array(prediction)


def predict_next_timestep_mixed_zip(model, rpy2Modules, current, dependent, noise_std):
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
    GLMMAdaptive = rpy2Modules['GLMMadaptive']
    #n = current.shape[0]

    # grab transition model
    with localconverter(ro.default_converter + pandas2ri.converter):
        currentRDF = ro.conversion.py2rpy(current)

    # grab count and zero prediction types
    # count determines values if they actually drink
    # zero determine probability of them not drinking

    #only fit subject_specific counts model to non-zero responses. its veryxpensive.
    zeros = stats.predict(model, newdata=currentRDF, type="zero_part")
    is_non_zero_value = np.random.uniform(size=len(zeros)) >= zeros

    non_zero_current = current.loc[is_non_zero_value, ]
    n = non_zero_current.shape[0]

    with localconverter(ro.default_converter + pandas2ri.converter):
        CurrentRDF = ro.conversion.py2rpy(non_zero_current)

    counts = stats.predict(model, newdata = CurrentRDF, type_pred='response', type="subject_specific", cores=8)
    #zeros = counts.do_slot("zi_probs")
    #zeros = stats.predict(model, currentRDF, type="zero_part")

    if noise_std:
        counts = counts.ro + stats.rnorm(n, 0, noise_std) # add gaussian noise.

    with localconverter(ro.default_converter + pandas2ri.converter):
        counts = ro.conversion.rpy2py(counts)
        #zeros = ro.conversion.rpy2py(zeros)


    # draw randomly if a person drinks
    # if they drink assign them their predicted value from count.
    # otherwise assign 0 (no spending).
    #preds = (np.random.uniform(size=zeros.shape) >= zeros) * counts
    preds = np.zeros(shape=current.shape[0])
    preds[is_non_zero_value, ] = counts
    #return np.ceil(preds)
    return preds



def randomise_fixed_effects(model, rpy2_modules, type):
    """ Randomise fixed effects according to multi-variate normal distribution common for transition models used in MINOS
    Parameters
    ----------
    model: rpy2.RO
        What model is having fixed affects adjusted?
    rpy2_modules: dict[rpy2.RO]
        Dictionary of R modules used to estimate transition probabilities
    type: string
        Type of model having fixed effects adjusted. REquired variables can have different names (e.g. beta or coefs).
        For now this is going to be clm and glmm. maybe extend to other types of models using MCMC.
    Returns
    -------
    model rpy2.RO
        Same model class with adjusted fixed effects.
    """

    if type == "glmm":
        beta = model.do_slot("beta")
        Sigma = model.do_slot("cov_matrix")
        MASS = rpy2_modules["MASS"]
        new_beta = MASS.mvrnorm(1, beta, Sigma)
        model.slots['beta'] = new_beta
    elif type == "lmm":
        beta = model.do_slot("beta")
        Sigma = model.do_slot("cov_matrix")
        MASS = rpy2_modules["MASS"]
        new_beta = MASS.mvrnorm(1, beta, Sigma)
        model.slots['beta'] = new_beta
    elif type == "clm":
        beta = model.rx2['beta']
        Sigma = model.rx2["cov_matrix"]
        MASS = rpy2_modules["MASS"]
        new_beta = MASS.mvrnorm(1, beta, Sigma)
        model.rx2['beta'] = new_beta
    elif type == "logit":
        beta = model.rx2['coefficients']
        Sigma = model.rx2["cov_matrix"]
        MASS = rpy2_modules["MASS"]
        new_beta = MASS.mvrnorm(1, beta, Sigma)
        model.rx2['beta'] = new_beta
    elif type == "zip":
        coefficients = model.rx2["coefficients"]
        count_betas = coefficients.rx2["count"]
        zero_betas = coefficients.rx2["zero"]

        count_Sigma = model.rx2["count_cov_matrix"]
        zero_Sigma = model.rx2["zero_cov_matrix"]

        MASS = rpy2_modules["MASS"]
        new_count_beta = MASS.mvrnorm(1, count_betas, count_Sigma)
        new_zero_beta = MASS.mvrnorm(1, zero_betas, zero_Sigma)
        new_coefficients = coefficients
        new_coefficients.rx2['count'] = new_count_beta
        new_coefficients.rx2['zero'] = new_zero_beta

        model.rx2["coefficients"] = new_coefficients

    return model