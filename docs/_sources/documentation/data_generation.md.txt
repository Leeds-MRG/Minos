# Data Generation
 This section reviews the data generation process of MINOS from raw 
 Understanding Society Stata files to final data used directly in MINOS 
 and transitions. 

## Raw Formatting

take raw stata files for US and make them more readable. change variable names from data codes e.g. 'jobstat\_dv' to 'labour\_state'. change integer code variables to strings. For example labour state provides integer values 1-9 that aren't readable. Labour state 'Employed' is better than labour state 3. Merges individual response (indresp) and household response (hhresp) datasets together. Need variables from both for analysis done simply using a left merge on household IDs.

## Missing Data Correction

there are a lot of missing data in US. Some of these data are missing deterministically. Individuals that are unemployed are registered as having a missing salary. Their salary is not missing and is technically 0. There are many logical operations like this to correct data that are not actually missing. US data also uses last observation carried forward formatting. Some attributes are only registered if they change values and are otherwise registered as missing. For example a persons ethnicity is  registered as they enter the dataset but is immutable and never updates. For future observations this value is incorrectly recorded as missing. The last observation carried forwards (LOCF) imputation algorithm is used to fill in these missing values using previous time values. Some variables are not immutable such as age and require more elaborate imputation. For age it is simply linear imputation but more complex methods can be used. 

## Composites

Some US variables are not useful in the MINOS framework. For one pathway we are particularly interested in changes to household disposable income. However US features different variables such as gross household income and council tax payments that are used to derive the desired household disposable income. These composite variables are derived in this step. 

## Complete Case

What observations are removed from complete case analysis.

The missing data correction stage above cannot remove all missing data. Some variables require complete columns with no missing values for MINOS to run. In this stage complete case missing correction is used to remove any individual observations from the data with missing values in a subset of critical columns. This is a fast but naive way of preparing a complete dataset for MINOS. 

## Replenishment

How is the replenishing population generated.