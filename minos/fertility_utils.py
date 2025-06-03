# HR 11/12/24 All utils particular to fertility work with/without parity and GB synthpop
# To include all post-processing, validation and visualisation

import os
import sys
from os.path import dirname as up
import pandas as pd
import geopandas as gpd
import yaml
from minos.data_generation.US_format_raw_children_ind_data import *
from minos.utils import *
import random

import warnings
# warnings.filterwarnings('error')
warnings.filterwarnings("ignore", category=RuntimeWarning)  # Suppress warning produced during metrics calculations

CURR_DIR = up(__file__)
MINOS_PATH = up(CURR_DIR)
PERSISTENT_PATH = os.path.join(up(CURR_DIR), 'persistent_data')
FERT_REF_PATH = os.path.join(PERSISTENT_PATH, 'fertility_reference')
OUTPUT_DEFAULT = os.path.join(up(CURR_DIR), 'output')
METRICS_FILE = 'metrics.csv'
LA_BOUNDARIES_FILES = {2022: 'Local_Authority_Districts_December_2022_UK_BFE_V2_-6894743385278129679.geojson',
                       }

ETH_GROUPS = {'White': ['WBI', 'WHO',],
              'Black': ['BLA', 'BLC', 'OBL',],
              'Asian': ['IND', 'PAK', 'BAN', 'CHI', 'OAS',],
              'Mixed': ['MIX',],
              'Other': ['OTH',],
              }


# HR 18/12/24 To get ethnic supergroup map
def get_ethnicity_map():
    _map = {}
    for k, v in ETH_GROUPS.items():
        for g in v:
            _map[g] = k
    return _map


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


# HR 20/12/24 Get range of years in sim output
def get_sim_info(parity=False,
                 synthpop=False,
                 ):
    path = get_latest(parity=parity, synthpop=synthpop)
    config_fullpath = os.path.join(path, 'config_file.yml')
    cd = get_config_data(config_fullpath)

    year_start = cd['time']['start']['year']
    year_end = cd['time']['num_years'] + year_start
    years = range(year_start, year_end+1)

    return path, years


# HR 20/12/24 Get single year of sim data to reduce memory usage
def get_latest_data_by_year(year,
                            parity=False,
                            synthpop=False,
                            # intervention=None,
                            ):
    path, years = get_sim_info(parity=parity, synthpop=synthpop)

    if year not in years:
        print('Year {} not in simulation years; returning None'.format(year))
        return None

    file = [f for f in os.listdir(path) if f.endswith(str(year) + '.csv')][0]  # HR 491 Workaround for HPC runs
    # data = pd.read_csv(os.path.join(path, file), low_memory=False)[COLUMNS_TO_READ]
    data = pd.read_csv(os.path.join(path, file), low_memory=False)
    return data


# HR 11/12/24 Get dictionary of year: data file for simulation output
def get_latest_data(parity=False,
                    synthpop=False,
                    # intervention=None,
                    ):
    path, years = get_sim_info(parity=parity, synthpop=synthpop)

    file_dict = {y: [f for f in os.listdir(path) if f.endswith(str(y) + '.csv')][0] for y in years}  # HR 491 Workaround for HPC runs
    # data = {y: pd.read_csv(os.path.join(path, f), low_memory=False)[COLUMNS_TO_READ] for y, f in file_dict.items()}
    data = {y: pd.read_csv(os.path.join(path, f), low_memory=False, index_col=False) for y, f in file_dict.items()}
    return data


# HR 04/03/25 Get single year of Minos data by tag (raw, final, etc.)
def get_minos_data_by_year(year,
                           tag='imputed_final',
                           add_alive=True,
                           ):
    _path = os.path.join(MINOS_PATH, 'data', tag + '_US')
    _file = str(year) + '_US_cohort.csv'
    _fullpath = os.path.join(_path, _file)
    try:
        data = pd.read_csv(_fullpath)
        if add_alive:
            data['alive'] = 'alive'
    except:
        print('Could not find Minos data for {} with tag {}; returning None'.format(year, tag))
        data = None
    return data


