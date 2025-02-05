Household Disposable Income
---------------------------

Household disposable income is a well known indicator of mental
well-being (Graham 2009). Estimating this is a crucial instrument for
the effects of many policy interventions

The output variable is monthly household disposable income. This is
calculated as a composite using several variables. Rent, mortgages, and
council tax are subtracted from net household income and adjusted by
household size. This value is then adjusted for yearly inflation
estimates.

.. math::     hh\_income\_intermediate = ((net\_hh\_income) - (rent + mortgage + council\_tax)) / hh\_size

.. math::     hh\_income = hh\_income\_intermediate * inflation\_factor

More information on these variables can be found at the following links:

-  `net_monthly_income <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fihhmnnet1_dv>`__

-  monthly_outgoings is the sum of
   `rent <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/rentgrs_dv>`__,
   `mortgage <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xpmg_dv>`__,
   and `council
   tax <https://www.understandingsociety.ac.uk/documentation/mainstage/variables/ctband_dv/>`__.

-  `oecd_equivalence_scale <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ieqmoecd_dv>`__

-  See note `below <#Council-Tax>`__ about council tax. \*

This produces a continuous distribution of pounds per month available
for a household to spend as it likes. This is plotted below with a
median income of :math:`~£1650`.

.. code:: r

   continuous_density(obs)

.. figure:: ./figure/hh_income_data-1.png
   :alt: plot of chunk hh_income_data

   plot of chunk hh_income_data

Methods
~~~~~~~

To estimate this variable we use a Generalised Linear Mixed Model (GLMM)
using the
`lme4 <https://www.rdocumentation.org/packages/lme4/versions/1.1-36>`__
package in R.

Data
~~~~

The formula for this linear regression is given as

.. math::   hh\_income\_next \~ hh\_income\_last + age + age\*\*2 +  age\*\*3 + sex + ethnicity + region + education\_state + job\_sec + SF\_12 + _labour\_state + (1\|pidp)

Each variable included is defined as follows. Each variable with
discrete values is defined in the data tables section of this
documentation
`here <https://leeds-mrg.github.io/Minos/documentation/data_tables.html>`__.

-  sex. Individual’s biological sex. (Dilmaghani 2018)
-  age. Age at time of interview.
-  ethnicity. Individual ethnicity. Discrete string values White
   British, Black African, etc. (Clemens and Dibben 2014)
-  region. Administrative region of the UK. Discrete strings such as
   London, North-East. (Brewer et al. 2007)
-  household income. Previous household income values are a strong
   indicator of current value. (Dilmaghani 2018)
-  job_sec. NSSEC code for individual’s employment. Ordinal values
   describing job quality. (Clemens and Dibben 2014)
-  labour state. Is a person employed, unemployed, student etc. Discrete
   states. (Dilmaghani 2018)
-  education state. Highest attained qualification. Ordinal values based
   on UK government education tiers (Eika, Mogstad, and Zafar 2019)
-  SF_12. Mental well-being. Continuous score indicating overall
   mental-wellbeing. (Viswanathan, Anderson, and Thomas 2005)
-  housing quality. Ordinal values indicating number of appliances in
   household. (Brewer et al. 2007)

Council Tax
^^^^^^^^^^^

In the UKHLS main release data, `council
tax <https://www.understandingsociety.ac.uk/documentation/mainstage/variables/ctband_dv/>`__
information is reported by band. Specific amount deductions are only
available in the Special Licence and Secure Access datasets. Instead of
reported deductions, we have simulated the amount of council tax each
household is paying by taking a random uniform draw for each household
within the confines of their band.

Results
~~~~~~~

Model coefficients and diagnostics are displayed below. To summarise:

-  r squared of 0.21 indicates reasonable fit.
-  Gender not significant. Some ethnicities see increases. Only London
   has higher income. High quality jobs earn more. PT employed earn less
   students earn more. Housing quality strong indicator of higher
   income.
