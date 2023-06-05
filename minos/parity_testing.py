##
## HR 25/05/23 Some utils for parity/ethnicity testing
##
from os.path import dirname as up
import os
from os.path import dirname as up
import pandas as pd
from minos.utils import dump_parity


# Mapping ONS ethnic categories to NewEthPop: not one-to-one!
# Specifically maps to ONS data here: https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/adhocs/15611livebirthsbyethnicityenglandandwales2010to2020
ONS_ETHNICITY_MAP = {"Bangladeshi":["BAN"],
                     "Indian": ["IND"],
                     "Pakistani": ["PAK"],
                     "Any other Asian background": ["CHI", "OAS"],
                     "Black African": ["BLA"],
                     "Black Caribbean": ["BLC"],
                     "Any other Black background": ["OBL"],
                     "Mixed/multiple ethnic groups": ["MIX"],
                     "Any Other ethnic group": ["OTH"],
                     "White British": ["WBI"],
                     "White Other": ["WHO"],
                     "Not Stated": [],
                     }


PARITY_DIR = up(__file__)
# PARITY_POP = os.path.join(PARITY_DIR, "parity_out.csv") # Originally produced from within Minos run, as a cache for use during testing
# print(PARITY_POP)
PARITY_POP2 = os.path.join(PARITY_DIR, "Minos", "output", "default_config", "hhIncomeIntervention", "2023_04_19_15_28_31", "2020.csv")
# print(PARITY_POP2)


if __name__ == "__main__":
    pop = pd.read_csv(PARITY_POP2)
    year = 2020
    outpath = PARITY_DIR
    dump_parity(pop, year)