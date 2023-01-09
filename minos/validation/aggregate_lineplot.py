import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime


def main(source, destination, v, method, prefix):
    """

    Parameters
    ----------
    source_directories: list[str]
        List of source directories to take aggregate data from.
    destination: str
        Where is plot being saved to?
    v, method: str
        Variable and aggergate functions used. Used in file name and plot titles.
    Returns
    -------

    """
    aggregate_lineplot(source, destination, v, method, prefix)
    #TODO looks redundant for now but more plots can go here as needed..

def aggregate_lineplot(source, destination, v, method, prefix):
    """ Plot lineplot over sources and years for aggregated v.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with mean SF12 values over time by intervention.
    destination : str
        Where is the plot being saved to.
    Returns
    -------
    None
    """
    # seaborn line plot does this easily. change colours, line styles, and marker styles for easier readibility.
    df = pd.read_csv(source)
    df[v] -= 1 # set centre at 0.

    # set year to int for formatting purposes
    df['year'] = pd.to_datetime(df['year'], format='%Y')

    # now rename some vars for plot labelling and formatting
    # Capital letter for 'year'
    # 'tag' renamed to 'Legend'
    df.rename(columns={"year": "Year",
                         "tag": "Legend"},
              inplace=True)

    f = plt.figure()
    sns.lineplot(data=df, x='Year', y=v, hue = 'Legend', style='Legend', markers=True, palette='Set2')
    if prefix:
        file_name = f"{prefix}_{v}_aggs_by_year.pdf"
    else:
        file_name = f"{v}_aggs_by_year.pdf"
    file_name = os.path.join(destination, file_name)

    # Sort out axis labels
    if v == 'SF_12':
        v = 'SF12 MCS'
    plt.ylabel(f"{v}")
    plt.tight_layout()
    plt.savefig(file_name)
    print(f"Lineplot saved to {file_name}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Lineplot several aggregates of MINOS batches..")
    parser.add_argument("-s", "--sources", required=True, type=str,
                        help="The source directory for Understanding Society/Minos data. Usually has form output/*. where * specified by model config e.g. baseline/childUplift/etc.")
    parser.add_argument("-d", "--destination", required=False, type=str, default=None,
                        help="Where is the aggregated csv being saved to. Defaults to source directory.")
    parser.add_argument("-v", "--variable", required=False, type=str, default='SF_12',
                        help="What variable from Minos is being aggregated. Defaults to SF12.")
    parser.add_argument("-m", "--method", required=False, type=str, default="nanmean",
                        help="What method is used to aggregate population. Defaults to np.nanmean.")
    parser.add_argument("-p", "--prefix", required=False, default=None,
                        help="Prefix for pdf output filename. used to differenate different plot types. e.g. all population vs treated only.")

    args = vars(parser.parse_args())
    sources = args['sources']
    destination = args['destination']
    v = args['variable']
    method = args['method']
    prefix = args['prefix']

    sources = sources.split(",")

    for i, source in enumerate(sources):
        # Handle the datetime folder inside the output. Select most recent run
        runtime = os.listdir(os.path.abspath(os.path.join('output/default_config', source)))
        if len(runtime) > 1:
            runtime = max(runtime, key=lambda d: datetime.strptime(d, "%Y_%m_%d_%H_%M_%S"))
        elif len(runtime) == 1:
            runtime = runtime[0]  # os.listdir returns a list, we only have 1 element
        else:
            raise RuntimeError("The output directory supplied contains no subdirectories, and therefore no data to "
                               "aggregate. Please check the output directory.")

        sources[i] = os.path.join(source, runtime)

    short_directories = []
    for i, source in enumerate(sources):
        if '/' in source:
            source = source.split('/')[0]
            short_directories.append(source)

    source = os.path.join('output/default_config', sources[0], "aggregated_" + "_".join(short_directories) + ".csv")
    main(source, destination, v, method, prefix)
