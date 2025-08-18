# HR 18/08/25 All infrastructure for IPF version of fertility model by age, ethnicity and parity, f(a, e, p)

import os
from os.path import dirname as up
import sys

import pyipf

# All other setup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import minos
from minos.utils import extend_series, get_nearest
from minos.RateTables import FertilityRateTable
from minos import fertility_utils as futils

MINOS_PATH = up(os.path.dirname(minos.__file__))
PERSISTENT_DATA = os.path.join(MINOS_PATH, 'persistent_data',)
DATA_PATH = os.path.join(MINOS_PATH, 'data')
FERTILITY_PATH = os.path.join(DATA_PATH, 'fertility')
BIRTHS_PATH = os.path.join(FERTILITY_PATH, 'births')
POP_PATH = os.path.join(FERTILITY_PATH, 'population')
SYNTHPOP_PATH = os.path.join(DATA_PATH, 'scaled_gb_US')
NEP_DATA_PATH = os.path.join(up(MINOS_PATH), 'Leeds2Projections', '2DataArchive')

TFR_PROJECTIONS_DEFAULT = os.path.join(PERSISTENT_DATA, 'fertility_reference', 'Figure_3__The_2022-based.csv')
ASFR_PROJECTIONS_DEFAULT = os.path.join(PERSISTENT_DATA, 'fertility_reference', 'Figure_4__Fertility_rates_for_women.csv')

AGE_RANGE_DEFAULT = (15, 44)
PARITY_MAX = 9

ZERO_VALUE = 1e-4
TRUNC_VALUE = 1
FILL_THRESHOLD = ZERO_VALUE / 10
FILL_VALUE = 1e-8
normaliser = 'nep'
# normaliser = 'ons'

VARS_3D = ['age', 'eth_group', 'nkids_ind']
VARS_2D = ['age', 'eth_group']

eth_map = futils.get_ethnicity_map()
headline_cols = ['LAD.code', 'ETH.group']  # Headers to retain

# Categories for labelling
cats = {'age': [el for el in range(AGE_RANGE_DEFAULT[0], AGE_RANGE_DEFAULT[1] + 1)],
        'eth_group': sorted([el.lower() for el in set(eth_map.values())]),
        'nkids_ind': [el for el in range(PARITY_MAX + 1)],
       }
names = list(cats.keys())
categories = list(cats.values())

# Parameters for PyIPF algorithm
pyipf_params = {'tol_convg': 1e-6,
                'convg': 'relative',
                'pbar': True,
               }


# HR 02/08/25 To get nearest year in NewEthpop data
def get_nearest_newethpop(year):
    pop_path = os.path.join(NEP_DATA_PATH, 'OutputData', 'Population')
    pop_years = [int(f.lstrip('Population').split('_')[0]) for f in os.listdir(os.path.join(pop_path)) if f.endswith('csv')]
    nearest_newethpop = get_nearest(pop_years, year)
    return nearest_newethpop

# HR 02/08/25 To get nearest year in ONS pop-births data
def get_nearest_ons(year):
    fert_ons = FertilityRateTable.parse_parity_ons()
    fert_years = fert_ons['year'].unique()
    nearest_ons = get_nearest(fert_years, year)
    return nearest_ons

# HR 30/07/25 For normalising constraints to reference totals
# Must use ONS fertility data, as common to population and births constraints calculations
def normalise_to_reference(to_be_normalised, reference_dataset):
    _sum = int(reference_dataset.sum().sum())
    normalised = []
    for dataset in to_be_normalised:
        dataset = dataset * _sum / dataset.sum().sum()
        normalised.append(dataset)
    return normalised

def get_synthpop_data(path=SYNTHPOP_PATH, pc=1):
    sp_file = '2019_US_cohort.csv'
    sp_full = os.path.join(path, str(pc) + 'pc', sp_file)
    sp = pd.read_csv(sp_full)
    return sp

# HR 05/08/25 Get ONS TFR projections
def get_tfr_projections(file=TFR_PROJECTIONS_DEFAULT):
    data = pd.read_csv(file, header=6).set_index('Year')[['2022-based principal projection']]
    data.columns = ['tfr']
    return data

