================
Household Income
================


Household Income
================

Household disposable income is a well known indicator of mental
well-being (Graham 2009). Estimating this is a crucial instrument for
the effects of many policy interventions

The output variable is monthly household disposable income. This is
calculated as a composite using several variables. Rent, mortgages, and
council tax are subtracted from net household income and adjusted by
household size. This value is then adjusted for yearly inflation
estimates.

.. math::     hh\_income\_intermediate = ((net\_hh\_income) - (rent + mortgage + council\_tax)) / hh\_size

.. math::     hh\_income = hh\_income\_ * inflation\_factor

This produces a continuous distribution of pounds per month available
for a household to spend as it likes. This is plotted below with a
median income of :math:`~£1250`.

.. code:: r

   continuous_density(obs)  

.. figure:: ./figure/hh_income_data-1.png
   :alt: plot of chunk hh_income_data

   plot of chunk hh_income_data

Methods
-------

To estimate this variable Ordinary Least Squares (OLS) linear regression
is used. This is a common technique for estimating Gaussian distributed
variables that is easy to implement using base R.

Data
----

The formula for this linear regression is given as

.. math:: hh\_income\_next ~ age + sex + factor(ethnicity) + factor(region) + scale(hh\_income) + factor(job\_sec) + factor(labour\_state) + factor(education\_state) + scale(SF\_12) + factor(housing\_quality)

Each variable included is defined as follows. Each variable with
discrete values is defined in the data tables section of this
documentation
`here <https://leeds-mrg.github.io/Minos/documentation/data_tables.html>`__.

- sex. Individual’s biological sex. (Dilmaghani 2018)
- ethnicity. Individual ethnicity. Discrete string values White British,
  Black African, etc. (Clemens and Dibben 2014)
- region. Administrative region of the UK. Discrete strings such as
  London, North-East. (Brewer et al. 2007)
- household income. Previous household income values are a strong
  indicator of current value. (Dilmaghani 2018)
- job_sec. NSSEC code for individual’s employment. Ordinal values
  describing job quality. (Clemens and Dibben 2014)
- labour state. Is a person employed, unemployed, student etc. Discrete
  states. (Dilmaghani 2018)
- education state. Highest attain qualification. Ordinal values based on
  UK government education tiers (Eika, Mogstad, and Zafar 2019)
- SF_12. Mental well-being. Continuous score indicating overall
  mental-wellbeing. is this an indicator of hh_income? (Viswanathan,
  Anderson, and Thomas 2005)
- housing quality. Ordinal values indicating number of appliances in
  household. (Brewer et al. 2007)

Results
-------

