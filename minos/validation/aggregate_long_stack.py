import os
import pandas as pd
import argparse
import numpy as np

def get_file_names(source_directories, v, method):
    file_names = []
    for source in source_directories:
        file_name = os.path.join("output", source, f"aggregated_{v}_by_{method}.csv")
        file_names.append(file_name)
    return file_names

def long_stack_minos_aggregates(file_names):
    """

    Parameters
    ----------
    file_names: list[str]
        List of strings with source directories. These will be used to

    Returns
    -------
    df : pd.DataFrame
        Data frame of minos results with three columns, year, tag, and v.
    """
    df = pd.DataFrame()
    for file_name in file_names:
        df = pd.concat([df, pd.read_csv(file_name)])
    return df

def relative_scaling(df, v, ref):
    """ Scale aggregate dataframe based on some reference source.

    For each year
        Find the mean of the reference column for each year xbar.
        Find the mean of the reference group x_bar.
        Divide all values within the year regardless of tag by xbar.
    E.g. reference = 'baseline' makes baseline values all 1.
    Any other policy change is relative to this.
    E.g. an uplift policy would likely produce values greater than 1 to signify increase in SF12 on average.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe df containing 3 columns year, tag, v. Long frame of aggregates by year and source.
    years: np.arange
        List of year
    v: str
        Variable to aggregate.
    ref: str
        Reference source to scale against.

    Returns
    -------
    df: pd.DataFrame
        Dataframe df containing 3 columns year, tag, v. Long frame of aggregates by year and source.
    """
    # if no reference column don't scale anything..
    if ref is not None:
        years = sorted(list(set(df['year'])))
        for year in years:
            year_df = df.loc[df['year']==year, ].copy()
            x_bar = np.nanmean(year_df.loc[year_df['tag'] == ref, v])
            year_df[v] /= x_bar
            df.loc[df['year'] == year, v] = year_df[v]
    else:
        print("No reference ref defined. No relative scaling used. May make hard to read plots..")
    return df

def main(source_directories, v="SF_12", method="nanmean", destination = None, ref=None):
    """

    Parameters
    ----------
    source_directories
    v
    method

    Returns
    -------

    """

    file_names = get_file_names(source_directories, v, method)
    df = long_stack_minos_aggregates(file_names)
    df = relative_scaling(df, v, ref)

    # join directories together to make name. put it in the first specified source directory.
    if not destination:
        print(f"No destination for output file defined. Storing in first specified source directory {source_directories[0]}.")
        destination = os.path.join("output", source_directories[0])
    out_file = os.path.join(destination, "aggregated_" + "_".join(source_directories) + ".csv")
    df.to_csv(out_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stack minos aggregate batches into long data frame for plotting.")
    parser.add_argument("-s", "--sources", required=True, type=str,
                        help="Source directories for aggregated data. Writted as one string separated by commas. E.g. baseline,childUplift,povertyUplift")
    parser.add_argument("-v", "--variable", required=False, type=str, default='SF_12',
                        help="What variable from Minos is being aggregated. Defaults to SF12.")
    parser.add_argument("-m", "--method", required=False, type=str, default="nanmean",
                        help="What method is used to aggregate population. Defaults to nanmean. Any further aggregators must be added in and will throw errors.")
    parser.add_argument("-d", "--destination", required=False, type=str, default=None,
                        help="Where is the aggregated csv being saved to. Defaults to source directory (usually baseline).")
    parser.add_argument("-r", "--ref", required=False, type=str, default=None,
                        help="If using relative scaling. which source is used as reference. Usually baseline.")

    args = vars(parser.parse_args())
    sources = args['sources']
    v = args['variable']
    method = args['method']
    destination = args['destination']
    ref = args['ref']

    sources = sources.split(",")
    main(sources, v, method, destination, ref)