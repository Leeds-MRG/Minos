
import random
import time
import os
import numpy as np
import pandas as pd

from minos.data_generation.generate_repl_pop import generate_replenishing
from scripts.run import run
from minos.data_generation.generate_composite_vars import calculate_equivalent_income

from sipherdb.sipher_database import SipherDatabase
from sipherdb.sipher_database import SqlDB
from sipherdb.query.general_queries import GeneralDataQueries


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def house_quality_intervention(
        x,
        sql_db,
        area_name,
        geographic_level_area,
        geographic_level_for_intervention,
):
    number_of_interventions = sum(x)

    # format geographic_level_area
    geographic_level_area = geographic_level_area.upper()
    # format geographic_level_divisions
    geographic_level_for_intervention = geographic_level_for_intervention.upper()

    db = SipherDatabase()
    db.init_class(sql_db=sql_db, db_config_file=os.path.join(os.getcwd(), 'database.ini'))
    sdb = GeneralDataQueries()

    if geographic_level_for_intervention == "MSOA":
        if geographic_level_area == "LAD":
            locations_for_intervantion = sdb.lad_msoa_codes(lad_name=area_name)
        elif geographic_level_area == "CA":
            locations_for_intervantion = sdb.ca_msoa_codes(ca_name=area_name)
        locations_for_intervention_df = pd.DataFrame(locations_for_intervantion, columns=['msoa_code'])
        locations_for_intervention_df.set_index('msoa_code', inplace=True)
    elif geographic_level_for_intervention == "LSOA":
        if geographic_level_area == "LAD":
            locations_for_intervantion = sdb.lad_lsoa_codes(lad_name=area_name)
        elif geographic_level_area == "CA":
            locations_for_intervantion = sdb.ca_lsoa_codes(ca_name=area_name)
        locations_for_intervention_df = pd.DataFrame(locations_for_intervantion, columns=['lsoa_code'])
        locations_for_intervention_df.set_index('lsoa_code', inplace=True)
    locations_for_intervention_df.loc[:, 'intervention'] = x

    # 1. Read the population file for intervention and upgrade the house quality
    df_in = (pd
             .read_csv(os.path.join('data/scaled_glasgow_US', '2020_US_cohort_original.csv'))
             .rename(columns={'ZoneID': 'lsoa_code'})
             )

    if geographic_level_for_intervention == "MSOA":
        # add LSOAs to MSOAs mapping to dataset
        if geographic_level_area == "LAD":
            codes_lst = sdb.lad_lsoa_msoa_codes(lad_name=area_name)
        elif geographic_level_area == "CA":
            codes_lst = sdb.ca_lsoa_msoa_codes(ca_name=area_name)
        codes_lst_df = pd.DataFrame(codes_lst, columns=['lsoa_code', 'msoa_code'])
        df_in = pd.merge(df_in, codes_lst_df, on='lsoa_code', how='left')
    df_in = pd.merge(df_in, locations_for_intervention_df, on='msoa_code', how='left')

    conditions = [df_in['S7_housing_quality'] == 'Yes to all',
                  df_in['S7_housing_quality'] == 'Yes to some',
                  df_in['S7_housing_quality'] == 'No to all']
    choices = [1, 2, 3]

    df_in['S7_house_quality_score'] = np.select(conditions, choices)
    df_in['S7_house_quality_score'] = np.where(
        (df_in['intervention'] == 1) & (df_in['S7_house_quality_score'] > 1),
        df_in['S7_house_quality_score'] - 1, df_in['S7_house_quality_score']
    )

    conditions = [df_in['S7_house_quality_score'] == 1,
                  df_in['S7_house_quality_score'] == 2,
                  df_in['S7_house_quality_score'] == 3]
    choices = ['Yes to all', 'Yes to some', 'No to all']
    df_in['S7_housing_quality'] = np.select(conditions, choices)

    choices = ['High', 'Medium', 'Low']
    df_in['housing_quality'] = np.select(conditions, choices)

    # recalculate equivalent income
    df_in = calculate_equivalent_income(df_in)

    # count the number of households with intervention
    df_h = df_in.drop_duplicates(subset=['hidp'])
    number_household_with_intervention = df_h['intervention'].sum()

    # remove the temporarily added columns and rename lsoa_code to ZoneID
    df_in.drop(['S7_house_quality_score', 'intervention', 'msoa_code', ], axis=1, inplace=True)
    df_in.rename(columns={'lsoa_code': 'ZoneID'}, inplace=True)
    # save the new population
    df_in.to_csv(os.path.join('data/scaled_glasgow_US', '2020_US_cohort.csv'), index=False)

    # 2. Replenishes the populations
    proj_file = "persistent_data/age-sex-ethnic_projections_2008-2061.csv"
    projections = pd.read_csv(proj_file)
    projections = projections.drop(labels='Unnamed: 0', axis=1)
    projections = projections.rename(columns={'year': 'time'})

    scotland_mode = False
    cross_validation = False
    inflated = False
    region = 'glasgow'

    generate_replenishing(projections=projections,
                          scotland_mode=scotland_mode,
                          cross_validation=cross_validation,
                          inflated=inflated,
                          region=region,
                          final_year=2026)

    # 3. Run the pipeline
    args = Namespace(config=os.path.join(os.getcwd(), 'config/S7_glasgow_scaled.yaml'),
                     intervention=None,
                     runID=None,
                     runtime=None,
                     subdir='SIPHER7_glasgow')
    output_file_path = run(args)

    # output_file_path = '/home/jduro/sipher/ws5/Minos/output/SIPHER7_glasgow/baseline/2024_03_15_10_09_46/'

    # Read the output population
    df = (pd
          .read_csv(output_file_path)
          .rename(columns={'ZoneID': 'lsoa_code'})
          )

    indicator_ei_mean = df['equivalent_income'].median()
    imd_ranks = sdb.simd_rank_in_lad(lad_name=area_name)
    lsoa_stats = pd.DataFrame(imd_ranks, columns=['lsoa_code', 'simdrank'])
    lsoa_stats['deciles'] = lsoa_stats['simdrank'].transform(
        lambda x: pd.qcut(x, 10, labels=False, duplicates='drop')
    )
    lsoa_stats = lsoa_stats.assign(
        deciles=lambda df_: df_['deciles'].astype('int8')
    )
    lsoa_stats.set_index('lsoa_code', inplace=True)
    df = df.set_index('lsoa_code').join(lsoa_stats[['deciles']])

    df_decile_grouped = df.groupby(['deciles'])
    indicators_decile = {
        'ei_mean_per_decile': df_decile_grouped['equivalent_income'].median(),
        'popsize_decile': df_decile_grouped['deciles'].count()
    }

    deciles_df = pd.DataFrame(indicators_decile)
    del df_decile_grouped
    deciles_df['prop_pop'] = deciles_df['popsize_decile'].transform(lambda x: x / x.sum())
    deciles_df['cumsum'] = deciles_df['prop_pop'].transform(lambda x: x.cumsum() * 100)
    indicator_ei_inequality = np.linalg.lstsq(np.vstack([deciles_df['cumsum'], np.ones(len(deciles_df['cumsum']))]).T,
                                              deciles_df['ei_mean_per_decile'], rcond=None)[0][0] * 100

    y = [number_of_interventions, indicator_ei_mean, indicator_ei_inequality, number_household_with_intervention]
    return y