-  diagnostic plots show under dispersion. Some extreme outlier values
   need investigating.
-  overall decent fit.

.. figure:: ./figure/income_output-1.png
   :alt: plot of chunk income_output

   plot of chunk income_output

::

   ## Generalized linear mixed model fit by maximum likelihood (Adaptive Gauss-Hermite Quadrature, nAGQ = 0) ['glmerMod']
   ##  Family: Gamma  ( log )
   ## Formula: hh_income_new ~ scale(hh_income) + scale(age) + I(scale(age)^2) +  
   ##     I(scale(age)^3) + factor(sex) + relevel(factor(ethnicity),  
   ##     ref = "WBI") + factor(region) + relevel(factor(education_state),  
   ##     ref = "1") + relevel(factor(job_sec), ref = "3") + scale(SF_12) +  
   ##     relevel(factor(S7_labour_state), ref = "FT Employed") + (1 |      pidp)
   ##    Data: data
   ## 
   ##       AIC       BIC    logLik  deviance  df.resid 
   ##  736465.9  736984.4 -368183.9  736367.9    291384 
   ## 
   ## Scaled residuals: 
   ##      Min       1Q   Median       3Q      Max 
   ## -22.6003  -0.3264  -0.0385   0.2922  13.3694 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance  Std.Dev.
   ##  pidp     (Intercept) 0.0004496 0.02120 
   ##  Residual             0.0019575 0.04424 
   ## Number of obs: 291433, groups:  pidp, 50777
   ## 
   ## Fixed effects:
   ##                                                                     Estimate Std. Error  t value Pr(>|z|)    
   ## (Intercept)                                                        2.813e+00  1.073e-03 2621.639  < 2e-16 ***
   ## scale(hh_income)                                                   1.830e-02  1.091e-04  167.735  < 2e-16 ***
   ## scale(age)                                                         1.273e-02  3.113e-04   40.889  < 2e-16 ***
   ## I(scale(age)^2)                                                    1.292e-03  1.532e-04    8.434  < 2e-16 ***
   ## I(scale(age)^3)                                                   -3.507e-03  1.173e-04  -29.886  < 2e-16 ***
   ## factor(sex)Male                                                    5.562e-04  2.817e-04    1.975 0.048286 *  
   ## relevel(factor(ethnicity), ref = "WBI")BAN                        -1.422e-02  1.063e-03  -13.382  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLA                        -1.775e-02  9.431e-04  -18.821  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLC                        -1.349e-02  9.841e-04  -13.707  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        -5.256e-03  1.974e-03   -2.663 0.007744 ** 
   ## relevel(factor(ethnicity), ref = "WBI")IND                        -4.811e-03  7.170e-04   -6.710 1.95e-11 ***
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        -7.574e-03  9.723e-04   -7.789 6.73e-15 ***
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -1.135e-02  1.131e-03  -10.039  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -1.222e-02  3.232e-03   -3.782 0.000156 ***
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -1.136e-02  2.133e-03   -5.327 1.00e-07 ***
   ## relevel(factor(ethnicity), ref = "WBI")PAK                        -1.320e-02  7.880e-04  -16.755  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        -4.153e-03  7.711e-04   -5.386 7.20e-08 ***
   ## factor(region)East of England                                      1.991e-03  6.241e-04    3.191 0.001420 ** 
   ## factor(region)London                                               4.195e-03  6.204e-04    6.763 1.35e-11 ***
   ## factor(region)North East                                          -3.440e-03  7.967e-04   -4.318 1.57e-05 ***
   ## factor(region)North West                                           6.041e-04  6.046e-04    0.999 0.317644    
   ## factor(region)Scotland                                             2.526e-03  6.585e-04    3.835 0.000125 ***
   ## factor(region)South East                                           4.291e-03  5.817e-04    7.377 1.62e-13 ***
   ## factor(region)South West                                           5.774e-05  6.334e-04    0.091 0.927361    
   ## factor(region)Wales                                               -5.970e-04  7.118e-04   -0.839 0.401627    
   ## factor(region)West Midlands                                        1.786e-03  6.304e-04    2.834 0.004601 ** 
   ## factor(region)Yorkshire and The Humber                            -8.007e-04  6.335e-04   -1.264 0.206258    
   ## relevel(factor(education_state), ref = "1")0                      -1.631e-03  9.410e-04   -1.733 0.083120 .  
   ## relevel(factor(education_state), ref = "1")2                       4.537e-03  9.497e-04    4.778 1.77e-06 ***
   ## relevel(factor(education_state), ref = "1")3                       8.429e-03  9.883e-04    8.529  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")5                       9.071e-03  1.011e-03    8.971  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")6                       1.663e-02  9.703e-04   17.134  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")7                       2.062e-02  1.002e-03   20.566  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")0                              -7.925e-03  6.404e-04  -12.376  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")1                               7.958e-03  6.802e-04   11.700  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")2                               7.014e-03  5.611e-04   12.501  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")4                              -3.583e-03  4.486e-04   -7.987 1.38e-15 ***
   ## relevel(factor(job_sec), ref = "3")5                              -8.894e-03  5.505e-04  -16.155  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")6                              -4.804e-03  5.906e-04   -8.135 4.14e-16 ***
   ## relevel(factor(job_sec), ref = "3")7                              -7.290e-03  4.404e-04  -16.554  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")8                              -7.995e-03  5.538e-04  -14.438  < 2e-16 ***
   ## scale(SF_12)                                                       1.532e-03  1.049e-04   14.608  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care  -7.244e-03  7.565e-04   -9.577  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education -4.245e-03  6.923e-04   -6.132 8.70e-10 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking  -6.115e-03  7.264e-04   -8.418  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working  -6.543e-03  6.292e-04  -10.399  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed  -3.980e-03  3.269e-04  -12.175  < 2e-16 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

