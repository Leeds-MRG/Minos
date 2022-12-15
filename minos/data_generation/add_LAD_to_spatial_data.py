import pandas as pd


def main():

    spatial_data = pd.read_csv("persistent_data/ADULT_population_GB_2018.csv")
    lsoa_to_lad_data = pd.read_csv("persistent_data/lsoa_to_LA_2022.csv")  # dictionary to map LSOA to LAD codes.
    lsoa_to_lad_data = dict(zip(lsoa_to_lad_data['lsoa11cd'], lsoa_to_lad_data['ladcd']))
    spatial_data.columns = ["LSOAcd", "pidp"]
    # spatial_data = spatial_data.head(100000)  # Smaller file for faster debugging. Should be hashed out.
    spatial_data["LADcd"] = spatial_data['LSOAcd'].map(lsoa_to_lad_data, na_action="ignore")
    spatial_data.to_csv("persistent_data/ADULT_population_GB_2018_with_LADs.csv", index=False)

if __name__ == '__main__':
    main()