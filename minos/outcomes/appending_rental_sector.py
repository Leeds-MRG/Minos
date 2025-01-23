import glob
import pandas as pd
from minos.data_generation.generate_composite_vars import generate_housing_sector

def main():
    # load data
    # get housing sector frmo tenure.
    # save data.

    source = "output/energy_manchester_scaled/goodHeatingDummy/"
    directory = sorted(glob.glob(source + "*"))[-1] # get last file.

    files = glob.glob(directory + "/*.csv")
    for i, file in enumerate(files):
        print(f"Appending file {file} with rental sector data. {i}/{len(files)} done.")
        data = pd.read_csv(file, low_memory=False)
        data = generate_housing_sector(data)
        data.to_csv(file, index=False)

if __name__ == '__main__':
    main()