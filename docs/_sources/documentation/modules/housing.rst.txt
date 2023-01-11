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

::

   ## 
   ##     1     2     3 
   ##   549 17066  9622

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

   ## formula: 
   ## housing_quality_next ~ factor(sex) + scale(age) + scale(SF_12) + factor(labour_state) + factor(ethnicity) + scale(hh_income)
   ## data:    data
   ## 
   ##  link  threshold nobs     logLik       AIC         niter max.grad cond.H 
   ##  logit flexible  44193278 -38114733.98 76229517.96 6(0)  1.15e-07 5.1e+03
   ## 
   ## Coefficients:
   ##                                       Estimate Std. Error z value Pr(>|z|)    
   ## factor(sex)Male                      0.0558236  0.0006313   88.42   <2e-16 ***
   ## scale(age)                          -0.1628516  0.0004907 -331.90   <2e-16 ***
   ## scale(SF_12)                         0.1508474  0.0004022  375.03   <2e-16 ***
   ## factor(labour_state)Family Care     -0.1570490  0.0018192  -86.33   <2e-16 ***
   ## factor(labour_state)Maternity Leave  0.6073570  0.0036212  167.72   <2e-16 ***
   ## factor(labour_state)PT Employed      0.1167170  0.0010727  108.81   <2e-16 ***
   ## factor(labour_state)Retired         -0.1090539  0.0011417  -95.52   <2e-16 ***
   ## factor(labour_state)Self-employed    0.0856879  0.0011851   72.31   <2e-16 ***
   ## factor(labour_state)Sick/Disabled   -0.5583446  0.0017725 -315.00   <2e-16 ***
   ## factor(labour_state)Student          0.1225262  0.0014395   85.11   <2e-16 ***
   ## factor(labour_state)Unemployed      -0.5506065  0.0017037 -323.18   <2e-16 ***
   ## factor(ethnicity)BLA                 0.1448945  0.0047652   30.41   <2e-16 ***
   ## factor(ethnicity)BLC                 0.2591639  0.0054113   47.89   <2e-16 ***
   ## factor(ethnicity)CHI                 0.3644415  0.0062071   58.71   <2e-16 ***
   ## factor(ethnicity)IND                 0.8851952  0.0044509  198.88   <2e-16 ***
   ## factor(ethnicity)MIX                 1.0575175  0.0046746  226.22   <2e-16 ***
   ## factor(ethnicity)OAS                 0.2031260  0.0048923   41.52   <2e-16 ***
   ## factor(ethnicity)OBL                 0.1965951  0.0129046   15.23   <2e-16 ***
   ## factor(ethnicity)OTH                 1.1101132  0.0063123  175.87   <2e-16 ***
   ## factor(ethnicity)PAK                 0.5495317  0.0047129  116.60   <2e-16 ***
   ## factor(ethnicity)WBI                 1.3434706  0.0040522  331.54   <2e-16 ***
   ## factor(ethnicity)WHO                 1.1678576  0.0042176  276.90   <2e-16 ***
   ## scale(hh_income)                     0.4693541  0.0004462 1051.91   <2e-16 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##      Estimate Std. Error z value
   ## 1|2 -1.231036   0.004078  -301.9
   ## 2|3  1.946753   0.004091   475.9

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