# HR 07/08/25 Get ONS ASFR projections
def get_asfr_projections(file=ASFR_PROJECTIONS_DEFAULT):
    data = pd.read_csv(file, header=6).set_index('Year')
    return data

# HR 13/08/25 Check fertility data folders exist and create if not
def check_fertility_folders():
    if not os.path.exists(BIRTHS_PATH):
        os.makedirs(BIRTHS_PATH)
        print('Births data path not found; created it!')
    if not os.path.exists(POP_PATH):
        os.makedirs(POP_PATH)
        print('Population data path not found; created it!')


# HR 06/08/25 Automate fertility rate table creation
def create_fertility_table(births_table, pop_table, scale_factor=1, zero_value=ZERO_VALUE, trunc_value=TRUNC_VALUE):
    # Apply scale factor; important that this comes before fertility rate table calculation
    if scale_factor != 1:
        births_table *= scale_factor
    rt = births_table['births'] / pop_table['population']
    rt = rt.to_frame(name='fertility')

    # Get conditions for correcting zero and very large fertility values, then correct
    zerof_mask = (rt < zero_value)
    trunc_mask = (rt > trunc_value)
    rt[zerof_mask] = 0
    rt[trunc_mask] = 1

    return rt


# HR 06/08/25 Get reference metric for specified year
# Initially intended for projected values for fitting at runtime
def get_reference_value(reference_metric, reference_year):
    if reference_metric == 'tfr':
        ref_val = get_tfr_projections().loc[reference_year].values[0]
    if reference_metric == 'asfr':
        ref_val = get_asfr_projections().loc[reference_year]
    # elif reference_metrics == 'gfr:
    #     ref_val = <SOMETHING>
    else:
        print('Reference metric not available for "{}"; returning None'.format(reference_metric))
        return
    return ref_val


# HR 06/08/25 To match fertility rate (by applying rate table to population) to reference value iteratively
def match_rate_table(pop, births_table, pop_table, cats, reference_metric, reference_value, tol=0.005, max_it=20):
    metric_functions = {'tfr': futils.get_tfr,
                        'gfr': futils.get_gfr,
                        'cbr': futils.get_cbr,
                        # 'sma': futils.get_sma,  # Not working - probably a direction-of-effect problem
                        }
    metric_method = metric_functions[reference_metric]

    # Get initial values before iteration
    bt = births_table.copy()
    pt = pop_table.copy()

    rate_table = create_fertility_table(bt, pt)
    pop = apply_fertility_model(pop, rate_table)
    metric_value = metric_method(pop)
    print('{} = {}, ref = {}'.format(reference_metric, metric_value, reference_value))
    conv = abs(metric_value - reference_value) / reference_value

    metric_history = [metric_value]
    conv_history = [conv]

    it = 0
    while conv > tol and it < max_it:
        scale_factor = reference_value / metric_value
        print(scale_factor)
        rate_table = create_fertility_table(bt, pt, scale_factor=scale_factor)
        pop = apply_fertility_model(pop, rate_table)
        metric_value = metric_method(pop)
        print('{} = {}, ref = {}'.format(reference_metric, metric_value, reference_value))
        conv = abs(metric_value - reference_value) / reference_value

        metric_history.append(metric_value)
        conv_history.append(conv)
        it += 1

    if it <= max_it:
        print('Converged!')
    else:
        print('Not converged, max. iterations reached')
    return rate_table, metric_history, conv_history


# HR 06/08/25 Simple RNG fertility calculator
# Acts on Minos-type population dataframe and computes newborns
# 2D (a, e) and 3D (a, e, p) versions differentiated by _vars parameter
def apply_fertility_model(pop, rate_table, age_range=AGE_RANGE_DEFAULT):
    # Convert rate table to dict for readability
    _vars = list(rate_table.index.names)
    rt_dict = rate_table['fertility'].to_dict()

    # Get women so all fertility variables can be added easily by index
    women = pop.loc[(pop['sex'] == 'Female') & (pop['age'].between(*age_range))]

    # Add tuple column, map fertility rates and get newborns
    pop.loc[women.index, 'fertcat'] = pop[_vars].apply(tuple, axis=1)
    pop.loc[women.index, 'rnd'] = np.random.rand(len(women))
    pop.loc[women.index, 'fertval'] = pop['fertcat'].map(rt_dict)
    pop.loc[women.index, 'nnewborn'] = pop['fertval'] > pop['rnd']

    # Drop temporary columns
    pop.drop(columns=['fertcat', 'rnd', 'fertval'])
    return pop


