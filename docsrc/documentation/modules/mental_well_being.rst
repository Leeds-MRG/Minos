Mental Well-Being
-----------------

Mental wellbeing is one of the key output of MINOS.

To measure mental wellbeing, we use the Short-Form 12 Mental Component
Score (SF-12 MCS). The Short-Form 12 survey is a survey consisting of 12
questions relating to both physical and mental health. `See
here <https://www.england.nhs.uk/wp-content/uploads/2022/12/Short-form-12-health-survey-questionnaire.pdf>`__
for a copy of the survey. Summary scores for both mental and physical
health can be calculated from the responses, leading to the Mental
Component Score (MCS). MCS is a measure ranging from 0 (low functioning)
to 100 (high functioning). SF-12 MCS is represented by a variable
directly from the survey -
```sf12mcs_dv`` <https://www.understandingsociety.ac.uk/documentation/mainstage/variables/sf12mcs_dv/>`__.
Each of the responses to the 12 questions are also available in the
survey.

.. code:: r

   continuous_density(obs)

.. figure:: ./figure/unnamed-chunk-1-1.png
   :alt: plot of chunk unnamed-chunk-1

   plot of chunk unnamed-chunk-1

Transition Model
~~~~~~~~~~~~~~~~

We use a Linear Mixed Model (LMM) from the
`lme4 <https://www.rdocumentation.org/packages/lme4/versions/1.1-36>`__
package in R.

Formula:

.. math::   SF\_12 \sim SF\_12\_last + age + sex + ethnicity + region + education\_state + hh\_income + \\housing\_quality + neighbourhood\_safety + loneliness + nutrition\_quality + ncigs + \\I(ncigs>0) + (1|pidp)  

.. code:: r

   print(summary(model))

