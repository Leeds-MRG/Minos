=======
Housing
=======


Housing Quality
===============

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

   ## formula: 
   ## y ~ factor(sex) + age + scale(SF_12) + factor(labour_state) + factor(job_sec) + factor(ethnicity) + scale(hh_income)
   ## data:    data
   ## 
   ##  link  threshold nobs     logLik       AIC         niter max.grad cond.H 
   ##  logit flexible  44418361 -37829212.83 75658491.67 8(20) 5.79e-06 7.1e+06
   ## 
   ## Coefficients:
   ##                                       Estimate Std. Error  z value Pr(>|z|)    
   ## factor(sex)Male                      6.692e-02  6.406e-04  104.465  < 2e-16 ***
   ## age                                 -9.855e-03  2.694e-05 -365.888  < 2e-16 ***
   ## scale(SF_12)                         1.337e-01  4.034e-04  331.468  < 2e-16 ***
   ## factor(labour_state)Family Care      1.035e-01  2.422e-03   42.724  < 2e-16 ***
   ## factor(labour_state)Maternity Leave  5.096e-01  3.601e-03  141.513  < 2e-16 ***
   ## factor(labour_state)PT Employed      2.135e-01  1.099e-03  194.394  < 2e-16 ***
   ## factor(labour_state)Retired          1.837e-01  2.006e-03   91.591  < 2e-16 ***
   ## factor(labour_state)Self-employed   -2.334e-03  1.748e-03   -1.335   0.1817    
   ## factor(labour_state)Sick/Disabled   -3.151e-01  2.366e-03 -133.210  < 2e-16 ***
   ## factor(labour_state)Student          3.096e-01  1.848e-03  167.517  < 2e-16 ***
   ## factor(labour_state)Unemployed      -2.878e-01  2.321e-03 -123.975  < 2e-16 ***
   ## factor(job_sec)1                     8.975e-01  2.526e-03  355.291  < 2e-16 ***
   ## factor(job_sec)2                     4.736e-01  2.117e-03  223.729  < 2e-16 ***
   ## factor(job_sec)3                     3.719e-01  1.812e-03  205.226  < 2e-16 ***
   ## factor(job_sec)4                     2.124e-01  1.947e-03  109.089  < 2e-16 ***
   ## factor(job_sec)5                     3.651e-01  2.438e-03  149.720  < 2e-16 ***
   ## factor(job_sec)6                     3.290e-01  2.201e-03  149.477  < 2e-16 ***
   ## factor(job_sec)7                     9.978e-02  1.834e-03   54.405  < 2e-16 ***
   ## factor(job_sec)8                    -2.184e-01  2.079e-03 -105.054  < 2e-16 ***
   ## factor(ethnicity)BLA                 1.923e-02  4.811e-03    3.997 6.41e-05 ***
   ## factor(ethnicity)BLC                 1.231e-01  5.461e-03   22.540  < 2e-16 ***
   ## factor(ethnicity)CHI                 1.840e-01  6.452e-03   28.516  < 2e-16 ***
   ## factor(ethnicity)IND                 7.111e-01  4.520e-03  157.306  < 2e-16 ***
   ## factor(ethnicity)MIX                 9.313e-01  4.732e-03  196.791  < 2e-16 ***
   ## factor(ethnicity)OAS                 6.606e-02  4.968e-03   13.298  < 2e-16 ***
   ## factor(ethnicity)OBL                 3.091e-02  1.227e-02    2.519   0.0118 *  
   ## factor(ethnicity)OTH                 7.924e-01  6.266e-03  126.458  < 2e-16 ***
   ## factor(ethnicity)PAK                 3.205e-01  4.789e-03   66.936  < 2e-16 ***
   ## factor(ethnicity)WBI                 1.231e+00  4.119e-03  298.918  < 2e-16 ***
   ## factor(ethnicity)WHO                 1.069e+00  4.281e-03  249.844  < 2e-16 ***
   ## scale(hh_income)                     4.348e-01  4.448e-04  977.551  < 2e-16 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##      Estimate Std. Error z value
   ## 1|2 -1.612189   0.004557  -353.8
   ## 2|3  1.629395   0.004560   357.3

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
