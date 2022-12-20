import pandas as pd

from daedalus.RateTables.BaseHandler import BaseHandler



class InternalMigrationMatrix(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.path_msoa_to_lad = self.configuration.path_msoa_to_lad
        self.path_to_OD_matrix_index_file = self.configuration.path_to_OD_matrix_index_file
        self.df_OD_matrix_with_LAD = None
        self.MSOA_location_index = {}
        self.df_OD_matrix_with_LAD = {}

    def _build(self):
        df_msoa_lad = pd.read_csv(self.path_msoa_to_lad)
        df_OD_matrix_dest = pd.read_csv(self.path_to_OD_matrix_index_file, index_col=0)
        print('Computing immigration OD matrices...')
        self.df_OD_matrix_with_LAD = df_OD_matrix_dest.merge(df_msoa_lad[["MSOA11CD", "LAD16CD"]],left_index=True,
                                                  right_on="MSOA11CD")
        self.df_OD_matrix_with_LAD.index = self.df_OD_matrix_with_LAD["indices"]
        # Create indices for MSOA and LAD
        self.MSOA_location_index = self.df_OD_matrix_with_LAD["MSOA11CD"].to_dict()
        self.LAD_location_index = self.df_OD_matrix_with_LAD["LAD16CD"].to_dict()




