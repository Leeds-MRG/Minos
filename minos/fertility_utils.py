# HR 11/12/24 All utils particular to fertility work with/without parity and GB synthpop
# To include all post-processing, validation and visualisation

import os
from os.path import dirname as up
import pandas as pd
import geopandas as gpd
import yaml
import matplotlib.pyplot as plt
from minos import utils
from minos.data_generation.US_format_raw_children_data import integer_child_ages_to_nkids as intch
import random

CURR_DIR = up(__file__)
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


# HR 20/12/24 To reformat age bins for plot labelling, etc.; takes Pandas (right closed) interval and returns string
def format_age_bins(interval):
    formatted = str(interval).strip('(').strip(']').replace(', ', '_')
    return formatted


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
        print('Year not in simulation years; returning None')
        return None

    file = str(year) + '.csv'
    # data = pd.read_csv(os.path.join(path, file), low_memory=False)[COLUMNS_TO_READ]
    data = pd.read_csv(os.path.join(path, file), low_memory=False)
    return data


# HR 11/12/24 Get dictionary of year: data file for simulation output
def get_latest_data(parity=False,
                    synthpop=False,
                    # intervention=None,
                    ):
    path, years = get_sim_info(parity=parity, synthpop=synthpop)

    file_dict = {y: str(y) + '.csv' for y in years}
    # data = {y: pd.read_csv(os.path.join(path, f), low_memory=False)[COLUMNS_TO_READ] for y, f in file_dict.items()}
    data = {y: pd.read_csv(os.path.join(path, f), low_memory=False) for y, f in file_dict.items()}
    return data


# HR 20/02/25 Get fertility metrics (TFR, GFR, CBR) according to ONS methodologies,
# ONS user guide is here: https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/methodologies/userguidetobirthstatistics#calculating-birth-and-fertility-rates

INTERVAL_DEFAULT = 5
BINS_DEFAULT = range(15, 50, INTERVAL_DEFAULT)  # These are standard bins for TFR, i.e. 15-19, ... , 45-49
AGE_RANGE_DEFAULT = (16, 17, 18)


# HR 21/02/25 General fertility rate (GFR) is calculated using births in all age groups as the numerator,
# but the population of the 15-44 yo cohort (women only) x 1000 as the denominator
# Additional tweak here to account for US/synthpop data only covering 16-49 yos:
# the size of the 15 yo cohort is estimated from the 16-18 yo cohort, i.e. the denominator (population size) is corrected
# Assumes negligible no. of births in 15 yo cohort
# Should be 50-60
def get_gfr(pop, age_range=AGE_RANGE_DEFAULT):
    women = pop.loc[pop.sex == 'Female']
    n_new = women.nnewborn.sum()
    n15 = len(women.loc[women.age.isin(age_range)]) / len(age_range)
    women_gfr = women.loc[women.age.between(15, 44)]
    gfr = 1000 * n_new / (len(women_gfr) + n15)
    return gfr


# HR 21/02/25 Total fertility rate (TFR) is calculated using five-year age intervals, for 15-49 yo women
# Additional tweak here to account for US/synthpop data only covering 16-49 yos:
# a 5/4 factor is applied to the cohort size (i.e. the denominator) for the 15-19 group, as US only contains 16-19
# Assumes negligible no. of births in 15 yo cohort
# Should be 1.5-1.6
def get_tfr(pop, bins=BINS_DEFAULT, interval=INTERVAL_DEFAULT):
    def get_cohort_tfr(cohort, age_group):
        try:
            tfr = cohort['nnewborn'].sum() / len(cohort)
        except:  # Sometimes get an exception if len(cohort) is zero
            tfr = 0.0
        if age_group == 15:
            tfr *= (4.0 / 5.0)  # Correction to account for absense of 15 yo cohort in US/synthpop
        return tfr

    pop = pop.copy()  # Best to copy to avoid Pandas SettingWithCopyWarning when creating age_bracket column
    pop['age_bracket'] = pd.cut(pop['age'], bins=bins, labels=bins[:-1], right=False)  # Apply left edges as labels for ease
    sub = pop.loc[(pop['sex'] == 'Female') & (~pop['age_bracket'].isna())]  # Get women in correct age range
    sums = sub.groupby('age_bracket').apply(lambda x: get_cohort_tfr(x, x.name))
    tfr = interval * sum(sums)

    return tfr