# HR 01/03/25 Get all Minos data by tag (raw, final, etc.)
def get_minos_data(tag='imputed_final',
                   add_alive=True,
                   ):
    def _add_alive(df):
        df['alive'] = 'alive'
        return df

    _path = os.path.join(MINOS_PATH, 'data', tag + '_US')
    minos_files = [file for file in os.listdir(_path) if file.endswith('_US_cohort.csv')]
    minos_years = [int(file.split('_')[0]) for file in minos_files]
    minos_data = [pd.read_csv(os.path.join(_path, file)) for file in minos_files]
    if add_alive:
        minos_data = [_add_alive(x) for x in minos_data]
    data = dict(zip(minos_years, minos_data))
    return data


# HR 20/02/25 Get fertility metrics (TFR, GFR, CBR) according to ONS methodologies,
# ONS user guide is here: https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/methodologies/userguidetobirthstatistics#calculating-birth-and-fertility-rates

INTERVAL_DEFAULT = 5
INTERVAL_SINGLE_DEFAULT = 1
AGE_RANGE_DEFAULT = (15, 45 + 1)
BINS_DEFAULT = range(*AGE_RANGE_DEFAULT, INTERVAL_DEFAULT)  # These are standard bins for TFR, i.e. 15-19, ... , 40-44
BINS_SINGLE_DEFAULT = range(*AGE_RANGE_DEFAULT, INTERVAL_SINGLE_DEFAULT)  # Single-year sequence for ASFRs and SMA
YOUTH_RANGE_DEFAULT = (16, 17, 18)


# HR 21/02/25 Get mortality rate from Minos output; this is NOT as general purpose as the fertility metrics,
# so MUST pass whole population AND year, as inferring year might cause errors (e.g. in edge case of lots of dead people)
# Should be about 0.8-1%
def get_mortality_rate(pop,
                       year=None,
                       ):

    # Filter for living people
    alive = pop.loc[(pop['alive'] == 'alive')]

    # Infer year if none given
    if year is None:
        year = alive['time'].mode()[0]

    dead = pop.loc[(pop['alive'] == 'dead') & (pop['time'] == year - 1)]
    try:
        mort = 100 * len(dead) / len(alive)
    except:
        mort = 0.0
    return mort


# HR 21/02/25 General fertility rate (GFR) is calculated using births in all age groups as the numerator,
# but the population of the 15-44 yo cohort (women only) x 1000 as the denominator
# Additional tweak here to account for US/synthpop data only covering 16-44 yos:
# the size of the 15 yo cohort is estimated from the 16-18 yo cohort, i.e. the denominator (population size) is corrected
# Assumes negligible no. of births in 15 yo cohort
# Should be 50-60
def get_gfr(pop,
            age_range=YOUTH_RANGE_DEFAULT,
            ):

    # Filter for living women
    women = pop.loc[(pop['sex'] == 'Female') & (pop['alive'] == 'alive')]

    n_new = women['nnewborn'].sum()
    n15 = len(women.loc[women['age'].isin(age_range)]) / len(age_range)
    women_gfr = women.loc[women['age'].between(15, 44)]
    try:
        gfr = 1000 * n_new / (len(women_gfr) + n15)
    except:
        gfr = 0.0
    return gfr


# HR 24/02/25 Auxiliary function to get ASFR per arbitrary cohort; used for both ASFR and SMA calculations
# A reduction factor is applied to the cohort size (i.e. the denominator) for any 15 yo group, as US only contains 16-19,
# e.g. 15 yo group only becomes zero; 15-19 yo cohort scaled by 4/5
# Assumes negligible no. of births in 15 yo cohort
def get_cohort_asfr(pop,
                    age_group,
                    interval,
                    ):

    # Filter for living women
    pop = pop.loc[(pop['sex'] == 'Female') & (pop['alive'] == 'alive')]

    if len(pop) == 0:  # Avoids division by zero
        asfr = 0.0
    else:
        asfr = pop['nnewborn'].sum() / len(pop)
        if age_group == 15:
            asfr *= (interval - 1) / interval  # Correction to account for absense of 15 yo cohort in US/synthpop
    return asfr


