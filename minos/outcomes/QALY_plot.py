import argparse
import pandas as pd
import numpy as np
import os
import yaml
from multiprocessing import Pool
from itertools import repeat
import glob as glob
from aggregate_subset_functions import dynamic_subset_function

import minos.utils as utils
import seaborn as sns
import matplotlib.pyplot as plt

from scipy.integrate import cumulative_simpson, cumulative_trapezoid

def QALY_lineplot(data, prefix, destination="plots/", baseline="Baseline"):

    #sort by time and run id.
    #data.sort_values(by=['year'], inplace=True)
    # note needs initial 0 in cumulative_simposon at the front to maintain array shape.
    data["QALYs_cumsum"] = data.groupby(by=["tag", 'run_id'])["QALYs"].transform(lambda x: cumulative_simpson(x, dx=1,initial=0))
    data["total_boost_cumsum"] = data.groupby(by=["tag", 'run_id'])["total_boost"].transform(np.cumsum)
    # cum sum qaly.
    data.reset_index(inplace=True)
    data = data.groupby(by=['tag','run_id', 'year'], as_index=False, sort=False).agg({"QALYs_cumsum": np.mean, "total_boost_cumsum": np.mean})
    data['QALYs_cumsum_diff'] = data['QALYs_cumsum'] - np.tile(data.loc[data['tag']==baseline, "QALYs_cumsum"].values, len(data['tag'].value_counts()))
    #data['QALYs_cumsum_diff'] = data['QALYs_cumsum'] - np.repeat(data.loc[data['tag']=="Baseline", "QALYs_cumsum"].values, len(data['tag'].value_counts()))
    data['QALYs_cumsum_percentage_diff'] = data['QALYs_cumsum_diff']/data["QALYs_cumsum"]

    # plot.
    f=plt.figure()
    #TODO: CHANGE TO TAG
    ax = sns.lineplot(data=data, x='year', y="QALYs_cumsum_diff", hue='tag', style='tag', markers=True, palette='Set2')
    ax.set(ylabel="QALYs difference (years)")
    file_name = prefix + ".pdf"
    file_name = os.path.join(destination, file_name)
    plt.tight_layout()
    plt.savefig(file_name)
    print("QALY plot done.")

def ICER_lineplot(data, prefix, destination="plots/", baseline="Baseline"):

    #sort by time and run id.
    #data.sort_values(by=['year'], inplace=True)

    # note needs initial 0 in cumulative_simposon at the front to maintain array shape.
    data["QALYs_cumsum"] = data.groupby(by=["tag", 'run_id'])["QALYs"].transform(lambda x: cumulative_simpson(x, dx=1,initial=0))
    data["total_boost_cumsum"] = data.groupby(by=["tag", 'run_id'])["total_boost"].transform(np.cumsum)
    # cum sum qaly.
    data.reset_index(inplace=True)
    data['QALYs_cumsum_diff'] = data['QALYs_cumsum'] - np.tile(data.loc[data['tag']==baseline, "QALYs_cumsum"].values, len(data['tag'].value_counts()))
    #data['QALYs_cumsum_diff'] = data['QALYs_cumsum'] - np.repeat(data.loc[data['tag']==baseline, "QALYs_cumsum"].values, len(data['tag'].value_counts()))
    data['QALYs_cumsum_percentage_diff'] = data['QALYs_cumsum_diff']/data["QALYs_cumsum"]

    data = data.loc[data['tag'].isin(["EPCG", "GBIS", "EPCG and GBIS"]), ]
    data.loc[data['QALYs_cumsum_diff']==0, 'QALYs_cumsum_diff'] += 1
    data['ICER'] = data['total_boost_cumsum']/data['QALYs_cumsum_diff']

    data.loc[data['ICER'].isna(), "ICER"]=0
    data['ICER'] = np.log10(np.abs(data['ICER'])+1)
    # plot.
    f=plt.figure()
    #TODO: CHANGE TO TAG
    ax = sns.lineplot(data=data, x='year', y="ICER", hue='tag',style='tag', markers=True, palette='Set2')
    ax.set(ylabel="ICER (log10(x+1) scale)")

    file_name = prefix + ".pdf"
    file_name = os.path.join(destination, file_name)
    plt.tight_layout()
    plt.savefig(file_name)
    print("ICER plot done.")


