# HR 11/12/24 All utils particular to fertility work with/without parity and GB synthpop
# To include all post-processing, validation and visualisation

import os
from os.path import dirname as up
import pandas as pd
import yaml
import matplotlib.pyplot as plt

CURR_DIR = up(__file__)
PERSISTENT_PATH = os.path.join(up(CURR_DIR), 'persistent_data')
FERT_REF_PATH = os.path.join(PERSISTENT_PATH, 'fertility_reference')
OUTPUT_DEFAULT = os.path.join(up(CURR_DIR), 'output')
METRICS_FILE = 'metrics.csv'

COLUMNS_TO_READ = ['alive', 'region', 'nkids_ind', 'age', 'sex',
                   'nnewborn', 'nnewborn_hh', 'ethnicity', 'child_ages', 'pidp', 'time', 'nkids', 'nresp']


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
    year_end = cd['time']['num_years'] + year_start
    years = range(year_start, year_end+1)
    print(config_fullpath)
    print(years)

    file_dict = {y: str(y) + '.csv' for y in years}
    data = {y: pd.read_csv(os.path.join(path, f), low_memory=False)[COLUMNS_TO_READ] for y, f in file_dict.items()}
    return data


# HR 11/12/24 Get mortality and fertility metrics
def get_metrics(pop,
                year,
                ):
    metrics = {}

    # Mortality rate, should be about 1%
    alive = pop.loc[(pop.alive == 'alive')]
    dead = pop.loc[(pop.alive == 'dead') & (pop.time == year-1)]
    mort = 100 * len(dead) / len(alive)
    # print('Mortality rate: {:.3f}% ({}/{})'.format(mort, len(dead), len(pop)))
    metrics['mort'] = mort

    # General fertility rate (GFR, i.e. birth rate per 1,000 women of age 15-44, ONS definition), should be 50-60
    # Includes estimate of number of 15 yos from mean of 16-18 yos so age range 15-44 is satisfied
    # However, births to 15 yos neglected
    women_alive = alive.loc[alive.sex == 'Female']
    age_range = [16, 17, 18]
    n15 = len(women_alive.loc[women_alive.age.isin(age_range)]) / len(age_range)
    women_gfr = women_alive.loc[women_alive.age.between(15, 44)]
    n_new = women_gfr.nnewborn.sum()
    gfr = 1000 * n_new / (len(women_gfr) + n15)
    # print('General fertility rate, births per 1,000 women (15-44): {:.3f} ({}/{})'.format(gfr, len(has_newborn), len(women_gfr)))
    metrics['gfr'] = gfr

    # Total fertility rate (TFR, i.e. mean children per woman), should be 1.5-1.6
    # Neglects births to <16 yos
    tfr = women_alive.nkids_ind.mean()
    # print('TFR (children per woman): {:.3f}'.format(tfr))
    metrics['tfr'] = tfr

    # Crude birth rate (CBR, i.e. births per 1,000 population), should be 10-12
    # Includes estimate of number of children under 16 (nresp, women only) for purpose of calculating total population
    # Neglects births to <16 yos
    n_u16 = women_alive.nresp.sum()
    n_adult = len(alive)
    cbr = 1000 * n_new / (n_adult + n_u16)
    # print('CBR, births per 1,000 total pop: {:.3f}'.format(cbr))
    metrics['cbr'] = cbr

    return metrics


# HR 17/12/24 To compute/cache/retrieve metrics
def get_metrics_post(parity=False,
                     synthpop=False,
                     cache=True,
                     overwrite=False,
                     ):

    latest = get_latest(parity=parity,
                        synthpop=synthpop,
                        )
    metrics_fullpath = os.path.join(latest, METRICS_FILE)

    if not overwrite:
        try:
            print('Trying to load metrics file from {}...'.format(metrics_fullpath))
            mdf = pd.read_csv(metrics_fullpath, index_col=0)
            print('Done!')
            return mdf
        except:
            print("Couldn't find it; computing...")

    year_dict = get_latest_data(parity=parity, synthpop=synthpop)
    for year, data in year_dict.items():
        m = get_metrics(data, year)
        try:
            mdf.loc[year] = m
        except:
            mdf = pd.DataFrame.from_dict({year: m}, orient='index')
            mdf.index.name = 'year'

    if cache:
        print('Caching to {}'.format(metrics_fullpath))
        mdf.to_csv(metrics_fullpath)

    return mdf


