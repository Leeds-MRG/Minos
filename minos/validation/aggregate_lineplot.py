import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

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
    f = plt.figure()
    sns.lineplot(data=df, x='year', y=v, hue = 'tag', style='tag', markers=True, palette='Set2')
    if prefix:
        file_name = f"{prefix}_{v}_aggs_by_year.pdf"
    else:
        file_name = f"{v}_aggs_by_year.pdf"
    file_name = os.path.join(destination, )
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
    source = os.path.join('output', sources[0], "aggregated_" + "_".join(sources) + ".csv")
    main(source, destination, v, method, prefix)