""" For now this file is simple. Extract from children datasets, get their ages and hidps. See how this lines up with indresp dataset and how much
missing data (if any) there is.

"""

import US_utils
import pandas as pd
import numpy as np

def main(input_raw_data, year):

    # download children datasets in one at a time
    child_name = US_utils.US_file_name(year, "../UKDA-6614-stata/stata/stata13_se/", "child")    # get hidp, pidp, and age.
    child_data = US_utils.load_file(child_name)

    attribute_columns = US_utils.wave_prefix(['hidp', 'age_dv'], year)
    child_data = child_data[attribute_columns]
    child_data.columns = ['hidp', 'age']
    child_data['is_child'] = True
    child_data['time'] = year

    # get collaped_children_US individual datasets
    #US_data = pd.read_csv(f"data/composite_US/{year}_US_cohort.csv")
    input_raw_data['is_child'] = False

    #children_by_house = collaped_children_US.groupby(['hidp'])['nkids']
    # group children by hidp to determine missing age data.

    #collaped_children_US_with_children = collaped_children_US.merge(child_data, 'inner', on='hidp')
    collaped_children_US_with_children = pd.concat([input_raw_data, child_data], sort=True)

    # removing orphans.
    collaped_children_US_with_children['is_adult'] = 1-collaped_children_US_with_children['is_child']
    collaped_children_US_with_children = collaped_children_US_with_children.groupby('hidp').filter(lambda x : sum(x['is_adult']) > 0)


    # sanity check for number of child rows vs declared nkids
    actual_children = collaped_children_US_with_children.groupby(['hidp'])['is_child'].sum()
    declared_children = collaped_children_US_with_children.groupby(['hidp'])['nkids'].max()
    print(sum(np.abs(actual_children - declared_children))) # Sum absolute error. lower is better.

    # grab children
    # join ages into a string seperated by -
    final_US_with_children = collaped_children_US_with_children.sort_values(by=['hidp', 'age'], ascending =True)
    final_US_with_children['age'] = final_US_with_children['age'].astype(str)
    chained_ages = final_US_with_children.loc[final_US_with_children['is_child'] == True, ].groupby('hidp', as_index=True)['age'].apply('_'.join)
    chained_ages = pd.DataFrame(chained_ages)
    chained_ages.columns = ['child_ages']
    chained_ages['hidp'] = chained_ages.index
    chained_ages = chained_ages.reset_index()

    # merge chained child ages back onto adults in the dataframe. tidy up generated child rows and columns needed.
    print(chained_ages, final_US_with_children)
    collaped_children_US = pd.merge(final_US_with_children, chained_ages, how='left', on='hidp')
    collaped_children_US['child_ages'] = collaped_children_US['age_y'] # sort out two age columns from the merge.
    collaped_children_US['age'] = collaped_children_US['age_x']
    collaped_children_US.reset_index(inplace=True, drop=True)
    collaped_children_US = collaped_children_US.loc[collaped_children_US['is_adult'] == 1, ]
    collaped_children_US = collaped_children_US.drop(['age_x', 'age_y', 'is_adult', 'is_child'], axis=1)

    # save data
    #US_utils.save_file(collaped_children_US, "children_ages_US/", "", year)
    return collaped_children_US

if __name__ == '__main__':

    years = np.arange(2009, 2020)
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    main(data, years)