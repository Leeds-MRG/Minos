import pandas as pd

from minos.RateTables.BaseHandler import BaseHandler
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
        df = pd.read_csv(self.source_file)
        print('Computing mortality rate table...')
        self.rate_table = self.transform_rate_table(df,
                                                    2011,
                                                    2012,
                                                    self.configuration.population.age_start,
                                                    self.configuration.population.age_end)

        if self.configuration["scale_rates"][self.scaling_method]["mortality"] != 1:
            print(f'Scaling the mortality migration rates by a factor of {self.configuration["scale_rates"][self.scaling_method]["mortality"]}')
            self.rate_table["mean_value"] *= float(self.configuration["scale_rates"][self.scaling_method]["mortality"])