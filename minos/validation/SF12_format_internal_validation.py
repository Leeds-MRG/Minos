# just finds yearly mean and variance for US SF_12 data by year.
import pandas as pd
import numpy as np
from minos.data_generation.US_utils import load_multiple_data, US_file_name


if __name__ == "__main__":
    years = np.arange(2009, 2018)
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = load_multiple_data(file_names)
    data = data.groupby(["time"])["SF_12"].agg(["mean", "var"]).reset_index()
    print(data)