""" File for subsetting US data. If only interested in fraction of population as input. """

import US_utils
import pandas as pd
import numpy as np

def get_scottish(data):
    "get the scots."
    return data.loc[data['region']=='Scotland',]

#def main():
#    # get files
#    # subset by X.
#    # save files.
#    file_names = ["data/upscaled_US/2018_US_cohort.csv"]
#    data = US_utils.load_multiple_data(file_names)[0]
#    data =get_scottish(data)
#    US_utils.save_multiple_files(data, [2018], "subsetted_US", "")


def main():
    # get files
    # subset by X.
    # save files.

    years = np.arange(2009, 2020) # only saving UKHLS data after 2009.
    file_names = [f"data/final_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    data = get_scottish(data)
    US_utils.save_multiple_files(data, years, "data/scotland_US/", "")

if __name__ == '__main__':
    main()