::

   ## Linear mixed model fit by REML ['lmerMod']
   ## Formula: SF_12 ~ time + scale(SF_12_last) + scale(age) + factor(sex) +  
   ##     relevel(factor(ethnicity), ref = "WBI") + relevel(factor(region),  
   ##     ref = "Scotland") + relevel(factor(education_state), ref = "1") +  
   ##     scale(hh_income) + factor(housing_quality) + factor(neighbourhood_safety) +  
   ##     factor(loneliness) + scale(nutrition_quality) + scale(ncigs) +  
   ##     I(factor(ncigs > 0)) + (1 | pidp)
   ##    Data: data
   ## Weights: weight
   ## 
   ## REML criterion at convergence: Inf
   ## 
   ## Scaled residuals: 
   ##     Min      1Q  Median      3Q     Max 
   ## -56.385  -0.245   0.097   0.386  16.960 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance Std.Dev.
   ##  pidp     (Intercept) 0.007167 0.08466 
   ##  Residual             0.002422 0.04921 
   ## Number of obs: 53940, groups:  pidp, 28030
   ## 
   ## Fixed effects:
   ##                                                                     Estimate
   ## (Intercept)                                                        5.2397331
   ## time                                                              -0.0006733
   ## scale(SF_12_last)                                                  0.1144965
   ## scale(age)                                                         0.0214391
   ## factor(sex)Male                                                    0.0203990
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         0.0004421
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         0.0305918
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         0.0181985
   ## relevel(factor(ethnicity), ref = "WBI")CHI                         0.0163969
   ## relevel(factor(ethnicity), ref = "WBI")IND                         0.0002626
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        -0.0042839
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -0.0009285
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -0.0003878
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -0.0694297
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         0.0049871
   ## relevel(factor(ethnicity), ref = "WBI")WHO                         0.0154492
   ## relevel(factor(region), ref = "Scotland")East Midlands             0.0110873
   ## relevel(factor(region), ref = "Scotland")East of England           0.0049586
   ## relevel(factor(region), ref = "Scotland")London                    0.0004213
   ## relevel(factor(region), ref = "Scotland")North East               -0.0047024
   ## relevel(factor(region), ref = "Scotland")North West                0.0006363
   ## relevel(factor(region), ref = "Scotland")Northern Ireland         -0.0001035
   ## relevel(factor(region), ref = "Scotland")South East                0.0011843
   ## relevel(factor(region), ref = "Scotland")South West               -0.0026575
   ## relevel(factor(region), ref = "Scotland")Wales                    -0.0053164
   ## relevel(factor(region), ref = "Scotland")West Midlands            -0.0012968
   ## relevel(factor(region), ref = "Scotland")Yorkshire and The Humber  0.0008975
   ## relevel(factor(education_state), ref = "1")0                      -0.0083117
   ## relevel(factor(education_state), ref = "1")2                       0.0030260
   ## relevel(factor(education_state), ref = "1")3                      -0.0001873
   ## relevel(factor(education_state), ref = "1")5                       0.0095867
   ## relevel(factor(education_state), ref = "1")6                       0.0014439
   ## relevel(factor(education_state), ref = "1")7                      -0.0004484
   ## scale(hh_income)                                                   0.0058742
   ## factor(housing_quality)Low                                        -0.0328952
   ## factor(housing_quality)Medium                                     -0.0037926
   ## factor(neighbourhood_safety)2                                      0.0040650
   ## factor(neighbourhood_safety)3                                      0.0161708
   ## factor(loneliness)2                                               -0.0765887
   ## factor(loneliness)3                                               -0.2656038
   ## scale(nutrition_quality)                                           0.0092193
   ## scale(ncigs)                                                      -0.0062644
   ## I(factor(ncigs > 0))TRUE                                          -0.0138892
   ##                                                                   Std. Error
   ## (Intercept)                                                        0.8345248
   ## time                                                               0.0004138
   ## scale(SF_12_last)                                                  0.0011534
   ## scale(age)                                                         0.0012782
   ## factor(sex)Male                                                    0.0022973
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         0.0143677
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         0.0093296
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         0.0120887
   ## relevel(factor(ethnicity), ref = "WBI")CHI                         0.0171940
   ## relevel(factor(ethnicity), ref = "WBI")IND                         0.0071384
   ## relevel(factor(ethnicity), ref = "WBI")MIX                         0.0093127
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         0.0101948
   ## relevel(factor(ethnicity), ref = "WBI")OBL                         0.0326152
   ## relevel(factor(ethnicity), ref = "WBI")OTH                         0.0183040
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         0.0084321
   ## relevel(factor(ethnicity), ref = "WBI")WHO                         0.0056132
   ## relevel(factor(region), ref = "Scotland")East Midlands             0.0059159
   ## relevel(factor(region), ref = "Scotland")East of England           0.0055977
   ## relevel(factor(region), ref = "Scotland")London                    0.0057530
   ## relevel(factor(region), ref = "Scotland")North East                0.0070295
   ## relevel(factor(region), ref = "Scotland")North West                0.0055444
   ## relevel(factor(region), ref = "Scotland")Northern Ireland          0.0079633
   ## relevel(factor(region), ref = "Scotland")South East                0.0052579
   ## relevel(factor(region), ref = "Scotland")South West                0.0056919
   ## relevel(factor(region), ref = "Scotland")Wales                     0.0072406
   ## relevel(factor(region), ref = "Scotland")West Midlands             0.0057667
   ## relevel(factor(region), ref = "Scotland")Yorkshire and The Humber  0.0057567
   ## relevel(factor(education_state), ref = "1")0                       0.0085502
   ## relevel(factor(education_state), ref = "1")2                       0.0085258
   ## relevel(factor(education_state), ref = "1")3                       0.0089178
   ## relevel(factor(education_state), ref = "1")5                       0.0089951
   ## relevel(factor(education_state), ref = "1")6                       0.0086299
   ## relevel(factor(education_state), ref = "1")7                       0.0088233
   ## scale(hh_income)                                                   0.0011286
   ## factor(housing_quality)Low                                         0.0040623
   ## factor(housing_quality)Medium                                      0.0023982
   ## factor(neighbourhood_safety)2                                      0.0025375
   ## factor(neighbourhood_safety)3                                      0.0033714
   ## factor(loneliness)2                                                0.0025868
   ## factor(loneliness)3                                                0.0046211
   ## scale(nutrition_quality)                                           0.0011070
   ## scale(ncigs)                                                       0.0014932
   ## I(factor(ncigs > 0))TRUE                                           0.0049971
   ##                                                                   t value
   ## (Intercept)                                                         6.279
   ## time                                                               -1.627
   ## scale(SF_12_last)                                                  99.267
   ## scale(age)                                                         16.772
   ## factor(sex)Male                                                     8.879
   ## relevel(factor(ethnicity), ref = "WBI")BAN                          0.031
   ## relevel(factor(ethnicity), ref = "WBI")BLA                          3.279
   ## relevel(factor(ethnicity), ref = "WBI")BLC                          1.505
   ## relevel(factor(ethnicity), ref = "WBI")CHI                          0.954
   ## relevel(factor(ethnicity), ref = "WBI")IND                          0.037
   ## relevel(factor(ethnicity), ref = "WBI")MIX                         -0.460
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         -0.091
   ## relevel(factor(ethnicity), ref = "WBI")OBL                         -0.012
   ## relevel(factor(ethnicity), ref = "WBI")OTH                         -3.793
   ## relevel(factor(ethnicity), ref = "WBI")PAK                          0.591
   ## relevel(factor(ethnicity), ref = "WBI")WHO                          2.752
   ## relevel(factor(region), ref = "Scotland")East Midlands              1.874
   ## relevel(factor(region), ref = "Scotland")East of England            0.886
   ## relevel(factor(region), ref = "Scotland")London                     0.073
   ## relevel(factor(region), ref = "Scotland")North East                -0.669
   ## relevel(factor(region), ref = "Scotland")North West                 0.115
   ## relevel(factor(region), ref = "Scotland")Northern Ireland          -0.013
   ## relevel(factor(region), ref = "Scotland")South East                 0.225
   ## relevel(factor(region), ref = "Scotland")South West                -0.467
   ## relevel(factor(region), ref = "Scotland")Wales                     -0.734
   ## relevel(factor(region), ref = "Scotland")West Midlands             -0.225
   ## relevel(factor(region), ref = "Scotland")Yorkshire and The Humber   0.156
   ## relevel(factor(education_state), ref = "1")0                       -0.972
   ## relevel(factor(education_state), ref = "1")2                        0.355
   ## relevel(factor(education_state), ref = "1")3                       -0.021
   ## relevel(factor(education_state), ref = "1")5                        1.066
   ## relevel(factor(education_state), ref = "1")6                        0.167
   ## relevel(factor(education_state), ref = "1")7                       -0.051
   ## scale(hh_income)                                                    5.205
   ## factor(housing_quality)Low                                         -8.098
   ## factor(housing_quality)Medium                                      -1.581
   ## factor(neighbourhood_safety)2                                       1.602
   ## factor(neighbourhood_safety)3                                       4.796
   ## factor(loneliness)2                                               -29.607
   ## factor(loneliness)3                                               -57.477
   ## scale(nutrition_quality)                                            8.328
   ## scale(ncigs)                                                       -4.195
   ## I(factor(ncigs > 0))TRUE                                           -2.779

::

   ## 
   ## Correlation matrix not shown by default, as p = 43 > 12.
   ## Use print(summary(model), correlation=TRUE)  or
   ##     vcov(summary(model))        if you need it

::

   ## optimizer (nloptwrap) convergence code: 0 (OK)
   ## Gradient contains NAs

Results
~~~~~~~

|plot of chunk SF12_Output|\ |image1|

References
~~~~~~~~~~

.. |plot of chunk SF12_Output| image:: ./figure/SF12_Output-1.png
.. |image1| image:: ./figure/SF12_Output-2.png