# HR 07/02/25 Standalone function to apply age brackets, as used in at least ASFR calculations and later in metrics subsetting
def apply_age_bracket(pop,
                      bins=BINS_DEFAULT,
                      ):
    pop['age_bracket'] = pd.cut(pop['age'], bins=bins, labels=bins[:-1], right=False)  # Apply left edges as labels for ease
    return pop


# HR 07/02/25 Standalone function to apply ethnicity groups, for use in metrics subsetting
def apply_ethnicity_group(pop,
                          ):
    eth_group_map = get_ethnicity_map()
    pop['eth_group'] = pop['ethnicity'].map(eth_group_map)
    return pop


# HR 24/03/25 Get age-standardised fertility rate (ASFR) by cohort, which can be single years
# Default cohorts are five-year intervals from 15-44, as ONS
def get_asfr(pop,
             bins=BINS_SINGLE_DEFAULT,
             interval=INTERVAL_SINGLE_DEFAULT,
             ):

    # Filter for living women
    pop = pop.loc[(pop['sex'] == 'Female') & (pop['alive'] == 'alive')].copy()  # Best to copy to avoid Pandas SettingWithCopyWarning when creating age_bracket column

    # pop['age_bracket'] = pd.cut(pop['age'], bins=bins, labels=bins[:-1], right=False)  # Apply left edges as labels for ease
    pop = apply_age_bracket(pop=pop, bins=bins)
    sub = pop.loc[~pop['age_bracket'].isna()]  # Get women in correct age range
    asfr = 1000 * sub.groupby('age_bracket').apply(lambda x: get_cohort_asfr(x, x.name, interval))
    asfr = asfr.fillna(0)
    asfr.index = asfr.index.astype(int)
    return asfr


# HR 21/02/25 Total fertility rate (TFR) is calculated using five-year age intervals, for 15-44 yo women
# Additional tweak here to account for US/synthpop data only covering 16-44 yos (i.e. no 15 yos):
# Should be 1.5-1.6
def get_tfr(pop,
            bins=BINS_DEFAULT,
            interval=INTERVAL_DEFAULT,
            ):

    # Filter for living women
    pop = pop.loc[(pop['sex'] == 'Female') & (pop['alive'] == 'alive')]

    asfr = get_asfr(pop, bins=bins, interval=interval)
    tfr = interval * sum(asfr) / 1000
    return tfr


# HR 21/02/25 Crude birth rate (CBR) is calculated from the total births and the total population x 1000
# Subtlety here is to account for U16 cohort using nresp (women only); also possible using child_ages_ind
# Assumes negligible no. of births in 15 yo cohort
# Should be 10-12
def get_cbr(pop):

    # Filter for living people
    pop = pop.loc[pop['alive'] == 'alive']

    n_adult = len(pop)
    women = pop.loc[pop['sex'] == 'Female'].copy()
    n_u16 = women['nresp'].sum()
    # Alternative method using child ages - not working as causes unexplained hang
    # women['children_ind'] = women['child_ages_ind'].astype('int64').apply(integer_child_ages_to_nkids)
    # n_u16 = women['children_ind'].sum()
    n_new = women['nnewborn'].sum()
    cbr = 1000 * n_new / (n_adult + n_u16)
    return cbr


# HR 24/02/25 Standard mean age (SMA) of mothers at their first birth
# Interval can be specified, in line with ASFR calculations
# Smaller intervals less likely to give meaningful results for smaller populations or less common ethnic groups
# N.B. Correction factor 0.5 * interval only verified as correct for interval = 1, as this is only value in literature
def get_sma(pop,
            bins=BINS_SINGLE_DEFAULT,
            interval=INTERVAL_SINGLE_DEFAULT,
            ):

    # Filter for living women
    pop = pop.loc[(pop['sex'] == 'Female') & (pop['alive'] == 'alive')].copy()

    asfr = get_asfr(pop=pop, bins=bins, interval=interval).to_frame().reset_index().rename(columns={0: 'asfr'})
    try:
        sma = sum(asfr['age_bracket'] * asfr['asfr']) / sum(asfr['asfr'])
        sma += 0.5 * interval
    except:
        sma = np.nan
    return sma


