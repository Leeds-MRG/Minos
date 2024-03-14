""" File for generating fake council tax contribution variable for estimating overall monthly overheads.
"""

import pandas as pd
import numpy as np

import US_utils
from string import ascii_uppercase as alphabet


def format_bands(df):
    # Tax band data oddly formatted. Put it into floats for math to work.
    df = df.apply(lambda x: x.str.rstrip()) # remove right whitespace.
    df = df.applymap(lambda x: str(x).replace('£', '')) # remove pounds.
    df = df.applymap(lambda x: str(x).replace(',', '')) # remove commas.
    df = df.astype(float)  # to floats.
    return df


def lower_bound(x, bands):
    # look up tax band lower bound by region.
    region = x["region"]
    band = x["council_tax"]
    # if both na return na.
    if region != region or band != band:
        return np.nan
    else:
        return bands.loc[region, band]


def upper_bound(x, bands):
    # lookup tax upper bound by region.
    band = x["council_tax"]
    region = x["region"]

    # if both na return na.
    if region != region or band != band:
        return np.nan

    # which integer tax band are we in (0-9).
    where = alphabet.find(band[-1])
    # if at the largest tax band set the upper limit to infinity.
    if region == "Wales":  # wales has one more tax band to consider.
        if where == 8:
            return np.nan
    elif where == 7:
        return np.nan
    # upper bound is where the next bound begins. E.g. band A's upper limit is the state of band B.
    # Find the band above and lookup upper bound.
    new_band = "Band " + alphabet[where]
    return bands.loc[x["region"], new_band]


def random_draw(x):
    # assume uniform distributed tax between upper and lower bounds.
    lb = x["council_tax_lower"]
    ub = x["council_tax_upper"]

    # if both na return na.
    if lb != lb and ub != ub:
        return np.nan

    if ub != ub:
        ub = lb + 1000  # if no upper limit just add on a thousand. #TODO can do better than this. geometric dist?
        # TODO can use pretty much any distribution you want here so long as it draws between these bounds.
    return np.random.uniform(lb, ub)


if __name__ == '__main__':
    maxyr = US_utils.get_data_maxyr()
    years = np.arange(1991, maxyr)
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
    ct_bands = lad_to_band.groupby(by="region").mean()

    # convert tax bands to lower/upper numeric bounds.
    data["council_tax"] = data["council_tax"].replace([-1, -2, -7, -8, -9], np.nan)
    data["region"] = data["region"].replace(['-1', '-2', '-7', '-8', '-9'], np.nan)

    band_dict = dict(zip(range(1, 10), band_columns))

    data['council_tax'] = data['council_tax'].map(band_dict)

    print("Simulating household council tax from bands...")
    data["council_tax_lower"] = data.apply(lambda x: lower_bound(x, ct_bands), axis=1)  # establish individual lower and upper bounds.
    data["council_tax_upper"] = data.apply(lambda x: upper_bound(x, ct_bands), axis=1)
    data["council_tax_draw"] = data.apply(random_draw, axis=1)  # draw randomly between these bounds.

    # Handle single case where someone in London gave has wrong council tax band (Band I which only exists in Wales)
    # data['council_tax_draw'][data['council_tax_draw'].isna()] = -9
    data.loc[data['council_tax_draw'].isna(), 'council_tax_draw'] = -9  # Avoids Pandas SettingWithCopyWarning

    print('Finished composite generation. Saving data...')
    US_utils.save_multiple_files(data, years, "data/adj_raw_US/", "")
