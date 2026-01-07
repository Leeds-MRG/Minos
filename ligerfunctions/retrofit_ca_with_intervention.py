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
from sipherdb.query.queries import Queries

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(ROOT_DIR)

without_intervention_path = '/home/jduro/sipher/ws5/complete_runs/without_intervention_2020_2035/raw'
simul_folders_baseline = ('2026_01_07_09_58_37_r1', '2025_07_22_10_21_39_r2', '2025_07_24_11_17_17_r3',
                          '2025_07_24_18_31_54_r4', '2025_07_25_22_07_36_r5', '2025_07_26_08_16_40_r6',
                          '2025_07_26_13_18_42_r7', '2025_07_26_21_09_48_r8', '2025_07_27_08_59_19_r9',
                          '2025_07_27_13_15_23_r10', '2025_07_28_00_05_48_r11')


def dbquery(sql_db=SqlDB.POSTGRESQL):
    db_obj = SipherDatabase()
    db_obj.init_class(sql_db=sql_db, db_config_file=os.path.join(ROOT_DIR, 'database.ini'))
    return Queries()

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def sp_merge_epc(data_ref_df: pd.DataFrame, epc_latest_df: pd.DataFrame) -> pd.DataFrame:

    # 1) Build lookup for the 2020 reference households
    lookup = build_house_lookup(data_ref_df, epc_latest_df, seed=42)

    # 2) Bring EPC features via house_id
    #    First expose house_id on EPC side to merge (same as inside helper)
    if epc_latest_df.index.name is None:
        epc_with_id = epc_latest_df.reset_index().rename(columns={'index': 'house_id'})
    else:
        epc_with_id = epc_latest_df.reset_index().rename(columns={epc_latest_df.index.name: 'house_id'})

    # Select only the columns you want to attach to people
    epc_cols_to_keep = [
        'house_id', 'imd_rank',
        'energy_rating', 'energy_rating_new', 'environment_impact'
    ]

    # 3) Merge onto the reference households (2025)
    data_ref_with_epc = (
        data_ref_df
        .merge(lookup, on='hidp', how='left')
        .merge(epc_with_id[epc_cols_to_keep], on='house_id', how='left')
    )

    return data_ref_with_epc


def build_house_lookup(data_ref_df: pd.DataFrame, epc_latest_df: pd.DataFrame, seed: int) -> pd.DataFrame:

    rng = np.random.default_rng(seed)

    # Ensure EPC frame exposes a house id
    if epc_latest_df.index.name is None:
        epc_with_id = epc_latest_df.reset_index().rename(columns={'index': 'house_id'})
    else:
        epc_with_id = epc_latest_df.reset_index().rename(columns={epc_latest_df.index.name: 'house_id'})

    keys = ['ZoneID', 'housing_tenure_num', 'number_of_habitable_rooms']

    # Group by all three keys for fast exact lookups
    epc_groups = epc_with_id.groupby(keys, sort=False)

    data_households = data_ref_df.drop_duplicates(subset='hidp')

    out_frames = []

    # Also group by (tenure, number of habitable rooms) that ignores ZoneID
    epc_by_zt = {
        zt_key: grp.copy()
        for zt_key, grp in epc_with_id.groupby(['housing_tenure_num', 'number_of_habitable_rooms'], sort=False)
    }

    for (zone_id, tenure_num, rooms), hh_grp in data_households.groupby(keys, sort=False):
        key_vals = (zone_id, tenure_num, rooms)

        if key_vals in epc_groups.groups:
            epc_pool = epc_groups.get_group(key_vals)
        else:
            zt_key = (tenure_num, rooms)
            epc_pool = epc_by_zt.get(zt_key)

        if epc_pool.empty:
            # If absolutely no match in the same ZoneID & tenure after widening, you might:
            # - raise an error,
            # - or relax ZoneID/tenure as a second-level fallback (not implemented here by request).
            raise ValueError(
                f"No EPC houses for group (ZoneID={zone_id}, housing_tenure_num={tenure_num}, rooms~{rooms}) "
                f"even after ignoring ZoneID.")

        n_households = len(hh_grp)
        house_ids = epc_pool['house_id'].to_numpy()
        m_houses = len(house_ids)

        # Repeat/shuffle to cover all households
        repeats = int(np.ceil(n_households / m_houses))
        pool = np.tile(house_ids, repeats)
        rng.shuffle(pool)
        assigned = pool[:n_households]

        out_frames.append(pd.DataFrame({
            'hidp': hh_grp['hidp'].to_numpy(),
            'house_id': assigned
        }))

    return pd.concat(out_frames, ignore_index=True)


