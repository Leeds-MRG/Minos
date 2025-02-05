Housing Quality
---------------

Housing Quality is one of the pathways outlined by the SIPHER consortium
that mediates the impact of changes in household disposable income on
mental wellbeing.

.. figure:: ./figure/housing_barchart-1.png
   :alt: plot of chunk housing_barchart

   plot of chunk housing_barchart

Transition Model
~~~~~~~~~~~~~~~~

We use a Random Forest Ordinal model from the
`ranger <https://www.rdocumentation.org/packages/ranger/versions/0.16.0>`__
package in R to estimate transitions for this variable.

Formula:

.. math::   housing\_quality \sim housing\_quality\_last + age + sex + ethnicity + region + education\_state + neighbourhood\_safety + loneliness + nutrition\_quality + ncigs + hh\_income + housing\_tenure + behind\_on\_bills + financial\_situation  

-  age: Age at time of interview.
-  sex: Individual’s biological sex.
-  ethnicity: Discrete string values White British, Black African, etc.
-  region: Administrative region of the UK. Discrete strings such as
   London, North-East.
-  education_state: Highest attained qualification. Ordinal values based
   on UK government education tiers
-  neighbourhood_safety: Ordinal values based on frequency of 6 factors
   related to safety
-  loneliness: Ordinal variable for frequency of feeling lonely.
   Often/Sometimes/Never
-  nutrition_quality: Household nutrition quality. Continuous variable
   proxied by frequency of consumption of fruit and vegetables.
-  ncigs: Tobacco consumption. Count of cigarettes smoked per week.
-  hh_income: Household Income. Continuous, equivalised household
   disposable income.
-  housing_tenure: Housing Tenure. Ordinal variable for tenure type
   e.g. Owned outright, Local authority rent
-  behind_on_bills: Subjective feeling of struggling to pay bills.
-  financial_situation: Ordinal variable for current subjective
   financial situation.
-  SF_12: Mental well-being. Continuous score indicating overall
   mental-wellbeing.

Results
~~~~~~~

What are the results. Coefficients tables. diagnostic plots. measures of
goodness of fit.

.. figure:: ./figure/housing_output-1.png
   :alt: plot of chunk housing_output

   plot of chunk housing_output

::

   ##                           Length Class         Mode     
   ## predictions               57678  -none-        numeric  
   ## num.trees                     1  -none-        numeric  
   ## num.independent.variables     1  -none-        numeric  
   ## mtry                          1  -none-        numeric  
   ## min.node.size                 1  -none-        numeric  
   ## variable.importance          14  -none-        numeric  
   ## prediction.error              1  -none-        numeric  
   ## forest                       11  ranger.forest list     
   ## splitrule                     1  -none-        character
   ## treetype                      1  -none-        character
   ## call                          7  -none-        call     
   ## importance.mode               1  -none-        character
   ## num.samples                   1  -none-        numeric  
   ## replace                       1  -none-        logical

References
~~~~~~~~~~