# HR 29/01/25 Get birth spacing - i.e. years between ages of children - from integer-form child ages
def get_birth_spacing(ages):
    age_list = integer_child_ages_to_list(ages)
    spacings = np.diff(age_list)
    return spacings


# HR 26/02/25 Add more detailed birth spacing information to pop
# N.b. mutates input dataframe
def add_birth_data(pop):

    # Filter for living women; must also remove child_ages_ind below zero (pipeline error to be resolved)
    pop = pop.loc[(pop['sex'] == 'Female') & (pop['alive'] == 'alive') & (pop['child_ages_ind'] >= 0)].copy()

    # Compute additional birth-related variables
    pop['children_ind'] = pop['child_ages_ind'].astype('int64').apply(integer_child_ages_to_list)
    pop['age_of_first_child'] = pop['children_ind'].str[0]
    pop['age_zero'] = pop['age'] - pop['age_of_first_child']
    pop['spacings'] = pop['child_ages_ind'].astype('int64').apply(get_birth_spacing)
    pop.loc[pop['spacings'].map(len) == 0, 'spacings'] = np.nan  # Must replace empty lists with NaNs

    # Get first n birth spacings and add random number if specified
    s_max = 3  # Max. spacings to get
    for i in range(s_max):
        var_name = 'spacing_' + str(i + 1)
        pop[var_name] = pop['spacings'].str[i]

    pop.drop(columns=['children_ind', 'age_of_first_child'], inplace=True)
    return pop


DERIVED_VARS = ('age_zero', 'spacing_1', 'spacing_2', 'spacing_3')

# HR 03/03/25 Get all derived birth data (age of first birth + spacings)
def get_derived_birth_metrics(pop,
                              vars_to_randomise=DERIVED_VARS,
                              ):

    metrics = {}

    # Must check if empty, as otherwise produced wacky results
    if not pop.empty:
        pop = add_birth_data(pop)

        # Add random number on [-0.5, 0.5] so median gives sensible value
        if vars_to_randomise:
            for _var in vars_to_randomise:
                pop[_var] = pop[_var].apply(lambda x: x + random.random() - 0.5)

        for _var in DERIVED_VARS:
            metrics[_var] = pop[_var].median()
            if 'spacing' in _var:
                metrics[_var] *= 12.0  # Convert to months as this is standard unit

    # If empty, just set to nan
    else:
        metrics.update({v: np.nan for v in DERIVED_VARS})

    return metrics


# HR 11/12/24 Get mortality and fertility metrics
def get_metrics(pop,
                year=None,
                ):
    metrics = {}

    # Mortality rate
    mort = get_mortality_rate(pop, year)
    # print('Mortality rate: {:.3f}% ({}/{})'.format(mort, len(dead), len(pop)))
    metrics['mort'] = mort

    # General fertility rate (GFR)
    gfr = get_gfr(pop)
    # print('General fertility rate, births (all ages) per 1,000 women (15-44 only): {:.3f} ({}/{})'.format(gfr, len(has_newborn), len(women_gfr)))
    metrics['gfr'] = gfr

    # Total fertility rate (TFR)
    tfr = get_tfr(pop)
    # print('TFR (children per woman): {:.3f}'.format(tfr))
    metrics['tfr'] = tfr

    # Crude birth rate (CBR)
    cbr = get_cbr(pop)
    # print('CBR, births per 1,000 total pop: {:.3f}'.format(cbr))
    metrics['cbr'] = cbr

    # Standardised mean age (SMA) at birth
    sma = get_sma(pop)
    # print('SMA, mean age at birth: {:.3f}'.format(sma))
    metrics['sma'] = sma

    # print('Done main metrics')

    # Add derived birth metrics
    derived = get_derived_birth_metrics(pop)
    metrics.update(derived)

    return metrics


