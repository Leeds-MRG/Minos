""" File for plots describing proportion of missing data in US dataset.
"""

import pandas as pd
import numpy as np
import US_utils
import matplotlib.pyplot as plt


# Select a subset of people missing some entry I.E. age, number of counts missing, etc.

##########################
# Single frame missingness
##########################

def split_data_by_missing(data, v1):
    """ Split data by whether v1 is missing or not.

    Parameters
    ----------
    data
    v1
    v2

    Returns
    -------

    """
    missing_set = ['-1', '-2', '-7', '-8', '-9']
    data1 = data.loc[data[v1].isin(missing_set)]
    data2 = data.loc[~data[v1].isin(missing_set)]
    return data1, data2

def missingness_table(data):
    """ Return a table of missing values for each variable as a percentage of total data.

    Parameters
    ----------
    data

    Returns
    -------

    """

    output = pd.DataFrame(0, index= [-1, -2, -7, -8, -9], columns=data.columns)
    for v in data.columns:
        output[v] = data.loc[data[v].isin(US_utils.missing_types)][v].astype(int).value_counts()
    output = output.replace(np.nan, 0)

    col_sums = np.sum(output)
    col_sums.name = "Col Sums"
    output = output.append(col_sums)
    row_sums = np.nansum(output, 1)
    output["Row Sums"] = row_sums

    percent_missing = round((100*row_sums[-1])/(data.shape[0]*data.shape[1]), 3)
    print(f"Number of missing data is {row_sums[-1]} which is {percent_missing}% of all data.")
    return output

def missingness_hist(data, v1, v2):
    """ If anyone is missing v1 plot their distribution of v2 in a histogram.

    Parameters
    ----------
    data:
    v1, v2 : str
        Variable 1 is the missing variable. Take a subset of data for anyone missing this variable.
        Variable 2 is the histogram variable. Plot a histogram for the distribution of v2 given v1 is missing.

    Returns
    -------
    """
    data1, data2 = split_data_by_missing(data, v1)
    data1, data2 = data1[v2], data2[v2]

    f = plt.figure()
    plt.hist(data1, alpha=0.5, color="blue", density=True, label="Missing")
    plt.hist(data2, alpha=0.5, color="orange", density=True, label = "Not Missing")
    plt.legend()
    plt.xlabel(f"Variable : {v2}")
    plt.ylabel("Density")
    plt.title(f"Distribution of {v2} for those missing {v1} ({len(data1)})\n and not missing {v1} ({len(data2)})")
    plt.show()

def missingness_bars(data, v1, v2):
    data1, data2 = split_data_by_missing(data, v1)
    data1, data2 = dict(data1[v2].value_counts()), dict(data2[v2].value_counts())

    for key in data1.keys():
        if key not in data2.keys():
            data2[key] = 0
    for key in data2.keys():
        if key not in data1.keys():
            data1[key] = 0

    sum1 = sum(data1.values())
    sum2 = sum(data2.values())
    missing_means = [data1[item] for item in sorted(data1)]
    if sum1 > 0:
        missing_means = [item/sum1 for item in missing_means]
    non_missing_means = [data2[item] for item in sorted(data2)]
    if sum2 > 0:
        non_missing_means = [item/sum2 for item in non_missing_means]

    v2_categories = sorted(data1)
    index = np.arange(len(v2_categories))
    bar_width = 0.35
    alpha = 0.8

    f, ax = plt.subplots()

    rects1 = plt.bar(index, missing_means, bar_width, alpha=alpha, color="blue", label="Missing")
    rects2 = plt.bar(index + bar_width, non_missing_means, bar_width, alpha=alpha,  color="orange", label="Not Missing")

    ax.set_xticks(index + (bar_width/2))
    ax.set_xticklabels(v2_categories, rotation=90)
    plt.legend()
    plt.xlabel(f"Variable : {v2}")
    plt.ylabel("Density")
    plt.title(f"Distribution of {v2} for those missing {v1} ({sum1})\n and not missing {v1} ({sum2})")
    plt.tight_layout()
    plt.show()

