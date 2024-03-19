"""File for merging Scotland and England/Wales """
# HR 02/02/24 This now grabs LSOAs/DZs from single source and maps LA names and codes onto it
# Default resolution of boundary geometry in final json (EWS_JSON) is 50m (see MAP_SCALE parameter)
# To generate the json at a different scale, delete EWS_JSON and change MAP_SCALE, then rerun
# File size is ~100 MB at 25m scale, ~65MB at 50m and ~40MB at 100m
# Once the final json has been generated at whatever scale is required, the shapefile (EWS_SHAPEFILE) can be deleted

# Geopandas update imminent, see issue #1387 here: https://github.com/geopandas/geopandas/issues/1387
# via Shapely PR #1969 here: https://github.com/shapely/shapely/pull/1969
# which would mean Topojson might not be required

# N.b. quite a lot of faffing with column names here, which is to preserve the pre-322 headers in the final json

import pandas as pd
import os
import sys
from os.path import dirname as up
import geopandas as gpd
import topojson as tp
from minos.utils import get_lsoa_la_map

# EWS LSOA/DZ 2011 shapefile, downloaded 02/02/24 from UKDS here:
# https://statistics.ukdataservice.ac.uk/dataset/2011-census-geography-boundaries-lower-layer-super-output-areas-and-data-zones
SPATIAL_DIR = os.path.join(up(__file__), 'spatial_data')
EWS_SHAPEFILE = os.path.join(SPATIAL_DIR, 'infuse_lsoa_lyr_2011_clipped', 'infuse_lsoa_lyr_2011_clipped.shp')
EWS_JSON = os.path.join(SPATIAL_DIR, 'UK_super_outputs.geojson')
MAP_SCALE = 50  # Unit in shapefile/geojson, appears to be metres
LA_DIR = os.path.join(SPATIAL_DIR, 'data_by_la')

# HR 21/02/24 Some city regions to LA maps for #413; all correct for LSOA (2011) and LA (2022)
REGIONAL_LA_DICT = {'Greater Manchester': ['Manchester', 'Salford', 'Trafford', 'Wigan', 'Stockport', 'Bury', 'Bolton',
                                           'Oldham', 'Tameside', 'Rochdale'],
                    'Glasgow City Region': ['East Dunbartonshire', 'East Renfrewshire', 'Glasgow City', 'Inverclyde',
                                            'North Lanarkshire', 'Renfrewshire', 'South Lanarkshire',
                                            'West Dunbartonshire'],
                    'South Yorkshire Combined Authority': ['Sheffield', 'Barnsley', 'Doncaster', 'Rotherham'],
                    'Sheffield City Region': ['Sheffield', 'Barnsley', 'Doncaster', 'Rotherham', 'Chesterfield',
                                              'North East Derbyshire', 'Bolsover', 'Bassetlaw', 'Derbyshire Dales'],
                    'Cardiff Capital Region': ['Blaenau Gwent', 'Bridgend', 'Caerphilly', 'Cardiff', 'Merthyr Tydfil',
                                               'Monmouthshire', 'Newport', 'Rhondda Cynon Taf', 'Torfaen',
                                               'Vale of Glamorgan'],
                    }


def add_local_authorities(df):

    df_out = df.copy()
    column_map = {'geo_code': 'LSOA11CD'}
    df_out.rename(columns=column_map, inplace=True)  # Standardise column headers for merge

    ews_map = get_lsoa_la_map()  # Get LSOA/DZ to LA lookup
    df_out = df_out.merge(ews_map, on='LSOA11CD')  # Map LA codes and names as new columns

    column_map = {'LSOA11CD': 'geo_code'}
    df_out.rename(columns=column_map, inplace=True)  # Reset original column headers

    return df_out


''' HR 05/02/24 Retaining this just in case gpd.simplify functionality is useful in future
    It does not snap adjacent boundaries to each other, so results in empty slivers between areas '''
# def create_simplified_json(ews_json_in,
#                            ews_json_simplified,
#                            scale=MAP_SCALE):
#
#     ews_json = ews_json_in.copy()
#     # Rescale to reduce file size; n.b. setting simplify.preserve_topology to True does NOT fill gaps between areas
#     ews_json['geometry'] = ews_json['geometry'].simplify(tolerance=scale)
#
#     # ews_out = ews_json.to_crs(epsg=4326)  # Convert to correct format
#     ews_out.to_file(ews_json_simplified, driver="GeoJSON")  # Cache rescaled json
#
#     return ews_out


