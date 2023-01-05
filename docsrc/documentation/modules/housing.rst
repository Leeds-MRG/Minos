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
   ##   564 17192  9667

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

   ## formula: housing_quality_next ~ sex + age + SF_12 + labour_state + ethnicity + hh_income
   ## data:    data
   ## 
   ##  link  threshold nobs     logLik       AIC         niter max.grad cond.H 
   ##  logit flexible  44407783 -38244069.49 76488188.98 8(0)  1.67e-07 1.1e+10
   ## 
   ## Coefficients:
   ##                               Estimate Std. Error z value Pr(>|z|)    
   ## sexMale                      5.890e-02  6.303e-04   93.44   <2e-16 ***
   ## age                         -9.076e-03  2.681e-05 -338.55   <2e-16 ***
   ## SF_12                        9.582e-03  2.503e-05  382.87   <2e-16 ***
   ## labour_stateFamily Care     -1.498e-01  1.796e-03  -83.43   <2e-16 ***
   ## labour_stateMaternity Leave  6.194e-01  3.631e-03  170.60   <2e-16 ***
   ## labour_statePT Employed      1.200e-01  1.073e-03  111.75   <2e-16 ***
   ## labour_stateRetired         -1.007e-01  1.139e-03  -88.39   <2e-16 ***
   ## labour_stateSelf-employed    9.279e-02  1.184e-03   78.38   <2e-16 ***
   ## labour_stateSick/Disabled   -5.547e-01  1.770e-03 -313.45   <2e-16 ***
   ## labour_stateStudent          1.122e-01  1.431e-03   78.44   <2e-16 ***
   ## labour_stateUnemployed      -5.421e-01  1.688e-03 -321.23   <2e-16 ***
   ## ethnicityBLA                 1.363e-01  4.727e-03   28.83   <2e-16 ***
   ## ethnicityBLC                 2.358e-01  5.388e-03   43.76   <2e-16 ***
   ## ethnicityCHI                 3.380e-01  6.198e-03   54.53   <2e-16 ***
   ## ethnicityIND                 8.453e-01  4.430e-03  190.81   <2e-16 ***
   ## ethnicityMIX                 1.021e+00  4.645e-03  219.84   <2e-16 ***
   ## ethnicityOAS                 1.783e-01  4.879e-03   36.54   <2e-16 ***
   ## ethnicityOBL                 1.277e-01  1.224e-02   10.43   <2e-16 ***
   ## ethnicityOTH                 1.082e+00  6.274e-03  172.47   <2e-16 ***
   ## ethnicityPAK                 4.655e-01  4.689e-03   99.28   <2e-16 ***
   ## ethnicityWBI                 1.318e+00  4.029e-03  327.08   <2e-16 ***
   ## ethnicityWHO                 1.127e+00  4.192e-03  268.89   <2e-16 ***
   ## hh_income                    3.039e-04  2.880e-07 1055.25   <2e-16 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##      Estimate Std. Error z value
   ## 1|2 -0.748224   0.004272  -175.1
   ## 2|3  2.439665   0.004293   568.3

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
