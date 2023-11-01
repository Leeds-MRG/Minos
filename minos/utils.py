"""
utility functions. A lot  borrowed from vivarium population spenser to avoid importing that package.
"""

import argparse
import yaml
import numpy as np
import os
from os.path import dirname as up
import pandas as pd
from datetime import datetime
from itertools import product
import scipy
from math import sqrt, log, ceil, floor
from random import random
from numpy.random import choice


import sys
import importlib
from vivarium.config_tree import ConfigTree


# All of this is borrowed from VPS.
DAYS_PER_YEAR = 365.25
DAYS_PER_MONTH = DAYS_PER_YEAR / 12

OUTPATH_DEFAULT = up(up(up(__file__)))
# BIN_EDGES_DEFAULT = [10, 20, 25, 30, 101]
# BIN_EDGES_DEFAULT = list(range(-1, 101, 5))
BIN_EDGES_DEFAULT = list(range(-1, 101))
# BIN_LABELS_DEFAULT = [str(el) + "to" + str(BIN_EDGES_DEFAULT[i + 1]) for i, el in enumerate(BIN_EDGES_DEFAULT[0:-1])]


def read_config(config_file):

    # Open the vivarium config yaml.
    with open(config_file) as file:
        config = ConfigTree(yaml.full_load(file))
    return config


def get_latest_subdirectory(runtime_list):
    """
    This function will return the latest runtime subdirectory when runtime_list is a list with len > 1. In the case that
    runtime_list is a list with only a single element, then that single element will be returned (as this indicates
    that there is only a single subdirectory to choose from.

    This function is required for generating outcomes based on the latest run of data, and can be modified if specific
    runs are required that are not the latest (although this will probably never be necessary).

    Parameters
    ----------
    runtime_list : list
        List of runtime subdirectories, which are all datetime values that were allocated the exact time when a run
        began.

    Returns
    -------
    runtime : string
        The latest (or only) runtime string for creating the directory when loading data from a Minos run.
    """

    if len(runtime_list) > 1:
        # if more than 1, select most recent datetime
        runtime = max(runtime_list, key=lambda d: datetime.strptime(d, "%Y_%m_%d_%H_%M_%S"))
    elif len(runtime_list) == 1:
        runtime = runtime_list[0]  # os.listdir returns a list, we only have 1 element
    else:
        raise RuntimeError("The output directory supplied contains no subdirectories, and therefore no data to "
                           "aggregate. Please check the output directory.")

    return runtime


# TODO Investigate the mock artifact manager. Not sure if this is what we should be using.
def base_plugins():
    config = {'required': {
                  'data': {
                      'controller': 'minos.testing.mock_artifact.MockArtifactManager',
                      'builder_interface': 'vivarium.framework.artifact.ArtifactInterface'
                  }
             }
    }
    return ConfigTree(config)


def get_age_bucket(simulation_data):
    """
    Assign age bucket to an input population. These are the age buckets:
    0 - 15;
    16 - 19;
    20 - 24;
    25 - 29;
    30 - 44;
    45 - 59;
    60 - 74;
    75 +

    Parameters
    ----------
    simulation_data : Dataframe
        Input data from the VPH simulation

    Returns:
    -------
    A dataframe with a new column with the age bucket.

    """
    # Age buckets based on the file names
    cut_bins = [-1, 16, 20, 25, 30, 45, 60, 75, 200]
    cut_labels = ["0to15", "16to19", "20to24", "25to29", "30to44", "45to59", "60to74", "75plus"]
    simulation_data.loc[:, "age_bucket"] = pd.cut(simulation_data['age'], bins=cut_bins, labels=cut_labels)

    return simulation_data