def get_ews_json(ews_json=EWS_JSON,
                 ews_shapefile=EWS_SHAPEFILE,
                 scale=MAP_SCALE,
                 cache=True):

    # 1. First try to get cached, oven-ready version of EWS geojson...
    try:
        print("Trying to load cached EWS json file with LA definitions...")
        ews_final = gpd.read_file(ews_json)
        print("Done")
        return ews_final
    except:
        print("Cached EWS json file with LA definitions not found; trying to create from shapefile...")

    # 2. ...if no json found, try to load master shapefile and create/cache json
    try:
        ews_raw = gpd.read_file(ews_shapefile)
        ews_raw.drop(labels=['geo_labelw'], axis=1, inplace=True)  # No need for Welsh names
    except:
        # 4. If no shapefile found, stop and direct user to where data can be downloaded
        print("Shapefile not found; download from here and move to the persistent_data/spatial_data folder...")
        print("...then rerun this script")
        return None

    print("Loaded shapefile; adding local authority names and codes...")
    ews_las = add_local_authorities(ews_raw)
    print("Done")

    print("Simplifying geometry to resolution of {}m...".format(scale))
    print("This will take several minutes, depending on the spatial resolution")
    la_col = 'LAD22NM'
    las = ews_las[la_col].unique()
    ews_split = {la: ews_las.loc[ews_las[la_col] == la] for la in las}

    ews_tp = {}
    l = len(ews_split)
    for i, (la, df_la) in enumerate(ews_split.items()):
        sys.stdout.write("\rProcessing LA {} of {}: ({})".format(i+1, l, la))
        topo = tp.Topology(df_la, prequantize=False)
        ews_tp[la] = topo.toposimplify(epsilon=scale).to_gdf()
    print("")

    # Concat all LAs into single df and convert to EPSG:4326, aka WGS:84
    ews_final = pd.concat(ews_tp.values())
    print("Converting to EPSG:4326/WGS:84")
    ews_final = ews_final.to_crs(epsg=4326)

    # Correct headers to match pre-322 version and cache
    column_map = {'geo_code': 'ZoneID',
                  'geo_label': 'name',
                  'LAD22CD': 'LA_Code',
                  'LAD22NM': 'LAName'}
    ews_final.rename(columns=column_map, inplace=True)

    if cache:
        print("Caching to {}...".format(ews_json))
        ews_final.to_file(ews_json)
        print("Done")

    return ews_final


def cache_by_la_json(df_in,
                     la_code='LA_Code',
                     out_path=LA_DIR):

    if not os.path.exists(out_path):
        print("Output folder not found, creating: {}".format(out_path))
        os.makedirs(out_path)

    print("Caching JSONs by local authority code to: {}".format(out_path))
    las = df_in[la_code].unique()
    jsons_by_la = {}
    for la in las:
        jsons_by_la[la] = df_in.loc[df_in[la_code] == la]
        jsons_by_la[la].to_file(os.path.join(out_path, la + ".json"))

    return jsons_by_la


def get_json_by_la(la_list=[],
                   la_code='LA_Code',
                   la_path=LA_DIR):

    # Check which are and aren't present in LA folder
    las_present = [el.split('.json')[0] for el in os.listdir(la_path)]
    las_valid = sorted(list(set(la_list) & set(las_present)))
    las_invalid = sorted(list(set(la_list) - set(las_present)))

    if las_invalid:
        print("Could not find the following local authorities in the cache folder: {}".format(las_invalid))

    jsons_by_la = {}
    for la in las_valid:
        jsons_by_la[la] = gpd.read_file(os.path.join(la_path, la + ".json"))

    return jsons_by_la


