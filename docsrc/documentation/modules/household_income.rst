================
Household Income
================


Household Income
================

Number of cigarettes consumed is an indicator of XXXX. test reference
(Nelson 1987).

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

   ## 
   ## Call:
   ## lm(formula = formula, data = data, weights = weight)
   ## 
   ## Weighted Residuals:
   ##        Min         1Q     Median         3Q        Max 
   ## -3.207e-09 -6.000e-12  0.000e+00  5.000e-12  3.826e-08 
   ## 
   ## Coefficients:
   ##                                          Estimate Std. Error    t value Pr(>|t|)    
   ## (Intercept)                             1.741e+03  7.812e-13  2.229e+15  < 2e-16 ***
   ## age                                     2.337e-15  4.108e-15  5.690e-01 0.569431    
   ## sexMale                                -1.471e-13  9.698e-14 -1.516e+00 0.129453    
   ## factor(ethnicity)BLA                    3.484e-13  7.222e-13  4.820e-01 0.629539    
   ## factor(ethnicity)BLC                   -1.530e-13  8.118e-13 -1.880e-01 0.850538    
   ## factor(ethnicity)CHI                   -4.459e-12  9.694e-13 -4.600e+00 4.25e-06 ***
   ## factor(ethnicity)IND                   -2.099e-12  6.789e-13 -3.092e+00 0.001994 ** 
   ## factor(ethnicity)MIX                   -2.890e-12  7.146e-13 -4.045e+00 5.26e-05 ***
   ## factor(ethnicity)OAS                   -1.745e-12  7.382e-13 -2.364e+00 0.018074 *  
   ## factor(ethnicity)OBL                   -2.635e-12  1.820e-12 -1.448e+00 0.147658    
   ## factor(ethnicity)OTH                   -1.953e-12  9.517e-13 -2.052e+00 0.040191 *  
   ## factor(ethnicity)PAK                   -1.785e-12  7.207e-13 -2.476e+00 0.013291 *  
   ## factor(ethnicity)WBI                   -4.003e-12  6.232e-13 -6.423e+00 1.37e-10 ***
   ## factor(ethnicity)WHO                   -2.771e-12  6.476e-13 -4.279e+00 1.89e-05 ***
   ## factor(region)East of England          -7.541e-13  2.154e-13 -3.501e+00 0.000465 ***
   ## factor(region)London                   -5.552e-12  2.139e-13 -2.596e+01  < 2e-16 ***
   ## factor(region)North East               -4.288e-13  2.686e-13 -1.596e+00 0.110396    
   ## factor(region)North West                3.935e-13  2.142e-13  1.838e+00 0.066124 .  
   ## factor(region)Northern Ireland          5.561e-13  3.284e-13  1.693e+00 0.090397 .  
   ## factor(region)Scotland                  3.801e-14  2.387e-13  1.590e-01 0.873463    
   ## factor(region)South East                1.689e-13  2.029e-13  8.320e-01 0.405295    
   ## factor(region)South West                6.343e-13  2.215e-13  2.864e+00 0.004189 ** 
   ## factor(region)Wales                     1.036e-12  2.816e-13  3.679e+00 0.000235 ***
   ## factor(region)West Midlands            -1.594e-13  2.234e-13 -7.130e-01 0.475550    
   ## factor(region)Yorkshire and The Humber -1.869e-14  2.236e-13 -8.400e-02 0.933373    
   ## scale(hh_income)                        1.675e+03  4.847e-14  3.457e+16  < 2e-16 ***
   ## factor(job_sec)1                       -1.465e-14  3.796e-13 -3.900e-02 0.969220    
   ## factor(job_sec)2                        2.151e-13  3.253e-13  6.610e-01 0.508407    
   ## factor(job_sec)3                        1.339e-13  2.774e-13  4.830e-01 0.629415    
   ## factor(job_sec)4                       -4.639e-14  2.972e-13 -1.560e-01 0.875966    
   ## factor(job_sec)5                       -1.881e-14  3.673e-13 -5.100e-02 0.959157    
   ## factor(job_sec)6                       -6.146e-14  3.371e-13 -1.820e-01 0.855327    
   ## factor(job_sec)7                       -3.186e-14  2.793e-13 -1.140e-01 0.909201    
   ## factor(job_sec)8                       -3.572e-14  3.147e-13 -1.140e-01 0.909631    
   ## factor(labour_state)Family Care        -1.087e-13  3.653e-13 -2.970e-01 0.766110    
   ## factor(labour_state)Maternity Leave    -4.179e-14  5.611e-13 -7.400e-02 0.940642    
   ## factor(labour_state)PT Employed        -1.033e-13  1.676e-13 -6.160e-01 0.537670    
   ## factor(labour_state)Retired            -1.651e-13  3.041e-13 -5.430e-01 0.587239    
   ## factor(labour_state)Self-employed      -7.441e-14  2.613e-13 -2.850e-01 0.775801    
   ## factor(labour_state)Sick/Disabled      -9.805e-14  3.556e-13 -2.760e-01 0.782725    
   ## factor(labour_state)Student            -2.255e-16  2.847e-13 -1.000e-03 0.999368    
   ## factor(labour_state)Unemployed         -1.075e-13  3.482e-13 -3.090e-01 0.757469    
   ## factor(education_state)1               -4.065e-14  3.673e-13 -1.110e-01 0.911895    
   ## factor(education_state)2                1.202e-14  1.310e-13  9.200e-02 0.926893    
   ## factor(education_state)3                3.323e-14  1.734e-13  1.920e-01 0.848065    
   ## factor(education_state)5                4.256e-13  1.873e-13  2.273e+00 0.023039 *  
   ## factor(education_state)6                4.860e-14  1.477e-13  3.290e-01 0.742176    
   ## factor(education_state)7               -6.484e-14  1.724e-13 -3.760e-01 0.706836    
   ## scale(SF_12)                           -6.972e-15  6.135e-14 -1.140e-01 0.909526    
   ## factor(housing_quality)2               -9.881e-14  3.128e-13 -3.160e-01 0.752101    
   ## factor(housing_quality)3                4.112e-14  3.190e-13  1.290e-01 0.897443    
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Residual standard error: 3.034e-10 on 17112 degrees of freedom
   ##   (254 observations deleted due to missingness)
   ## Multiple R-squared:      1,  Adjusted R-squared:      1 
   ## F-statistic: 2.612e+31 on 50 and 17112 DF,  p-value: < 2.2e-16

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
