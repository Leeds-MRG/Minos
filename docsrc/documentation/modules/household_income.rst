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
   ##  690154.9  690670.4 -345028.5  690056.9    273797 
   ## 
   ## Scaled residuals: 
   ##      Min       1Q   Median       3Q      Max 
   ## -23.0617  -0.3223  -0.0378   0.2887  13.5232 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance  Std.Dev.
   ##  pidp     (Intercept) 0.0004627 0.02151 
   ##  Residual             0.0018799 0.04336 
   ## Number of obs: 273846, groups:  pidp, 49982
   ## 
   ## Fixed effects:
   ##                                                                     Estimate Std. Error  t value Pr(>|z|)    
   ## (Intercept)                                                        2.832e+00  1.084e-03 2612.421  < 2e-16 ***
   ## scale(hh_income)                                                   1.768e-02  1.112e-04  158.948  < 2e-16 ***
   ## scale(age)                                                         1.296e-02  3.181e-04   40.750  < 2e-16 ***
   ## I(scale(age)^2)                                                    1.451e-03  1.573e-04    9.227  < 2e-16 ***
   ## I(scale(age)^3)                                                   -3.553e-03  1.202e-04  -29.551  < 2e-16 ***
   ## factor(sex)Male                                                    3.177e-04  2.859e-04    1.111  0.26643    
   ## relevel(factor(ethnicity), ref = "WBI")BAN                        -1.372e-02  1.079e-03  -12.713  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLA                        -1.795e-02  9.504e-04  -18.887  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLC                        -1.391e-02  9.952e-04  -13.972  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        -4.079e-03  2.001e-03   -2.038  0.04153 *  
   ## relevel(factor(ethnicity), ref = "WBI")IND                        -5.179e-03  7.281e-04   -7.113 1.14e-12 ***
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        -7.445e-03  9.897e-04   -7.523 5.36e-14 ***
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -1.216e-02  1.140e-03  -10.663  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -1.173e-02  3.274e-03   -3.583  0.00034 ***
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -1.168e-02  2.144e-03   -5.450 5.03e-08 ***
   ## relevel(factor(ethnicity), ref = "WBI")PAK                        -1.285e-02  8.007e-04  -16.047  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        -3.883e-03  7.802e-04   -4.977 6.44e-07 ***
   ## factor(region)East of England                                      1.971e-03  6.335e-04    3.111  0.00186 ** 
   ## factor(region)London                                               4.584e-03  6.294e-04    7.283 3.27e-13 ***
   ## factor(region)North East                                          -3.182e-03  8.079e-04   -3.938 8.22e-05 ***
   ## factor(region)North West                                           7.896e-04  6.135e-04    1.287  0.19811    
   ## factor(region)Scotland                                             2.734e-03  6.692e-04    4.086 4.39e-05 ***
   ## factor(region)South East                                           4.000e-03  5.909e-04    6.770 1.29e-11 ***
   ## factor(region)South West                                           7.862e-05  6.433e-04    0.122  0.90273    
   ## factor(region)Wales                                               -3.985e-04  7.234e-04   -0.551  0.58174    
   ## factor(region)West Midlands                                        1.828e-03  6.402e-04    2.856  0.00429 ** 
   ## factor(region)Yorkshire and The Humber                            -7.302e-04  6.436e-04   -1.135  0.25654    
   ## relevel(factor(education_state), ref = "1")0                      -2.283e-03  9.476e-04   -2.409  0.01600 *  
   ## relevel(factor(education_state), ref = "1")2                       3.957e-03  9.571e-04    4.135 3.55e-05 ***
   ## relevel(factor(education_state), ref = "1")3                       7.848e-03  9.970e-04    7.872 3.50e-15 ***
   ## relevel(factor(education_state), ref = "1")5                       8.388e-03  1.020e-03    8.222  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")6                       1.593e-02  9.790e-04   16.277  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")7                       1.959e-02  1.012e-03   19.363  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")0                              -7.934e-03  6.545e-04  -12.122  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")1                               7.728e-03  6.996e-04   11.046  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")2                               6.981e-03  5.761e-04   12.118  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")4                              -3.572e-03  4.602e-04   -7.761 8.46e-15 ***
   ## relevel(factor(job_sec), ref = "3")5                              -8.391e-03  5.619e-04  -14.935  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")6                              -4.396e-03  6.028e-04   -7.293 3.04e-13 ***
   ## relevel(factor(job_sec), ref = "3")7                              -7.190e-03  4.499e-04  -15.979  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")8                              -7.880e-03  5.651e-04  -13.945  < 2e-16 ***
   ## scale(SF_12)                                                       1.524e-03  1.066e-04   14.299  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care  -7.318e-03  7.674e-04   -9.537  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education -4.598e-03  7.050e-04   -6.522 6.93e-11 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking  -6.202e-03  7.399e-04   -8.383  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working  -6.709e-03  6.411e-04  -10.465  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed  -3.925e-03  3.340e-04  -11.751  < 2e-16 ***
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
