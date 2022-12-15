"""File for creating area code conversion JSONs"""

import pandas as pd
from US_utils import save_json

if __name__ == "__main__":
    # conversion table from ONS. This version was released in 2019 and is currently (21/02/22) the latest.
    # Note two tables for Great Britain and Northern Ireland respectively.
    GB_area_conversion = pd.read_csv("persistent_data/area_lookup_GB.csv")
    NI_area_conversion = pd.read_csv("persistent_data/area_lookup_NI.csv")

    # create dictionaries convesting LAD to region codes and names.
    GB_lad_region_code = zip(GB_area_conversion["LAD17CD"], GB_area_conversion["RGN11CD"])
    GB_lad_region_name = zip(GB_area_conversion["LAD17NM"], GB_area_conversion["RGN11NM"])
    NI_lad_region_code = zip(NI_area_conversion["LAD18CD"], NI_area_conversion["RGN11CD"])
    NI_lad_region_name = zip(NI_area_conversion["LAD18NM"], NI_area_conversion["RGN11NM"])

    # Merge GB and NI dicts into one whole UK dict for name and code conversions each.
    LAD_to_region_code = dict(GB_lad_region_code)
    LAD_to_region_code.update(dict(NI_lad_region_code))
    LAD_to_region_name = dict(GB_lad_region_name)
    LAD_to_region_name.update(NI_lad_region_name)

    # manual override of a number of keys to match daedalus rate tables.
    update_codes = {'E07000104': "W92000004",  # Welwyn Hetfield in Wales
                    'E07000101': "E12000006",  # Stevenage in East of England.
                    'E07000097': "E12000006",  # East Hertfordshire in East of England.
                    'E06000048': "E12000001",  # Northhumberland (UA) in North East.
                    'E09000001+E09000033': "E12000007",  # City of London and Westminister in London.
                    'E06000052+E06000053': "E12000009",  # Cornwall and Isles of Scilly in the South West.
                    'E07000100': "E12000006",  # St. Albans in East of England.
                    'E08000020': "E12000001", # Gateshead in North West.
                    'S12000036': "S92000003", # Edinburgh scotland
                    'S12000035': "S92000003", # Argyll and Bute Scotland
                    'N09000011': "N92000002", # Ards and North Down NI
                    'S12000024': "S92000003", # Perth Scotland
                    'S12000013': "S92000003", # Eilean Siar Scotland
                    'S12000006': "S92000003", # Dumfries Scotland
                    'N09000002': "N92000002", # Armagh NI
                    'N09000005': "N92000002", # Derry and Strabane NI
    }
    LAD_to_region_code.update(update_codes)

    update_names = {'Stevenage': "East of England", # See above.
                    'St Albans': "East of England",
                    'Welwyn Hatfield': "Wales",
                    'City of London+Westminster': "London",
                    'Northumberland UA': "North East",
                    'Cornwall+Isles of Scilly': "South West",
                    'Gateshead': "North East",
                    'East Hertfordshire': "East of England",
                    'Eilean Siar': "Scotland",
                    'Dumfries & Galloway': "Scotland",
                    'Derry City and Strabane': "Northern Ireland",
                    'Perth & Kinross': "Scotland",
                    'Armagh City, Banbridge and Craigavon': "Northern Ireland",
                    'Banbridge and Craigavon': "Northern Ireland",
                    'Argyll & Bute': "Scotland",
                    'Edinburgh, City of': "Scotland",
                    'Ards and North Down': "Northern Ireland",
    }
    LAD_to_region_name.update(update_names)
    # Save to JSONs in persistent data.
    #print(LAD_to_region_code, LAD_to_region_name)
    # TODO check any differences between this and BHPS LADs.
    save_json(LAD_to_region_code, "persistent_data/JSON/LAD_to_region_code.json")
    save_json(LAD_to_region_name, "persistent_data/JSON/LAD_to_region_name.json")