Model coefficients and diagnostics are displayed below. To summarise - r
squared of 0.21 indicates reasonable fit. - Gender not significant. Some
ethnicities see increases. Only London has higher income. High quality
jobs eanr more. PT employed earn less students earn more. Housing
quality strong indicator of higher income. - diagnostic plots show
underdispersion. Some extreme outlier values need investigating. -
overall decent fit.

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
   ##  686691.4  687206.9 -343296.7  686593.4    273972 
   ## 
   ## Scaled residuals: 
   ##      Min       1Q   Median       3Q      Max 
   ## -22.7420  -0.3217  -0.0375   0.2895  13.4051 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance Std.Dev.
   ##  pidp     (Intercept) 0.000466 0.02159 
   ##  Residual             0.001933 0.04397 
   ## Number of obs: 274021, groups:  pidp, 49998
   ## 
   ## Fixed effects:
   ##                                                                     Estimate Std. Error  t value Pr(>|z|)    
   ## (Intercept)                                                        2.818e+00  1.093e-03 2578.811  < 2e-16 ***
   ## scale(hh_income)                                                   1.796e-02  1.125e-04  159.629  < 2e-16 ***
   ## scale(age)                                                         1.319e-02  3.212e-04   41.065  < 2e-16 ***
   ## I(scale(age)^2)                                                    1.488e-03  1.589e-04    9.364  < 2e-16 ***
   ## I(scale(age)^3)                                                   -3.616e-03  1.214e-04  -29.777  < 2e-16 ***
   ## factor(sex)Male                                                    2.745e-04  2.882e-04    0.952 0.340947    
   ## relevel(factor(ethnicity), ref = "WBI")BAN                        -1.382e-02  1.089e-03  -12.697  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLA                        -1.816e-02  9.587e-04  -18.938  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLC                        -1.411e-02  1.003e-03  -14.061  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        -4.245e-03  2.016e-03   -2.106 0.035235 *  
   ## relevel(factor(ethnicity), ref = "WBI")IND                        -5.212e-03  7.341e-04   -7.100 1.24e-12 ***
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        -7.412e-03  9.978e-04   -7.428 1.10e-13 ***
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -1.218e-02  1.150e-03  -10.593  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -1.175e-02  3.301e-03   -3.560 0.000371 ***
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -1.170e-02  2.162e-03   -5.410 6.29e-08 ***
   ## relevel(factor(ethnicity), ref = "WBI")PAK                        -1.291e-02  8.076e-04  -15.988  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        -4.212e-03  7.863e-04   -5.356 8.49e-08 ***
   ## factor(region)East of England                                      1.973e-03  6.388e-04    3.089 0.002010 ** 
   ## factor(region)London                                               4.580e-03  6.347e-04    7.216 5.37e-13 ***
   ## factor(region)North East                                          -3.213e-03  8.143e-04   -3.945 7.97e-05 ***
   ## factor(region)North West                                           6.901e-04  6.186e-04    1.116 0.264568    
   ## factor(region)Scotland                                             2.743e-03  6.747e-04    4.066 4.78e-05 ***
   ## factor(region)South East                                           3.930e-03  5.958e-04    6.596 4.22e-11 ***
   ## factor(region)South West                                          -1.576e-05  6.486e-04   -0.024 0.980609    
   ## factor(region)Wales                                               -4.399e-04  7.294e-04   -0.603 0.546478    
   ## factor(region)West Midlands                                        1.787e-03  6.455e-04    2.768 0.005638 ** 
   ## factor(region)Yorkshire and The Humber                            -7.755e-04  6.489e-04   -1.195 0.232062    
   ## relevel(factor(education_state), ref = "1")0                      -2.102e-03  9.552e-04   -2.201 0.027733 *  
   ## relevel(factor(education_state), ref = "1")2                       4.241e-03  9.648e-04    4.396 1.11e-05 ***
   ## relevel(factor(education_state), ref = "1")3                       8.111e-03  1.005e-03    8.070 7.05e-16 ***
   ## relevel(factor(education_state), ref = "1")5                       8.696e-03  1.028e-03    8.456  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")6                       1.623e-02  9.868e-04   16.445  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")7                       2.005e-02  1.020e-03   19.653  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")0                              -7.989e-03  6.625e-04  -12.059  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")1                               7.950e-03  7.075e-04   11.237  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")2                               7.097e-03  5.822e-04   12.190  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")4                              -3.700e-03  4.653e-04   -7.954 1.81e-15 ***
   ## relevel(factor(job_sec), ref = "3")5                              -8.421e-03  5.678e-04  -14.832  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")6                              -4.453e-03  6.095e-04   -7.305 2.77e-13 ***
   ## relevel(factor(job_sec), ref = "3")7                              -7.323e-03  4.549e-04  -16.099  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")8                              -8.020e-03  5.713e-04  -14.038  < 2e-16 ***
   ## scale(SF_12)                                                       1.556e-03  1.079e-04   14.427  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care  -7.395e-03  7.767e-04   -9.521  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education -4.700e-03  7.136e-04   -6.587 4.48e-11 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking  -6.383e-03  7.492e-04   -8.519  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working  -6.818e-03  6.490e-04  -10.505  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed  -3.969e-03  3.380e-04  -11.743  < 2e-16 ***
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
----------

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
