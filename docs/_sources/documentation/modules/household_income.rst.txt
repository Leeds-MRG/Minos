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

.. math::   hh\_income\_next \sim hh\_income\_last + age + age^2 +  age^3 + sex + ethnicity + region + education\_state + job\_sec + SF\_12 + labour\_state + (1\|pidp)

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
   ##  661167.7  661680.8 -330534.8  661069.7    260689 
   ## 
   ## Scaled residuals: 
   ##      Min       1Q   Median       3Q      Max 
   ## -23.4789  -0.3230  -0.0373   0.2904  13.4183 
   ## 
   ## Random effects:
   ##  Groups   Name        Variance  Std.Dev.
   ##  pidp     (Intercept) 0.0004404 0.02099 
   ##  Residual             0.0018138 0.04259 
   ## Number of obs: 260738, groups:  pidp, 49574
   ## 
   ## Fixed effects:
   ##                                                                     Estimate Std. Error  t value Pr(>|z|)    
   ## (Intercept)                                                        2.8528929  0.0010843 2631.175  < 2e-16 ***
   ## scale(hh_income)                                                   0.0174064  0.0001115  156.071  < 2e-16 ***
   ## scale(age)                                                         0.0124048  0.0003113   39.843  < 2e-16 ***
   ## I(scale(age)^2)                                                    0.0017669  0.0001579   11.188  < 2e-16 ***
   ## I(scale(age)^3)                                                   -0.0033816  0.0001177  -28.741  < 2e-16 ***
   ## factor(sex)Male                                                    0.0002612  0.0002837    0.921 0.357287    
   ## relevel(factor(ethnicity), ref = "WBI")BAN                        -0.0141235  0.0010795  -13.083  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLA                        -0.0176375  0.0009462  -18.641  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLC                        -0.0135069  0.0009932  -13.600  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI                        -0.0038817  0.0019702   -1.970 0.048813 *  
   ## relevel(factor(ethnicity), ref = "WBI")IND                        -0.0050109  0.0007227   -6.933 4.12e-12 ***
   ## relevel(factor(ethnicity), ref = "WBI")MIX                        -0.0070664  0.0009810   -7.203 5.89e-13 ***
   ## relevel(factor(ethnicity), ref = "WBI")OAS                        -0.0124392  0.0011283  -11.025  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")OBL                        -0.0110584  0.0032666   -3.385 0.000711 ***
   ## relevel(factor(ethnicity), ref = "WBI")OTH                        -0.0106252  0.0021376   -4.971 6.67e-07 ***
   ## relevel(factor(ethnicity), ref = "WBI")PAK                        -0.0126038  0.0007953  -15.848  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")WHO                        -0.0036134  0.0007731   -4.674 2.96e-06 ***
   ## factor(region)East of England                                      0.0018730  0.0006287    2.979 0.002889 ** 
   ## factor(region)London                                               0.0044187  0.0006248    7.072 1.53e-12 ***
   ## factor(region)North East                                          -0.0029585  0.0008009   -3.694 0.000221 ***
   ## factor(region)North West                                           0.0007816  0.0006081    1.285 0.198690    
   ## factor(region)Scotland                                             0.0025678  0.0006630    3.873 0.000107 ***
   ## factor(region)South East                                           0.0039767  0.0005858    6.788 1.13e-11 ***
   ## factor(region)South West                                           0.0001110  0.0006381    0.174 0.861841    
   ## factor(region)Wales                                               -0.0002777  0.0007181   -0.387 0.699006    
   ## factor(region)West Midlands                                        0.0018035  0.0006349    2.840 0.004505 ** 
   ## factor(region)Yorkshire and The Humber                            -0.0007299  0.0006379   -1.144 0.252516    
   ## relevel(factor(education_state), ref = "1")0                      -0.0021716  0.0009516   -2.282 0.022482 *  
   ## relevel(factor(education_state), ref = "1")2                       0.0037212  0.0009599    3.877 0.000106 ***
   ## relevel(factor(education_state), ref = "1")3                       0.0075971  0.0009990    7.605 2.85e-14 ***
   ## relevel(factor(education_state), ref = "1")5                       0.0081579  0.0010214    7.987 1.38e-15 ***
   ## relevel(factor(education_state), ref = "1")6                       0.0154652  0.0009813   15.760  < 2e-16 ***
   ## relevel(factor(education_state), ref = "1")7                       0.0190660  0.0010132   18.817  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")0                              -0.0078132  0.0006532  -11.961  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")1                               0.0075903  0.0006925   10.961  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")2                               0.0069326  0.0005710   12.141  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")4                              -0.0035172  0.0004567   -7.702 1.34e-14 ***
   ## relevel(factor(job_sec), ref = "3")5                              -0.0083782  0.0005587  -14.995  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")6                              -0.0043917  0.0005979   -7.345 2.06e-13 ***
   ## relevel(factor(job_sec), ref = "3")7                              -0.0069715  0.0004468  -15.602  < 2e-16 ***
   ## relevel(factor(job_sec), ref = "3")8                              -0.0077591  0.0005616  -13.817  < 2e-16 ***
   ## scale(SF_12)                                                       0.0014762  0.0001070   13.796  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Family Care  -0.0070913  0.0007662   -9.255  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")FT Education -0.0043898  0.0007029   -6.245 4.23e-10 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Job Seeking  -0.0059765  0.0007395   -8.082 6.37e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")Not Working  -0.0062820  0.0006407   -9.805  < 2e-16 ***
   ## relevel(factor(S7_labour_state), ref = "FT Employed")PT Employed  -0.0037179  0.0003325  -11.182  < 2e-16 ***
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
