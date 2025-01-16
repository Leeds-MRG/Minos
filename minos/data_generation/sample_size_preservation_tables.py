import numpy as np
import pandas as pd

def main():

    # Load in datasets. Get number of columns by source and by year.
    # Plot in 2x2 grid by year and by processing step.

    out = pd.DataFrame()

    processing_steps = ["raw_US", "corrected_US",  "composite_US", "mice_US", "imputed_complete_US", "imputed_final_US"]
    years = np.arange(2009, 2021, 1)
    out["year"] = years
    for file_path in processing_steps:
        n_columns = []
        for year in years:
            try: # mildly stupid but easiest way to get around MICE imputation not doing all years of data.
                df = pd.read_csv(f"data/{file_path}/{year}_US_cohort.csv")
                n_columns.append(df.shape[0])
            except:
                print(f"No data for source {file_path} for year {year}.")
                n_columns.append(np.nan)
        out[file_path] = n_columns

    print(out)

if __name__ == '__main__':
    main()