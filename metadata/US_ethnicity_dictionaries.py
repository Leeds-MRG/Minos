"""Ethnicity dictionaries for US data."""

import numpy as np
import json

# dictionary for converting US codes to daedalus codes.
# Original BHPS dictionary for ethnicity. Really simplistic.
ethnicity_bhps_2002 = {

    # White.
    1: "WBI",  # White British.

    # Black.
    2: "BLC",  # Black Caribbean.
    3: "BLA",  # Black African.
    4: "OBL",  # Other Black.

    # Asians.
    5: "IND",  # Indian.
    6: "PAK",  # Pakistani.
    7: "BAN",  # Bangladeshi.
    8: "CHI",  # Chinese.
    # TODO add arab ethnicity? not in US data.

    # Other.
    9: "OTH",  # Other with BHPS' other id 97

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan,  # Missing
}

# race variable changes for BHPS 2002 - 2008
ethnicity_bhps_2008 = {
    1: "WBI",  # White British.

    # Misc white aggregated into white other WHO.
    2: "WBI",  # Irish
    3: "WBI",  # Welsh
    4: "WBI",  # Scottish
    5: "WHO",  # Other

    # Mixed races aggregated into MIX.
    6: "MIX",  # White Black Caribbean.
    7: "MIX",  # White Black African.
    8: "MIX",  # White Asian.
    9: "MIX",  # Mixed Other.

    # Asians.
    10: "IND",  # Indian.
    11: "PAK",  # Pakistani.
    12: "BAN",  # Bangladeshi.
    17: "CHI",  # Chinese.
    # TODO add arab ethnicity?

    13: "OAS",  # Other Asian.

    # Black.
    14: "BLC",  # Black Caribbean.
    15: "BLA",  # Black African.
    16: "OBL",  # Other Black.
    # Other.

    18: "OTH",  # Other with BHPS' other id 97

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan,  # Missing
}

# UKLHS dictionary post 2008.
ethnicity_ukhls = {
    1: "WBI",  # White British.

    # Misc white aggregated into white other WHO.
    2: "WHO",  # Irish.
    3: "WHO",  # Traveller.
    4: "WHO",  # Other.

    # Mixed races aggregated into MIX.
    5: "MIX",  # White black caribbean.
    6: "MIX",  # White black african.
    7: "MIX",  # White Asian.
    8: "MIX",  # Mixed Other.

    # Asians.
    9: "IND",  # Indian.
    10: "PAK",  # Pakistani.
    11: "BAN",  # Bangladeshi.
    12: "CHI",  # Chinese.
    # TODO add arab ethnicity?

    17: "OAS",  # Arab put into other asian as not (yet?) in daedalus rate frames.
    13: "OAS",  # Other Asian.

    # Black.
    14: "BLC",  # Black Caribbean.
    15: "BLA",  # Black African.
    16: "OBL",  # Other Black.
    # Other.

    97: "OTH",  # Other with BHPS' other id 97

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # Missing
    -9: np.nan,  # Missing
}

with open("metadata/ethnicity_bhps_2002.json", "w") as outfile:
    json.dump(ethnicity_bhps_2002, outfile)
with open("metadata/ethnicity_bhps_2008.json", "w") as outfile:
    json.dump(ethnicity_bhps_2008, outfile)
with open("metadata/ethnicity_uklhs.json", "w") as outfile:
    json.dump(ethnicity_ukhls, outfile)