"""File for mergeing Scotland and England/Wales """
import geojson

def format_scotland_geojson(scot_file):
    """Format scotland geojson so it can be merged with the england and wales one.

    data from https://spatialdata.gov.scot/geonetwork/srv/api/records/7d3e8709-98fa-4d71-867c-d5c8293823f2.
    converted to geojson using mapshaper.org.
    polygons simplified using 3% visvalingam weighted area algorithm. Lower resolution and file size.
    - convert Name property to name
    - convert DataZone to LSOA11Cd
    - remove every other property.
    - keep the geometry.

    """
    with open(scot_file) as f:
        scot_geojson = geojson.load(f)

    for i, item in enumerate(scot_geojson["features"]):
        # rename name and data zone code properties.
        # discard everything else.
        item['properties'] = {"name": item['properties']['Name'],
                              "ZoneID": item['properties']['DataZone']}
    return scot_geojson

def format_england_geojson(eng_file):
    """Format england geojson so it can be merged with the england and wales one.

    - convert Name property to name

    """
    with open(eng_file) as f:
        eng_geojson = geojson.load(f)

    for i, item in enumerate(eng_geojson["features"]):
        # rename name and lsoa code properties.
        # discard everything else.
        item['properties'] = {"name": item['properties']['LSOA11NM'],
                              "ZoneID": item['properties']['LSOA11CD']}
    return eng_geojson

def merge_and_save_jsons(d1, d2, f_name):

    merged_json = [d1['features'] + d2['features']][0] # seems stupid but can't find a better way to merge feature collections.
    merged_json = geojson.FeatureCollection(merged_json)
    print(f"Saving to {f_name}.")
    with open(f_name, 'w') as outfile:
        geojson.dump(merged_json, outfile)

if __name__ == '__main__':

    scot_json = format_scotland_geojson("persistent_data/SG_DataZone_Bdry_2011.json")
    eng_json = format_england_geojson("persistent_data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson")
    merge_and_save_jsons(eng_json, scot_json, "persistent_data/UK_super_outputs.geojson")
