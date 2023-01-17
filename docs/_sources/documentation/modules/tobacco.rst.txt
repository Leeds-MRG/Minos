=======
Tobacco
=======


Tobacco
=======

Number of cigarettes consumed is an indicator of several mental
illnesses including anxiety (Lawrence et al. 2010).

Data
----

What variables are included? Why is this output chosen. What explanatory
variables are used and why are they chosen

.. code:: r

   counts_density('ncigs')

.. figure:: ./figure/tobacco_data-1.png
   :alt: plot of chunk tobacco_data

   plot of chunk tobacco_data

Methods
-------

The number of zero inflated values is higher than expected for a count
distribution such as a poisson distribution. This inflation occurs
naturally as a large proportion (over 50%) of the population do not
smoke. There are two sources of cigarette consumption that can be
modelled using zero inflated models. In this case a zero-inflated
poisson (ZIP) is used. Two models are fitted simulatenously. One is a
logistic regression that estimates whether a person smokes cigarettes or
not. This provides a simple probability of smoking or not. The second is
a poisson counts model estimating the number of cigarettes consumed.

.. _data-1:

Data
----

Two set of variables are needed for the logistic and poisson parts of
the ZIP model respectively.

Variables that predict how much a person smokes.

age. persons age. generally older people and very young smoke. SF_12.
wellbeing estimates number of cigarettes smoked. labour_state. whether a
person is employed or not. ethnicity. certain ethnicities more likely to
smoke cigarettes. education_state. highest qualification. job_sec job
quality hh_income household income ncigs previous number consumed.

Variables that predict whether a person smokes

ethnicity. certain ethnicities more likely to smoke cigarettes.
labour_state. whether a person is employed or not. age SF_12. wellbeing
estimates number of cigarettes smoked. ncigs previous number consumed.

Results
-------

Almost all coefficients significant. Particularly prevous consumption of
cigarettes. Good estimation of the number of non-smokers in the
population at around 55%. Counts of smoking are underdispersed and fail
to estimate consumption over 20 cigarettes.