''' HR 21/02/24 Renaming to match json dumping below (generate_subset_jsons) '''
def generate_subsets(spatial_path=SPATIAL_DIR):
    # load in full UK wide lookup.
    # get this data here https://geoportal.statistics.gov.uk/datasets/0d11d17118ec44fcbe890fed53df4a9d_0/explore
    # lookup_file_name = os.path.join(spatial_path, "Output_Area_to_LSOA_to_MSOA_to_Local_Authority_District_(December_2017)_Lookup_with_Area_Classifications_in_Great_Britain.csv")
    # lsoa_lookup = pd.read_csv(lookup_file_name)
    # la_name = 'LAD17NM'
    # country_name = 'CTRY11NM'
    # lsoa_code = 'LSOA11CD'

    ''' HR 06/02/24 Standardising lookups, re. 389 '''
    lsoa_lookup = get_lsoa_la_map()
    la_name = 'LAD22NM'
    country_name = 'CTRY11NM'
    lsoa_code = 'LSOA11CD'

    # Subsetting data from desired regions
    sheffield_subset = lsoa_lookup.loc[lsoa_lookup[la_name] == "Sheffield", ]
    manchester_subset = lsoa_lookup.loc[lsoa_lookup[la_name] == "Manchester", ]
    glasgow_subset = lsoa_lookup.loc[lsoa_lookup[la_name] == "Glasgow City", ]
    scotland_subset = lsoa_lookup.loc[lsoa_lookup[country_name] == "Scotland", ]

    greater_manchester_subset = lsoa_lookup.loc[lsoa_lookup['LAD22NM'].isin(REGIONAL_LA_DICT['Greater Manchester'])]
    glasgow_city_region_subset = lsoa_lookup.loc[lsoa_lookup['LAD22NM'].isin(REGIONAL_LA_DICT['Glasgow City Region'])]
    sheffield_city_region_subset = lsoa_lookup.loc[lsoa_lookup['LAD22NM'].isin(REGIONAL_LA_DICT['Sheffield City Region'])]

    # Only taking required column
    sheffield_lsoas = sheffield_subset[lsoa_code]
    manchester_lsoas = manchester_subset[lsoa_code]
    glasgow_data_zones = glasgow_subset[lsoa_code]
    scotland_data_zones = scotland_subset[lsoa_code]

    greater_manchester_lsoas = greater_manchester_subset[lsoa_code]
    glasgow_city_region_lsoas = glasgow_city_region_subset[lsoa_code]
    sheffield_city_region_lsoas = sheffield_city_region_subset[lsoa_code]

    # Saving
    sheffield_lsoas.to_csv(os.path.join(spatial_path, "sheffield_lsoas.csv"))
    manchester_lsoas.to_csv(os.path.join(spatial_path, "manchester_lsoas.csv"))
    glasgow_data_zones.to_csv(os.path.join(spatial_path, "glasgow_data_zones.csv"))
    scotland_data_zones.to_csv(os.path.join(spatial_path, "scotland_data_zones.csv"))

    greater_manchester_lsoas.to_csv(os.path.join(spatial_path, "greater_manchester_lsoas.csv"))
    glasgow_city_region_lsoas.to_csv(os.path.join(spatial_path, "glasgow_city_region_lsoas.csv"))
    sheffield_city_region_lsoas.to_csv(os.path.join(spatial_path, "sheffield_city_region_lsoas.csv"))


''' HR 21/02/24 Dump jsons for any subset region '''
def generate_subset_jsons(lsoa_files,
                          geo=None,
                          spatial_path=SPATIAL_DIR):
    if geo is None:
        geo = get_ews_json()

    for file in lsoa_files:
        file_full = os.path.join(spatial_path, file)
        lsoas = pd.read_csv(file_full)['LSOA11CD']
        geometry = geo.loc[geo['ZoneID'].isin(lsoas)]
        bits = file_full.split('.')
        file_json = bits[0] + '.json'
        geometry.to_file(file_json)


if __name__ == '__main__':

    ''' Run these two lines to generate cached json of LSOAs/DZs '''
    ews = get_ews_json(cache=True)
    ews_cached = cache_by_la_json(ews)

    ''' Run line below to generate all geographical subsets and dump to CSV '''
    generate_subsets()

    ''' Testing for #413: create, retrieve and plot geometry from json for all LSOAs in Greater Manchester '''
    subset_files = ["greater_manchester_lsoas.csv"]
    geo = get_ews_json()
    generate_subset_jsons(subset_files, geo=geo)
    # gm_geom = gpd.read_file(os.path.join(SPATIAL_DIR, "greater_manchester_lsoas.json"))
    # gm_geom.plot()
