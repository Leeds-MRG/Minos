import glob
import pandas as pd
import numpy as np
import itertools

def get_files(year, *params):
    search_string = 'output/ex1/'
    for item in params:
        search_string += str(item) + '_'
    search_string += f'*{year}.csv'
    print(search_string)
    return glob.glob(search_string)


def get_SF12_mean(file_names, year, *params):

    means = []
    for file in file_names:
        print(file)
        data = pd.read_csv(file)
        mean = np.nanmean(data.loc[data['SF_12']>0, 'SF_12'])
        print(mean)
        means.append(mean)

    means = pd.DataFrame(means, columns=["SF_12"])
    print(means)
    out_filename = "output/ex1/means_"
    for item in params:
        out_filename += str(item) + '_'
    out_filename += f'{year}.csv'
    means.to_csv(out_filename)

def main(year, test=False):
    uplift = [0.0, 1000.0, 10000.0]  # assimilation rates
    percentage_uplift = [25.0, 50.0, 75.0] #gaussian observation noise standard deviation

    # Assemble lists into grand list of all combinations.
    # Each experiment will use one item of this list.
    if test:
        parameter_lists = [[1000.0, 75.0]]
    else:
        parameter_lists = [item for item in itertools.product(*[uplift, percentage_uplift])]

    for params in parameter_lists:
        file_names = get_files(year, *params)
        print(file_names)
        get_SF12_mean(file_names, year, *params)

if __name__ == '__main__':
    main(2016)