def get_constraints_data(year, age_range=AGE_RANGE_DEFAULT):
    fert_ons = FertilityRateTable.parse_parity_ons()
    year_nearest_ons = get_nearest_ons(year)
    year_nearest_newethpop = get_nearest_newethpop(year)

    ### DATASET 1 ###
    filename_1 = 'Population' + str(year_nearest_newethpop) + '_LEEDS2.csv'
    ageeth_p = pd.read_csv(os.path.join(NEP_DATA_PATH, 'OutputData', 'Population', filename_1))

    # Tidy pop data
    dfp = ageeth_p.T
    dfp = dfp.loc[~dfp.index.str.startswith('M')]
    dfp = dfp.loc[~dfp.index.astype(str).isin(headline_cols)]
    dfp = dfp.loc[dfp.index.str.startswith('F')]
    dfp.index = dfp.index.str.rstrip('p').str.lstrip('F').astype(int)
    tidy_p = pd.concat([ageeth_p[headline_cols], dfp.loc[age_range[0]:age_range[1]].T], axis=1)

    # Subset for England and Wales - all ONS data is also EW only
    tidy_p = tidy_p.loc[tidy_p['LAD.code'].str[0].isin(('E', 'W'))]

    # Get population by age-ethnicity
    tidy_p['ethnicity'] = tidy_p['ETH.group'].map(eth_map)
    tidy_p = tidy_p.set_index(headline_cols)
    xy_p = tidy_p.groupby('ethnicity').sum().T
    xy_p.columns = [el.lower() for el in xy_p.columns]

    ### DATASET 2 ###
    # 1. Get population by ethnicity
    margin_e = tidy_p.groupby('ethnicity').sum().sum(axis=1).to_list()

    # 2. Get population by parity
    # HR 29/07/25 Get ONS data for population by age and parity
    fert_ym = fert_ons.loc[(fert_ons['year'] == year_nearest_ons), ['age', 'p1', 'p2', 'p3', 'p4', 'p5']].set_index(
        'age')

    margin_p = fert_ym.sum()
    margin_p = extend_series(margin_p.to_list(), PARITY_MAX - len(margin_p) + 2)
    corrector = sum(margin_e) / sum(margin_p)
    margin_p = [el * corrector for el in margin_p]

    # 3. Get population by ethnicity-parity using IPF
    dims = (len(margin_e), len(margin_p))
    m = np.ones(dims)
    marginals = [margin_p, margin_e]
    result = pyipf.ipf(m, marginals, **pyipf_params)

    # Final format
    yz_p = pd.DataFrame(result)
    yz_p.index = [el.lower() for el in xy_p.columns]

    ### DATASET 3 ###
    # Get population by age-parity
    val = fert_ym.loc[age_range[0]:age_range[1]]
    valx = val.apply(lambda x: extend_series(x.to_list(), PARITY_MAX - val.shape[1] + 2), axis=1)
    valx = pd.DataFrame(valx.to_list())
    valx.index = val.index
    xz_p = valx

    ### DATASET 4 ###
    filename_4 = 'Fertility' + str(year_nearest_newethpop) + '_LEEDS1_2.csv'
    ageeth_f = pd.read_csv(os.path.join(NEP_DATA_PATH, 'InputData', 'Fertility', filename_4))

    # Tidy fertility data
    dff = ageeth_f.T
    dff = dff.loc[~dff.index.str.startswith('M')]
    dff = dff.loc[~dff.index.astype(str).isin(headline_cols)]
    dff = dff.loc[dff.index.str.startswith('F')]
    dff.index = dff.index.str.rstrip('p').str.lstrip('F').str.split('.').str[-1].astype(int) - 1
    tidy_f = pd.concat([ageeth_f[headline_cols], dff.loc[age_range[0]:age_range[1]].T], axis=1)

    # Subset for England and Wales - all ONS data is also EW only
    tidy_f = tidy_f.loc[tidy_f['LAD.code'].str[0].isin(('E', 'W'))]

    # Get fertility rate by births by age-ethnicity
    tidy_f['ethnicity'] = tidy_f['ETH.group'].map(eth_map)
    tidy_f = tidy_f.set_index(headline_cols)

    # Multiply fertility rate by population to get births by age-ethnicity
    tidy_b = tidy_p.loc[:, tidy_p.columns != 'ethnicity'] * tidy_f.loc[:, tidy_f.columns != 'ethnicity']
    tidy_b['ethnicity'] = tidy_b.reset_index()['ETH.group'].map(
        eth_map).to_list()  # Must add to_list at end as resetting index causes index mismatch
    xy_b = tidy_b.groupby('ethnicity').sum().T
    xy_b.columns = [el.lower() for el in xy_b.columns]

    ### DATASET 5 ###
    # Get birth by ethnicity-parity
    ETH_FILE = "20182022livebirthssexparity.xlsx"
    ETH_FULL = os.path.join(PERSISTENT_DATA, ETH_FILE)

    eth_raw = pd.read_excel(ETH_FULL,
                            sheet_name='2',
                            header=5,
                            )

    ethnicity = ['asian', 'black', 'asian', 'black', 'black', 'asian', 'mixed', 'not stated', 'other', 'asian', 'white', 'white']
    eth_raw.insert(0, 'ethnicity', ethnicity)
    eth_raw.drop(columns=eth_raw.columns[1], inplace=True)
    eth_raw = eth_raw.loc[eth_raw.ethnicity != 'not stated']

    eth_t = eth_raw.groupby('ethnicity').sum().T
    eth_tp = eth_t.loc[eth_t.index.str.split(' ').str[0].isin(('First', 'Second', 'Third'))].copy()
    eth_tp['parity'] = eth_tp.index.str[0].map({'F': 0, 'S': 1, 'T': 2})

    eth_tpg = eth_tp.groupby('parity').sum().T
    eth_ext = eth_tpg.apply(lambda x: extend_series(x.to_list(), PARITY_MAX - eth_tpg.shape[1] + 2), axis=1)
    eth_done = pd.DataFrame(eth_ext.to_list())
    eth_done.index = eth_ext.index
    yz_b = eth_done / 5  # Accounts for data being for five-year period, 2018-2022

    ### DATASET 6 ###
    fert_ym = fert_ons.loc[(fert_ons['year'] == year_nearest_ons), ['age', 'b1', 'b2', 'b3', 'b4', 'b5']].set_index('age')

    val = fert_ym.loc[age_range[0]:age_range[1]]
    valx = val.apply(lambda x: extend_series(x.to_list(), PARITY_MAX - val.shape[1] + 2), axis=1)
    valx = pd.DataFrame(valx.to_list())
    valx.index = val.index
    xz_b = valx

    return xy_p, yz_p, xz_p, xy_b, yz_b, xz_b


