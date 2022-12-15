import numpy as np
import json

sexes = {

    # White.
    1: "Male",  # Male
    2: "Female",  # Female

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan,  # Missing
}
with open("metadata/sexes.json", "w") as outfile:
    json.dump(sexes, outfile)
