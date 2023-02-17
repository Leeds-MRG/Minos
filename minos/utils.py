"""
utility functions. A lot  borrowed from vivarium population spenser to avoid importing that package.
"""

import argparse
import yaml
import numpy as np
import os
import pandas as pd
import datetime
from itertools import product
import scipy

import sys
import importlib
from vivarium.config_tree import ConfigTree


# All of this is borrowed from VPS.
DAYS_PER_YEAR = 365.25
DAYS_PER_MONTH = DAYS_PER_YEAR / 12


def read_config(config_file):

    # Open the vivarium config yaml.
    with open(config_file) as file:
        config = ConfigTree(yaml.full_load(file))
    return config


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
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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