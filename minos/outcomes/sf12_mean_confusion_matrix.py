import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
from matplotlib.cm import viridis

plt.rcParams.update({'font.size': 22})

def get_file_name(params, year):

    return f"output/ex1/means_{params[0]}_{params[1]}_{year}.csv"

def get_means_dataframe(params, year):
    out = {}
    for p in params:
        file_name = get_file_name(p, 2016)
        if p[0] not in out.keys():
            out[p[0]] = {}
        try:
            out[p[0]][p[1]] = np.nanmean(pd.read_csv(file_name)["SF_12"])
        except:
            out[p[0]][p[1]] = np.nanmean(pd.read_csv(file_name)["0"])

def get_all_dataframe(params, year):
    out = pd.DataFrame()
    for p in params:
        file_name = get_file_name(p, 2016)
        new_data = pd.read_csv(file_name)
        new_data.columns = ['index', "SF_12"]
        new_data = new_data.drop('index', axis=1)
        new_data['uplift'] = p[0]
        new_data['prop'] = p[1]
        out = out.append(new_data)
    out = out.replace({1000.0: 20.0, 10000.0: 100.0})
    return out


def confusion_matrix_plot(data):
    f = plt.figure(figsize=(10, 7))
    sns.heatmap(data, cmap=viridis, fmt='f', annot=True, cbar_kws={'label': 'Mean SF12'})
    plt.xlabel("Percentage Uplift (%)")
    plt.ylabel("Household Uplift Amount (£)")
    plt.savefig("plots/sf12_means_confusion.pdf")

def sf12_catplot(data):
    f = plt.figure()
    sns.catplot(x='uplift', y='SF_12', col='prop', kind='boxen', data=data)
    plt.xlabel("Percentage Uplift (%)")
    plt.ylabel("Household Uplift Amount (£)")
    plt.savefig("plots/sf12_means_catplot.pdf")

if __name__ == '__main__':
    uplift = [0.0, 1000.0, 10000.0]  # assimilation rates
    percentage_uplift = [25.0, 50.0, 75.0]  # gaussian observation noise standard deviation

    # Assemble lists into grand list of all combinations.
    # Each experiment will use one item of this list.
    parameter_lists = [item for item in itertools.product(*[uplift, percentage_uplift])]

    #data = get_means_dataframe(parameter_lists, 2016)
    #data.index = [0.0, 20.0, 100.0]
    #data.columns = percentage_uplift
    #confusion_matrix_plot(data)
    data = get_all_dataframe(parameter_lists, 2016)
    sf12_catplot(data)