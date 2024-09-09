""" File for missing data correction using last observation carried forward.

Note this is quite slow to do. Lambda functions aren't terrible but this can probably be improved.
"""

import pandas as pd
import numpy as np
import US_utils
import US_missing_description
from multiprocessing import Pool, cpu_count
from functools import partial
from itertools import repeat
from scipy import interpolate


def applyParallelLOCF(dfGrouped, func, columns):
    """ Apply pandas.apply() methods in parallel on groupby object.

    Parameters
    ----------
    dfGrouped : pandas.groupby
        Groupby object in pandas sorted by pidp and interview year (time) usually.
    func : function
        Function to apply in parallel over groupby object
    Returns
    -------
    dfGrouped : pandas.groupby
        Object with func applied.
    """
    with Pool(cpu_count()) as p:
        #ret_list = p.map(partial(func, **kwargs), [group for name, group in dfGrouped])
        #dfGrouped = zip([group for name, group in dfGrouped])
        ret_list = p.starmap(func, zip(dfGrouped, repeat(columns)))
    return pd.concat(ret_list)


def ffill_groupby(pid_groupby, f_columns):
    """ forward fill groupby object

    Parameters
    ----------
    pid_groupby : pandas.groupby
        Pandas groupby object with data sorted by some set of variables. pidp and interview year (time) usually.

    Returns
    -------
    pid_groupby : Object with forward filled variables.
    """
    #return pid_groupby.apply(lambda x: x.replace(US_utils.missing_types, method="ffill"))
    return pid_groupby[f_columns].infer_objects().ffill()


def bfill_groupby(pid_groupby, b_columns):
    """ back fill groupby object

    Parameters
    ----------
    pid_groupby : Pandas groupby object with data sorted by some set of variables. pidp and interview year (time) usually.

    Returns
    -------
    pid_groupby : Object with back filled variables.
    """
    #return pid_groupby.apply(lambda x: x.replace(US_utils.missing_types, method="bfill"))
    #return pid_groupby.apply(lambda x: x.replace(US_utils.missing_types, method="bfill"))
    return pid_groupby[b_columns].infer_objects().bfill()


def fbfill_groupby(pid_groupby, fb_columns):
    """ forward and back fill groupby object
    Parameters
    ----------
    pid_groupby : pandas.groupby
        Pandas groupby object with data sorted by some set of variables. pidp and interview year (time) usually.
    Returns
    -------
    pid_groupby : Object with forward-back filled variables.
    """
    #return pid_groupby.apply(lambda x: x.replace(US_utils.missing_types, method="ffill").replace(US_utils.missing_types, method="bfill"))
    return pid_groupby[fb_columns].infer_objects().ffill().bfill()


def mffill_groupby(pid_groupby, mf_columns):
    """
    Forward fill the maximum observation in groupby object. The filled variable would only be able to increase over
    time.
    Originally used for education_state, as we have the weird problem that some individuals seem to
    bounce between defined education states and lower levels (often 0).
    Subsequently also found to be an issue for number of children ever had by women (US: lnprnt, Minos: nkids_ind_raw);
    v. small number decrease over time

    Parameters
    ----------
    pid_groupby : pandas.groupby
        Pandas groupby object with data sorted by some set of variables. pidp and interview year (time) usually.
    Returns
    -------
    pid_groupby : Object with maximum observation forward filled objects
    """
    return pid_groupby[mf_columns].apply(
        lambda x: pd.DataFrame.cummax(x))


def interpolate(data, interpolate_columns, type='linear'):
    """ Interpolate column based on year time index.

    groupby on pidp
    sort by time year
    set index to time year.
    interpolate linearly using time index.
    reset index.
    return column.

    Parameters
    ----------
    data : pd.DataFrame

    type : str
        Type of interpolation specified by pandas.interpolate. Defaults to linear but others are available and may be useful.
    """
    #return pid_groupby.apply(lambda x: x.replace(US_utils.missing_types, method="ffill").replace(US_utils.missing_types, method="bfill"))
    data = data.sort_values(by=["pidp", "time"])
    #data[interpolate_columns] = data[interpolate_columns].replace(US_utils.missing_types, np.nan)
    data.index = data['time']
    data_groupby = data.groupby('pidp', sort=False, as_index=False)
    new_columns = data_groupby[interpolate_columns].apply(lambda x: x.interpolate(method=type, limit_direction='both', axis=0))
    new_columns = new_columns.reset_index(drop=True)
    data = data.reset_index(drop=True) # groupby messes with the index. make them unique again.

    new_columns.columns = interpolate_columns
    data[interpolate_columns] = new_columns
    return data


def linear_interpolator_groupby(pid_groupby, type="forward"):
    """ Linear interpolation for deterministic increases like age.

    Filling in deterministically missing age values isn't possible with locf filling. Need to increase age year on year.
    This does linear interpolation in this case.

    Parameters
    ----------
    pid_groupby : pandas.groupby
        Pandas groupby object with data sorted by some set of variables. pidp and interview year (time) usually.
    type : str
        Determine forward/back/both direction interpolation. usually both for age as its deterministic but need to be careful if
        not e.g. job duration can be interpolated forwards but not backwards. Choice of "forward", "backward" and "both".
        See docs of pandas.interpolate for loads of other interpolation methods and args.

    Returns
    -------
    pid_groupby : pandas.groupby
        Groupby with linear interpolation filled in.
    """
    # TODO needs fixing. isnt quite interpolating age properly. Can't get this to work. come back later and use stupid version for now.
    # only interpolate if there are any missing values.
    # TODO could be a better condition really. needs to include strings or anything in US_utils.missing_types.
    #try:
    #    if any(pid_groupby["age"]<0) or any(pid_groupby["age"]==np.nan):
    #        if len(pid_groupby>1): # cant interpolate if there are no data available! needs alternative derivation.
    #            pid_groupby.index = pid_groupby["time"]
    #            return pid_groupby.apply(lambda x: x.interpolate(method="index", limit_direction=type, axis=0))
    #except:
    #    pass
    return pid_groupby.apply(lambda x: x.interpolate(method="linear", limit_direction=type))
    #return pid_groupby.apply(lambda x: interpolate.interp1d(x["time"], x["age"])(x["age"]))


