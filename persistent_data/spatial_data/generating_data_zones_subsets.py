import pandas as pd


def main():
    UK_DZ_lookup = pd.read_csv("persistent_data/spatial_data/area_lookup_GB.csv")


    manchester_LADs = ['Tameside',
                        'Bolton',
                        'Bury',
                        'Manchester',
                        'Oldham',
                        'Rochdale',
                        'Salford',
                        'Stockport',
                        'Trafford',
                        'Wigan']

    scotland_data_zones = UK_DZ_lookup.loc[UK_DZ_lookup['CTRY11NM'] == "Scotland", ]
    glasgow_data_zones = scotland_data_zones.loc[scotland_data_zones['LAD17NM'] == "Glasgow City", ]
    edinburgh_data_zones = scotland_data_zones.loc[scotland_data_zones['LAD17NM'] == "Edinburgh", ]
    manchester_lsoas =  UK_DZ_lookup.loc[UK_DZ_lookup['LAD17NM'].isin(manchester_LADs), ]
    sheffield_lsoas = UK_DZ_lookup.loc[UK_DZ_lookup['LAD17NM'] == "Sheffield", ]

    scotland_data_zones.to_csv("persistent_data/spatial_data/scotland_data_zones.csv")
    glasgow_data_zones.to_csv("persistent_data/spatial_data/glasgow_data_zones.csv")
    edinburgh_data_zones.to_csv("persistent_data/spatial_data/edinburgh_data_zones.csv")
    manchester_lsoas = manchester_lsoas.to_csv("persistent_data/spatial_data/manchester_lsoas.csv")
    sheffield_lsoas = sheffield_lsoas.to_csv("persistent_data/spatial_data/sheffield_lsoas.csv")


if __name__ == '__main__':

    main()