def to_years(time: pd.Timedelta) -> float:
    """Converts a time delta to a float for years."""
    return time / pd.Timedelta(days=DAYS_PER_YEAR)


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_uniform_pop_data(age_bin_midpoint=False):
    age_bins = [(n, n + 5) for n in range(0, 100, 5)]
    sexes = ('Male', 'Female')
    years = zip(range(1990, 2018), range(1991, 2019))
    locations = (1, 2)

    age_bins, sexes, years, locations = zip(*product(age_bins, sexes, years, locations))
    mins, maxes = zip(*age_bins)
    year_starts, year_ends = zip(*years)

    pop = pd.DataFrame({'age_start': mins,
                        'age_end': maxes,
                        'sex': sexes,
                        'year_start': year_starts,
                        'year_end': year_ends,
                        'location': locations,
                        'value': [100] * len(mins)})
    if age_bin_midpoint:  # used for population tests
        pop['age'] = pop.apply(lambda row: (row['age_start'] + row['age_end']) / 2, axis=1)
    return pop


REPLACEMENTS_DEFAULT = {"\n": "\n"} # i.e. do nothing


def get_nearest(reference_list, value):
    # HR 17/04/23 To grab nearest value in list of integers
    if value in reference_list:
        nearest = value
    elif value < min(reference_list):
        nearest = min(reference_list)
    elif value > max(reference_list):
        nearest = max(reference_list)
    return nearest


def sample_discrete(dict_in, n_samples=1):
    """
    Get sample(s) from discrete distribution

    Parameters
    ----------
    dict_in : dict
        Dict of values and number of occurrences of each
    n_samples
        Number of samples to be returned

    Returns
    -------
    samples : list of float
        n_samples x values sampled from input distribution

    """
    _sum = sum(dict_in.values())
    occurrences = [el/_sum for el in dict_in.values()]
    samples = choice(list(dict_in.keys()), size=n_samples, p=occurrences)
    return samples


def replace_text(input_text, replacements=REPLACEMENTS_DEFAULT):
    num_rep = len(replacements)
    print('++ Total replacements:', num_rep)
    for i, (old_text, new_text) in enumerate(replacements.items()):
        print('Replacement', i+1, 'of', num_rep, ':', old_text, 'for', new_text)
        print('Before:', input_text.count(old_text), input_text.count(new_text))
        input_text = input_text.replace(old_text, new_text)
        print('After:', input_text.count(old_text), input_text.count(new_text))
    return input_text


def patch(module, modification_function=replace_text, *args, **kwargs):
    '''
    HR 09/02/23
    To patch module at runtime arbitrarily

    1. Adapted from here: https://stackoverflow.com/questions/5362771/how-to-load-a-module-from-code-in-a-string
    2. ...and here: https://stackoverflow.com/questions/41858147/how-to-modify-imported-source-code-on-the-fly

    Much simpler ways are available for:
    1. Adding/removing methods entirely
    2. Overriding methods entirely
    3. Wrapping/decorating methods, e.g. if only inputs/outputs need to be modified

    Usage:
    e.g. replace block of code:
    module = patch(module, replacements={'old_text':'new_text'})

    By default, method does nothing
    '''
    print('Running "patch"')

    module_name = module.__name__
    # 1. Retrieve module code as text
    spec = importlib.util.find_spec(module_name, None)
    old_source = spec.loader.get_source(module_name)

    # 2. Modify code of module in text form
    new_source = modification_function(old_source, *args, **kwargs)

    # 3. Create/load module using modified text
    module = importlib.util.module_from_spec(spec)
    codeobj = compile(new_source, module.__spec__.origin, 'exec')
    exec(codeobj, module.__dict__)
    sys.modules[module_name] = module
    globals()[module_name] = module
    return module


## SERIES SOLVER FUNCTIONS BELOW, FOR FERTILITY/PARITY
## FEB 23 ONWARDS

# HR 20/02/23 To solve a geometric series for the ratio r
# Adapted from this: https://math.stackexchange.com/questions/3473457/how-to-find-r-in-a-finite-geometric-series
# Required for:
# 1. Estimating fertility rates by parity to data binned into N+ births
# 2. Breaking up fertility/parity when given in age group (i.e <14y and >44y) into individual years

# HR 05/06/23 Update for readability
# Functionality is implementation of Newton method and contains some tweaks using perturbations to avoid blow-up
# Also adding more documentation to make it more obvious how to use it


