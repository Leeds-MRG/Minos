=============
Neighbourhood
=============


Neighbourhood
=============

Neighbourhood quality is an indicator of well-being suggested by the
SIPHER-7 XXXX ref and others?.

Methods
-------

.. figure:: ./figure/neighbourhood_barchart-1.png
   :alt: plot of chunk neighbourhood_barchart

   plot of chunk neighbourhood_barchart

Neighbourhood data are presented as a likert scale from 1-6 indicating
the number of harmful activities that happen in a persons neighbourhood
for individual health. These include robberies and vandalism with the
full encoding available in the data tables.

Data
----

What variables are included? Why is this output chosen. What explanatory
variables are used and why are they chosen

Results
-------

What are the results. Coefficients tables. diagnostic plots. measures of
goodness of fit.

.. figure:: ./figure/housing_output-1.png
   :alt: plot of chunk housing_output

   plot of chunk housing_output

::

   ## formula: 
   ## next_neighbourhood_safety ~ age + factor(sex) + factor(job_sec) + relevel(factor(ethnicity), ref = "WBI") + hh_income + factor(housing_quality) + relevel(factor(region), ref = "South East")
   ## data:    data
   ## 
   ##  link  threshold nobs     logLik AIC    niter max.grad cond.H 
   ##  logit flexible  86.54996 -86.52 245.04 5(0)  2.53e-12 1.9e+10
   ## 
   ## Coefficients:
   ##                                                                       Estimate Std. Error z value Pr(>|z|)
   ## age                                                                  1.580e-02  1.266e-02   1.248    0.212
   ## factor(sex)Male                                                      1.241e-01  4.232e-01   0.293    0.769
   ## factor(job_sec)2                                                    -1.706e-01  1.179e+00  -0.145    0.885
   ## factor(job_sec)3                                                    -1.016e-01  1.049e+00  -0.097    0.923
   ## factor(job_sec)4                                                    -2.637e-01  1.130e+00  -0.233    0.815
   ## factor(job_sec)5                                                     9.020e-02  1.154e+00   0.078    0.938
   ## factor(job_sec)6                                                    -3.180e-01  1.310e+00  -0.243    0.808
   ## factor(job_sec)7                                                    -2.333e-01  1.101e+00  -0.212    0.832
   ## factor(job_sec)8                                                    -2.819e-01  1.180e+00  -0.239    0.811
   ## relevel(factor(ethnicity), ref = "WBI")BAN                          -1.546e-01  3.543e+00  -0.044    0.965
   ## relevel(factor(ethnicity), ref = "WBI")BLA                           2.714e-01  2.208e+00   0.123    0.902
   ## relevel(factor(ethnicity), ref = "WBI")BLC                           1.910e-01  2.807e+00   0.068    0.946
   ## relevel(factor(ethnicity), ref = "WBI")CHI                           3.934e-01  3.010e+00   0.131    0.896
   ## relevel(factor(ethnicity), ref = "WBI")IND                           3.402e-02  1.521e+00   0.022    0.982
   ## relevel(factor(ethnicity), ref = "WBI")MIX                           1.447e-02  1.884e+00   0.008    0.994
   ## relevel(factor(ethnicity), ref = "WBI")OAS                           1.241e-01  2.093e+00   0.059    0.953
   ## relevel(factor(ethnicity), ref = "WBI")OBL                          -2.734e-01  8.015e+00  -0.034    0.973
   ## relevel(factor(ethnicity), ref = "WBI")OTH                           2.144e-01  3.452e+00   0.062    0.950
   ## relevel(factor(ethnicity), ref = "WBI")PAK                          -2.653e-01  1.947e+00  -0.136    0.892
   ## relevel(factor(ethnicity), ref = "WBI")WHO                           4.266e-02  1.001e+00   0.043    0.966
   ## hh_income                                                            1.805e-05  7.135e-05   0.253    0.800
   ## factor(housing_quality)2                                            -1.799e-01  4.393e-01  -0.410    0.682
   ## factor(housing_quality)3                                            -3.019e-01  8.725e-01  -0.346    0.729
   ## relevel(factor(region), ref = "South East")East Midlands            -6.778e-02  8.957e-01  -0.076    0.940
   ## relevel(factor(region), ref = "South East")East of England           2.812e-02  8.137e-01   0.035    0.972
   ## relevel(factor(region), ref = "South East")London                   -9.578e-01  8.313e-01  -1.152    0.249
   ## relevel(factor(region), ref = "South East")North East                3.711e-02  1.157e+00   0.032    0.974
   ## relevel(factor(region), ref = "South East")North West               -2.699e-01  7.952e-01  -0.339    0.734
   ## relevel(factor(region), ref = "South East")Northern Ireland          1.177e+00  1.617e+00   0.728    0.467
   ## relevel(factor(region), ref = "South East")Scotland                  2.446e-01  9.829e-01   0.249    0.803
   ## relevel(factor(region), ref = "South East")South West                3.499e-01  8.257e-01   0.424    0.672
   ## relevel(factor(region), ref = "South East")Wales                     3.385e-01  1.325e+00   0.256    0.798
   ## relevel(factor(region), ref = "South East")West Midlands            -2.749e-01  8.748e-01  -0.314    0.753
   ## relevel(factor(region), ref = "South East")Yorkshire and The Humber -1.631e-01  8.737e-01  -0.187    0.852
   ## 
   ## Threshold coefficients:
   ##     Estimate Std. Error z value
   ## 1|2   -0.461      1.311  -0.352
   ## 2|3    1.849      1.328   1.392
   ## (40 observations deleted due to missingness)

References
----------