::

   ## 
   ## Call:
   ## zeroinfl(formula = ncigs_next ~ factor(sex) + age + SF_12 + factor(labour_state) + relevel(factor(ethnicity), 
   ##     ref = "WBI") + factor(education_state) + factor(job_sec) + scale(hh_income) + ncigs | relevel(factor(ethnicity), 
   ##     ref = "WBI") + age + SF_12 + ncigs, data = data, dist = "pois", link = "logit", model = T)
   ## 
   ## Pearson residuals:
   ##      Min       1Q   Median       3Q      Max 
   ## -13.5258  -0.1851  -0.1546  -0.1317  44.3375 
   ## 
   ## Count model coefficients (poisson with log link):
   ##                                              Estimate Std. Error z value Pr(>|z|)    
   ## (Intercept)                                 2.0851576  0.0401255  51.966  < 2e-16 ***
   ## factor(sex)Male                             0.0141691  0.0129642   1.093 0.274419    
   ## age                                         0.0064996  0.0005318  12.222  < 2e-16 ***
   ## SF_12                                      -0.0021571  0.0005780  -3.732 0.000190 ***
   ## factor(labour_state)Family Care             0.2254327  0.0297159   7.586 3.29e-14 ***
   ## factor(labour_state)Maternity Leave        -0.0855599  0.3206467  -0.267 0.789596    
   ## factor(labour_state)PT Employed             0.0066390  0.0219167   0.303 0.761950    
   ## factor(labour_state)Retired                -0.0026351  0.0238955  -0.110 0.912191    
   ## factor(labour_state)Self-employed           0.0766447  0.0334323   2.293 0.021875 *  
   ## factor(labour_state)Sick/Disabled           0.0407686  0.0259998   1.568 0.116872    
   ## factor(labour_state)Student                -0.3281149  0.0483501  -6.786 1.15e-11 ***
   ## factor(labour_state)Unemployed              0.1073869  0.0257229   4.175 2.98e-05 ***
   ## relevel(factor(ethnicity), ref = "WBI")BAN -0.4125926  0.0624020  -6.612 3.80e-11 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLA -0.4577618  0.0761570  -6.011 1.85e-09 ***
   ## relevel(factor(ethnicity), ref = "WBI")BLC -0.5435353  0.0558868  -9.726  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI -0.3517933  0.1429282  -2.461 0.013842 *  
   ## relevel(factor(ethnicity), ref = "WBI")IND -0.5251485  0.0623874  -8.418  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")MIX -0.2655940  0.0448645  -5.920 3.22e-09 ***
   ## relevel(factor(ethnicity), ref = "WBI")OAS -0.1213163  0.0986363  -1.230 0.218721    
   ## relevel(factor(ethnicity), ref = "WBI")OBL -0.6448752  0.2198301  -2.934 0.003351 ** 
   ## relevel(factor(ethnicity), ref = "WBI")OTH -0.1538574  0.1165979  -1.320 0.186984    
   ## relevel(factor(ethnicity), ref = "WBI")PAK -0.6059558  0.0535081 -11.325  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")WHO -0.1146488  0.0308163  -3.720 0.000199 ***
   ## factor(education_state)1                   -0.0895149  0.0496629  -1.802 0.071475 .  
   ## factor(education_state)2                    0.0056618  0.0147358   0.384 0.700815    
   ## factor(education_state)3                   -0.0370368  0.0242143  -1.530 0.126130    
   ## factor(education_state)5                   -0.0462688  0.0251651  -1.839 0.065972 .  
   ## factor(education_state)6                   -0.1420103  0.0255623  -5.555 2.77e-08 ***
   ## factor(education_state)7                   -0.0570756  0.0308758  -1.849 0.064522 .  
   ## factor(job_sec)1                           -0.0605048  0.0554776  -1.091 0.275441    
   ## factor(job_sec)2                            0.3299314  0.0406703   8.112 4.97e-16 ***
   ## factor(job_sec)3                            0.0584352  0.0246486   2.371 0.017753 *  
   ## factor(job_sec)4                            0.0625456  0.0277822   2.251 0.024367 *  
   ## factor(job_sec)5                            0.1283189  0.0319127   4.021 5.80e-05 ***
   ## factor(job_sec)6                            0.2190621  0.0272359   8.043 8.76e-16 ***
   ## factor(job_sec)7                            0.1136585  0.0226746   5.013 5.37e-07 ***
   ## factor(job_sec)8                            0.1684281  0.0243215   6.925 4.36e-12 ***
   ## scale(hh_income)                            0.0236496  0.0066289   3.568 0.000360 ***
   ## ncigs                                       0.0171283  0.0002817  60.800  < 2e-16 ***
   ## 
   ## Zero-inflation model coefficients (binomial with logit link):
   ##                                             Estimate Std. Error z value Pr(>|z|)    
   ## (Intercept)                                 2.174538   0.171951  12.646  < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BAN -0.409017   0.243218  -1.682  0.09263 .  
   ## relevel(factor(ethnicity), ref = "WBI")BLA -0.407966   0.246538  -1.655  0.09797 .  
   ## relevel(factor(ethnicity), ref = "WBI")BLC -0.957178   0.208264  -4.596 4.31e-06 ***
   ## relevel(factor(ethnicity), ref = "WBI")CHI  0.773182   0.658884   1.173  0.24061    
   ## relevel(factor(ethnicity), ref = "WBI")IND  0.299649   0.215367   1.391  0.16412    
   ## relevel(factor(ethnicity), ref = "WBI")MIX -0.462840   0.205337  -2.254  0.02419 *  
   ## relevel(factor(ethnicity), ref = "WBI")OAS  0.793557   0.512057   1.550  0.12120    
   ## relevel(factor(ethnicity), ref = "WBI")OBL -1.086962   0.814659  -1.334  0.18212    
   ## relevel(factor(ethnicity), ref = "WBI")OTH -0.122495   0.680492  -0.180  0.85714    
   ## relevel(factor(ethnicity), ref = "WBI")PAK -0.206189   0.196713  -1.048  0.29456    
   ## relevel(factor(ethnicity), ref = "WBI")WHO -0.410170   0.165281  -2.482  0.01308 *  
   ## age                                         0.016152   0.002193   7.367 1.75e-13 ***
   ## SF_12                                       0.012717   0.003382   3.760  0.00017 ***
   ## ncigs                                      -0.516195   0.010658 -48.434  < 2e-16 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1 
   ## 
   ## Number of iterations in BFGS optimization: 59 
   ## Log-likelihood: -1.362e+04 on 54 Df

.. figure:: ./figure/tobacco_output-1.png
   :alt: plot of chunk tobacco_output

   plot of chunk tobacco_output

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-lawrence2010anxiety

      Lawrence, David, Julie Considine, Francis Mitrou, and Stephen R
      Zubrick. 2010. “Anxiety Disorders and Cigarette Smoking: Results
      from the Australian Survey of Mental Health and Wellbeing.”
      *Australian & New Zealand Journal of Psychiatry* 44 (6): 520–27.
