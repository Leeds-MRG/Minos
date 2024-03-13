import glob
import pandas as pd
import numpy as np
import itertools


def get_SF12_mean(file_names, year, source):

    means = []
    for file in file_names:
        #print(file)
        data = pd.read_csv(file)
        mean = np.nanmean(data['SF_12_MCS'])
        #print(mean)
        means.append(mean)

    means = pd.DataFrame(means, columns=["SF_12_MCS"])
    print(year, means)
    out_filename = source + f"means_{year}.csv"
    means.to_csv(out_filename)

def main(sources, years):
    # Assemble lists into grand list of all combinations.
    # Each experiment will use one item of this list.

    for source in sources:
        for year in years:
            file_names = glob.glob(f"{source}/*{year}.csv")
            print(file_names)
            get_SF12_mean(file_names, year, source)

if __name__ == '__main__':
    #sources = ['output/baseline/', 'output/povertyUplift/', 'output/childUplift/']
    sources = ['output/twentyFivePovertyUplift/']
    years = np.arange(2010, 2019)
    main(sources, years)

