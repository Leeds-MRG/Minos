# HR 19/01/24 Quickie to plot up child poverty metrics (or any binary variable)
# in identical style to Rob's existing SF-12 aggregation plots;
# whereas SF-12 plotted via make target and shown as % change relative to baseline,
# here just want absolute trend over time, with error bars (actually 95% CI by default via Seaborn) inter-run (N=100)

import os
from os.path import dirname as up
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from minos.data_generation import generate_composite_vars as gcv

CONFIG_DEFAULT = 'default_config'
BASELINE_LABEL = 'baseline'
# INTERVENTION_LABEL = '25RelativePoverty'
# INTERVENTION_LABEL = 'ChildPovertyReductionSUSTAIN'

CURR_DIR = up(__file__)
BASELINE_DIR = os.path.join(up(up(CURR_DIR)), 'output', CONFIG_DEFAULT, BASELINE_LABEL)
# INTERVENTION_DIR = os.path.join(up(up(CURR_DIR)), 'output', CONFIG_DEFAULT, INTERVENTION_LABEL)
NMAX_DEFAULT = 30  # Number of years to process, for testing; NOT number of runs per year!
VARS_DEFAULT = ['relative_poverty', 'absolute_poverty', 'low_income_matdep_child', 'persistent_poverty']

TAG_DICT = {'baseline': 'Baseline',
            '25RelativePoverty': '£25 Relative Poverty',
            'ChildPovertyReductionSUSTAIN': 'Target-2030 intervention'}

''' For reference, although redundant as using get_latest '''
# baseline_latest_dir = '2024_01_17_11_58_39'
# intervention_latest_dir = '2024_01_17_12_02_35'  # 25RelativePoverty
# intervention_latest_dir = '2024_01_17_12_56_58'  # ChildPovertyReductionSUSTAIN


def get_intervention_dir(intervention_mode):
    intervention_dir = os.path.join(up(up(CURR_DIR)), 'output', CONFIG_DEFAULT, intervention_mode)
    return intervention_dir


def get_latest(parent_dir):
    file_map = {int(file.replace('_', '')): file for file in os.listdir(parent_dir)}
    latest = file_map[max(file_map)]
    return latest


def get_var_output_names(_vars):
    var_names = {var: var.replace('_', ' ').title() for var in _vars}
    return var_names


def agg_lineplot(intervention_mode,  # Name of intervention type; any from TAG_DICT
             baseline_dir=BASELINE_DIR,
             nmax=NMAX_DEFAULT,
             _vars=VARS_DEFAULT):

    baseline_latest_dir = get_latest(baseline_dir)
    intervention_dir = get_intervention_dir(intervention_mode)
    intervention_latest_dir = get_latest(intervention_dir)

    baseline_path = os.path.join(baseline_dir, baseline_latest_dir)
    intervention_path = os.path.join(intervention_dir, intervention_latest_dir)

    print(baseline_path, '\n', intervention_path)

    baseline_files = [file for file in os.listdir(baseline_path) if file.endswith('csv')]
    intervention_files = [file for file in os.listdir(intervention_path) if file.endswith('csv')]

    # n_baseline = len(set([file.split('_')[0] for file in baseline_files]))
    yrs_baseline = sorted(set([file.rstrip('.csv').split('_')[-1] for file in baseline_files]))
    # n_intervention = len(set([file.split('_')[0] for file in intervention_files]))
    yrs_intervention = sorted(set([file.rstrip('.csv').split('_')[-1] for file in intervention_files]))

    yrs = sorted(list(set(yrs_baseline) & set(yrs_intervention)))
    if len(yrs) > nmax:
        yrs = yrs[0:nmax]
    print(yrs)

    yr_dict_base = {}
    yr_dict_int = {}
    for yr in yrs:
        yr_dict_base[yr] = [os.path.join(baseline_path, file) for file in baseline_files if file.rstrip('.csv').split('_')[-1] == yr]
        yr_dict_int[yr] = [os.path.join(intervention_path, file) for file in intervention_files if file.rstrip('.csv').split('_')[-1] == yr]

    vars_to_retain = ['hidp', 'hh_income', 'time', 'nkids']  # Everything needed for metric calcs and plotting
    var_types = ['int', 'float', 'str']  # To avoid annoying Pandas "inconsistent column type" warnings
    var_type_map = dict(zip(vars_to_retain, var_types))
    print(var_type_map)
    vars_to_retain.extend(_vars)

    base = {}
    int_ = {}
    for yr in yrs:
        print(yr)

        base[yr] = [pd.read_csv(file,
                                usecols=vars_to_retain,
                                dtype=var_type_map) for file in yr_dict_base[yr]]
        int_[yr] = [pd.read_csv(file,
                                usecols=vars_to_retain,
                                dtype=var_type_map) for file in yr_dict_int[yr]]

    base_metrics = {}
    int_metrics = {}
    combined = {}

    for i, yr in enumerate(yrs):

        base_metrics[yr] = pd.concat([gcv.get_poverty_metrics(el,
                                                              poverty_vars=_vars,
                                                              _print=False,
                                                              condense=True) for el in base[yr]],
                                     axis=1).T
        base_metrics[yr]['tag'] = TAG_DICT['baseline']

        int_metrics[yr] = pd.concat([gcv.get_poverty_metrics(el,
                                                             poverty_vars=_vars,
                                                             _print=False,
                                                             condense=True) for el in int_[yr]],
                                    axis=1).T
        int_metrics[yr]['tag'] = TAG_DICT[intervention_mode]

        if i == 0:  # Ignore intervention for first year to avoid funny plot, as in Rob's plot method
            combined[yr] = base_metrics[yr]
        else:
            combined[yr] = pd.concat([base_metrics[yr], int_metrics[yr]], ignore_index=True)

    combined_all = pd.concat(combined, ignore_index=True)

    # int_plot_dir = os.path.join(INTERVENTION_DIR, '2024_01_17_12_02_35', 'plots')  # From testing phase
    int_plot_dir = os.path.join(intervention_path, 'plots')

    for v in _vars:

        f = plt.figure()
        s = sns.lineplot(data=combined_all, x='time', y=v + '_prop', hue='tag', style='tag', markers=True, palette='Set2')

        plt.xticks(yrs[::2])
        plt.xlabel('Year')
        plt.ylabel(v.replace('_', ' ').title() + ' Proportion')

        s.legend_.set_title(None)
        plt.tight_layout()

        file_name = os.path.join(int_plot_dir, v + "_agg.pdf")
        plt.savefig(file_name)
        print("Lineplot for {} saved to {}".format(v, file_name))

    return


if __name__ == "__main__":
    # agg_lineplot(intervention_mode='25RelativePoverty')
    agg_lineplot(intervention_mode='ChildPovertyReductionSUSTAIN')