# HR 21/02/25 Crude birth rate (CBR) is calculated from the total births and the total population x 1000
# Subtlety here is to account for U16 cohort using nresp (women only); also possible using child_ages_ind
# Assumes negligible no. of births in 15 yo cohort
# Should be 10-12
def get_cbr(pop):
    n_adult = len(pop)
    women = pop.loc[pop.sex == 'Female'].copy()
    n_u16 = women.nresp.sum()
    # Alternative method using child ages - not working as causes unexplained hang
    # women['children_ind'] = women['child_ages_ind'].astype('int64').apply(intch)
    # n_u16 = women['children_ind'].sum()
    n_new = women.nnewborn.sum()
    cbr = 1000 * n_new / (n_adult + n_u16)
    return cbr


# HR 21/02/25 Get mortality rate from Minos output; this is NOT as general purpose as the fertility metrics,
# so MUST pass whole population AND year, as inferring year might cause errors (e.g. in edge case of lots of dead people)
# Should be about 0.8-1%
def get_mortality_rate(pop, year):
    alive = pop.loc[(pop.alive == 'alive')]
    dead = pop.loc[(pop.alive == 'dead') & (pop.time == year - 1)]
    mort = 100 * len(dead) / len(alive)
    return mort


# HR 11/12/24 Get mortality and fertility metrics
def get_metrics(pop,
                year,
                ):
    metrics = {}

    # Get all living individuals
    alive = pop.loc[(pop.alive == 'alive')]

    # Mortality rate
    mort = get_mortality_rate(pop, year)
    # print('Mortality rate: {:.3f}% ({}/{})'.format(mort, len(dead), len(pop)))
    metrics['mort'] = mort

    # General fertility rate (GFR)
    gfr = get_gfr(alive)
    # print('General fertility rate, births (all ages) per 1,000 women (15-44 only): {:.3f} ({}/{})'.format(gfr, len(has_newborn), len(women_gfr)))
    metrics['gfr'] = gfr

    # Total fertility rate (TFR)
    tfr = get_tfr(alive)
    # print('TFR (children per woman): {:.3f}'.format(tfr))
    metrics['tfr'] = tfr

    # Crude birth rate (CBR)
    cbr = get_cbr(alive)
    # print('CBR, births per 1,000 total pop: {:.3f}'.format(cbr))
    metrics['cbr'] = cbr

    return metrics


# HR 17/12/24 To compute/cache/retrieve metrics
def get_metrics_post(parity=False,
                     synthpop=False,
                     cache=True,
                     overwrite=False,
                     outfile=METRICS_FILE,
                     ):

    latest = get_latest(parity=parity, synthpop=synthpop)
    metrics_fullpath = os.path.join(latest, outfile)

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


# # HR 20/12/24 Get metrics in disaggregated form, i.e. by age group, ethnicity, parity and area
# def get_metrics_post_disaggregated(disaggregator=None,
#                                    parity=False,
#                                    synthpop=False,
#                                    cache=True,
#                                    overwrite=False,
#                                    outfile=METRICS_FILE,
#                                    ):
#     path, years = get_sim_info(parity=parity, synthpop=synthpop)
#
#     if disaggregator is None:
#         gb = {'all', data}
#     elif disaggregator == 'age':
#         bins = [16, 18, 20, 25, 30, 35, 40, 50, 120]
#         gb = data.groupby(pd.cut(data.age, bins))
#     elif disaggregator == 'region':
#         gb = data.groupby('region')
#     elif disaggregator == 'ethnicity':
#         eth_map = get_ethnicity_map()
#         data['ethnicity_super'] = data['ethnicity'].map(ethnicity_map)
#         gb = data.groupby('ethnicity_super')
#     elif disaggregator == 'parity':
#         gb = data.groupby('nkids_ind')
#
#     return