def QALY_quintiles_lineplot(data, prefix, destination="plots/", baseline="Baseline"):
    # sort by time and run id.
    # data.sort_values(by=['year'], inplace=True)
    # note needs initial 0 in cumulative_simposon at the front to maintain array shape.

    plot_data= pd.DataFrame()

    for i, level in enumerate(["first", "second", "third", "fourth", "fifth"]):
        subset_data = data.loc[data['subset'] == f"who_{level}_simd_quintile"]
        subset_data["QALYs_cumsum"] = subset_data.groupby(by=["tag", 'run_id'])["QALYs"].transform(
            lambda x: cumulative_simpson(x, dx=1, initial=0))
        subset_data["total_boost_cumsum"] = subset_data.groupby(by=["tag", 'run_id'])["total_boost"].transform(np.cumsum)
        # cum sum qaly.
        subset_data.reset_index(inplace=True)
        subset_data = subset_data.groupby(by=['tag', 'run_id', 'year'], as_index=False, sort=False).agg(
            {"QALYs_cumsum": np.mean, "total_boost_cumsum": np.mean})
        subset_data['QALYs_cumsum_diff'] = subset_data['QALYs_cumsum'] - np.tile(subset_data.loc[subset_data['tag'] == baseline, "QALYs_cumsum"].values,
                                                                   len(subset_data['tag'].value_counts()))
        # subset_data['QALYs_cumsum_diff'] = subset_data['QALYs_cumsum'] - np.repeat(subset_data.loc[subset_data['tag']=="Baseline", "QALYs_cumsum"].values, len(subset_data['tag'].value_counts()))
        subset_data['QALYs_cumsum_percentage_diff'] = subset_data['QALYs_cumsum_diff'] / subset_data["QALYs_cumsum"]
        subset_data['tag'] = f"Quintile {i+1}"
        plot_data = pd.concat([plot_data, subset_data])

    # plot.
    f = plt.figure()
    # TODO: CHANGE TO TAG
    ax = sns.lineplot(data=plot_data, x='year', y="QALYs_cumsum_diff", hue='tag', style='tag', markers=True, palette='Set2')
    ax.set(ylabel="QALYs difference (years)")
    file_name = prefix + ".pdf"
    file_name = os.path.join(destination, file_name)
    plt.tight_layout()
    plt.savefig(file_name)
    print("QALY plot done.")

def ICER_quintiles_lineplot(data, prefix, destination="plots/", baseline="Baseline"):

    #sort by time and run id.
    #data.sort_values(by=['year'], inplace=True)

    plot_data= pd.DataFrame()

    for i, level in enumerate(["first", "second", "third", "fourth", "fifth"]):
        # note needs initial 0 in cumulative_simposon at the front to maintain array shape.
        subset_data = data.loc[data['subset'] == f"who_{level}_simd_quintile"]
        subset_data["QALYs_cumsum"] = subset_data.groupby(by=["tag", 'run_id'])["QALYs"].transform(lambda x: cumulative_simpson(x, dx=1,initial=0))
        subset_data["total_boost_cumsum"] = subset_data.groupby(by=["tag", 'run_id'])["total_boost"].transform(np.cumsum)
        # cum sum qaly.
        subset_data.reset_index(inplace=True)
        subset_data['QALYs_cumsum_diff'] = subset_data['QALYs_cumsum'] - np.tile(subset_data.loc[subset_data['tag']==baseline, "QALYs_cumsum"].values, len(subset_data['tag'].value_counts()))
        #subset_data['QALYs_cumsum_diff'] = subset_data['QALYs_cumsum'] - np.repeat(subset_data.loc[subset_data['tag']==baseline, "QALYs_cumsum"].values, len(subset_data['tag'].value_counts()))
        subset_data['QALYs_cumsum_percentage_diff'] = subset_data['QALYs_cumsum_diff']/subset_data["QALYs_cumsum"]

        subset_data = subset_data.loc[subset_data['tag'].isin(["EPCG", "GBIS", "EPCG and GBIS"]), ]
        subset_data.loc[subset_data['QALYs_cumsum_diff']==0, 'QALYs_cumsum_diff'] += 1
        subset_data['ICER'] = subset_data['total_boost_cumsum']/subset_data['QALYs_cumsum_diff']

        subset_data.loc[subset_data['ICER'].isna(), "ICER"]=0
        subset_data['ICER'] = np.log10(np.abs(subset_data['ICER'])+1)
        subset_data['tag'] = f"Quintile {i+1}"
        plot_data = pd.concat([plot_data, subset_data])

    # plot.
    f=plt.figure()
    #TODO: CHANGE TO TAG
    ax = sns.lineplot(data=plot_data, x='year', y="ICER", hue='tag',style='tag', markers=True, palette='Set2')
    ax.set(ylabel="ICER (log10(x+1) scale)")

    file_name = prefix + ".pdf"
    file_name = os.path.join(destination, file_name)
    plt.tight_layout()
    plt.savefig(file_name)
    print("ICER plot done.")



def main(mode, interventions):
    # downlaod three qaly datasets

    qaly_data = pd.DataFrame()
    tags = ["Baseline", "EPCG", "GBIS", "EPCG and GBIS"]
    for i, intervention in enumerate(interventions):
        file_dir = os.path.join('output/', mode, intervention)
        runtime_list = os.listdir(os.path.abspath(file_dir))
        runtime = utils.get_latest_subdirectory(runtime_list)
        batch_source= os.path.join(file_dir, runtime)
        qaly_subset = pd.read_csv(batch_source + f'/who_alive_qalys.csv')
        qaly_subset['tag'] =tags[i]
        qaly_data = pd.concat([qaly_data, qaly_subset])

    # plot just qalys
    QALY_lineplot(qaly_data, f"{mode}_energy_combined_QALY_lineplot")

    # plot icer ratios.
    ICER_lineplot(qaly_data, f"{mode}_energy_combined_ICR_lineplot")



if __name__ == '__main__':

    #sources to get required data.
    #main("energy_manchester_scaled",["baseline", "goodHeatingDummy", "EPCG", "GBIS"])
    main("energy_manchester_scaled",["baseline", "EPCG", "GBIS", "EPCGandGBIS"])