::

   ## 
   ## Correlation matrix not shown by default, as p = 47 > 12.
   ## Use print(summary(model), correlation=TRUE)  or
   ##     vcov(summary(model))        if you need it

.. figure:: ./figure/income_output-2.png
   :alt: plot of chunk income_output

   plot of chunk income_output

References
~~~~~~~~~~

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-brewer2007poverty

      Brewer, Mike, Alastair Muriel, David Phillips, and Luke Sibieta.
      2007. “Poverty and Inequality in the UK: 2008.”

   .. container:: csl-entry
      :name: ref-clemens2014method

      Clemens, Tom, and Chris Dibben. 2014. “A Method for Estimating
      Wage, Using Standardised Occupational Classifications, for Use in
      Medical Research in the Place of Self-Reported Income.” *BMC
      Medical Research Methodology* 14 (1): 1–8.

   .. container:: csl-entry
      :name: ref-dilmaghani2018sexual

      Dilmaghani, Maryam. 2018. “Sexual Orientation, Labour Earnings,
      and Household Income in Canada.” *Journal of Labor Research* 39
      (1): 41–55.

   .. container:: csl-entry
      :name: ref-eika2019educational

      Eika, Lasse, Magne Mogstad, and Basit Zafar. 2019. “Educational
      Assortative Mating and Household Income Inequality.” *Journal of
      Political Economy* 127 (6): 2795–835.

   .. container:: csl-entry
      :name: ref-graham2009understanding

      Graham, Hilary. 2009. *Understanding Health Inequalities*.
      McGraw-hill education (UK).

   .. container:: csl-entry
      :name: ref-viswanathan2005nature

      Viswanathan, Hema, Rodney Anderson, and Joseph Thomas. 2005.
      “Nature and Correlates of SF-12 Physical and Mental Quality of
      Life Components Among Low-Income HIV Adults Using an HIV Service
      Center.” *Quality of Life Research* 14 (4): 935–44.
