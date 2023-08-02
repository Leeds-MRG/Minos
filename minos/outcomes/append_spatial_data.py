"""For glasgow spatial MINOS runs we want to subset by spatial attributes such as SIMD decile and KNN clusters

rather than run through a massive
"""
import multiprocessing
from glob import glob
import pandas as pd
from multiprocessing import Pool
from itertools import repeat, chain
import sys

def append_spatial_attribute(file_path, spatial_dict, key_variable, attribute_name):
    data = pd.read_csv(file_path, low_memory=False, engine='c')
    #if attribute_name not in data.columns: # only do this if the variable isn't already added..
    data[attribute_name] = data[key_variable].map(spatial_dict)
    data.to_csv(file_path)

def get_simd_dict():
    # get simd to data-zone map

    try:
        simd_data = pd.read_csv("persistent_data/spatial_data/scotland_simd_to_data_zones.csv")[
            ["DZ", "SIMD2020v2_Decile"]]
        # simd_data.columns = ["ZoneID", "simd_decile"]
        simd_dict = dict(zip(simd_data["DZ"], simd_data["SIMD2020v2_Decile"]))
    except FileNotFoundError as e:
        print(e)
        print("""
              \nREADME::\n
              "SIMD to datazone map shouldn't be in the MINOS git. 
              If you don't have it download it from here (as of july 2023).\n 
              https://www.gov.scot/publications/scottish-index-of-multiple-deprivation-2020v2-data-zone-look-up/
              """)
    return simd_dict


def main():
    # get all intervention directories for glasgow spatial data. Could change this to a specified list.
    directory_list = glob("output/glasgow_scaled/*/", recursive=True)
    print("Using interventions: ", directory_list)

    # get latest directory by time for each intervention.
    latest_experiments_list = [max(glob(item+"*/", recursive=True)) for item in directory_list]
    print("Using latest data for interventions: ", latest_experiments_list)

    # get all csvs for latest experiments for each intervention.
    file_list = list(chain(*[glob(item + "/*.csv", recursive=True) for item in latest_experiments_list]))
    print(f"Updating file {sys.argv[1]/len(file_list)} files with simd_decile information.")
    simd_dict = get_simd_dict()

    print(sys.argv)
    append_spatial_attribute(file_list[sys.argv[1]], simd_dict, "ZoneID", "simd_decile")
    #with Pool() as pool:
    #    pool.starmap(append_spatial_attribute, zip(file_list, repeat(simd_dict), repeat("ZoneID"), repeat("simd_decile")))


if __name__ == '__main__':
    main()
