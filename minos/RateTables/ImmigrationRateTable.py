import pandas as pd

from daedalus.RateTables.BaseHandler import BaseHandler
from os.path import exists
from os import remove


class ImmigrationRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.scaling_method = self.configuration["scale_rates"]["method"]
        self.source_file = self.configuration.path_to_immigration_file
        self.total_population_file = self.configuration.path_to_total_population_file
        self.total_immigrants = None
        self.location = self.configuration.location

        # cater for LADs where rates are joing toguether.
        if self.configuration.location == 'E09000001' or self.configuration.location == 'E09000033':
            self.location = 'E09000001+E09000033'
        if self.configuration.location == 'E06000052' or self.configuration.location == 'E06000053':
            self.location = 'E06000052+E06000053'

        self.filename = f'immigration_rate_table_{self.location}_{self.configuration["scale_rates"][self.scaling_method]["immigration"]}.csv'
        self.rate_table_path = self.rate_table_dir + self.filename


    def _build(self):
        df_immigration = pd.read_csv(self.source_file)
        df_total_population = pd.read_csv(self.total_population_file)

        df_immigration = df_immigration[df_immigration['LAD.code'].isin([self.location])]

        df_total_population = df_total_population[df_total_population['LAD'].isin([self.location])]
        print('Computing immigration rate table...')
        self.rate_table = self.compute_migration_rates(df_immigration, df_total_population,
                                                       2011,
                                                       2012,
                                                       self.configuration.population.age_start,
                                                       self.configuration.population.age_end)
        if self.configuration["scale_rates"][self.scaling_method]["immigration"] != 1:
            print(f'Scaling the immigration rates by a factor of {self.configuration["scale_rates"][self.scaling_method]["immigration"]}')
            self.rate_table["mean_value"] *= float(self.configuration["scale_rates"][self.scaling_method]["immigration"])

    def set_total_immigrants(self):
        df_immigration = pd.read_csv(self.source_file)

        df_immigration = df_immigration[df_immigration['LAD.code'].isin([self.location])]

        print('Computing total immigration number for location '+self.location)
        self.total_immigrants = int(df_immigration[df_immigration.columns[4:]].sum().sum())

