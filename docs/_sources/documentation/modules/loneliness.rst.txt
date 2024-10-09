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

   discrete_barplot("data/transitions/loneliness/clm/loneliness_2018_2019.rds", 'next_loneliness')

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

   ## formula: 
   ## next_loneliness ~ age + factor(sex) + SF_12_MCS + relevel(factor(education_state), ref = "3") + relevel(factor(job_sec), ref = "3") + hh_income + relevel(factor(hh_comp), ref = "3") + relevel(factor(marital_status), ref = "Partnered") + relevel(factor(ethnicity), ref = "WBI")
   ## data:    data
   ## 
   ##  link  threshold nobs     logLik AIC    niter max.grad cond.H 
   ##  logit flexible  103.1594 -75.90 223.81 6(0)  5.05e-12 1.7e+10
   ## 
   ## Coefficients:
   ##                                                               Estimate Std. Error z value Pr(>|z|)    
   ## age                                                         -5.569e-03  1.835e-02  -0.303 0.761523    
   ## factor(sex)Male                                             -3.589e-01  4.577e-01  -0.784 0.432936    
   ## SF_12_MCS                                                       -8.155e-02  2.343e-02  -3.480 0.000501 ***
   ## relevel(factor(education_state), ref = "3")0                 2.914e-02  8.171e-01   0.036 0.971555    
   ## relevel(factor(education_state), ref = "3")1                -9.217e-01  2.282e+00  -0.404 0.686310    
   ## relevel(factor(education_state), ref = "3")2                -9.872e-02  7.794e-01  -0.127 0.899213    
   ## relevel(factor(education_state), ref = "3")5                 3.943e-02  9.663e-01   0.041 0.967449    
   ## relevel(factor(education_state), ref = "3")6                -2.789e-02  8.153e-01  -0.034 0.972708    
   ## relevel(factor(education_state), ref = "3")7                -1.657e-02  8.952e-01  -0.019 0.985232    
   ## relevel(factor(job_sec), ref = "3")1                        -5.268e-02  1.178e+00  -0.045 0.964341    
   ## relevel(factor(job_sec), ref = "3")2                        -4.476e-02  8.804e-01  -0.051 0.959455    
   ## relevel(factor(job_sec), ref = "3")4                         1.111e-01  7.103e-01   0.156 0.875694    
   ## relevel(factor(job_sec), ref = "3")5                         1.473e-01  8.046e-01   0.183 0.854767    
   ## relevel(factor(job_sec), ref = "3")6                         1.387e-01  1.024e+00   0.135 0.892287    
   ## relevel(factor(job_sec), ref = "3")7                         1.219e-01  6.942e-01   0.176 0.860594    
   ## relevel(factor(job_sec), ref = "3")8                         4.119e-01  8.313e-01   0.496 0.620235    
   ## hh_income                                                   -2.184e-05  1.065e-04  -0.205 0.837501    
   ## relevel(factor(hh_comp), ref = "3")1                         6.569e-01  8.048e-01   0.816 0.414395    
   ## relevel(factor(hh_comp), ref = "3")2                         1.534e-01  1.360e+00   0.113 0.910192    
   ## relevel(factor(hh_comp), ref = "3")4                        -7.012e-04  5.634e-01  -0.001 0.999007    
   ## relevel(factor(marital_status), ref = "Partnered")Separated  4.325e-01  9.785e-01   0.442 0.658485    
   ## relevel(factor(marital_status), ref = "Partnered")Single     5.185e-01  7.343e-01   0.706 0.480147    
   ## relevel(factor(marital_status), ref = "Partnered")Widowed    5.301e-01  1.257e+00   0.422 0.673306    
   ## relevel(factor(ethnicity), ref = "WBI")BAN                   2.416e-01  2.916e+00   0.083 0.933978    
   ## relevel(factor(ethnicity), ref = "WBI")BLA                  -1.811e-01  1.841e+00  -0.098 0.921640    
   ## relevel(factor(ethnicity), ref = "WBI")BLC                   1.215e-02  2.594e+00   0.005 0.996264    
   ## relevel(factor(ethnicity), ref = "WBI")CHI                  -2.081e-01  3.374e+00  -0.062 0.950826    
   ## relevel(factor(ethnicity), ref = "WBI")IND                   5.520e-02  1.409e+00   0.039 0.968742    
   ## relevel(factor(ethnicity), ref = "WBI")MIX                  -1.125e-01  1.678e+00  -0.067 0.946581    
   ## relevel(factor(ethnicity), ref = "WBI")OAS                   2.742e-01  2.027e+00   0.135 0.892424    
   ## relevel(factor(ethnicity), ref = "WBI")OBL                  -6.353e-01  1.022e+01  -0.062 0.950411    
   ## relevel(factor(ethnicity), ref = "WBI")OTH                   3.507e-01  3.219e+00   0.109 0.913227    
   ## relevel(factor(ethnicity), ref = "WBI")PAK                   3.829e-01  1.886e+00   0.203 0.839100    
   ## relevel(factor(ethnicity), ref = "WBI")WHO                  -1.210e-01  9.828e-01  -0.123 0.902043    
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Threshold coefficients:
   ##     Estimate Std. Error z value
   ## 1|2   -3.515      1.582  -2.221
   ## 2|3   -1.130      1.544  -0.732
   ## (273 observations deleted due to missingness)

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
