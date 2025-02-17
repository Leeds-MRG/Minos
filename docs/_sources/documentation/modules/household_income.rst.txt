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
   ##  613008.8  613529.0 -306454.4  612908.8    243509 
   ## 
   ## Scaled residuals: 
   ##      Min       1Q   Median       3Q      Max 
   ## -24.4319  -0.3191  -0.0358   0.2879  13.8735 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance  Std.Dev.
   ##  pidp     (Intercept) 0.0004164 0.02041 
   ##  Residual             0.0016751 0.04093 
   ## Number of obs: 243559, groups:  pidp, 44786
   ## 
   ## Fixed effects:
   ##                                                                     Estimate
   ## (Intercept)                                                        2.8979520
   ## scale(hh_income)                                                   0.0160822
   ## scale(age)                                                         0.0120929
   ## I(scale(age)^2)                                                    0.0012216
   ## I(scale(age)^3)                                                   -0.0033154
   ## factor(sex)Male                                                    0.0005396
   ## relevel(factor(ethnicity), ref = "WBI")BAN                        -0.0136153
   ## relevel(factor(ethnicity), ref = "WBI")BLA                        -0.0168486
   ## relevel(factor(ethnicity), ref = "WBI")BLC                        -0.0129549
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        -0.0032698
   ## relevel(factor(ethnicity), ref = "WBI")IND                        -0.0056127
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        -0.0074509
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -0.0125539
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -0.0097935
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -0.0103571
   ## relevel(factor(ethnicity), ref = "WBI")PAK                        -0.0124615
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        -0.0035002
   ## factor(region)East of England                                      0.0018300
   ## factor(region)London                                               0.0035819
   ## factor(region)North East                                          -0.0030824
   ## factor(region)North West                                           0.0007767
   ## factor(region)Northern Ireland                                     0.0018609
   ## factor(region)Scotland                                             0.0018760
   ## factor(region)South East                                           0.0040448
   ## factor(region)South West                                           0.0005513
   ## factor(region)Wales                                               -0.0007271
   ## factor(region)West Midlands                                        0.0017096
   ## factor(region)Yorkshire and The Humber                            -0.0011342
   ## relevel(factor(education_state), ref = "1")0                      -0.0031670
   ## relevel(factor(education_state), ref = "1")2                       0.0031113
   ## relevel(factor(education_state), ref = "1")3                       0.0073201
   ## relevel(factor(education_state), ref = "1")5                       0.0078578
   ## relevel(factor(education_state), ref = "1")6                       0.0146968
   ## relevel(factor(education_state), ref = "1")7                       0.0183334
   ## relevel(factor(job_sec), ref = "3")0                              -0.0039326
   ## relevel(factor(job_sec), ref = "3")1                               0.0054402
   ## relevel(factor(job_sec), ref = "3")2                               0.0047022
   ## relevel(factor(job_sec), ref = "3")4                              -0.0025526
   ## relevel(factor(job_sec), ref = "3")5                              -0.0052549
   ## relevel(factor(job_sec), ref = "3")6                              -0.0033454
   ## relevel(factor(job_sec), ref = "3")7                              -0.0049347
   ## relevel(factor(job_sec), ref = "3")8                              -0.0052046
   ## scale(SF_12)                                                       0.0013967
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed  -0.0042774
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking  -0.0094277
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education -0.0069735
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care  -0.0104980
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working  -0.0095974
   ##                                                                   Std. Error
   ## (Intercept)                                                        0.0010673
   ## scale(hh_income)                                                   0.0001109
   ## scale(age)                                                         0.0003157
   ## I(scale(age)^2)                                                    0.0001576
   ## I(scale(age)^3)                                                    0.0001210
   ## factor(sex)Male                                                    0.0002856
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         0.0011174
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         0.0009813
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         0.0010300
   ## relevel(factor(ethnicity), ref = "WBI")CHI                         0.0020226
   ## relevel(factor(ethnicity), ref = "WBI")IND                         0.0007316
   ## relevel(factor(ethnicity), ref = "WBI")MIX                         0.0010118
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         0.0011458
   ## relevel(factor(ethnicity), ref = "WBI")OBL                         0.0033721
   ## relevel(factor(ethnicity), ref = "WBI")OTH                         0.0021535
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         0.0008084
   ## relevel(factor(ethnicity), ref = "WBI")WHO                         0.0006811
   ## factor(region)East of England                                      0.0006461
   ## factor(region)London                                               0.0006437
   ## factor(region)North East                                           0.0008351
   ## factor(region)North West                                           0.0006310
   ## factor(region)Northern Ireland                                     0.0007644
   ## factor(region)Scotland                                             0.0006955
   ## factor(region)South East                                           0.0006056
   ## factor(region)South West                                           0.0006574
   ## factor(region)Wales                                                0.0007573
   ## factor(region)West Midlands                                        0.0006554
   ## factor(region)Yorkshire and The Humber                             0.0006606
   ## relevel(factor(education_state), ref = "1")0                       0.0009311
   ## relevel(factor(education_state), ref = "1")2                       0.0009364
   ## relevel(factor(education_state), ref = "1")3                       0.0009768
   ## relevel(factor(education_state), ref = "1")5                       0.0009995
   ## relevel(factor(education_state), ref = "1")6                       0.0009584
   ## relevel(factor(education_state), ref = "1")7                       0.0009921
   ## relevel(factor(job_sec), ref = "3")0                               0.0004014
   ## relevel(factor(job_sec), ref = "3")1                               0.0006015
   ## relevel(factor(job_sec), ref = "3")2                               0.0004893
   ## relevel(factor(job_sec), ref = "3")4                               0.0003893
   ## relevel(factor(job_sec), ref = "3")5                               0.0004595
   ## relevel(factor(job_sec), ref = "3")6                               0.0005098
   ## relevel(factor(job_sec), ref = "3")7                               0.0003723
   ## relevel(factor(job_sec), ref = "3")8                               0.0004588
   ## scale(SF_12)                                                       0.0001068
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed   0.0003318
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking   0.0005120
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education  0.0005826
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care   0.0005256
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working   0.0003963
   ##                                                                    t value
   ## (Intercept)                                                       2715.174
   ## scale(hh_income)                                                   145.019
   ## scale(age)                                                          38.304
   ## I(scale(age)^2)                                                      7.753
   ## I(scale(age)^3)                                                    -27.409
   ## factor(sex)Male                                                      1.889
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         -12.185
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         -17.170
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         -12.577
   ## relevel(factor(ethnicity), ref = "WBI")CHI                          -1.617
   ## relevel(factor(ethnicity), ref = "WBI")IND                          -7.672
   ## relevel(factor(ethnicity), ref = "WBI")MIX                          -7.364
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         -10.957
   ## relevel(factor(ethnicity), ref = "WBI")OBL                          -2.904
   ## relevel(factor(ethnicity), ref = "WBI")OTH                          -4.809
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         -15.415
   ## relevel(factor(ethnicity), ref = "WBI")WHO                          -5.139
   ## factor(region)East of England                                        2.832
   ## factor(region)London                                                 5.565
   ## factor(region)North East                                            -3.691
   ## factor(region)North West                                             1.231
   ## factor(region)Northern Ireland                                       2.434
   ## factor(region)Scotland                                               2.697
   ## factor(region)South East                                             6.679
   ## factor(region)South West                                             0.839
   ## factor(region)Wales                                                 -0.960
   ## factor(region)West Midlands                                          2.608
   ## factor(region)Yorkshire and The Humber                              -1.717
   ## relevel(factor(education_state), ref = "1")0                        -3.402
   ## relevel(factor(education_state), ref = "1")2                         3.323
   ## relevel(factor(education_state), ref = "1")3                         7.494
   ## relevel(factor(education_state), ref = "1")5                         7.861
   ## relevel(factor(education_state), ref = "1")6                        15.334
   ## relevel(factor(education_state), ref = "1")7                        18.480
   ## relevel(factor(job_sec), ref = "3")0                                -9.798
   ## relevel(factor(job_sec), ref = "3")1                                 9.045
   ## relevel(factor(job_sec), ref = "3")2                                 9.611
   ## relevel(factor(job_sec), ref = "3")4                                -6.558
   ## relevel(factor(job_sec), ref = "3")5                               -11.436
   ## relevel(factor(job_sec), ref = "3")6                                -6.562
   ## relevel(factor(job_sec), ref = "3")7                               -13.254
   ## relevel(factor(job_sec), ref = "3")8                               -11.343
   ## scale(SF_12)                                                        13.083
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed   -12.890
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking   -18.415
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education  -11.969
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care   -19.972
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working   -24.215
   ##                                                                   Pr(>|z|)    
   ## (Intercept)                                                        < 2e-16 ***
   ## scale(hh_income)                                                   < 2e-16 ***
   ## scale(age)                                                         < 2e-16 ***
   ## I(scale(age)^2)                                                   8.98e-15 ***
   ## I(scale(age)^3)                                                    < 2e-16 ***
   ## factor(sex)Male                                                   0.058881 .  
   ## relevel(factor(ethnicity), ref = "WBI")BAN                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLA                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLC                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        0.105964    
   ## relevel(factor(ethnicity), ref = "WBI")IND                        1.69e-14 ***
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        1.78e-13 ***
   ## relevel(factor(ethnicity), ref = "WBI")OAS                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        0.003681 ** 
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        1.51e-06 ***
   ## relevel(factor(ethnicity), ref = "WBI")PAK                         < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        2.76e-07 ***
   ## factor(region)East of England                                     0.004622 ** 
   ## factor(region)London                                              2.63e-08 ***
   ## factor(region)North East                                          0.000223 ***
   ## factor(region)North West                                          0.218351    
   ## factor(region)Northern Ireland                                    0.014919 *  
   ## factor(region)Scotland                                            0.006993 ** 
   ## factor(region)South East                                          2.41e-11 ***
   ## factor(region)South West                                          0.401696    
   ## factor(region)Wales                                               0.337018    
   ## factor(region)West Midlands                                       0.009096 ** 
   ## factor(region)Yorkshire and The Humber                            0.086005 .  
   ## relevel(factor(education_state), ref = "1")0                      0.000670 ***
   ## relevel(factor(education_state), ref = "1")2                      0.000892 ***
   ## relevel(factor(education_state), ref = "1")3                      6.67e-14 ***
   ## relevel(factor(education_state), ref = "1")5                      3.80e-15 ***
   ## relevel(factor(education_state), ref = "1")6                       < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")7                       < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")0                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")1                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")2                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")4                              5.47e-11 ***
   ## relevel(factor(job_sec), ref = "3")5                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")6                              5.30e-11 ***
   ## relevel(factor(job_sec), ref = "3")7                               < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")8                               < 2e-16 ***
   ## scale(SF_12)                                                       < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed   < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking   < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care   < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working   < 2e-16 ***
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

.. figure:: ./figure/hh_income_handovers-1.png
   :alt: plot of chunk hh_income_handovers

   plot of chunk hh_income_handovers

.. code:: r

   handover_lineplots(raw.dat, base.dat, v)

.. figure:: ./figure/hh_income_handovers-2.png
   :alt: plot of chunk hh_income_handovers

   plot of chunk hh_income_handovers

.. code:: r

   multi_year_boxplots(raw, cv, 'hh_income')

.. figure:: ./figure/hh_income_cv-1.png
   :alt: plot of chunk hh_income_cv

   plot of chunk hh_income_cv

.. code:: r

   q_q_comparison(raw, cv, 'hh_income')

.. figure:: ./figure/hh_income_cv-2.png
   :alt: plot of chunk hh_income_cv

   plot of chunk hh_income_cv

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
