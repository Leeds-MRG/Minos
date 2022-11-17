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

from vivarium.config_tree import ConfigTree


# All of this is borrowed from VPS.
DAYS_PER_YEAR = 365.25
DAYS_PER_MONTH = DAYS_PER_YEAR / 12


def get_config(config):

    # Open the vivarium config yaml.
    with open(config) as config_file:
        config = ConfigTree(yaml.full_load(config_file))
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
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


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