# HR 17/12/24 To compute/cache/retrieve metrics
# HR 05/03/25 Updated to create general-purpose disaggregation functionality on arbitrary variables
def get_metrics_post(parity=False,
                     synthpop=False,
                     disaggregator=None,
                     cache=False,
                     recalculate=False,
                     outfile=METRICS_FILE,
                     ):

    path, years = get_sim_info(parity=parity, synthpop=synthpop)
    latest_path = get_latest(parity=parity, synthpop=synthpop)
    metrics_fullpath = os.path.join(latest_path, outfile)

    print('Running metrics post for years {}'.format(list(years)))
    print('Disaggregator(s): {}'.format(disaggregator))

    if not recalculate:
        try:
            print('Trying to load metrics file from {}...'.format(metrics_fullpath))
            mdf = pd.read_csv(metrics_fullpath, index_col=0)
            print('Done!')
            return mdf
        except:
            print("Couldn't find it; computing...")

    # Configure disaggregator; if none given, default to entire dataset; fiddly but works
    if disaggregator is None:
        disagg_vars = ['all']
    else:
        disagg_vars = disaggregator

    mdf = pd.DataFrame()
    leny = len(years)
    for i, year in enumerate(years):

        sys.stdout.write('\rYear: {} ({} of {})'.format(year, i + 1, leny))

        data = get_latest_data_by_year(year=year, parity=parity, synthpop=synthpop)

        # Add derived columns for metrics subsetting
        if 'eth_group' in disagg_vars:
            data = apply_ethnicity_group(data)
        if 'age_bracket' in disagg_vars:
            data = apply_age_bracket(data)

        # Must add dummy column if using whole pop
        if disagg_vars == ['all']:
            data['all'] = 'all'

        m = data.groupby(disagg_vars).apply(lambda x: get_metrics(x, year)).to_frame()[0].apply(pd.Series)
        m['year'] = year
        mdf = pd.concat([mdf, m])
        del data
    print('\n')

    # Rearrange columns so year always first
    mdf.reset_index(inplace=True)
    popped = mdf.pop('year')
    mdf.insert(0, "year", popped)
    mdf.set_index(['year'] + disagg_vars, inplace=True)

    if cache:
        print('Caching to {}'.format(metrics_fullpath))
        mdf.to_csv(metrics_fullpath)

    return mdf


# HR 26/02/25 Get birth spacing reference data, as different format to other metrics
def get_birth_spacing_reference_data(fert_path=FERT_REF_PATH,
                                     ):
    _path = fert_path
    _file = 'parentscharacteristics2022.xlsx'
    _fullpath = os.path.join(_path, _file)
    bs = pd.read_excel(_fullpath,
                       sheet_name='Table_7',
                       header=7 - 1)
    bs.columns = ['year', 'spacing_1', 'spacing_2', 'spacing_3']
    bs = bs.set_index('year')
    return bs


SOURCES_DEFAULT = {'mort': 'ons',
                   'tfr': 'ons',
                   'gfr': 'ons',
                   'cbr': 'ons',
                   'sma': 'ons',
                   }

