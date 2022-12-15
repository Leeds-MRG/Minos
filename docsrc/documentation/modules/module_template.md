

# Module Template
DO NOT OVERWRITE THIS FILE. IF WRITING NEW DOCUMENTATION COPY ME FIRST.

This file provides a template structure of MINOS module documentation.
A recommended structure is given looking at the outcome variables used,
justification and definition of explanatory variates, definition of methods used,
and coefficients.

## Data

Describing the data used in a transition model. 
What outcome variables will be used? What data type are they? What is their range?
Are there any odd shaped distributions such as zero-inflated or polymodal?
What explanatory variates are going to be used. Again similar data description is helpful.
Justification of why all variables are used in terms of how the outcome influences SF12 and how explanatory
variates influence the outcome. Any data sources should be defined here. 

## Methods

What methods are used to create the transition model. This is usually pretty brief. 
Pre-established methods such as logistic regression are usually used.
Describe any model assumptions and requirements.
Any software packages in R. or otherwise should be stated here.
Any visualisation and post-hoc model goodness of fit tests should be defined here.
Expected model results can be defined here. Should a variable have a certain coefficient?
Should this model perform better versus something else?

## Coefficients

Any model coefficients are displayed here in tables.
Easiest way to do this is to create tex tables using texreg directly in R. 
These tex tables can be converted to Markdown and then imported directly.
Don't make your own tables if you value your time whatsoever. 
Worth investigating htmlreg in R and if these html tables can be imported directly into sphinx. Probably.