def locf_sort(data, sort_vars, group_vars):
    """ Put data into pandas groupby for LOCF interpolation

    Parameters
    ----------
    data : pandas.DataFrame
        Data frame to put into groupby.
    group_vars : list
        Variables to group by in pandas. This is typically a unique identifier (pidp/hidp).
    sort_vars: list
        On top of groupby it is worth sorting a dataframe by logical values such as time.

    Returns
    -------

    """
    print("Starting pandas groupby.. Grab a coffee")
    data = data.sort_values(by=sort_vars)
    # Group data into individuals to fill in separately.
    # Acts as a for loop to fill items by each individual. If you dont this it will try and fill the whole dataframe
    # at once.
    pid_groupby = data.groupby(by=["pidp"], sort=False, as_index=False)
    return pid_groupby


def locf(data, f_columns=None, b_columns=None, fb_columns=None, mf_columns=None):
    """ Last observation carrying for correcting missing data.

    Data is often only recorded when someone either enters the study for
    the first time (immutable values e.g. ethnicity) is
    updated (mutable values e.g. education).
    Otherwise attributes are recorded as missing due to non-applicability (-8).
    This function aims to fill in any missing values due to this. E.g. ethnicity
    will be registered all the way through an individual's observations.

    Parameters
    ----------
    data : pd.DataFrame
        The main `data` frame for US to fix leading entries for. This frame must have pidp, time, and the desired list
        of columns.
    f_columns, b_columns, fb_columns, mf_columns : list
        Lists of columns to forward, back, forward-and-back and forward-monotonic LOCF interpolate respectivelty.
    li_columns: list
        List of columns to linearly interpolate e.g. age

    Returns
    -------
    data : pd. DataFrame
        The data frame with missing data correction done by observation carrying.

    """
    print("Starting locf. Grab a coffee..")
    # sort values by pidp and time. Need chronological order for carrying to make sense.
    # Also allows for easy replacing of filled data later.
    data = data.sort_values(by=["pidp", "time"])

    # Group data into individuals to fill in separately.
    # Acts as a for loop to fill items by each individual. If you dont this it will try and fill the whole dataframe
    # at once.
    pid_groupby = data.groupby(by=["pidp"], sort=False, as_index=False)
    pid_groupby = [group for name, group in pid_groupby]

    print("groupby done. interpolating..")
    # Fill missing data by individual for given carrying type. Forwards, backwards, or forward then backwards.
    # See pandas ffill and bfill functions for more details.
    if f_columns:
        # Forward fill.
        fill = applyParallelLOCF(pid_groupby, ffill_groupby, f_columns)
        data[f_columns] = fill[f_columns]
    if b_columns:
        # backward fill. only use this on IMMUTABLE attributes.
        fill = applyParallelLOCF(pid_groupby, bfill_groupby, b_columns)
        data[b_columns] = fill[b_columns]
    if fb_columns:
        # forwards and backwards fill. again immutables only.
        fill = applyParallelLOCF(pid_groupby, fbfill_groupby, fb_columns)
        data[fb_columns] = fill[fb_columns]
    if mf_columns:
        # Forward fill monotonic
        fill = applyParallelLOCF(pid_groupby, mffill_groupby, mf_columns)
        data[mf_columns] = fill[mf_columns]
    data = data.reset_index(drop=True) # groupby messes with the index. make them unique again.
    return data


def main(data, save=False):

    US_missing_description.missingness_table(data)

    #f_columns = ["education_state", "depression", "depression_change",
    #             "labour_state", "job_duration_m", "job_duration_y", "job_occupation",
    #             "job_industry", "job_sec", "heating"]  # add more variables here.
    # define columns to be forward filled, back filled, and linearly interpolated.
    # note columns can be forward and back filled for immutables like ethnicity.
    f_columns = ['education_state', 'labour_state_raw', 'job_sec', 'heating',
                 'yearly_gas', 'yearly_electric', 'yearly_gas_electric', 'yearly_oil', 'yearly_other_fuel', 'smoker',
                 'nkids_ind_raw', 'nresp', 'region',  # 'ncigs', 'ndrinks']
                 'loneliness',
                 'burglaries', 'car_crime', 'drunks', 'muggings', 'racial_abuse', 'teenagers', 'vandalism',  # nh_safety
                 'fruit_days', 'fruit_per_day', 'veg_days', 'veg_per_day']
    fb_columns = ["sex", "ethnicity", "birth_year", 'pidp', 'nkids_ind_raw']  # or here if they're immutable.
    mf_columns = ['education_state', 'nkids_ind_raw', 'pidp']
    li_columns = ["age"]
    data = locf(data, f_columns=f_columns, fb_columns=fb_columns, mf_columns=mf_columns)
    print("After LOCF correction.")
    US_missing_description.missingness_table(data)
    data = interpolate(data, li_columns)
    print("After interpolation of linear variables.")
    US_missing_description.missingness_table(data)

    if save:
        US_utils.save_multiple_files(data, years, 'data/locf_US/', "")
    return data


if __name__ == "__main__":
    # Load in data.
    maxyr = US_utils.get_data_maxyr()
    years = np.arange(2009, maxyr)
    # Process data by year and pidp.
    # perform LOCF using lambda forward fill functions.
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    data = main(data)
