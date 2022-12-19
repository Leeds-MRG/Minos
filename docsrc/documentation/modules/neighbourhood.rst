=============
Neighbourhood
=============


Neighbourhood
=============

Introductory fluff. Why do we need this module? test reference (Nelson
1987).

Methods
-------

What methods are used? Justification due to output data type.
explanation of model output.

Data
----

What variables are included? Why is this output chosen. What explanatory
variables are used and why are they chosen

Results
-------

What are the results. Coefficients tables. diagnostic plots. measures of
goodness of fit.

::

   ## formula: 
   ## y ~ factor(sex) + age + SF_12 + labour_state + factor(job_sec) + ethnicity + hh_income + factor(housing_quality) + region + factor(education_state)
   ## data:    data
   ## 
   ##  link  threshold nobs  logLik   AIC     niter max.grad cond.H 
   ##  logit flexible  23856 -2860.76 5825.52 8(0)  5.75e-07 2.7e+09
   ## 
   ## Coefficients:
   ##                                  Estimate Std. Error z value Pr(>|z|)    
   ## factor(sex)Male                -7.433e-03  8.726e-02  -0.085 0.932119    
   ## age                            -1.417e-02  3.997e-03  -3.546 0.000391 ***
   ## SF_12                           5.326e-03  1.896e-03   2.808 0.004981 ** 
   ## labour_stateFamily Care         1.084e-01  3.040e-01   0.357 0.721327    
   ## labour_stateMaternity Leave    -2.137e-01  5.962e-01  -0.359 0.719959    
   ## labour_statePT Employed        -1.660e-01  1.634e-01  -1.016 0.309575    
   ## labour_stateRetired             2.885e-01  2.793e-01   1.033 0.301558    
   ## labour_stateSelf-employed       7.228e-02  2.630e-01   0.275 0.783406    
   ## labour_stateSick/Disabled      -4.128e-01  2.984e-01  -1.383 0.166548    
   ## labour_stateStudent            -5.854e-01  2.744e-01  -2.134 0.032871 *  
   ## labour_stateUnemployed         -6.740e-02  2.974e-01  -0.227 0.820697    
   ## factor(job_sec)1                9.682e-01  4.197e-01   2.307 0.021064 *  
   ## factor(job_sec)2                7.176e-01  3.302e-01   2.173 0.029767 *  
   ## factor(job_sec)3                7.121e-01  2.686e-01   2.651 0.008014 ** 
   ## factor(job_sec)4                4.698e-01  2.869e-01   1.638 0.101513    
   ## factor(job_sec)5                3.924e-01  3.472e-01   1.130 0.258435    
   ## factor(job_sec)6                5.140e-01  3.317e-01   1.549 0.121266    
   ## factor(job_sec)7                6.130e-01  2.702e-01   2.268 0.023301 *  
   ## factor(job_sec)8                3.719e-01  2.931e-01   1.269 0.204446    
   ## ethnicityBLA                    6.616e-03  3.230e-01   0.020 0.983660    
   ## ethnicityBLC                   -1.223e-01  3.192e-01  -0.383 0.701695    
   ## ethnicityCHI                    3.686e-01  7.571e-01   0.487 0.626382    
   ## ethnicityIND                    6.230e-02  2.986e-01   0.209 0.834736    
   ## ethnicityMIX                   -4.516e-01  3.187e-01  -1.417 0.156475    
   ## ethnicityOAS                   -4.108e-01  3.426e-01  -1.199 0.230512    
   ## ethnicityOBL                   -8.174e-01  7.875e-01  -1.038 0.299336    
   ## ethnicityOTH                   -4.708e-01  5.723e-01  -0.823 0.410701    
   ## ethnicityPAK                    1.189e+00  4.270e-01   2.784 0.005365 ** 
   ## ethnicityWBI                   -5.071e-02  2.557e-01  -0.198 0.842780    
   ## ethnicityWHO                   -3.015e-01  3.012e-01  -1.001 0.316771    
   ## hh_income                       3.817e-05  3.492e-05   1.093 0.274322    
   ## factor(housing_quality)2        3.150e-01  1.854e-01   1.699 0.089294 .  
   ## factor(housing_quality)3        6.931e-01  2.015e-01   3.439 0.000584 ***
   ## regionEast of England          -4.332e-03  2.519e-01  -0.017 0.986282    
   ## regionLondon                   -1.134e+00  2.130e-01  -5.324 1.02e-07 ***
   ## regionNorth East               -4.285e-01  2.784e-01  -1.539 0.123771    
   ## regionNorth West               -6.880e-01  2.174e-01  -3.164 0.001554 ** 
   ## regionNorthern Ireland          1.404e+00  4.878e-01   2.878 0.004006 ** 
   ## regionScotland                 -1.432e-01  2.560e-01  -0.559 0.576023    
   ## regionSouth East               -6.845e-01  2.141e-01  -3.197 0.001389 ** 
   ## regionSouth West               -2.518e-01  2.412e-01  -1.044 0.296578    
   ## regionWales                    -2.918e-01  2.667e-01  -1.094 0.273899    
   ## regionWest Midlands            -6.104e-01  2.280e-01  -2.678 0.007416 ** 
   ## regionYorkshire and The Humber  3.864e-02  2.537e-01   0.152 0.878937    
   ## factor(education_state)1       -7.356e-02  2.486e-01  -0.296 0.767347    
   ## factor(education_state)2        1.133e-01  1.155e-01   0.981 0.326416    
   ## factor(education_state)3        1.441e-01  1.590e-01   0.907 0.364537    
   ## factor(education_state)5        1.252e-01  1.697e-01   0.738 0.460595    
   ## factor(education_state)6        5.090e-03  1.365e-01   0.037 0.970244    
   ## factor(education_state)7       -2.060e-03  1.608e-01  -0.013 0.989775    
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##     Estimate Std. Error z value
   ## 1|2  -6.8529     0.5014 -13.669
   ## 2|3  -3.7729     0.4686  -8.051

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
