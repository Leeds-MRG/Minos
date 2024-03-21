"""File for parsing, Chris' spatial data, Nik's knn clustering by attributes and Lukes MINOS living wage intervention"""


import pandas as pd
import geojson
from collections import defaultdict

def main(year, params, param_names, source):
    # read data
    spatial_data = pd.read_csv("persistent_data/ADULT_population_GB_2018.csv",)
    lsoa_clusters = pd.read_csv("persistent_data/KNN_LSOA_clusters.csv", index_col=0)
    lsoa_clusters['ZoneID'] = lsoa_clusters.index
    lsoa_clusters = lsoa_clusters[['ZoneID', 'Cluster']]
    lsoa_clusters.reset_index(drop=True, inplace=True)


    # Left merge Nik's data onto Niks LSOA data. Aim to get three columns of pidp, ZoneID (LSOA), and cluster.
    spatial_data = spatial_data.merge(lsoa_clusters, how='left', on='ZoneID')
    spatial_data = spatial_data.loc[~spatial_data['Cluster'].isnull(),]


    # Left merge with Luke's data to get two extra baseline and living wage SF12 columns.

    SF12_data = pd.read_csv("output/livingWage/baseline_vs_livingWage.csv")
    spatial_data = spatial_data.merge(SF12_data, how='left')

    # generate new SF_12_MCS column that is living wage if in cluster 5 and baseline otherwise.
    spatial_data["SF_12_MCS"] = spatial_data["baseline"]
    spatial_data["SF_12_MCS"] = spatial_data["lwage"]
    # TODO make this clearer as a function.
    # OMIT ME IF NO INCLUSION OF CLUSTER DIFFERENCE.
    #spatial_data.loc[spatial_data['Cluster'] == 5, "SF_12_MCS"] = spatial_data.loc[spatial_data['Cluster'] == 5, "lwage"]
    spatial_data.drop(labels=['baseline', 'lwage'],
              axis=1,
              inplace=True)

    # group by lsoa and take SF12 mean.
    spatial_data = spatial_data.groupby("ZoneID", as_index=False)[["Cluster", "SF_12_MCS"]].mean()

    # save to useful data.
    sf12_dict = defaultdict(int, zip(spatial_data["ZoneID"], spatial_data["SF_12"]))
    cluster_dict = defaultdict(int, zip(spatial_data["ZoneID"], spatial_data["Cluster"]))

    json_source = "persistent_data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson"
    #json_source = "/Users/robertclay/data/Lower_Layer_Super_Output_Areas_(December_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson"
    with open(json_source) as f:
        map_geojson = geojson.load(f)

    for i, item in enumerate(map_geojson["features"]):
        ons_code = item["properties"]["LSOA11CD"]
        SF12_code = sf12_dict[ons_code]
        cluster_code = cluster_dict[ons_code]
        if SF12_code == 0:
            SF12_code = None
        if cluster_code == 0:
            cluster_code = None
        item['properties']["SF_12"] = SF12_code
        item['properties']["Cluster"] = cluster_code
        map_geojson['features'][i] = item

    fname = source
    for p, n in zip(params, param_names):
        fname += n + '_' + str(p) + '_'
    fname += f"{year}.geojson"

    with open(fname, 'w') as outfile:
        geojson.dump(map_geojson, outfile)
    print(f"Saved to {fname}.")

if __name__ == '__main__':
    year = 2016
    params = []
    param_names = []
    source = 'output/livingWage/'
    #source = 'output/knnClusterLivingWage/'
    main(year, params, param_names, source)