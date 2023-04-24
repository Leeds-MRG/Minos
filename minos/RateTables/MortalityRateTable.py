import pandas as pd

from minos.RateTables.BaseHandler import BaseHandler
from minos.data_generation.convert_rate_data import cache_mortality_by_region
from os.path import exists
from os import remove


class MortalityRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.scaling_method = self.configuration["scale_rates"]["method"]
        self.filename = f'mortality_rate_table_{self.configuration["scale_rates"][self.scaling_method]["mortality"]}.csv'
        self.rate_table_path = self.rate_table_dir + self.filename
        self.source_file = self.configuration.path_to_mortality_file

    def _build(self):
        # HR 21/04/23 Try and load from source file, otherwise create from primary data
        try:
            print("Trying to load from source file...")
            df = pd.read_csv(self.source_file)
        except FileNotFoundError as e:
            print("Couldn't load from source file")
            print("\n", e, "\n")
            print("Creating source file from primary data...")
            dump_path = cache_mortality_by_region()
            if dump_path:
                print("Dumped source file to:", dump_path)
                self.source_file = dump_path
                df = pd.read_csv(self.source_file)
            else:
                print("Couldn't dump source file")

        yr_start = self.configuration['time']['start']['year']
        yr_end = self.configuration['time']['end']['year']
        print('Computing mortality rate table for years in range [', yr_start, ',', yr_end, ']...')

        # self.rate_table = self.transform_rate_table(df,
        #                                             2011,
        #                                             2013,
        #                                             self.configuration.population.age_start,
        #                                             self.configuration.population.age_end)
        self.rate_table = self.transform_rate_table(df,
                                                    yr_start,
                                                    yr_end,
                                                    self.configuration.population.age_start,
                                                    self.configuration.population.age_end)

        if self.configuration["scale_rates"][self.scaling_method]["mortality"] != 1:
            print(f'Scaling the mortality migration rates by a factor of {self.configuration["scale_rates"][self.scaling_method]["mortality"]}')
            self.rate_table["mean_value"] *= float(self.configuration["scale_rates"][self.scaling_method]["mortality"])