TOL_DEFAULT = 1e-6
MAX_ITER_DEFAULT = 50
FACTOR_DEFAULT = 0.2 # Very important! Test case 1 blows up if this is close to unity
ROUND_DEFAULT = "up"


def f0(a, r, n, s):
    """
    Function for which root is sought
    Ultimately a rearrangement of expression for finite geometric series
    i.e. s = a * (1 - r^n) / (1 - r)

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio of series
    n : int
        Number of terms in series
    s : float
        Sum of series

    Returns
    -------
    f : float

    """
    f = a * (1 - r ** n) - s * (1 - r)
    return f


def f1(a, r, n, s):
    """
    First derivative of f0 w.r.t common ratio r
    Used in Newton solution (i.e. "solve" method)

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio of series
    n : int
        Number of terms in series
    s : float
        Sum of series

    Returns
    -------
    f : float

    """
    f = -a * n * (r ** (n - 1)) + s
    return f


def f2(a, r, n, s):
    """
    Second derivative of f0 w.r.t common ratio r
    Used in Newton solution (i.e. "solve" method)

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio of series
    n : int
        Number of terms in series
    s : float
        Sum of series

    Returns
    -------
    f : float

    """
    f = -a * n * (n - 1) * (r ** (n - 2))
    return f


def get_guess_infinite(a, s):
    """
    Get initial guess for common ratio of geometric series
    by approximating series as infinite
    Ultimately rearrangement of s = a / (1 - r)

    Parameters
    ----------
    a : float
        First term of series
    s : float
        Sum of series

    Returns
    -------
    r0 : float
        Common ratio for infinite geometric series

    """
    r0 = 1 - a / s
    return r0


def get_r_star(a, n, s):
    """
    Get initial estimate of common ratio using
    Used to generate first guess r0, see "get_guess_taylor"

    Parameters
    ----------
    a : float
        First term of series
    n : int
        Number of terms in series
    s : float
        Sum of series

    Returns
    -------
    r_s : float
        Value of r at which f0 is minimum

    """
    r_s = (s / (a * n)) ** (1 / (n - 1))
    return r_s


def get_guess_taylor(a, r_s, n, s):
    """
    Get starting guess for common ratio, r

    Parameters
    ----------
    a : float
        First term of series
    r_s : float
        Estimate for common ratio from "get_r_star"
    n : int
        Number of terms in series
    s : float
        Sum of series

    Returns
    -------
    r0 : float
        First guess for common ratio, r

    """
    upper = f0(a, r_s, n, s)
    lower = f2(a, r_s, n, s)
    # print(upper,lower)
    try:
        r0 = r_s + sqrt(-2 * upper / lower)
    except:
        lower += (random() - 0.5) / 100  # Introduce perturbation to avoid division by zero
        r0 = r_s + sqrt(-2 * upper / lower)
    return r0


def get_next_value(a, r_old, n, s):
    """
    Get next iteration of common ratio, r

    Parameters
    ----------
    a : float
        First term of series
    r_old : float
        Value of common ratio from previous iteration
    n : int
        Number of terms in series
    s : float
        Sum of series

    Returns
    -------
    r_new : float
        Next value of common ratio, r

    """
    upper = f0(a, r_old, n, s)
    lower = f1(a, r_old, n, s)
    # print(upper,lower)
    try:
        r_new = r_old - upper / lower
    except:
        print(lower)
        lower += (random() - 0.5) / 100  # Introduce perturbation to avoid division by zero
        print(lower)
        r_new = r_old - upper / lower
    return r_new


