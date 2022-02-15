import pandas as pd

from daedalus.RateTables.BaseHandler import BaseHandler
from os.path import exists
from os import remove


class FertilityRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.scaling_method = self.configuration["scale_rates"]["method"]
        self.filename = f'fertility_rate_table_{self.configuration["scale_rates"][self.scaling_method]["fertility"]}.csv'
        self.rate_table_path = self.rate_table_dir + self.filename
        self.source_file = self.configuration.path_to_fertility_file

    def _build(self):
        df_fertility = pd.read_csv(self.source_file)
        print('Computing fertility rate table...')
        self.rate_table = self.transform_rate_table(df_fertility,
                                                    2011,
                                                    2012,
                                                    10, 50, [2])

        if self.configuration["scale_rates"][self.scaling_method]["fertility"] != 1:
            print(f'Scaling the fertility rates by a factor of {self.configuration["scale_rates"][self.scaling_method]["fertility"]}')
            self.rate_table["mean_value"] *= float(self.configuration["scale_rates"][self.scaling_method]["fertility"])