# HR 13/08/25 Rolling IPF solution into a function
def get_ipf_solutions(year, normaliser='nep', recalculate=False):
    # First try and load from file, if present
    births_fullpath = os.path.join(BIRTHS_PATH, 'births_' + str(year) + '.csv')
    pop_fullpath = os.path.join(POP_PATH, 'population_' + str(year) + '.csv')

    if not recalculate:
        try:
            df_b = pd.read_csv(births_fullpath, index_col=names)
            df_p = pd.read_csv(pop_fullpath, index_col=names)
            print('Loaded cached data from file for year {}'.format(year))
            return df_b, df_p
        except Exception as e:
            print(e)
            print('Cached data not found; computing and caching for year {}'.format(year))

    # 1. Fill structural (i.e. real) zeroes with small value to prevent IPF having a nervous breakdown
    xy_p, yz_p, xz_p, xy_b, yz_b, xz_b = get_constraints_data(year)
    constraints = [xy_p, yz_p, xz_p, xy_b, yz_b, xz_b]
    for c in constraints:
        c[c < FILL_THRESHOLD] = FILL_VALUE

    # 2. Normalise all constraints to reference dataset, either ONS or NEP; must do this otherwise PyIPF complains
    if normaliser == 'nep':
        xy_p_corr, yz_p_corr, xz_p_corr = normalise_to_reference([xy_p, yz_p, xz_p], xy_p)
        xy_b_corr, yz_b_corr, xz_b_corr = normalise_to_reference([xy_b, yz_b, xz_b], xy_b)
    elif normaliser == 'ons':
        xy_p_corr, yz_p_corr, xz_p_corr = normalise_to_reference([xy_p, yz_p, xz_p], xz_p)
        xy_b_corr, yz_b_corr, xz_b_corr = normalise_to_reference([xy_b, yz_b, xz_b], xz_b)

    ### BIRTHS ###
    m0 = yz_b_corr.to_numpy()  # yz
    m1 = xz_b_corr.to_numpy()  # xz
    m2 = xy_b_corr.to_numpy()  # xy
    marginals_births = [m0, m1, m2]
    seed_b = np.stack([m1] * len(cats['eth_group']), axis=1)  # Seed table, retains zeroes
    result_b = pyipf.ipf(seed_b, marginals_births, **pyipf_params)

    ### POPULATION ###
    m3 = yz_p_corr.to_numpy()  # yz
    m4 = xz_p_corr.to_numpy()  # xz
    m5 = xy_p_corr.to_numpy()  # xy
    marginals_pop = [m3, m4, m5]
    seed_p = np.stack([m4] * len(cats['eth_group']), axis=1)  # Seed table, retains zeroes
    result_p = pyipf.ipf(seed_p, marginals_pop, **pyipf_params)

    # Convert to dataframes and dump
    index = pd.MultiIndex.from_product(categories, names=names)
    df_b = pd.DataFrame({'births': result_b.flatten()}, index=index)
    df_p = pd.DataFrame({'population': result_p.flatten()}, index=index)

    # Check/create data folders and dump data
    check_fertility_folders()
    df_b.to_csv(births_fullpath)
    df_p.to_csv(pop_fullpath)

    return df_b, df_p


