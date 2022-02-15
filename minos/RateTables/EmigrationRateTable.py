import pandas as pd

from daedalus.RateTables.BaseHandler import BaseHandler
from os.path import exists
from os import remove


class EmigrationRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.scaling_method = self.configuration["scale_rates"]["method"]
        self.filename = f'emigration_rate_table_{self.configuration["scale_rates"][self.scaling_method]["emigration"]}.csv'
        self.rate_table_path = self.rate_table_dir + self.filename
        self.source_file = self.configuration.path_to_emigration_file
        self.total_population_file = self.configuration.path_to_total_population_file

    def _build(self):
        df_emigration = pd.read_csv(self.source_file)
        df_total_population = pd.read_csv(self.total_population_file)
        print('Computing emigration rate table...')
        self.rate_table = self.compute_migration_rates(df_emigration, df_total_population,
                                                       2011,
                                                       2012,
                                                       self.configuration.population.age_start,
                                                       self.configuration.population.age_end)

        if self.configuration["scale_rates"][self.scaling_method]["emigration"] != 1:
            print(f'Scaling the emigration rates by a factor of {self.configuration["scale_rates"][self.scaling_method]["emigration"]}')
            self.rate_table["mean_value"] *= float(self.configuration["scale_rates"][self.scaling_method]["emigration"])
