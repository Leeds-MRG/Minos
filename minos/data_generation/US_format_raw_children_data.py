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

    # format child data.
    attribute_columns = US_utils.wave_prefix(['hidp', 'age_dv'], year)
    child_data = child_data[attribute_columns]
    child_data.columns = ['hidp', 'age', 'n_parents']
    child_data['is_child'] = True
    child_data['is_adult'] = False
    child_data['time'] = year

    # assign adults from indresp data as adults. over 16s.
    #US_data = pd.read_csv(f"data/composite_US/{year}_US_cohort.csv")
    input_raw_data['is_child'] = False
    input_raw_data['is_adult'] = True
    #collaped_children_US_with_children = collaped_children_US.merge(child_data, 'inner', on='hidp')
    collapsed_children_US_with_children = pd.concat([input_raw_data, child_data])

    # removing orphans.
    # calculating number of adults per hidp.
    # if 0 adults in the house the children are orphans?
    #orphans = collapsed_children_US_with_children.groupby(['hidp']).filter(lambda x : sum(x['is_adult']) == 0)
    collapsed_children_US_with_children = collapsed_children_US_with_children.groupby('hidp').filter(lambda x : sum(x['is_adult']) > 0)


    # sanity check for number of child rows vs declared nkids
    actual_children = collapsed_children_US_with_children.groupby(['hidp'])['is_child'].sum()
    declared_children = collapsed_children_US_with_children.groupby(['hidp'])['nkids'].max()
    # print(sum(np.abs(actual_children - declared_children))) # Sum absolute error. lower is better.

    # grab children
    # join ages into a string seperated by -
    final_US_with_children = collapsed_children_US_with_children.sort_values(by=['hidp', 'age'], ascending =True)
    final_US_with_children['age'] = final_US_with_children['age'].astype(str)
    chained_ages = final_US_with_children.loc[final_US_with_children['is_child'] == True, ].groupby('hidp', as_index=False)['age'].apply('_'.join)

    # merge chained child ages back onto adults in the dataframe. tidy up generated child rows and columns needed.
    collapsed_children_US = pd.merge(final_US_with_children, chained_ages, how='left', on='hidp')
    collapsed_children_US['child_ages'] = collapsed_children_US['age_y'] # sort out two age columns from the merge.
    # people with na child values either have no children or their children aren't present in the child data for some reason.
    # set everyone with no children and NA child ages to custom missing value "childless".
    # some households have positive nkids but their children aren't in the child dataset so can't determine their ages. set to missing (-9)
    # maybe need to estimate ages from age bins instead for these.
    # maybe these are all newborns? theres three in one year though. may be triplets but unlikely.
    collapsed_children_US['child_ages'] = collapsed_children_US.groupby(['hidp'])['child_ages'].transform('first')
    collapsed_children_US['nkids'] = collapsed_children_US.groupby(['hidp'])['nkids'].transform('max')

    # households with nkids >0 but no children in the child dataset?? assign better error values.
    who_children_not_in_data = (collapsed_children_US['child_ages'].isna()) & (collapsed_children_US['nkids']>0.0)
    collapsed_children_US.loc[who_children_not_in_data, 'nkids'] *= 0# force children to 0 for these 20 or so wierd households with children not in the dataset. (newborns?)
    who_childless = (collapsed_children_US['child_ages'].isna()) & (collapsed_children_US['nkids']==0.0)
    collapsed_children_US.loc[who_childless, 'child_ages'] = "childless"# no children in household.

    collapsed_children_US['age'] = collapsed_children_US['age_x']
    collapsed_children_US.reset_index(inplace=True, drop=True)
    collapsed_children_US = collapsed_children_US.loc[collapsed_children_US['is_adult'] == 1, ]
    collapsed_children_US = collapsed_children_US.drop(['age_x', 'age_y', 'is_adult', 'is_child'], axis=1)

    # save data
    #US_utils.save_file(collaped_children_US, "children_ages_US/", "", year)
    return collapsed_children_US

if __name__ == '__main__':

    years = [2020]
    file_names = [f"data/raw_US/{item}_US_cohort.csv" for item in years]
    data = US_utils.load_multiple_data(file_names)
    main(data, 2020)