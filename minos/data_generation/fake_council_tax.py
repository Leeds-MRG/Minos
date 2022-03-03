""" File for generating fake council tax contribution variable for estimating overall monthly overheads.
"""

import pandas as pd
import numpy as np
import math

import US_utils
from string import ascii_uppercase as alphabet

def format_bands(df):
    df = df.apply(lambda x: x.str.rstrip()) # remove right whitespace.
    df = df.applymap(lambda x: str(x).replace('£', '')) # remove pounds.
    df = df.applymap(lambda x: str(x).replace(',', '')) # remove commas.
    df = df.astype(float)  # to floats.
    return df

def lower_bound(x):
    region = x["region"]
    band = x["council_tax"]
    if region != region or band != band:
        return np.nan
    else:
        return g.loc[region, band]

def upper_bound(x):
    band = x["council_tax"]
    region = x["region"]

    if region != region or band != band:
        return np.nan

    where = alphabet.find(band[-1])
    # if at the largest tax band set the upper limit to infinity.
    if region == "Wales": # wales has one more tax band to consider.
        if where == 8:
            return np.nan
    else:
        if where == 7:
            return np.nan
    # upper bound is where the next bound begins. E.g. band A's upper limit is the state of band B.
    # Find the band above.
    new_band = "Band " + alphabet[where+1]
    return g.loc[x["region"], new_band]

def random_draw(x):
    lb = x["council_tax_lower"]
    ub = x["council_tax_upper"]

    if lb!= lb and ub != ub:
        return np.nan

    if ub != ub:
        ub = lb + 1000 # if no upper limit just add on a thousand. #TODO can do better than this. geometric dist?
        # TODO can use pretty much any distribution you want here so long as it draws between these bounds.
    if lb > ub:
        print('aaaa')
    return np.random.uniform(lb, ub)

if __name__ == '__main__':
    years = [2010]
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)

    # data for conversions between LADs to region and council tax band (A, B,...) to numeric boundaries (£1200-£1400)
    lad_to_band = pd.read_csv("persistent_data/lad_tax_bands.csv")
    lad_to_region = US_utils.load_json("persistent_data/JSON/", "LAD_to_region_name.json")

    band_columns = ['Band A', 'Band B', 'Band C', 'Band D', 'Band E',
       'Band F', 'Band G', 'Band H', 'Band I']
    # band columns messy. formatting..
    lad_to_band[band_columns] = format_bands(lad_to_band[band_columns])
    # add regional data to band columns
    lad_to_band["region"] = lad_to_band["Area"].map(lad_to_region)

    # group bands by region.
    g = lad_to_band.groupby(by="region").mean()

    # convert tax bands to lower/upper numeric bounds.
    data["council_tax"] = data["council_tax"].replace([-1,-2,-7,-8,-9], np.nan)
    data["region"] = data["region"].replace(['-1','-2','-7','-8','-9'], np.nan)

    data["council_tax"] = data["council_tax"].map(dict(zip(range(1, 10), band_columns)))

    # lookup minimum bound by region and tax band


    data["council_tax_lower"] = data.apply(lower_bound, axis=1)
    data["council_tax_upper"] = data.apply(upper_bound, axis=1)
    data["council_tax_draw"] = data.apply(random_draw, axis=1)