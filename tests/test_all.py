import pytest
import yaml
import pandas as pd
from os.path import exists
from os import remove
from vivarium import InteractiveContext

from daedalus.RateTables import ImmigrationRateTable
from daedalus.utils import get_config
#from daedalus.PopulationSynthesis import static

from daedalus.RateTables import FertilityRateTable
from daedalus.RateTables import MortalityRateTable
from daedalus.RateTables import EmigrationRateTable

from pathlib import Path

from vivarium.framework.configuration import build_simulation_configuration
from vivarium.config_tree import ConfigTree


@pytest.fixture()
def configuration():

    configuration = get_config("tests/test_configs/test_config.yaml")

    return configuration

# TODO These tests are for the Synthesing the populations as MSOA11 level. They need the DUMMY key to work.

# def test_1_static_Bradford():
#     region = "E08000032"
#     resolution = "MSOA11"
#     variant = "ppp"
#     cache = "./cache"
#     microsim = static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
#     microsim.run(2011, 2012)
#
#
# def test_2_static_Calderdale():
#     region = "E08000033"
#     resolution = "MSOA11"
#     variant = "ppp"
#     cache = "./cache"
#     microsim = static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
#     microsim.run(2011, 2012)
#
#
# def test_3_static_Kirklees():
#     region = "E08000034"
#     resolution = "MSOA11"
#     variant = "ppp"
#     cache = "./cache"
#     microsim = static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
#     microsim.run(2011, 2012)
#
#
# def test_4_static_leeds():
#     region = "E08000035"
#     resolution = "MSOA11"
#     variant = "ppp"
#     cache = "./cache"
#     microsim = static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
#     microsim.run(2011, 2012)
#
#
# def test_5_static_wakefield():
#     region = "E08000036"
#     resolution = "MSOA11"
#     variant = "ppp"
#     cache = "./cache"
#     microsim = static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
#     microsim.run(2011, 2012)


def test_6_fertility_rate_table(configuration):
    RateTable = FertilityRateTable.FertilityRateTable(configuration=configuration)
    # Override to test cache.
    RateTable.rate_table_path = 'tests/cache/' + RateTable.filename
    RateTable.set_rate_table()
    # Process data and cache first time
    RateTable.cache()
    assert exists(RateTable.rate_table_path)
    RateTable.rate_table = None
    RateTable.set_rate_table()
    print(RateTable.rate_table)
    assert isinstance(RateTable.rate_table, pd.DataFrame)
    RateTable.clear_cache()


def test_7_mortality_rate_table(configuration):
    RateTable = MortalityRateTable.MortalityRateTable(configuration=configuration)
    # Override to test cache.
    RateTable.rate_table_path = 'tests/cache/' + RateTable.filename
    RateTable.set_rate_table()
    # Process data and cache first time
    RateTable.cache()
    assert exists(RateTable.rate_table_path)
    RateTable.rate_table = None
    RateTable.set_rate_table()
    print(RateTable.rate_table)
    assert isinstance(RateTable.rate_table, pd.DataFrame)
    RateTable.clear_cache()


def test_8_emigration_rate_table(configuration):
    RateTable = EmigrationRateTable.EmigrationRateTable(configuration=configuration)
    # Override to test cache.
    RateTable.rate_table_path = 'tests/cache/' + RateTable.filename
    RateTable.set_rate_table()
    # Process data and cache first time
    RateTable.cache()
    assert exists(RateTable.rate_table_path)
    RateTable.rate_table = None
    RateTable.set_rate_table()
    print(RateTable.rate_table)
    assert isinstance(RateTable.rate_table, pd.DataFrame)
    RateTable.clear_cache()


def test_9_immigration_rate_table(configuration):
    RateTable = ImmigrationRateTable.ImmigrationRateTable(configuration=configuration)
    # Override to test cache.
    RateTable.rate_table_path = 'tests/cache/' + RateTable.filename
    RateTable.set_rate_table()
    # Process data and cache first time
    RateTable.cache()
    assert exists(RateTable.rate_table_path)
    RateTable.rate_table = None
    RateTable.set_rate_table()
    print(RateTable.rate_table)
    assert isinstance(RateTable.rate_table, pd.DataFrame)
    RateTable.clear_cache()

# def test_9_simulation(self):
#     sim = InteractiveContext('config/model_specification.yaml', setup=False)
#     sim.configuration.update({'population': {'population_size': len(pd.read_csv('data/Testfile.csv'))}})
#     sim.setup()
#     sim.run()
#     print(sim.get_population())
