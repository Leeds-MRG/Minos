"""Education dictionaries for US data. Useful for translating digits into readable strings.
Noone knows what BHPS education value 7 is. They know what GCSE is.
"""

import json
import numpy as np

# different encodings for each survey..
education_bhps = {
    # Less than GCSE
    7: "Less than GCSE",  # No secondary education.

    # GCSE and equivalnt
    5: "GCSE",  # Certificate of Sixth Year Studies. Very old AS level.
    6: "CSE",  # CSE

    # A-Level and equivalents.
    4: "A-Level",  # A-level

    # Degrees/Further Vocational Eduation
    2: "Degree",  # First Degree
    3: "HE Diploma",  # Higher Diplomas / PGCE for teaching.

    # Doctorate and Above
    1: "Higher Degree",  # PhD and masters not separate here.

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan,  # Missing
}

# This is the actual values of UKLHS Education. They are much more detailed than BHPS.

education_uklhs = {
    # Less than GCSE
    96: "Less than GCSE",  # No secondary education.

    # GCSE and equivalnt
    12: "AS-Level",  # Certificate of Sixth Year Studies. Very old AS level.
    13: "GCSE",  # GSCE/O-Level
    14: "CSE",  # CSE
    15: "Standard/Lower",  # Scottish standard/ordinary grade / lower
    16: "Other Secondary Cert",  # Other school leaving certificates/matriculations.

    # A-Level and equivalents.
    7: "A-Level",  # A-level
    8: "Welsh Baccalaureate",  # Welsh Baccalaureate
    9: "International Baccalaureate",  # International Baccalaureate
    10: "AS-Level",  # AS-level
    # Scottish Highers/Advanced Highers are annoyingly rolled into one.
    # Can graudate with highers from 15-18.
    11: "Highers (Scotland)",  # Scotland Higher /Advanced Higher.

    # Degrees/Further Vocational Eduation
    2: "Degree",  # First Degree
    3: "HE Diploma",  # Higher Education Diploma
    4: "Teaching (Non-PGCE)",  # Teaching qualification. ( TODO probably needs its own category.)
    5: "Medical Education",  # Nursing or other medical qualification.
    6: "Degree",  # Other higher degree.

    # Doctorate and Above
    1: "Higher Degree",  # PhD and masters not separate here.

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan  # Missing
}

# Here is the simplifed UKLHS educations.  For the sake of consistency.
# These are simplified to to align with BHPS. If we want longer terms longitudinal patterns going to have to do this.
# Or find some way for individuals to transition as new data arrives. E.G. will need to initialise educations again..
# The scots will all shift to scottish highers for example. Migrants will have IBs rather than A-Levels and so on..

education_uklhs_simple = {
    # Less than GCSE
    96: "Less than GCSE",  # No secondary education.

    # GCSE and equivalnt
    12: "A-Level",  # Certificate of Sixth Year Studies. Very old AS level.
    13: "GCSE",  # GSCE/O-Level
    14: "CSE",  # CSE
    15: "GCSE",  # Scottish standard/ordinary grade / lower
    16: "GCSE",  # Other school leaving certificates/matriculations.

    # A-Level and equivalents.
    7: "A-Level",  # A-level
    8: "A-Level",  # Welsh Baccalaureate
    9: "A-Level",  # International Baccalaureate
    10: "A-Level",  # AS-level
    # Scottish Highers/Advanced Highers are annoyingly rolled into one.
    # Can graudate with highers from 15-18.
    11: "A-Level",  # Scotland Higher /Advanced Higher.

    # Degrees/Further Vocational Eduation
    2: "Degree",  # First Degree
    3: "HE Diploma",  # Higher Education Diploma
    4: "HE Diploma",  # Teaching qualification.
    5: "Higher Degree",  # Nursing or other medical qualification.
    6: "Degree",  # Other higher degree.

    # Doctorate and Above
    1: "Higher Degree",  # PhD and masters not separate here.

    -1: np.nan,  # Unknown
    -2: np.nan,  # Refusal
    -7: np.nan,  # Proxy
    -8: np.nan,  # N/A
    -9: np.nan  # Missing
}

with open("metadata/education_bhps.json", "w") as outfile:
    json.dump(education_bhps, outfile)
with open("metadata/education_uklhs.json", "w") as outfile:
    json.dump(education_uklhs, outfile)
with open("metadata/education_uklhs_simple.json", "w") as outfile:
    json.dump(education_uklhs_simple, outfile)