def solve(a, n, s, r0=None, tol=TOL_DEFAULT, imax=MAX_ITER_DEFAULT):
    """
    Seek common ratio of finite geometric series

    Parameters
    ----------
    a : float
        First term of series
    n : int
        Number of terms in series
    s : float
        Sum of series
    r0 : float
        Initial guess for common ratio
    tol : float
        Tolerance for convergence
    imax : int
        Maximum number of iterations

    Returns
    -------
    r : float
        Common ratio of finite geometric series

    """
    # Initialise list of estimates
    r_star = get_r_star(a, n, s)
    # print("r_star:", r_star)

    if not r0:
        r0 = get_guess_taylor(a, r_star, n, s)
        # r0 = get_guess_infinite(a, s)

    # print("\nRunning 'solve' with a,n,s =", a, n, s)
    # print("r0, tol, imax: ", r0, tol, imax)
    #
    # print("Initial guess:", r0)
    r = [r0]
    r1 = get_next_value(a, r0, n, s)
    r.append(r1)

    while abs(r[-1] - r[-2]) > tol:
        if len(r) > imax:
            # print("Max. iterations reached in 'solve'; aborting at iteration", len(r), imax)
            # print("tol =", tol, "; abs(diff) =", abs(r[-1] - r[-2]))
            # print("r = ", r[-1])
            return r
        r_old = r[-1]
        r_new = get_next_value(a, r_old, n, s)
        r.append(r_new)

    # print("Tolerance reached in 'solve' after iteration", len(r) - 1, ", abs(diff) =", abs(r[-1] - r[-2]))
    # print("r = ", r[-1])
    return r


def get_sum(a, r, n):
    """
    Calculate sum of finite geometric series

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio
    n : int
        Number of terms in series

    Returns
    -------
    s : float
        Sum of finite geometric series

    """
    s = a * (1 - r ** n) / (1 - r)
    return s


def generate_series(a, r, n):
    """
    Generate finite geometric series

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio
    n : int
        Number of terms in series

    Returns
    -------
    series : list of float
        Geometric series

    """
    series = [a * r ** (i - 1) for i in range(1, n + 1)]
    return series


def series_ok(a, r, n, series, tol=TOL_DEFAULT):
    """
    Check if sum of series passed as argument matches
    sum of series generated from parameters a, r, n

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio
    n : int
        Number of terms in series
    series : list of float
        Pre-calculated series to be compared
    tol : float
        Tolerance for comparison of two series

    Returns
    -------
    bool
        True if two series are equal (within tolerance)
        False otherwise

    """
    sum_calc = get_sum(a, r, n)
    sum_series = sum(series)
    d = abs(sum_calc - sum_series) / abs(sum_series)
    if d < tol:
        print("Series correct, tol, d =", tol, d)
        return True
    else:
        print("Series NOT correct, tol, d =", tol, d)
        return False


def test_r(a, r, n, s):
    """
    Calculate difference between calculated and correct sum
    with common ratio r
    Used in wrapper function "search" to check for convergence

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio
    n : int
        Number of terms in series
    s : float
        Pre-calculated sum of series

    Returns
    -------
    difference : float
        Difference between correct and calculated sums of series

    """
    try:
        sum = get_sum(a, r, n)
    except:
        r += r * (random() - 0.5) / 100  # Introduce perturbation to avoid division by zero
        sum = get_sum(a, r, n)
    difference = abs(sum - s)
    return difference


def get_series_for_n(a, r, s, round=ROUND_DEFAULT):
    """
    Wrapper for "solve_for_n" to recalculate series
    so that n is an integer as "solve_for_n"
    generally returns a non-integer value for n

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio of series
    s : float
        Sum of series
    round : str
        String used as switch to determine rounding method

    Returns
    -------
    series_n : list of float
        Resulting series
    r_new : int
        Common ratio of series
    n : int
        Number of terms in resulting series

    """
    round_dict = {"up": ceil,
                  "down": floor, }

    # Get estimate for n, which may not be an integer value
    n = solve_for_n(a, r, s)
    if not n:
        print("Could not find n; returning None")

    # Check if integer, else round up/down and create new series with integer-valued n
    if not n.is_integer():
        print("n is not an integer")
        round_method = round_dict.get(round, ROUND_DEFAULT)
        n = round_method(n)

    r_new = search(a, n, s)
    series_n = generate_series(a, r_new, n)
    return series_n, r_new, n


def solve_for_n(a, r, s):
    """
    Solve for number of terms, n, given a, r, s
    Note that n is not generally an integer

    Parameters
    ----------
    a : float
        First term of series
    r : float
        Common ratio of series
    s : float
        Sum of series

    Returns
    -------
    n : float
        Number of terms in series

    """
    r_check = 1 - (a / s)
    print("r_check:", r_check)
    if not r > r_check:
        print("No solution exists; must satisfy r > 1 - a/s; returning None")
        return None

    n = log(1 - (s / a) * (1 - r)) / log(r)
    print("Solved for n =", n)
    return n