def get_fertility_reference_data(sources=None,
                                 fert_path=FERT_REF_PATH,
                                 ):
    if sources is None:
        sources = SOURCES_DEFAULT

    refdata = pd.DataFrame()

    # Get EW mortality data
    if sources['mort'] == 'ons':
        mort_path = fert_path
        mort_ref = 'dr2022corrected.xlsx'
        mort_fullpath = os.path.join(mort_path, mort_ref)
        mort_data = pd.read_excel(mort_fullpath,
                                  sheet_name='8',
                                  header=6 - 1,
                                  nrows=35 - 7 + 1,
                                  )
        mort_data = mort_data.set_index('Year of registration')[['All causes']]
        mort_data /= 1000

    elif sources['mort'] == 'hfd':
        mort_data = None

    # Get general fertility rate (GFR)
    if sources['gfr'] == 'hfd':
        br_path = fert_path
        br_ref1 = 'GBR_NPbirthsRR.txt'
        br_ref2 = 'GBR_NPexposRR.txt'
        br_fullpath1 = os.path.join(br_path, br_ref1)
        br_fullpath2 = os.path.join(br_path, br_ref2)
        br1 = pd.read_csv(br_fullpath1, header=2, delim_whitespace=True).set_index('Year')
        br2 = pd.read_csv(br_fullpath2, header=2, delim_whitespace=True).set_index('Year')

        br1c = br1.loc[~br1.Age.isin(['12-', '55+'])]
        br1c = br1c.loc[br1c.Age.astype(int).between(15, 44)]
        br1cg = br1c.groupby(br1c.index)['Total'].sum()

        br2c = br2.loc[~br2.Age.isin(['12', '55'])]
        br2c = br2c.loc[br2.Age.astype(int).between(15, 44)]
        br2cg = br2c.groupby(br2c.index)['Exposure'].sum()

        gfr_data = 1000*(br1cg / br2cg)[-8:].to_frame()

    elif sources['gfr'] == 'ons':
        gfr_path = fert_path
        gfr_ref = 'birthssummary2022refreshedpopulations.xlsx'
        gfr_fullpath = os.path.join(gfr_path, gfr_ref)
        gfr_data = pd.read_excel(gfr_fullpath,
                                sheet_name='Table_1',
                                header=9 - 1)
        gfr_data = gfr_data.set_index('Year')[[gfr_data.columns[7]]]

    if sources['tfr'] == 'hfd':
        # Get UK TFR (average kids per woman ever born)
        tfr_path = fert_path
        tfr_ref = 'GBR_NPtfrRRbo.txt'
        tfr_fullpath = os.path.join(tfr_path, tfr_ref)
        tfr_data = pd.read_csv(tfr_fullpath, header=2, delim_whitespace=True).set_index('Year')['TFR']
        # print(tfr_data)

    elif sources['tfr'] == 'ons':
        tfr_path = fert_path
        tfr_ref = 'birthssummary2022refreshedpopulations.xlsx'
        tfr_fullpath = os.path.join(tfr_path, tfr_ref)
        tfr_data = pd.read_excel(tfr_fullpath,
                                 sheet_name='Table_1',
                                 header=9 - 1)
        tfr_data = tfr_data.set_index('Year')[[tfr_data.columns[6]]]

    if sources['cbr'] == 'hfd':
        # Get UK CBR (births per 1,000 total pop)
        cbr_path = fert_path
        cbr_ref = 'GBR_NPcbrRRbo.txt'
        cbr_fullpath = os.path.join(cbr_path, cbr_ref)
        cbr_data = pd.read_csv(cbr_fullpath, header=2, delim_whitespace=True).set_index('Year')['CBR']
        # print(cbr_data)

    elif sources['cbr'] == 'ons':
        cbr_path = fert_path
        cbr_ref = 'birthssummary2022refreshedpopulations.xlsx'
        cbr_fullpath = os.path.join(cbr_path, cbr_ref)
        cbr_data = pd.read_excel(cbr_fullpath,
                                sheet_name='Table_1',
                                header=9 - 1)
        cbr_data = cbr_data.set_index('Year')[[cbr_data.columns[8]]]

    if sources['sma'] == 'hfd':
        sma_data = None

    elif sources['sma'] == 'ons':
        sma_path = fert_path
        sma_ref = 'birthssummary2022refreshedpopulations.xlsx'
        sma_fullpath = os.path.join(sma_path, sma_ref)
        sma_data = pd.read_excel(sma_fullpath,
                                 sheet_name='Table_1',
                                 header=9 - 1)
        sma_data = sma_data.set_index('Year')[[sma_data.columns[11]]]

    refdata = pd.concat([mort_data, gfr_data, tfr_data, cbr_data, sma_data], axis=1)
    refdata.index.name = 'year'
    refdata.columns = ['mort', 'gfr', 'tfr', 'cbr', 'sma']

    # Add derived birth metrics
    spacing_data = get_birth_spacing_reference_data()
    refdata = refdata.merge(spacing_data, how='left', on='year')

    # Add '_ref' tag to everything
    refdata.columns = [el + '_ref' for el in refdata.columns]

    return refdata


