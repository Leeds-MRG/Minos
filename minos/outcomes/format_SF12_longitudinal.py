import pandas as pd
import glob as glob
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# DEPRECATED.
# DEPRECATED.
# DEPRECATED.
# DEPRECATED.
# DEPRECATED.
# DEPRECATED.

def aggregate_variables_by_year(source, years, label, v, agger):
    """ Get aggregate values for value v using agger function. Do this over the specified source and years.

    A MINOS batch run under a certain intervention will produce 1000 files over 10 years and 100 iterations.
    These files will all be in the source directory.

    For each year this function grabs all files. If the model runs from 2010-2020 there would be 100 files for 2010.

    For each file within a year the agger function is used over variable v.
    The default is taking the mean over SF12 using np.nanmean.

    For each file this will produce a scalar value.
    This scalar value is used along with a year and label tag as a row in the output dataframe df.
    These tags determine which year and which source the dataframe row belongs to.
    If the source is a £25 uplift intervention the label tag will correspond to this.
    This is used later by sns.lineplot.

    This is repeated over all years to produce an output dataframe with 1000 rows.
    Each row is an aggregated v value for each iteration and year pair.

    Parameters
    ----------
    source: str
        What directory is being aggregated. E.g. output/baseline/
    years, v : list
        What range of years are being used. What set of variables are being aggregated.
    label: str
        Which data source are being processed. adds a label column to the df with this tag.
    agger: func

    Returns
    -------
    df: pd.DataFrame
        Data frame with columns year, label and v. Year is year of observation, label is MINOS batch run and intervention
        it has come from, v is aggregated variable. Usually SF12.
    """

    df = pd.DataFrame(columns = ["year", "label", v]) # keep year, label and columns specified by user v.
    for year in years:
        files = glob.glob(f"{source}*{year}.csv") # grab all files at source with suffix year.csv.
        for file in files:
            agg_value = agger(pd.read_csv(file, low_memory=False)[v])
            new_df = pd.DataFrame([[agg_value, label, year]], columns = [v, 'label', 'year'])
            df = pd.concat([df, new_df])
    return df

def multiple_aggregates_by_year(sources, years, labels, v, agger):
    """ This function builds on aggregate_variables_by_year by combining data from several sources together.

    The aggregate_variables_by_year function takes all files from one MINOS batch run and aggregates them by variable v.
    This is useful on its own but what if we want to compare multiple batch runs using different interventions?

    This function simply stacks many aggregated minos batch runs into a long dataframe that seaborn can plot.


    This function combines
    Parameters
    ----------
    sources : list
        Microsimulation output directories to source data from.
    years : np.arange
        Range of years to plot data for.
    ref: str
        If doing relative aggregates use ref as the reference label.
        For example, using mean as the aggregate. setting ref as the label for the baseline source will calculate mean
        change in SF12 relative to baseline.
        A value greater than 1 implies the mean increases and less that 1 implies the mean decreases.
        Useful for comparing interventions if they have an effect. Particularly for large populations where the overall
        change is small relative to yearly noise and hard to see on a graph.

        For now just doing relative means. Reference will constantly have mean 1.
        Can probably extend to more elaborate scalings as desired.
    Returns
    -------
    df : pd.DataFrame
        Dataframe with SF12 mean values by time and interventions in sources.
    """
    # Loop over sources and concat aggregate data frames together.
    df = pd.DataFrame()
    for source, label in zip(sources, labels):
        print(f"Aggregating for {source} with label {label}..")
        new_df = aggregate_variables_by_year(source, years, label, v, agger)
        df = pd.concat([df, new_df])
        print("Done!")
    df.reset_index(inplace=True, drop=True)
    return df

def relative_scaling(df, years, v, ref):
    """ Scale aggregate dataframe based on some reference source.

    For each year
        Find the mean of the reference column for each year xbar.
        Find the mean of the reference group x_bar.
        Divide all values within the year regardless of label by xbar.
    E.g. reference = 'baseline' makes baseline values all 1.
    Any other policy change is relative to this.
    E.g. an uplift policy would likely produce values greater than 1 to signify increase in SF12 on average.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe df containing 3 columns year, label, v. Long frame of aggregates by year and source.
    years: np.arange
        List of year
    v: str
        Variable to aggregate.
    ref: str
        Reference source to scale against.

    Returns
    -------
    df: pd.DataFrame
        Dataframe df containing 3 columns year, label, v. Long frame of aggregates by year and source.
    """
    # if no reference column don't scale anything..
    if ref:
        for year in years:
            if ref is not None:
                year_df = df.loc[df['year']==year, ].copy()
                x_bar = np.nanmean(year_df.loc[year_df['label'] == ref, v])
                year_df[v] /= x_bar
                df.loc[df['year'] == year, v] = year_df[v]
    return df
def main(sources, years, labels, v="SF_12_MCS", destination="plots/", agger=np.nanmean, ref=None):
    """

    Parameters
    ----------
    sources: list
        List of MINOS batch runs to plot.
    years: list
        Range of years to plot.
    labels: list
        Corresponding names of directories from source. Usually correspond to an intervention "baseline", "uplift etc.
    v: str
        What variable to aggregate on.
    destination: str
        Where to save final plots.
    agger: func
        What function to aggregate over. Default np.nanmean.

    Returns
    -------

    """
    df = multiple_aggregates_by_year(sources, years, labels, v) # get aggregated v values by year and source.
    df = relative_scaling(df, years, v, ref) # scale data by reference level if provided.
    aggregate_lineplot(df, destination, v) # plot aggregate values over time using seaborn lineplot.


if __name__ == '__main__':
    years = np.arange(2010, 2019)
    sources = ['output/baseline/', 'output/povertyUplift/', 'output/childUplift/']
    labels = ['Baseline', '£20 Poverty Line', '£20 All']
    main(sources, years, labels, ref='Baseline')