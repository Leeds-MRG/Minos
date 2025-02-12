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

.. math::     hh\_income\_intermediate = ((net\_hh\_income) - (rent + mortgage + council\_tax)) / oecd\_equivalence\_factor

.. math::     hh\_income = hh\_income\_intermediate * inflation\_factor

More information on these variables can be found at the following links:

-  `net_monthly_income <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fihhmnnet1_dv>`__
-  monthly_outgoings is the sum of
   `rent <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/rentgrs_dv>`__,
   `mortgage <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xpmg_dv>`__,
   and `council
   tax <https://www.understandingsociety.ac.uk/documentation/mainstage/variables/ctband_dv/>`__.
-  `oecd_equivalence_scale <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ieqmoecd_dv>`__
-  See note `below <#Council-Tax>`__ about council tax.

This produces a continuous distribution of pounds per month available
for a household to spend as it likes. This is plotted below with a
median income of :math:`\sim£1650`.

.. code:: r

   continuous_density(obs)

.. figure:: ./figure/hh_income_data-1.png
   :alt: plot of chunk hh_income_data

   plot of chunk hh_income_data

Transition Model
~~~~~~~~~~~~~~~~

To estimate this variable we use a Generalised Linear Mixed Model (GLMM)
using the
`lme4 <https://www.rdocumentation.org/packages/lme4/versions/1.1-36>`__
package in R.

Formula:

.. math::   hh\_income\_next \sim hh\_income\_last + age + age^2 +  age^3 + sex + ethnicity + region + \\education\_state + job\_sec + SF\_12 + labour\_state + (1|pidp)

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

.. code:: r

   print(summary(model))