if __name__ == "__main__":

    random.seed(10)
    np.random.seed(10)

    sql_db = SqlDB.POSTGRESQL
    db = SipherDatabase()
    db.init_class(sql_db=sql_db, db_config_file=os.path.join(os.getcwd(), 'database.ini'))
    sdb = GeneralDataQueries()

    area_name = "Glasgow City"
    geographic_level_area = "LAD"
    geographic_level_for_intervention = "MSOA"
    n_locations_for_intervention = 136

    if geographic_level_area == "LAD":
        if geographic_level_for_intervention == "MSOA":
            n_locations_for_intervention = sdb.number_of_msoas_in_lad(lad_name=area_name)
        elif geographic_level_for_intervention == "LSOA":
            n_locations_for_intervention = sdb.number_of_lsoas_in_lad(lad_name=area_name)
    elif geographic_level_area == "CA":
        if geographic_level_for_intervention == "MSOA":
            n_locations_for_intervention = sdb.number_of_msoas_in_ca(ca_name=area_name)
        elif geographic_level_for_intervention == "LSOA":
            n_locations_for_intervention = sdb.number_of_lsoas_in_ca(ca_name=area_name)

    input_data = [True for _ in range(n_locations_for_intervention)]

    start = time.time()
    y = house_quality_intervention(
        x=input_data, sql_db=sql_db, area_name=area_name,
        geographic_level_area=geographic_level_area,
        geographic_level_for_intervention=geographic_level_for_intervention
    )

    print(f"{(time.time() - start):.2f} Seconds ")
    print(y)
    print(len(y))