# HR 14/08/25 Get naive GFR from IPF results, i.e. GFR = births / population
def get_simple_gfr(births, population):
    gfr = 1000 * births.sum().sum() / population.sum().sum()
    return gfr


# HR 14/08/25 Get effect of correcting fertility rate table in terms of births and population
def get_correction_effects(births, population, show_results=True):
    # Get fertility rate tables
    fert = create_fertility_table(births, population)

    # Get masks
    zerof_mask = fert.loc[fert['fertility'] == 0].index
    trunc_mask = fert.loc[fert['fertility'] == 1].index

    # Get corresponding population size
    zerof_pop = 100 * population.loc[zerof_mask].sum() / population.sum()
    trunc_pop = 100 * population.loc[trunc_mask].sum() / population.sum()

    # Get corresponding population size
    zerof_births = 100 * births.loc[zerof_mask].sum() / births.sum()
    trunc_births = 100 * births.loc[trunc_mask].sum() / births.sum()

    if not show_results:
        return zerof_pop, trunc_pop, zerof_births, trunc_births

    print('### Calculating zero and unity cells in fertility rate table ###')
    print('Zero cells in result: {}'.format(len(zerof_mask)))
    print('Unity cells in result: {}'.format(len(trunc_mask)))

    print('Proportion of population with zero fertility rate (i.e. f = 0): {0:.4g}%'.format(zerof_pop[0]))
    print('Proportion of population with truncated fertility rate (i.e. f > 1 before correction): {0:.4g}%'.format(
        trunc_pop[0]))

    print('Proportion of births with zero fertility rate (i.e. f = 0): {0:.4g}%'.format(zerof_births[0]))
    print('Proportion of births with truncated fertility rate (i.e. f > 1 before correction): {0:.4g}%'.format(
        trunc_births[0]))

    return zerof_pop, trunc_pop, zerof_births, trunc_births


if __name__ == "__main__":
    # HR 18/08/25 Testing for integration of IPF fertility model into Minos
    y = 2020
