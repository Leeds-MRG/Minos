########################
# Employment Dictionaries
########################

import json
import numpy as np
labour_status_bhps = {
    1: "Self-employed",
    2: "Employed",
    3: "Unemployed",
    4: "Retired",
    5: "Maternity Leave",
    6: "Family Care",
    7: "Student",
    8: "Sick/Disabled",
    9: "Government Training",
    10: "Other",
    97: "Other",

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan  # Missing
}

labour_status_uklhs = {
    1: "Self-employed",
    2: "Employed",
    3: "Unemployed",
    4: "Retired",
    5: "Maternity Leave",
    6: "Family Care",
    7: "Student",
    8: "Sick/Disabled",
    9: "Government Training",
    10: "Employed", # Simplified from Unpaid Family Business because its too rare.
    11: "Employed", # Simpliied from Apprenticeship because its too rare.
    97: "Other",

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan  # Missing
}

with open("metadata/labour_status_bhps.json", "w") as outfile:
    json.dump(labour_status_bhps, outfile)
with open("metadata/labour_status_uklhs.json", "w") as outfile:
    json.dump(labour_status_uklhs, outfile)