def do_intervention(df_in, geographic_level_for_intervention, locations_for_intervention_df, sdb):

    if geographic_level_for_intervention == "MSOA":
        # add LSOAs to MSOAs mapping to dataset
        if geographic_level_area == "LAD":
            codes_lst = sdb.lad_lsoa_msoa_codes(lad_name=area_name)
        elif geographic_level_area == "CA":
            codes_lst = sdb.ca_lsoa_msoa_codes(ca_name=area_name)
        codes_lst_df = pd.DataFrame(codes_lst, columns=['lsoa_code', 'msoa_code'])
        df_in = pd.merge(df_in, codes_lst_df, on='lsoa_code', how='left')
    df_in = pd.merge(df_in, locations_for_intervention_df, on='lsoa_code', how='left')

    df_in['household_with_intervention'] = np.where(
        (df_in['intervention'] == 1) & (df_in['heating'] == 0), True, False)
    df_in['heating'] = np.where(
        (df_in['household_with_intervention'] == True), 1, df_in['heating']
    )

    core_list = ['fridge_freezer', 'washing_machine', 'heating']
    bonus_list = ['tumble_dryer', 'dishwasher', 'microwave']

    df_in["housing_core_sum"] = df_in[core_list].gt(0).sum(axis=1)
    df_in["housing_bonus_sum"] = df_in[bonus_list].gt(0).sum(axis=1)

    # conditions for housing quality
    conditions = [
        (df_in["housing_core_sum"] >= 0) & (df_in["housing_core_sum"] < 3),  # less than full core
        (df_in["housing_core_sum"] == 3) & (df_in["housing_bonus_sum"] >= 0) & (df_in["housing_bonus_sum"] < 3),
        # all core some bonus
        (df_in["housing_core_sum"] == 3) & (df_in["housing_bonus_sum"] == 3),  # all core all bonus
    ]
    values = ['Low', 'Medium', 'High']
    df_in["housing_quality"] = np.select(conditions, values)
    df_in['housing_quality'][df_in['housing_quality'] == 0] = -9

    # conditions for Sipher-7 housing quality
    df_in['S7_housing_quality'] = "-9.0"  # changed this from -9 int for consistency and to supress type warning.
    df_in['S7_housing_quality'][(df_in['housing_core_sum'] + df_in['housing_bonus_sum']) == 6] = 'Yes to all'
    df_in['S7_housing_quality'][
        (df_in['housing_core_sum'] + df_in['housing_bonus_sum']).isin(range(1, 6))] = 'Yes to some'
    df_in['S7_housing_quality'][(df_in['housing_core_sum'] + df_in['housing_bonus_sum']) == 0] = 'No to all'

    # recalculate equivalent income
    df_in = calculate_equivalent_income(df_in)

    # remove the temporarily added columns and rename lsoa_code to ZoneID
    df_in.drop(['intervention', 'housing_core_sum', 'housing_bonus_sum', ], axis=1, inplace=True)
    df_in.rename(columns={'lsoa_code': 'ZoneID'}, inplace=True)

    # Remove the following columns because they conflict with some Minos components:
    # - tracked: population_manager
    # - has_newborn: nkids_age_specific_fertility
    # - entrance_time: no_replenishment
    df_in.drop(['tracked', 'has_newborn', 'entrance_time', ], axis=1, inplace=True)

    return df_in


