"""File for hotdecking US data. Aims to provide a complete dataset for microsimulaton rather than for calibrating transitions
"""

import pandas as pd
import US_utils
import numpy as np
from sklearn.impute import KNNImputer
import sklearn
import US_missing_description

def hotdeck_mean(data, columns, types):
    """Mean hotdecking replaces missing values with column means"""

    for i, c in enumerate(columns):
        mean = data.loc[~data[c].isin(US_utils.missing_types)][c].mean()
        if types[i] == 'int':
            mean = int(mean)
        data.loc[data[c].isin(US_utils.missing_types)][c] = mean
    return data

def hotdeck_knn(data, columns):


    imp = KNNImputer(n_neighbors=5, weights="distance")
    imp.fit_transform(data)
    #for i, c in enumerate(columns):
    #    col = imp.fit_transform(data[["age", c]])
    #    data[c] = col
    return data

if __name__ == "__main__":
    years = [2010]  # np.arange(2008,2019)
    file_names = [f"data/corrected_US/{item}_US_cohort.csv" for item in years]

    data = US_utils.load_multiple_data(file_names)
    int_columns = ['pidp', 'hidp', 'job_sec', "fridge_freezer", "washing_machine", "tumble_dryer", "dishwasher", "microwave", "heating", "job_duration_m", "job_duration_y", "birth_month"]
    data[int_columns] = data[int_columns].astype(int)


    before = US_missing_description.missingness_table(data)
    data = data.replace(US_utils.missing_types, np.nan)
    #print(before)
    print(before.loc["Col Sums"]/len(data))
    #data = hotdeck_mean(data, ["age", "job_sec"], ['float', 'int'])
    data = hotdeck_knn(data, ["age", "job_sec"])
    US_utils.save_multiple_files(data, years, 'data/hotdecking_US/', "")
