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


def cache_ews_json(ews_json=EWS_JSON,
                   ews_shapefile=EWS_SHAPEFILE,
                   scale=MAP_SCALE):

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


if __name__ == '__main__':

    ''' Just run this line to generate cached json of LSOAs/DZs '''
    ews = cache_ews_json()
    ews_cached = cache_by_la_json(ews)

    # ''' Testing 1: Just Glasgow, comparing with pre-322 version '''
    # glasgow = os.path.join(up(__file__), 'spatial_data', 'glasgow_data_zones.csv')
    # g = pd.read_csv(glasgow)['lsoa11cd']
    #
    # js = os.path.join(up(__file__), 'spatial_data', 'UK_super_outputs_pre322.geojson')  # Pre-322
    # # js = os.path.join(up(__file__), 'spatial_data', 'UK_super_outputs.geojson')  # New version
    # df_uk = gpd.read_file(js)
    # df_glas = df_uk.loc[df_uk['ZoneID'].isin(g)]
    # df_glas.plot()
    #
    # ''' Testing 2: Look at Manchester and Salford overlaps/gaps '''
    # la_name = 'LAName'
    # df_manc = ews.loc[ews[la_name].isin(['Manchester', 'Salford'])].copy()
    # df_manc['color'] = df_manc[la_name].map({'Manchester': 'r', 'Salford': 'b'})
    # df_manc.plot(color=df_manc['color'])
    #
    # ''' HR 08/02/24 Testing for caching/retrieval by LA '''
    # las = ['E06000038', 'E08000027', 'W06000020', 'W06000021']  # Last one is made up, so should be excluded
    # loaded = get_json_by_la(las)
    # la_code = 'LA_Code'
    # colour_map = {'E06000038': 'r', 'E08000027': 'b', 'W06000020': 'g'}
    #
    # conc = pd.concat(loaded.values())
    # conc['c'] = conc[la_code].map(colour_map)
    # conc.plot(color=conc.c)