def get_fertility_reference_data():
    fert_path = FERT_REF_PATH
    index_header = 'year'

    # Get EW mortality data
    mort_path = fert_path
    mort_ref = 'dr2022corrected.xlsx'
    mort_fullpath = os.path.join(mort_path, mort_ref)
    mort_data = pd.read_excel(mort_fullpath,
                              sheet_name='8',
                              header=6 - 1,
                              nrows=10)
    mort_data = mort_data.set_index('Year of registration')[['All causes']].loc[range(2013, 2021)]
    mort_data /= 1000

    # Get UK birth rate (proportion of women giving birth)
    ''' OPTION 1: HFD '''
    # br_path = fert_path
    # br_ref1 = 'GBR_NPbirthsRR.txt'
    # br_ref2 = 'GBR_NPexposRR.txt'
    # br_fullpath1 = os.path.join(br_path, br_ref1)
    # br_fullpath2 = os.path.join(br_path, br_ref2)
    # br1 = pd.read_csv(br_fullpath1, header=2, delim_whitespace=True).set_index('Year')
    # br2 = pd.read_csv(br_fullpath2, header=2, delim_whitespace=True).set_index('Year')
    #
    # br1c = br1.loc[~br1.Age.isin(['12-', '55+'])]
    # br1c = br1c.loc[br1c.Age.astype(int).between(15, 44)]
    # br1cg = br1c.groupby(br1c.index)['Total'].sum()
    #
    # br2c = br2.loc[~br2.Age.isin(['12', '55'])]
    # br2c = br2c.loc[br2.Age.astype(int).between(15, 44)]
    # br2cg = br2c.groupby(br2c.index)['Exposure'].sum()
    #
    # br_data = 1000*(br1cg / br2cg)[-8:].to_frame()

    ''' OPTION 2: ONS '''
    br_path = fert_path
    br_ref = 'birthssummary2022refreshedpopulations.xlsx'
    br_fullpath = os.path.join(br_path, br_ref)
    br_data = pd.read_excel(br_fullpath,
                            sheet_name='Table_1',
                            header=9 - 1)
    br_data = br_data.set_index('Year')[[br_data.columns[7]]][2:10]

    # Get UK TFR (average kids per woman ever born)
    tfr_path = fert_path
    tfr_ref = 'GBR_NPtfrRRbo.txt'
    tfr_fullpath = os.path.join(tfr_path, tfr_ref)
    tfr_data = pd.read_csv(tfr_fullpath, header=2, delim_whitespace=True).set_index('Year')['TFR']
    # print(tfr_data)

    # Get UK CBR (births per 1,000 total pop)
    cbr_path = fert_path
    cbr_ref = 'GBR_NPcbrRRbo.txt'
    cbr_fullpath = os.path.join(cbr_path, cbr_ref)
    cbr_data = pd.read_csv(cbr_fullpath, header=2, delim_whitespace=True).set_index('Year')['CBR']
    # print(cbr_data)

    refdata = pd.concat([mort_data, br_data, tfr_data, cbr_data], axis='columns')
    refdata.index.name = 'year'
    refdata.columns = ['mort', 'gfr', 'tfr','cbr']
    refdata.columns = [el + '_ref' for el in refdata.columns]
    return refdata


# HR 17/12/24 To plot metrics over time for different simulation configurations
def plot_metrics(data,
                 ref_data,
                 ):

    labels = ['US only w/o parity', 'US only with parity', 'Synthpop (10%) w/o parity', 'Synthpop (10%) with parity']

    n = len(data[0].columns)
    _vars = data[0].columns[-n:]
    line_styles = ['--', '-', '--', '-']
    line_colours = ['b', 'b', 'r', 'r']

    fig, ax = plt.subplots(nrows=1, ncols=n, figsize=(16, 4))

    for i, ax in enumerate(fig.axes):
        for j, dataset in enumerate(data):
            ax.plot(dataset.index[1:], dataset[_vars[i]][1:], linestyle=line_styles[j], color=line_colours[j])

        ax.plot(ref_data.index, ref_data[ref_data.columns[i]], color='black')

        ax.set(xlabel=_vars[i])

    fig.legend(labels + ['External data'], loc='right', bbox_to_anchor=(1.07, 0.5))
    # fig.legend(labels[0:2], loc='right', bbox_to_anchor=(1.07, 0.5))
    fig_path = OUTPUT_DEFAULT
    fig_full = os.path.join(fig_path, 'metrics.png')
    fig.savefig(fig_full, bbox_inches='tight')


if __name__ == '__main__':
    m1 = get_metrics_post(parity=False, synthpop=False)
    m2 = get_metrics_post(parity=True, synthpop=False)
    m3 = get_metrics_post(parity=False, synthpop=True)
    m4 = get_metrics_post(parity=True, synthpop=True)

    data = [m1, m2, m3, m4]
    ref_data = get_fertility_reference_data()

    plot_metrics(data=data,
                 ref_data=ref_data)

