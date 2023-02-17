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

.. figure:: ./figure/housing_barchart-1.png
   :alt: plot of chunk housing_barchart

   plot of chunk housing_barchart

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

   ## formula: next_housing_quality ~ age + factor(sex) + SF_12 + relevel(factor(ethnicity), ref = "WBI") + hh_income
   ## data:    data
   ## 
   ##  link  threshold nobs     logLik AIC    niter max.grad cond.H 
   ##  logit flexible  103.1594 -97.99 229.99 5(0)  8.47e-07 9.2e+09
   ## 
   ## Coefficients:
   ##                                              Estimate Std. Error z value Pr(>|z|)  
   ## age                                         0.0082681  0.0113336   0.730   0.4657  
   ## factor(sex)Male                            -0.0938937  0.3845571  -0.244   0.8071  
   ## SF_12                                      -0.0136238  0.0202522  -0.673   0.5011  
   ## relevel(factor(ethnicity), ref = "WBI")BAN  1.0235392  2.6780803   0.382   0.7023  
   ## relevel(factor(ethnicity), ref = "WBI")BLA  1.3244641  1.6063660   0.825   0.4097  
   ## relevel(factor(ethnicity), ref = "WBI")BLC  0.6422992  2.4039794   0.267   0.7893  
   ## relevel(factor(ethnicity), ref = "WBI")CHI  1.3129964  2.8385130   0.463   0.6437  
   ## relevel(factor(ethnicity), ref = "WBI")IND  0.4518321  1.2442697   0.363   0.7165  
   ## relevel(factor(ethnicity), ref = "WBI")MIX  0.2691325  1.5009851   0.179   0.8577  
   ## relevel(factor(ethnicity), ref = "WBI")OAS  0.7642680  1.8362644   0.416   0.6773  
   ## relevel(factor(ethnicity), ref = "WBI")OBL  1.5285576  8.6893576   0.176   0.8604  
   ## relevel(factor(ethnicity), ref = "WBI")OTH  0.4339788  3.1233946   0.139   0.8895  
   ## relevel(factor(ethnicity), ref = "WBI")PAK  0.5250905  1.7236335   0.305   0.7606  
   ## relevel(factor(ethnicity), ref = "WBI")WHO  0.1788316  0.8328175   0.215   0.8300  
   ## hh_income                                  -0.0003135  0.0001778  -1.764   0.0778 .
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##     Estimate Std. Error z value
   ## 1|2   -1.325      1.042  -1.272
   ## 2|3    1.189      1.044   1.139
   ## (273 observations deleted due to missingness)

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
