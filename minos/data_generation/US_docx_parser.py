"""
File to take LAD codes from BHPS rtf format data dictionary.
"""

import re  # regex
import pandas as pd
from striprtf.striprtf import rtf_to_text

from US_utils import save_json

def rtf_to_list(source):
    with open(source, 'r') as file:
        text = file.read() # read in rtf file.
        text = rtf_to_text(text) # decode rtf format into uft-8.
        text = text.replace("\t", "    ")  # replace tab characters with 4 spaces for readability.
        var_names = re.findall('Variable = (.+?)    ', text) # find variable names from main string.
        text = text.split("\n")  # split string into list by new line character.
        text = [row for row in text if row != '']  # remove missing rows
    return text, var_names

def rtf_list_to_dict(rtf_data):
    """Convert rtf documentation lists of values into dictionaries. """
    out_dict = {}
    for item in rtf_data:
        item += ','  # add apostrophe to last item so regex is consistent.

        v = re.search('Value = (.+?)    ', item)
        l = re.search('Label = (.+?),', item)

        if not v or not l:
            continue
        else:
            v = v.group(1)
            l = l.group(1)
            out_dict[v] = l
    return out_dict

if __name__ == "__main__":
    file = "/Users/robertclay/data/UKDA-6614-stata/mrdoc/ukda_data_dictionaries/bhps/ba_indresp_ukda_data_dictionary.rtf"
    text, var_names = rtf_to_list(file)

    breaks = [i for i, row in enumerate(text) if row[:7] == "Pos. = "]
    parts = [text[breaks[i]:breaks[i + 1]] for i in range(len(breaks) - 1)]
    # what is the variable position, what is its name, where is it in the document.
    positions = dict(zip(var_names, parts))

    region_data = positions["ba_gor_dv"]
    region_dict = rtf_list_to_dict(region_data)
    print(region_dict)

    LAD_data = positions["ba_plb4d"]
    LAD_dict = rtf_list_to_dict(LAD_data)
    print(LAD_dict)
    save_json(LAD_dict, "persistent_data/JSON/LAD_dict.json")