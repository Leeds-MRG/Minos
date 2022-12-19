==========
Loneliness
==========


Loneliness
==========

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
   ## y ~ factor(sex) + age + scale(SF_12) + factor(labour_state) + factor(job_sec) + relevel(factor(ethnicity), ref = "WBI") + scale(hh_income) + scale(alcohol_spending) + scale(ncigs)
   ## data:    data
   ## 
   ##  link  threshold nobs  logLik    AIC      niter max.grad cond.H 
   ##  logit flexible  20954 -15942.99 31955.97 6(0)  5.20e-09 2.1e+06
   ## 
   ## Coefficients:
   ##                                             Estimate Std. Error z value Pr(>|z|)    
   ## factor(sex)Male                            -0.294212   0.031895  -9.224  < 2e-16 ***
   ## age                                        -0.007143   0.001343  -5.317 1.05e-07 ***
   ## scale(SF_12)                               -0.820147   0.016403 -50.001  < 2e-16 ***
   ## factor(labour_state)Family Care            -0.190843   0.112725  -1.693  0.09046 .  
   ## factor(labour_state)Maternity Leave        -0.244461   0.183887  -1.329  0.18371    
   ## factor(labour_state)PT Employed             0.016507   0.052299   0.316  0.75228    
   ## factor(labour_state)Retired                -0.150188   0.095031  -1.580  0.11401    
   ## factor(labour_state)Self-employed           0.064390   0.085027   0.757  0.44888    
   ## factor(labour_state)Sick/Disabled           0.466449   0.113628   4.105 4.04e-05 ***
   ## factor(labour_state)Student                -0.056042   0.089504  -0.626  0.53122    
   ## factor(labour_state)Unemployed             -0.006102   0.110895  -0.055  0.95612    
   ## factor(job_sec)1                           -0.660150   0.124140  -5.318 1.05e-07 ***
   ## factor(job_sec)2                           -0.425380   0.102559  -4.148 3.36e-05 ***
   ## factor(job_sec)3                           -0.419313   0.086636  -4.840 1.30e-06 ***
   ## factor(job_sec)4                           -0.345326   0.093158  -3.707  0.00021 ***
   ## factor(job_sec)5                           -0.354301   0.119470  -2.966  0.00302 ** 
   ## factor(job_sec)6                           -0.266585   0.108189  -2.464  0.01374 *  
   ## factor(job_sec)7                           -0.146876   0.087454  -1.679  0.09306 .  
   ## factor(job_sec)8                           -0.186697   0.100598  -1.856  0.06347 .  
   ## relevel(factor(ethnicity), ref = "WBI")BAN  0.001875   0.118255   0.016  0.98735    
   ## relevel(factor(ethnicity), ref = "WBI")BLA  0.169172   0.119458   1.416  0.15673    
   ## relevel(factor(ethnicity), ref = "WBI")BLC  0.346748   0.113282   3.061  0.00221 ** 
   ## relevel(factor(ethnicity), ref = "WBI")CHI  0.056151   0.224360   0.250  0.80238    
   ## relevel(factor(ethnicity), ref = "WBI")IND  0.162074   0.078792   2.057  0.03969 *  
   ## relevel(factor(ethnicity), ref = "WBI")MIX  0.160012   0.104382   1.533  0.12529    
   ## relevel(factor(ethnicity), ref = "WBI")OAS  0.431569   0.137970   3.128  0.00176 ** 
   ## relevel(factor(ethnicity), ref = "WBI")OBL -0.209107   0.419575  -0.498  0.61822    
   ## relevel(factor(ethnicity), ref = "WBI")OTH  0.027826   0.250353   0.111  0.91150    
   ## relevel(factor(ethnicity), ref = "WBI")PAK -0.082421   0.092343  -0.893  0.37210    
   ## relevel(factor(ethnicity), ref = "WBI")WHO  0.029460   0.074714   0.394  0.69336    
   ## scale(hh_income)                           -0.064153   0.015739  -4.076 4.58e-05 ***
   ## scale(alcohol_spending)                    -0.045078   0.036883  -1.222  0.22163    
   ## scale(ncigs)                                0.094840   0.015290   6.203 5.55e-10 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##     Estimate Std. Error z value
   ## 1|2  -0.2100     0.1021  -2.057
   ## 2|3   2.1909     0.1042  21.028

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