::

   ## Generalized linear mixed model fit by maximum likelihood (Adaptive
   ##   Gauss-Hermite Quadrature, nAGQ = 0) [glmerMod]
   ##  Family: Gamma  ( log )
   ## Formula: hh_income_new ~ scale(hh_income) + scale(age) + I(scale(age)^2) +  
   ##     I(scale(age)^3) + factor(sex) + relevel(factor(ethnicity),  
   ##     ref = "WBI") + factor(region) + relevel(factor(education_state),  
   ##     ref = "1") + relevel(factor(job_sec), ref = "3") + scale(SF_12) +  
   ##     relevel(factor(S7_labour_state), ref = "FT Employed") + (1 |      pidp)
   ##    Data: data
   ## 
   ##       AIC       BIC    logLik  deviance  df.resid 
   ##  615185.3  615705.6 -307542.6  615085.3    244291 
   ## 
   ## Scaled residuals: 
   ##      Min       1Q   Median       3Q      Max 
   ## -24.4404  -0.3194  -0.0358   0.2882  13.8460 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance Std.Dev.
   ##  pidp     (Intercept) 0.000414 0.02035 
   ##  Residual             0.001674 0.04091 
   ## Number of obs: 244341, groups:  pidp, 45218
   ## 
   ## Fixed effects:
   ##                                                                     Estimate
   ## (Intercept)                                                        2.8993384
   ## scale(hh_income)                                                   0.0161330
   ## scale(age)                                                         0.0120801
   ## I(scale(age)^2)                                                    0.0011894
   ## I(scale(age)^3)                                                   -0.0033103
   ## factor(sex)Male                                                    0.0005210
   ## relevel(factor(ethnicity), ref = "WBI")BAN                        -0.0138111
   ## relevel(factor(ethnicity), ref = "WBI")BLA                        -0.0168078
   ## relevel(factor(ethnicity), ref = "WBI")BLC                        -0.0132551
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        -0.0027026
   ## relevel(factor(ethnicity), ref = "WBI")IND                        -0.0055084
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        -0.0071087
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -0.0125302
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -0.0091845
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -0.0100708
   ## relevel(factor(ethnicity), ref = "WBI")PAK                        -0.0123893
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        -0.0035166
   ## factor(region)East of England                                      0.0017831
   ## factor(region)London                                               0.0034875
   ## factor(region)North East                                          -0.0031138
   ## factor(region)North West                                           0.0006368
   ## factor(region)Northern Ireland                                     0.0018572
   ## factor(region)Scotland                                             0.0018503
   ## factor(region)South East                                           0.0040047
   ## factor(region)South West                                           0.0005561
   ## factor(region)Wales                                               -0.0008582
   ## factor(region)West Midlands                                        0.0016249
   ## factor(region)Yorkshire and The Humber                            -0.0011430
   ## relevel(factor(education_state), ref = "1")0                      -0.0031482
   ## relevel(factor(education_state), ref = "1")2                       0.0031436
   ## relevel(factor(education_state), ref = "1")3                       0.0072619
   ## relevel(factor(education_state), ref = "1")5                       0.0078787
   ## relevel(factor(education_state), ref = "1")6                       0.0147230
   ## relevel(factor(education_state), ref = "1")7                       0.0183995
   ## relevel(factor(job_sec), ref = "3")0                              -0.0039234
   ## relevel(factor(job_sec), ref = "3")1                               0.0054748
   ## relevel(factor(job_sec), ref = "3")2                               0.0047179
   ## relevel(factor(job_sec), ref = "3")4                              -0.0025015
   ## relevel(factor(job_sec), ref = "3")5                              -0.0052788
   ## relevel(factor(job_sec), ref = "3")6                              -0.0031744
   ## relevel(factor(job_sec), ref = "3")7                              -0.0049089
   ## relevel(factor(job_sec), ref = "3")8                              -0.0051268
   ## scale(SF_12)                                                       0.0013832
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care  -0.0105363
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education -0.0069073
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking  -0.0095454
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working  -0.0096224
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed  -0.0042999
   ##                                                                   Std. Error
   ## (Intercept)                                                        0.0010620
   ## scale(hh_income)                                                   0.0001105
   ## scale(age)                                                         0.0003153
   ## I(scale(age)^2)                                                    0.0001568
   ## I(scale(age)^3)                                                    0.0001208
   ## factor(sex)Male                                                    0.0002845
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         0.0011092
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         0.0009740
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         0.0010234
   ## relevel(factor(ethnicity), ref = "WBI")CHI                         0.0020174
   ## relevel(factor(ethnicity), ref = "WBI")IND                         0.0007275
   ## relevel(factor(ethnicity), ref = "WBI")MIX                         0.0010081
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         0.0011395
   ## relevel(factor(ethnicity), ref = "WBI")OBL                         0.0033619
   ## relevel(factor(ethnicity), ref = "WBI")OTH                         0.0021406
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         0.0008037
   ## relevel(factor(ethnicity), ref = "WBI")WHO                         0.0006784
   ## factor(region)East of England                                      0.0006436
   ## factor(region)London                                               0.0006409
   ## factor(region)North East                                           0.0008313
   ## factor(region)North West                                           0.0006284
   ## factor(region)Northern Ireland                                     0.0007615
   ## factor(region)Scotland                                             0.0006929
   ## factor(region)South East                                           0.0006034
   ## factor(region)South West                                           0.0006549
   ## factor(region)Wales                                                0.0007543
   ## factor(region)West Midlands                                        0.0006527
   ## factor(region)Yorkshire and The Humber                             0.0006579
   ## relevel(factor(education_state), ref = "1")0                       0.0009258
   ## relevel(factor(education_state), ref = "1")2                       0.0009314
   ## relevel(factor(education_state), ref = "1")3                       0.0009717
   ## relevel(factor(education_state), ref = "1")5                       0.0009944
   ## relevel(factor(education_state), ref = "1")6                       0.0009534
   ## relevel(factor(education_state), ref = "1")7                       0.0009871
   ## relevel(factor(job_sec), ref = "3")0                               0.0004000
   ## relevel(factor(job_sec), ref = "3")1                               0.0006001
   ## relevel(factor(job_sec), ref = "3")2                               0.0004880
   ## relevel(factor(job_sec), ref = "3")4                               0.0003883
   ## relevel(factor(job_sec), ref = "3")5                               0.0004581
   ## relevel(factor(job_sec), ref = "3")6                               0.0005083
   ## relevel(factor(job_sec), ref = "3")7                               0.0003712
   ## relevel(factor(job_sec), ref = "3")8                               0.0004573
   ## scale(SF_12)                                                       0.0001064
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care   0.0005240
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education  0.0005810
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking   0.0005103
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working   0.0003953
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed   0.0003311
   ##                                                                    t value
   ## (Intercept)                                                       2730.051
   ## scale(hh_income)                                                   146.042
   ## scale(age)                                                          38.312
   ## I(scale(age)^2)                                                      7.584
   ## I(scale(age)^3)                                                    -27.402
   ## factor(sex)Male                                                      1.831
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         -12.452
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         -17.256
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         -12.952
   ## relevel(factor(ethnicity), ref = "WBI")CHI                          -1.340
   ## relevel(factor(ethnicity), ref = "WBI")IND                          -7.572
   ## relevel(factor(ethnicity), ref = "WBI")MIX                          -7.052
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         -10.996
   ## relevel(factor(ethnicity), ref = "WBI")OBL                          -2.732
   ## relevel(factor(ethnicity), ref = "WBI")OTH                          -4.705
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         -15.416
   ## relevel(factor(ethnicity), ref = "WBI")WHO                          -5.183
   ## factor(region)East of England                                        2.771
   ## factor(region)London                                                 5.441
   ## factor(region)North East                                            -3.746
   ## factor(region)North West                                             1.013
   ## factor(region)Northern Ireland                                       2.439
   ## factor(region)Scotland                                               2.670
   ## factor(region)South East                                             6.637
   ## factor(region)South West                                             0.849
   ## factor(region)Wales                                                 -1.138
   ## factor(region)West Midlands                                          2.489
   ## factor(region)Yorkshire and The Humber                              -1.737
   ## relevel(factor(education_state), ref = "1")0                        -3.401
   ## relevel(factor(education_state), ref = "1")2                         3.375
   ## relevel(factor(education_state), ref = "1")3                         7.473
   ## relevel(factor(education_state), ref = "1")5                         7.923
   ## relevel(factor(education_state), ref = "1")6                        15.443
   ## relevel(factor(education_state), ref = "1")7                        18.641
   ## relevel(factor(job_sec), ref = "3")0                                -9.808
   ## relevel(factor(job_sec), ref = "3")1                                 9.123
   ## relevel(factor(job_sec), ref = "3")2                                 9.668
   ## relevel(factor(job_sec), ref = "3")4                                -6.442
   ## relevel(factor(job_sec), ref = "3")5                               -11.524
   ## relevel(factor(job_sec), ref = "3")6                                -6.246
   ## relevel(factor(job_sec), ref = "3")7                               -13.224
   ## relevel(factor(job_sec), ref = "3")8                               -11.212
   ## scale(SF_12)                                                        12.999
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care   -20.108
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education  -11.888
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking   -18.707
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working   -24.343
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed   -12.987
   ##                                                                   Pr(>|z|)    
   ## (Intercept)                                                        < 2e-16 ***
   ## scale(hh_income)                                                   < 2e-16 ***
   ## scale(age)                                                         < 2e-16 ***
   ## I(scale(age)^2)                                                   3.34e-14 ***
   ## I(scale(age)^3)                                                    < 2e-16 ***
   ## factor(sex)Male                                                   0.067063 .  
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        0.180354    
   ## relevel(factor(ethnicity), ref = "WBI")IND                        3.67e-14 ***
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        1.77e-12 ***
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        0.006296 ** 
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        2.54e-06 ***
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        2.18e-07 ***
   ## factor(region)East of England                                     0.005593 ** 
   ## factor(region)London                                              5.28e-08 ***
   ## factor(region)North East                                          0.000180 ***
   ## factor(region)North West                                          0.310841    
   ## factor(region)Northern Ireland                                    0.014732 *  
   ## factor(region)Scotland                                            0.007575 ** 
   ## factor(region)South East                                          3.20e-11 ***
   ## factor(region)South West                                          0.395824    
   ## factor(region)Wales                                               0.255270    
   ## factor(region)West Midlands                                       0.012795 *  
   ## factor(region)Yorkshire and The Humber                            0.082357 .  
   ## relevel(factor(education_state), ref = "1")0                      0.000672 ***
   ## relevel(factor(education_state), ref = "1")2                      0.000738 ***
   ## relevel(factor(education_state), ref = "1")3                      7.83e-14 ***
   ## relevel(factor(education_state), ref = "1")5                      2.32e-15 ***
   ## relevel(factor(education_state), ref = "1")6                       < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")7                       < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")0                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")1                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")2                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")4                              1.18e-10 ***
   ## relevel(factor(job_sec), ref = "3")5                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")6                              4.22e-10 ***
   ## relevel(factor(job_sec), ref = "3")7                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")8                               < 2e-16 ***
   ## scale(SF_12)                                                       < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care   < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking   < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working   < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed   < 2e-16 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

