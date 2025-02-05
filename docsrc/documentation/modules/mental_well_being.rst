Mental Well-Being
-----------------

Introduction.
~~~~~~~~~~~~~

Prediction of future Short Form 12 Mental Component Score (SF-12 MCS).

Methods
~~~~~~~

What methods are used? Justification due to output data type.
explanation of model output.

Data
~~~~

What variables are included? Why is this output chosen. What explanatory
variables are used and why are they chosen

Results
~~~~~~~

What are the results. Coefficients tables. diagnostic plots. measures of
goodness of fit.

.. figure:: ./figure/SF12_Output-1.png
   :alt: plot of chunk SF12_Output

   plot of chunk SF12_Output

::

   ## Linear mixed model fit by REML ['lmerMod']
   ## Formula: SF_12 ~ time + scale(SF_12_last) + scale(age) + factor(sex) +  
   ##     relevel(factor(ethnicity), ref = "WBI") + relevel(factor(region),  
   ##     ref = "Scotland") + relevel(factor(education_state), ref = "1") +  
   ##     scale(hh_income) + factor(housing_quality) + factor(neighbourhood_safety) +  
   ##     factor(loneliness) + scale(nutrition_quality) + scale(ncigs) +      I(factor(ncigs > 0)) + (1 | pidp)
   ##    Data: data
   ## Weights: weight
   ## 
   ## REML criterion at convergence: Inf
   ## 
   ## Scaled residuals: 
   ##     Min      1Q  Median      3Q     Max 
   ## -53.126  -0.250   0.106   0.408   7.420 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance  Std.Dev.
   ##  pidp     (Intercept) 0.0013139 0.03625 
   ##  Residual             0.0004477 0.02116 
   ## Number of obs: 60762, groups:  pidp, 30674
   ## 
   ## Fixed effects:
   ##                                                                     Estimate Std. Error t value
   ## (Intercept)                                                        3.746e+00  8.181e-01   4.579
   ## time                                                               6.504e-05  4.058e-04   0.160
   ## scale(SF_12_last)                                                  1.208e-01  1.064e-03 113.520
   ## scale(age)                                                         2.105e-02  1.116e-03  18.867
   ## factor(sex)Male                                                    1.934e-02  2.009e-03   9.628
   ## relevel(factor(ethnicity), ref = "WBI")BAN                        -6.375e-03  1.342e-02  -0.475
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         2.864e-02  8.322e-03   3.441
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         1.821e-02  1.117e-02   1.630
   ## relevel(factor(ethnicity), ref = "WBI")CHI                         1.718e-02  1.415e-02   1.215
   ## relevel(factor(ethnicity), ref = "WBI")IND                         5.724e-03  6.388e-03   0.896
   ## relevel(factor(ethnicity), ref = "WBI")MIX                         1.531e-03  8.282e-03   0.185
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -9.973e-03  8.981e-03  -1.110
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -4.316e-04  2.922e-02  -0.015
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -2.879e-02  1.446e-02  -1.991
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         8.164e-03  7.769e-03   1.051
   ## relevel(factor(ethnicity), ref = "WBI")WHO                         1.432e-02  4.686e-03   3.057
   ## relevel(factor(region), ref = "Scotland")East Midlands             9.789e-03  5.069e-03   1.931
   ## relevel(factor(region), ref = "Scotland")East of England           5.390e-03  4.781e-03   1.128
   ## relevel(factor(region), ref = "Scotland")London                   -3.812e-03  4.838e-03  -0.788
   ## relevel(factor(region), ref = "Scotland")North East               -4.736e-03  5.997e-03  -0.790
   ## relevel(factor(region), ref = "Scotland")North West                2.759e-03  4.687e-03   0.589
   ## relevel(factor(region), ref = "Scotland")South East                4.251e-04  4.465e-03   0.095
   ## relevel(factor(region), ref = "Scotland")South West               -3.047e-03  4.901e-03  -0.622
   ## relevel(factor(region), ref = "Scotland")Wales                    -4.485e-03  6.160e-03  -0.728
   ## relevel(factor(region), ref = "Scotland")West Midlands            -3.852e-03  4.927e-03  -0.782
   ## relevel(factor(region), ref = "Scotland")Yorkshire and The Humber  1.550e-03  4.887e-03   0.317
   ## relevel(factor(education_state), ref = "1")0                      -6.917e-04  7.484e-03  -0.092
   ## relevel(factor(education_state), ref = "1")2                       5.044e-03  7.504e-03   0.672
   ## relevel(factor(education_state), ref = "1")3                      -1.346e-03  7.854e-03  -0.171
   ## relevel(factor(education_state), ref = "1")5                       8.275e-03  7.913e-03   1.046
   ## relevel(factor(education_state), ref = "1")6                       3.654e-03  7.591e-03   0.481
   ## relevel(factor(education_state), ref = "1")7                       2.992e-03  7.752e-03   0.386
   ## scale(hh_income)                                                   7.890e-03  1.026e-03   7.687
   ## factor(housing_quality)Low                                        -7.020e-03  3.040e-03  -2.309
   ## factor(housing_quality)Medium                                      5.693e-03  3.604e-03   1.580
   ## factor(neighbourhood_safety)2                                      4.983e-03  2.360e-03   2.111
   ## factor(neighbourhood_safety)3                                      1.132e-02  3.155e-03   3.587
   ## factor(loneliness)2                                               -7.890e-02  2.342e-03 -33.686
   ## factor(loneliness)3                                               -2.546e-01  4.101e-03 -62.071
   ## scale(nutrition_quality)                                           7.079e-03  1.005e-03   7.046
   ## scale(ncigs)                                                      -5.924e-03  1.458e-03  -4.064
   ## I(factor(ncigs > 0))TRUE                                          -1.461e-02  4.525e-03  -3.228

::

   ## 
   ## Correlation matrix not shown by default, as p = 42 > 12.
   ## Use print(summary(model), correlation=TRUE)  or
   ##     vcov(summary(model))        if you need it

::

   ## optimizer (nloptwrap) convergence code: 0 (OK)
   ## Gradient contains NAs

.. figure:: ./figure/SF12_Output-2.png
   :alt: plot of chunk SF12_Output

   plot of chunk SF12_Output

References
~~~~~~~~~~