def house_retrofit_intervention(
        x,
        sql_db,
        area_name,
        geographic_level_area,
        geographic_level_for_intervention,
        run_number=0
):
    # 1. Read the population for intervention: synthetic pop 2025
    folder_name = os.path.join(without_intervention_path, simul_folders_baseline[run_number])
    synpop = pd.read_csv(folder_name + '/2025.csv')
    # synpop.rename(columns={'ZoneID': 'lsoa_code'}, inplace=True)

    # 2. Format number of rooms, number of bedrooms, and housing tenure
    synpop = synpop.astype({'number_of_rooms': int, 'housing_tenure': int, 'number_of_bedrooms': int})

    max_number_of_rooms = 8  # this is a parameter
    synpop['number_of_habitable_rooms'] = synpop['number_of_rooms'] + synpop['number_of_bedrooms']
    synpop['number_of_habitable_rooms'] = np.where(synpop['number_of_habitable_rooms'] > max_number_of_rooms,
                                                   max_number_of_rooms, synpop['number_of_habitable_rooms'])

    # simplify housing tenure
    synpop['housing_tenure_simple'] = synpop['housing_tenure']
    synpop['housing_tenure_simple'] = synpop['housing_tenure_simple'].replace(3, 4)  # social rented
    synpop['housing_tenure_simple'] = synpop['housing_tenure_simple'].replace(5, 3)  # private rented
    synpop['housing_tenure_simple'] = synpop['housing_tenure_simple'].replace(6, 3)  # private rented
    synpop['housing_tenure_simple'] = synpop['housing_tenure_simple'].replace(7, 3)  # private rented

    # map housing tenure to 3 categories
    housing_tenure_dic = {
        1: 1,  # owned outright => owned
        2: 1,  # owned with mortgage => owned
        3: 2,  # private rented => private rented
        4: 3,  # social rented => social rented
    }
    synpop['housing_tenure_num'] = synpop['housing_tenure_simple'].map(housing_tenure_dic)

    # 3. Load EPC latest data
    epc_latest_df = pd.read_csv('data/epc_latest_gmca.csv')

    # 4. Merge synthetic population with EPC latest data
    synpop_epc = sp_merge_epc(synpop, epc_latest_df)

    # 5. Build model to predict thermal comfort
    model_keys = ['imd_rank', 'number_of_habitable_rooms', 'housing_tenure_num', 'energy_rating', 'net_hh_income', 'heating']
    model_data = synpop_epc[model_keys]

    # format geographic_level_area
    geographic_level_area = geographic_level_area.upper()
    # format geographic_level_divisions
    geographic_level_for_intervention = geographic_level_for_intervention.upper()

    sdb = dbquery(sql_db)
    if geographic_level_for_intervention == "MSOA":
        if geographic_level_area == "LAD":
            locations_for_intervention = sdb.lad_msoa_codes(lad_name=area_name)
        elif geographic_level_area == "CA":
            locations_for_intervention = sdb.ca_msoa_codes(ca_name=area_name)
        locations_for_intervention_df = pd.DataFrame(locations_for_intervention, columns=['msoa_code'])
        locations_for_intervention_df.set_index('msoa_code', inplace=True)
    elif geographic_level_for_intervention == "LSOA":
        if geographic_level_area == "LAD":
            locations_for_intervention = sdb.lad_lsoa_codes(lad_name=area_name)
        elif geographic_level_area == "CA":
            locations_for_intervention = sdb.ca_lsoa_codes(ca_name=area_name)
        locations_for_intervention_df = pd.DataFrame(locations_for_intervention, columns=['lsoa_code'])
        locations_for_intervention_df.set_index('lsoa_code', inplace=True)
    else:
        raise ValueError(f'Invalid geographic level {geographic_level_for_intervention}.')

    locations_for_intervention_df.loc[:, 'intervention'] = x

    # 3. Do the intervention
    # Read the 2025 population
    folder_name = os.path.join(without_intervention_path, simul_folders_baseline[run_number])
    df2 = pd.read_csv(folder_name + '/2025.csv')
    df2.rename(columns={'ZoneID': 'lsoa_code'}, inplace=True)
    df2 = do_intervention(df2, geographic_level_for_intervention, locations_for_intervention_df, sdb)
    # Save the population
    df2.to_csv(os.path.join('data/scaled_manchester_aligned_US', '2025_US_cohort.csv'), index=False)

    # 4. Run the pipeline (part-2)
    output_file_folder = simul_folders_baseline[run_number]
    args = Namespace(config=os.path.join(ROOT_DIR, 'config/energy_manchester_scaled_part2.yaml'),
                     intervention=None,
                     runID=None,
                     runtime=output_file_folder,
                     subdir='energy_manchester')
    run(args)
    return

if __name__ == "__main__":

    random.seed(10)
    np.random.seed(10)

    sql_db = SqlDB.POSTGRESQL
    sdb = dbquery(sql_db)

    area_name = "Greater Manchester"
    geographic_level_area = "CA"
    geographic_level_for_intervention = "LSOA"
    n_locations_for_intervention = 1702

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
    else:
        raise ValueError(f'Invalid geographic level {geographic_level_for_intervention}.')

    input_data = [True for _ in range(n_locations_for_intervention)]

    run_number = 0
    start = time.time()
    house_retrofit_intervention(
        x=input_data, sql_db=sql_db, area_name=area_name,
        geographic_level_area=geographic_level_area,
        geographic_level_for_intervention=geographic_level_for_intervention,
        run_number=run_number
    )

    print(f"{(time.time() - start):.2f} Seconds ")