::

   ## 
   ## Correlation matrix not shown by default, as p = 48 > 12.
   ## Use print(summary(model), correlation=TRUE)  or
   ##     vcov(summary(model))        if you need it

Council Tax
^^^^^^^^^^^

In the UKHLS main release data, `council
tax <https://www.understandingsociety.ac.uk/documentation/mainstage/variables/ctband_dv/>`__
information is reported by band. Specific amount deductions are only
available in the Special Licence and Secure Access datasets. Instead of
reported deductions, we have simulated the amount of council tax each
household is paying by taking a random uniform draw for each household
within the confines of their band.

Validation
~~~~~~~~~~

.. code:: r

   handover_boxplots(raw.dat, base.dat, v)

.. figure:: ./figure/hh_income_validation-1.png
   :alt: plot of chunk hh_income_validation

   plot of chunk hh_income_validation

Results
~~~~~~~

Model diagnostics are displayed below. To summarise:

-  r squared of 0.21 indicates reasonable fit.
-  Gender not significant. Some ethnicities see increases. Only London
   has higher income. High quality jobs earn more. PT employed earn less
   students earn more. Housing quality strong indicator of higher
   income.
-  diagnostic plots show under dispersion. Some extreme outlier values
   need investigating.
-  overall decent fit.

|plot of chunk income_output|\ |image1|

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

.. |plot of chunk income_output| image:: ./figure/income_output-1.png
.. |image1| image:: ./figure/income_output-2.png