# HR 25/02/25 Separate method for ASFR data as in a different format to the rest
def get_asfr_reference_data(fert_path=FERT_REF_PATH,
                            ):
    _path = fert_path
    _file = 'GBR_NPasfrRRbo.txt'
    _fullpath = os.path.join(_path, _file)
    _data = pd.read_csv(_fullpath, header=2, delim_whitespace=True)[['Year', 'Age', 'ASFR']]
    _data = _data.loc[~_data['Age'].str.endswith(('-', '+'))]
    _data['Age'] = _data['Age'].astype(int)
    _data = _data.loc[_data['Age'].astype(int).between(15, 44)]
    _data.columns = ['year', 'age', 'asfr']
    _data.set_index(['year', 'age'], inplace=True)
    return _data


if __name__ == '__main__':

    # # HR 04/03/25 Testing of improved metrics for use everywhere, i.e. with:
    # # 1. Minos processed data (i.e. pre-sim)
    # # 2. US-type simulation data (i.e. no synthpop)
    # # 3. Simulation data with synthpop
    # # 4. Get all reference data for comparison
    #
    # # Required columns to reduce memory usage
    # cols_to_retain = ['age', 'child_ages', 'nkids', 'ethnicity', 'birth_year', 'time', 'region', 'pidp', 'nnewborn_hh',
    #                   'child_ages_ind', 'sex', 'nnewborn', 'nkids_ind', 'nresp', 'alive']
    # cols_to_retain_sim = cols_to_retain + ['LSOA11CD']
    #
    # # 1. Minos processed data (i.e. pre-sim)
    # mdata = get_minos_data_by_year(2020, tag='imputed_final')
    # mdata = mdata.loc[(mdata['region'] != 'Northern Ireland') & (~mdata['region'].isna())].copy()  # Drop NI data
    # mdata['alive'] = 'alive'  # To harmonise format with sim data
    # mdata = mdata[cols_to_retain]
    # mmetrics = get_metrics(mdata)
    #
    # # 2. US-type simulation data (i.e. no synthpop)
    # y1 = 2025
    # s1 = get_latest_data_by_year(year=y1, parity=False, synthpop=False)
    # s2 = get_latest_data_by_year(year=y1, parity=True, synthpop=False)
    # for data in (s1, s2):
    #     data = data[cols_to_retain]
    # s1metrics = get_metrics(s1)
    # s2metrics = get_metrics(s2)
    #
    # # 3. Simulation data with synthpop
    # y2 = 2025
    # s3 = get_latest_data_by_year(year=y2, parity=False, synthpop=True)
    # s4 = get_latest_data_by_year(year=y2, parity=True, synthpop=True)
    # for data in (s3, s4):
    #     data = data[cols_to_retain_sim]
    # s3metrics = get_metrics(s3)
    # s4metrics = get_metrics(s4)
    #
    # # 4. Get all reference data for comparison
    # main_ref = get_fertility_reference_data()
    # asfr_ref = get_asfr_reference_data()


    # dl = get_latest_data(parity=True, synthpop=False)
    pop25 = get_latest_data_by_year(year=2025, parity=True, synthpop=False)
    mp25 = get_metrics(pop=pop25, year=2025)
    # mpall = get_metrics_post(parity=True, synthpop=True, recalculate=True, cache=False, disaggregator=['region'])
    # mpall = get_metrics_post(parity=True, synthpop=False, recalculate=True, cache=False, disaggregator=['region', 'ethnicity'])
    # mpall = get_metrics_post(parity=True, synthpop=False, recalculate=True, cache=False)