def search(a, n, s, r0=None, tol=1e-8, iters=100, factor=FACTOR_DEFAULT):
    """
    Wrapper for "solve" function to avoid numerical instabilities

    Parameters
    ----------
    a : float
        First term of series
    n : int
        Number of terms in series
    s : float
        Pre-calculated sum of series
    r0 : float
        Initial guess for r
    tol : float
        Tolerance for convergence
    iters : int
        Maximum number of iterations
    factor : float


    Returns
    -------
    r : float
        Common ratio of series

    """

    if not r0:
        r_star = get_r_star(a, n, s)
        r0 = get_guess_taylor(a, r_star, n, s)
        # r0 = get_guess_infinite(a, s)

    # print("\nRunning 'search' with a,n,s =", a,n,s)
    # print("r0, tol, iters, factor: ", r0, tol, iters, factor)

    r = solve(a, n, s, r0)[-1]
    d = test_r(a, r, n, s)

    i = 0
    while abs(d) > tol:
        i += 1
        if i > iters:
            # print("Max. iterations reached in 'search'; aborting at iteration", i+1, iters)
            # print("r = ", r)
            return r
        power = (-factor * i) ** i  # Power index toggling between r^i and r^(-i), to cause to stray from unity
        r0 = r0 ** power
        # print("i, r, power =", i, r, power)

        r = solve(a, n, s, r0)[-1]
        d = test_r(a, r, n, s)

    # print("\nTolerance reached in 'search' after iteration ", i+1)
    # print("r =", r)
    # print("abs(d) =", abs(d))
    return r


# # HR 01/03/23 To get first term of series with three known ratios
# # First and second apply to t2/t1 and t3/t2; third applies to all higher terms
# # S is sum to N terms
# def get_first_term(S, N, r1, r2, r3):
#     t1 = T * (1 + r1 + r1 * r2 * ((1 - r3 ** (N - 3)) / (1 - r3))) ** (-1)
#
#     return t1


def extend_series(series_in, n, reverse=False, return_r=False, **kwargs):
    """
    HR 03/03/23 Take truncated series (i.e. one with n terms, the last of which is a sum of n+ terms)...
    and return expanded series following a geometric progression, i.e. without truncation
    Just specify how many terms to expand final term into
    Basic wrapper for "search"

    Parameters
    ----------
    series_in : list of float
        Series to be extended
    n : int
        Number of terms by which series will be extended
    reverse : bool
        True if series is to be prepended, rather than extended
        False if series is to be extended
    return_r : bool
        True if r is to be returned
        False otherwise
    kwargs : kwargs
        Any keyword arguments to be passed to "solve"

    Returns
    -------
    series_out : list of float
        Series
    r : float
        Common ratio of series

    """
    # HR 06/06/23 Adding functionality to prepend series rather than extend
    # Logic is just to reverse series before and after extending
    if reverse:
        series_in = series_in[::-1]

    # Return series of zeroes if either of the last two entries is zero:
    # 1. If last entry, then obvs later ones will be zero
    # 2. If second to last entry, then r will be positive -> not desired; also most likely when numbers are very small
    # if series_in[-1] in [0, 0.0] or series_in[-2] in [0, 0.0]:
    if series_in[-1] <= 0.0 or series_in[-2] <= 0.0:
        series_out = series_in
        series_out.extend([0] * (n - 1))
        r = 0

    else:
        # Main functionality, assuming data are good (i.e. no zeroes in last two entries)
        r = search(series_in[-2], n + 1, sum(series_in[-2:]), **kwargs)  # n+1 important here!
        new_series = generate_series(series_in[-2], r, n + 1)  # n+1 very important here!
        series_out = series_in[:-2]
        series_out.extend(new_series[:])

    if reverse:
        series_out = series_out[::-1]

    if return_r:
        return series_out, r
    else:
        return series_out