SOURCES_DEFAULT = {'mort': 'ons',
                   'tfr': 'ons',
                   'gfr': 'ons',
                   'cbr': 'ons',
                   }

def get_fertility_reference_data(sources=None):
    if sources is None:
        sources = SOURCES_DEFAULT

    fert_path = FERT_REF_PATH

    # Get EW mortality data
    if sources['mort'] == 'ons':
        mort_path = fert_path
        mort_ref = 'dr2022corrected.xlsx'
        mort_fullpath = os.path.join(mort_path, mort_ref)
        mort_data = pd.read_excel(mort_fullpath,
                                  sheet_name='8',
                                  header=6 - 1,
                                  nrows=10)
        mort_data = mort_data.set_index('Year of registration')[['All causes']].loc[range(2013, 2021)]
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

        br_data = 1000*(br1cg / br2cg)[-8:].to_frame()

    elif sources['gfr'] == 'ons':
        gfr_path = fert_path
        gfr_ref = 'birthssummary2022refreshedpopulations.xlsx'
        gfr_fullpath = os.path.join(gfr_path, gfr_ref)
        gfr_data = pd.read_excel(gfr_fullpath,
                                sheet_name='Table_1',
                                header=9 - 1)
        gfr_data = gfr_data.set_index('Year')[[gfr_data.columns[7]]][2:10]

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
        tfr_data = tfr_data.set_index('Year')[[tfr_data.columns[6]]][2:10]

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
        cbr_data = cbr_data.set_index('Year')[[cbr_data.columns[8]]][2:10]

    refdata = pd.concat([mort_data, gfr_data, tfr_data, cbr_data], axis='columns')
    refdata.index.name = 'year'
    refdata.columns = ['mort', 'gfr', 'tfr','cbr']
    refdata.columns = [el + '_ref' for el in refdata.columns]
    return refdata


# HR 17/12/24 To plot metrics over time for different simulation configurations
def plot_metrics(data,
                 ref_data,
                 outfile,
                 ):

    labels = ['US only w/o parity', 'US only with parity', 'Synthpop (1%) w/o parity', 'Synthpop (1%) with parity']

    n = len(data[0].columns)
    _vars = data[0].columns[-n:]
    line_styles = ['--', '-', '--', '-']
    line_colours = ['b', 'b', 'r', 'r']

    fig, ax = plt.subplots(nrows=1, ncols=n, figsize=(16, 4))

    for i, ax in enumerate(fig.axes):
        for j, dataset in enumerate(data):
            ax.plot(dataset.index[1:], dataset[_vars[i]][1:], linestyle=line_styles[j], color=line_colours[j])
            # ax.plot(dataset.index, dataset[_vars[i]], linestyle=line_styles[j], color=line_colours[j])

        ax.plot(ref_data.index, ref_data[ref_data.columns[i]], color='black')

        ax.set(xlabel=_vars[i])

    fig.legend(labels + ['External data'], loc='right', bbox_to_anchor=(1.07, 0.5))
    # fig.legend(labels[0:2], loc='right', bbox_to_anchor=(1.07, 0.5))
    fig_path = OUTPUT_DEFAULT
    fig_full = os.path.join(fig_path, outfile)
    fig.savefig(fig_full, bbox_inches='tight')


# HR 17/02/25 Basic plotter for fertility data using LA boundaries
def plot_gb_data(data_by_area, col_to_plot=None, boundaries_file=None, outfile=None, outformat='pdf', _save=True):

    if boundaries_file is None:
        boundaries_file = os.path.join(PERSISTENT_PATH, 'spatial_data', LA_BOUNDARIES_FILES[2022])

    if outfile is None:
        outfile = os.path.join(OUTPUT_DEFAULT, 'fertility_by_area.' + outformat)

    # Convert to WSG 84/EPSG4326, else breaks plotting; then filter for GB
    boundaries = gpd.read_file(boundaries_file).to_crs(epsg=4326)
    boundaries = boundaries.loc[boundaries['LAD22CD'].str[0].isin(('E', 'S', 'W'))]

    # Merge spatial data with pop data
    if col_to_plot is None:
        col_to_plot = 'random_number'  # Create random variable for testing
        boundaries[col_to_plot] = random.sample(range(1, 2 * len(boundaries)), len(boundaries))

    merged = boundaries.merge(data_by_area, right_index=True, left_on='LAD22CD')

    # Plot and save
    merged.plot(column=col_to_plot, edgecolor='black', legend=True, linewidth=0.1)
    plt.tight_layout()
    plt.axis('off')

    if _save:
        # Dump to file
        print('Saving to {}'.format(outfile))
        plt.savefig(outfile, bbox_inches='tight', pad_inches=0.01)


