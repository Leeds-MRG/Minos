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

.. code:: r

   discrete_barplot("loneliness")

.. figure:: ./figure/loneliness_data-1.png
   :alt: plot of chunk loneliness_data

   plot of chunk loneliness_data

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

   ## formula: loneliness_next ~ sex + age + SF_12 + labour_state + ethnicity + hh_income + alcohol_spending + ncigs
   ## data:    data
   ## 
   ##  link  threshold nobs  logLik   AIC      niter max.grad cond.H 
   ##  logit flexible  11783 -8923.25 17900.50 6(0)  4.40e-10 5.5e+09
   ## 
   ## Coefficients:
   ##                               Estimate Std. Error z value Pr(>|z|)    
   ## sexMale                     -2.697e-01  4.232e-02  -6.373 1.85e-10 ***
   ## age                         -7.553e-03  1.660e-03  -4.550 5.37e-06 ***
   ## SF_12                       -7.867e-02  2.113e-03 -37.230  < 2e-16 ***
   ## labour_stateFamily Care      5.510e-01  5.467e-01   1.008 0.313520    
   ## labour_stateMaternity Leave -2.198e-01  1.969e-01  -1.116 0.264236    
   ## labour_statePT Employed      9.390e-02  5.471e-02   1.716 0.086116 .  
   ## labour_stateRetired         -2.204e-01  2.365e-01  -0.932 0.351325    
   ## labour_stateSelf-employed    2.228e-02  6.223e-02   0.358 0.720305    
   ## labour_stateSick/Disabled   -1.658e-01  3.757e-01  -0.441 0.659011    
   ## labour_stateStudent          1.625e-01  1.184e-01   1.372 0.169918    
   ## labour_stateUnemployed      -6.677e-01  4.732e-01  -1.411 0.158225    
   ## ethnicityBLA                 2.511e-01  2.115e-01   1.187 0.235048    
   ## ethnicityBLC                 3.825e-01  2.107e-01   1.815 0.069451 .  
   ## ethnicityCHI                -1.732e-01  2.976e-01  -0.582 0.560682    
   ## ethnicityIND                 1.519e-01  1.845e-01   0.824 0.410186    
   ## ethnicityMIX                 6.144e-02  2.017e-01   0.305 0.760680    
   ## ethnicityOAS                 3.816e-01  2.354e-01   1.621 0.104998    
   ## ethnicityOBL                -6.142e-01  5.588e-01  -1.099 0.271695    
   ## ethnicityOTH                -1.805e-01  3.976e-01  -0.454 0.649771    
   ## ethnicityPAK                -1.340e-02  2.017e-01  -0.066 0.947035    
   ## ethnicityWBI                -7.840e-02  1.603e-01  -0.489 0.624841    
   ## ethnicityWHO                -9.354e-02  1.840e-01  -0.509 0.611099    
   ## hh_income                   -5.025e-05  1.430e-05  -3.513 0.000443 ***
   ## alcohol_spending            -5.027e-05  6.421e-05  -0.783 0.433742    
   ## ncigs                        2.436e-02  4.435e-03   5.494 3.94e-08 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##     Estimate Std. Error z value
   ## 1|2  -3.7748     0.1899 -19.874
   ## 2|3  -1.3542     0.1874  -7.228

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