def complete_missing_hists(data, v1, v1type, v2, save = False):
    """Show distributional differences between full complete and missing cases.


    Parameters
    ----------
    data: pd.DataFrame
    v1 : str
        Categorical parameter to compare distributions for v2.
    v1type : str
        Which level of v1 to compare. E.g. A-Level for education_state.
    v2 : str
        Which continuous variable to compare distributions for.

    Returns
    -------

    """

    data = data.replace(['-1', '-2', '-7', '-8', '-9', -1, -2, -7, -8, -9], np.nan) # everyone.
    data2 = data.dropna() # complete only.
    data2 = data2.loc[data2[v1] == v1type][v2]
    data = data.loc[data[v1]==v1type][v2]
    bins = np.arange(min(min(data), min(data2)), max(max(data), max(data2)))

    # # Everyone histogram.
    # f = plt.figure()
    # plt.hist(data, bins=np.arange(100), density=True)
    # plt.xlabel(f"{v2}: mean - {np.mean(data)}")
    # plt.ylabel(f"{v1} - {v1type}")
    # plt.title("All available individuals.")
    # plt.show()
    # if save:
    #     plt.tight_layout()
    #     f.savefig(f"plots/all_available_{v1}_{v1type}_by_{v2}.pdf")
    # # Complete cases histogram.
    # g = plt.figure()
    # plt.hist(data2, color=u'#ff7f0e', bins=np.arange(100), density=True)
    # plt.xlabel(f"{v2}: mean - {np.mean(data2)}")
    # plt.ylabel(f"{v1} - {v1type}")
    # plt.title("Complete case")
    # plt.show()
    # if save:
    #     plt.tight_layout()
    #     g.savefig(f"plots/complete_case_{v1}_{v1type}_by_{v2}.pdf")


    h = plt.figure()
    plt.hist([data, data2], alpha=0.8, bins=bins, density=True, label=["Complete + Partial", "Complete Only"], align="left")
    plt.ylabel(f"{v1} - {v1type}")
    plt.xlabel(f"{v2}: Mean complete - {np.mean(data2):.2f}, Mean complete + partial - {np.mean(data):.2f}")
    plt.title("Complete cases + Partial Missing.")
    plt.legend()
    if save:
         plt.tight_layout()
         h.savefig(f"plots/complete_case_vs_partial_{v1}_{v1type}_by_{v2}.pdf")
    else:
        plt.show()

def longitudinal_hist(data):
    """ Count number of observations for each individual by pidp. make a histogram.

    Parameters
    ----------
    data

    Returns
    -------

    """

    # Stacked histogram for three types of people.
    both = data.loc[data["time"]>=2008]["pidp"] # UKLHS and BHPS IDs
    bhps = data.loc[data["time"]<2008]["pidp"] #BHPS only.
    uklhs = set(both)-set(bhps)

    data1 = data.loc[data["pidp"].isin(bhps)]["pidp"].value_counts() #BHPS only.
    data2 = data.loc[data["pidp"].isin(uklhs)]["pidp"].value_counts() #UKLHS only.

    biggest = max(max(data1), max(data2))
    bins = np.arange(1, biggest)-0.5

    f = plt.figure()
    #plt.hist(data1, alpha=1., density=True, bins=bins)
    plt.hist([data1,data2], alpha=1., density=True, histtype="barstacked", bins=bins, label=["BHPS", "UKLHS"], align="left")
    #plt.hist(data2, alpha=0.4, density=True, bins=bins + 0.25, label="UKLHS")
    #plt.hist(data3, alpha=0.4, density=True, bins=bins + 0.5, label="BHPS")
    plt.legend()
    plt.xlabel(f"Number of observations.")
    plt.ylabel("Density")
    #plt.title(f"Number of observations per individual.")
    plt.savefig("plots/US_obs_hist.pdf")

    g = plt.figure()
    plt.hist([data1, data2], alpha=0.5, density=True, bins=bins, cumulative=-1, label=["BHPS","UKLHS"])
    plt.xlabel(f"Number of observations.")
    plt.ylabel("Density")
    plt.legend()
    #plt.title(f"Cumulative observations per individual.")
    plt.savefig("plots/US_obs_survival_hist.pdf")

def main():
    # Load in data.
    wave_years = np.arange(1990, 2017)
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in wave_years]
    full_US_data = US_utils.load_multiple_data(file_names)
    # Summary table of missing values by variable.
    missingness_table(full_US_data)
    # Missingness graphs.
    missingness_hist(full_US_data, "education_state", "age")
    missingness_bars(full_US_data, "labour_state", "sex")
    missingness_bars(full_US_data, "education_state", "ethnicity")
    full_US_data["depression_state"] = full_US_data["depression_state"].astype(str)
    longitudinal_hist(full_US_data)
    complete_missing_hists(full_US_data, "education_state", "A-Level", "age")
    complete_missing_hists(full_US_data, "ethnicity", "WBI", "age", True)
    complete_missing_hists(full_US_data, "depression_state", "1", "age", True)

    return full_US_data


if __name__ == "__main__":
    data = main()

