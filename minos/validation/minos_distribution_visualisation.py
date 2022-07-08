import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def minos_hist(df, names, destination):
    """ Histogram of distribution of single variable at single point in time.

    Parameters
    ----------
    df : pd.DataFrame
    name: str
        Variable name.
    destination: str
        Where is file being saved.
    Returns
    -------

    """
    df.columns = names
    f = plt.figure()
    sns.histplot(df, kde=True, stat="density", common_norm=False)
    plt.savefig("output")