if __name__ == '__main__':

    # ref_data = get_fertility_reference_data()
    #
    # ''' Plot up mort and fert metrics with and without synthpop and parity '''
    # m1 = get_metrics_post(parity=False, synthpop=False)
    # m2 = get_metrics_post(parity=True, synthpop=False)
    # m3 = get_metrics_post(parity=False, synthpop=True)
    # m4 = get_metrics_post(parity=True, synthpop=True)
    #
    # data = [m1, m2, m3, m4]
    #
    # plot_metrics(data=data,
    #              ref_data=ref_data,
    #              outfile='metrics_all.jpg')

    # ''' Get latest data '''
    # d1 = get_latest_data(parity=False, synthpop=False)
    # d2 = get_latest_data(parity=True, synthpop=False)
    # d3 = get_latest_data(parity=False, synthpop=True)
    # d4 = get_latest_data(parity=True, synthpop=True)
    #
    # ''' Adding spatial attributes '''
    # lsoa_col = 'LSOA11CD'
    # ward_col = 'WD22CD'
    # la_col = 'LAD22CD'
    # region_col = 'RGN22CD'
    # region_name_col = 'RGN22NM'
    #
    # m1 = utils.get_lsoa_to_ward_map()
    # m2, m3, m4 = utils.get_ward_to_region_map()
    # # to_add_spatial = [d1, d2, d3, d4]
    #
    # ### Workaround until LSOA11 linkage data available
    # to_add_regional = [d1, d2]
    # to_add_spatial = [d3, d4]
    # m4_rev = {v: k for k, v in m4.items()}
    #
    # for dataset in to_add_regional:
    #     for yr, ds in dataset.items():
    #         ds[region_col] = ds['region'].map(m4_rev)
    # ###
    #
    # for dataset in to_add_spatial:
    #     for yr, ds in dataset.items():
    #         ds = utils.add_spatial_attributes(ds)
    #         ds['region'] = ds['RGN22CD'].map(m4)
    #
    # ''' Can now disaggregate and plot by groups '''
    # # By age groups
    # # bins = [16, 18, 20, 25, 30, 35, 40, 50, 120]
    # # by_age_bin = {}
    # # for i, ds in enumerate([d1, d2, d3, d4]):
    # #     by_age_bin[i] = {}
    # #     for y, d in ds.items():
    # #         for _bin, g in d.groupby(pd.cut(d.age, bins)):
    # #             by_age_bin[i][_bin] = get_metrics(g, y)
    # #
    # # for i, ds in [d1, d2, d3, d4]:
    # #     for _bin, met in by_age_bin[i].items():
    # #         label = '_age_' + '' + '.jpg'
    #
    #
    # # By ethnicity
    #
    #
    # # By region
    #
    #
    # # By parity


    # HR 17/02/25 Get some synthpop fertility data and plot up
    y = 2025
    data = get_latest_data_by_year(year=y, synthpop=True, parity=False)
    data = utils.add_spatial_attributes(data)  # Add wards, LAs and regions
    fert_data_by_la = data.groupby('LAD22CD').apply(lambda x: get_metrics(x, y)).to_frame()[0].apply(pd.Series)  # Get mort/fert data by LA
    # fert_data_by_region = data.groupby('RGN22CD').apply(lambda x: get_metrics(x, y)).to_frame()[0].apply(pd.Series)  # Get mort/fert data by region

    plot_gb_data(data_by_area=fert_data_by_la, col_to_plot='tfr', outformat='png')
