# HR 11/12/24 All utils particular to fertility work with/without parity and GB synthpop
# To include all post-processing, validation and visualisation

import os
from os.path import dirname as up
import pandas as pd
import yaml

CURR_DIR = up(__file__)
PERSISTENT_PATH = os.path.join(up(CURR_DIR), 'persistent_data')
OUTPUT_DEFAULT = os.path.join(up(CURR_DIR), 'output')

COLUMNS_TO_READ = ['alive', 'region', 'nkids_ind', 'age', 'sex',
                   'nnewborn', 'ethnicity', 'child_ages', 'pidp', 'time', 'nkids']


# HR 11/12/24 Get path to latest set of output for specific run configuration
def get_latest(parity=False,
               synthpop=False,
               intervention=None,
               ):
    if parity:
        parity_mode = 'parity'
    else:
        parity_mode = 'noparity'

    if synthpop:
        pop_mode = 'gb_scaled'
    else:
        pop_mode = 'default_config'

    if intervention:
        intervention_mode = intervention  # Placeholder - can replace with dict lookup later if necessary
    else:
        intervention_mode = 'baseline'

    modepath = os.path.join(OUTPUT_DEFAULT, pop_mode + '_' + parity_mode, intervention_mode)
    latest = sorted(os.listdir(modepath))[-1]
    fullpath = os.path.join(modepath, latest)
    return fullpath


# HR 11/12/24 Get run config from file for efficient parsing
def get_config_data(file):
    with open(file, 'r') as f:
        config_data = yaml.safe_load(f)
    return config_data


# HR 11/12/24 Get dictionary of year: data file for simulation output
def get_latest_data(parity=False,
                    synthpop=False,
                    intervention=None,
                    ):
    path = get_latest(parity=parity, synthpop=synthpop)
    config_fullpath = os.path.join(path, 'config_file.yml')
    cd = get_config_data(config_fullpath)

    year_start = cd['time']['start']['year']
    year_end = cd['time']['end']['year']
    years = range(year_start, year_end+1)

    file_dict = {y: str(y) + '.csv' for y in years}
    data = {y: pd.read_csv(os.path.join(path, f))[COLUMNS_TO_READ] for y, f in file_dict.items()}
    return data


# HR 11/12/24 Get mortality and fertility metrics
def get_metrics(pop,
                year,
                ):
    metrics = {}

    # Mortality rate, should be about 10
    alive = pop.loc[(pop.alive == 'alive')]
    dead = pop.loc[(pop.alive == 'dead') & (pop.time == year-1)]
    mort = 100 * len(dead) / len(alive)
    # print('Mortality rate: {:.3f}% ({}/{})'.format(mort, len(dead), len(pop)))
    metrics['mort'] = mort

    # General fertility rate (GFR, i.e. birth rate per 1,000 women of age 15-44, ONS definition), should be 50-60
    women_alive = alive.loc[(alive.alive == 'alive') & (alive.sex == 'Female')]
    women_gfr = women_alive.loc[women_alive.age.between(15, 44)]  # No 15yos in pop, but near enough
    has_newborn = women_gfr.loc[women_gfr.nkids_ind_new == 1]
    gfr = 1000 * len(has_newborn) / len(women_gfr)
    # print('General fertility rate, births per 1,000 women (15-44): {:.3f} ({}/{})'.format(gfr, len(has_newborn), len(women_gfr)))
    metrics['gfr'] = gfr

    # Total fertility rate (TFR, i.e. mean children per woman), should be 1.5-1.6
    tfr = women_alive.nkids_ind.mean()
    # print('TFR (children per woman): {:.3f}'.format(tfr))
    metrics['tfr'] = tfr

    # Crude birth rate (CBR), should be 10-12 per 1,000 people, according to HFD
    n_u16 = women_alive.nresp.sum()
    n_adult = len(pop.loc[pop.alive == 'alive'])
    n_babs = len(women_alive.loc[women_alive.nkids_ind_new == 1])
    cbr = 1000 * n_babs / (n_adult + n_u16)
    # print('CBR, births per 1,000 total pop: {:.3f}'.format(cbr))
    metrics['cbr'] = cbr

    return metrics

if __name__ == '__main__':
    # lat1 = get_latest(False, False)
    # lat2 = get_latest(True, False)
    # lat3 = get_latest(False, True)
    # lat4 = get_latest(True, True)

    dt = get_latest_data()
