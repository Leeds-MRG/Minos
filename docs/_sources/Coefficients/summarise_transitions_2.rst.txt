=======================
MINOS Transition Models
=======================


Tobacco Coefficients
====================

Tobacco consumption is measured in the usual number of cigarettes smoked
per day, and is taken directly from a US variable
(`ncigs <https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ncigs>`__).

We estimated a zero inflated poisson model, with the formula:

   ncigs ~ age + sex + SF_12 + labour_state + job_sec + ethnicity +
   hh_income ethnicity + labour_state + SF_12

.. container:: snugshade

   .. container:: Highlighting

      require(tidyverse)

::

   ## Loading required package: tidyverse

::

   ## -- Attaching packages --------------------------------------- tidyverse 1.3.2 --
   ## v ggplot2 3.3.6      v purrr   0.3.4 
   ## v tibble  3.1.8      v dplyr   1.0.10
   ## v tidyr   1.2.0      v stringr 1.4.0 
   ## v readr   2.1.2      v forcats 0.5.1 
   ## -- Conflicts ------------------------------------------ tidyverse_conflicts() --
   ## x dplyr::filter() masks stats::filter()
   ## x dplyr::lag()    masks stats::lag()

.. container:: snugshade

   .. container:: Highlighting

      require(pscl)

::

   ## Loading required package: pscl
   ## Classes and Methods for R developed in the
   ## Political Science Computational Laboratory
   ## Department of Political Science
   ## Stanford University
   ## Simon Jackman
   ## hurdle and zeroinfl functions by Achim Zeileis

.. container:: snugshade

::

   ## 
   ## Call:
   ## zeroinfl(formula = y ~ factor(sex) + scale(age) + scale(SF_12) + factor(labour_state) | 
   ##     relevel(factor(ethnicity), ref = "WBI") + scale(age), data = data, 
   ##     dist = "pois")
   ## 
   ## Pearson residuals:
   ##      Min       1Q   Median       3Q      Max 
   ## -1.75024 -0.76329 -0.05563  0.58683 17.88004 
   ## 
   ## Count model coefficients (poisson with log link):
   ##                                      Estimate Std. Error z value Pr(>|z|)    
   ## (Intercept)                          1.158187   0.024071  48.116  < 2e-16 ***
   ## factor(sex)Male                      0.106336   0.025077   4.240 2.23e-05 ***
   ## scale(age)                           0.107561   0.017073   6.300 2.97e-10 ***
   ## scale(SF_12)                        -0.029366   0.013324  -2.204 0.027518 *  
   ## factor(labour_state)Family Care      0.207191   0.057175   3.624 0.000290 ***
   ## factor(labour_state)Maternity Leave -0.302883   0.501065  -0.604 0.545525    
   ## factor(labour_state)PT Employed      0.039547   0.044232   0.894 0.371273    
   ## factor(labour_state)Retired         -0.028738   0.042805  -0.671 0.501989    
   ## factor(labour_state)Self-employed    0.006792   0.047900   0.142 0.887239    
   ## factor(labour_state)Sick/Disabled    0.107874   0.044940   2.400 0.016377 *  
   ## factor(labour_state)Student         -0.391335   0.101514  -3.855 0.000116 ***
   ## factor(labour_state)Unemployed       0.052690   0.047488   1.110 0.267196    
   ## 
   ## Zero-inflation model coefficients (binomial with logit link):
   ##                                             Estimate Std. Error z value
   ## (Intercept)                                 -1.74690    0.06856 -25.480
   ## relevel(factor(ethnicity), ref = "WBI")BAN  -0.14975    0.51269  -0.292
   ## relevel(factor(ethnicity), ref = "WBI")BLA  -0.65053    0.86881  -0.749
   ## relevel(factor(ethnicity), ref = "WBI")BLC   0.31791    0.40897   0.777
   ## relevel(factor(ethnicity), ref = "WBI")CHI   1.51817    0.70312   2.159
   ## relevel(factor(ethnicity), ref = "WBI")IND   0.52296    0.36411   1.436
   ## relevel(factor(ethnicity), ref = "WBI")MIX   0.20122    0.35581   0.566
   ## relevel(factor(ethnicity), ref = "WBI")OAS   0.93407    0.60401   1.546
   ## relevel(factor(ethnicity), ref = "WBI")OBL -13.01639  538.48954  -0.024
   ## relevel(factor(ethnicity), ref = "WBI")OTH  -0.19411    0.99293  -0.195
   ## relevel(factor(ethnicity), ref = "WBI")PAK   0.03483    0.37297   0.093
   ## relevel(factor(ethnicity), ref = "WBI")WHO  -0.17955    0.31947  -0.562
   ## scale(age)                                  -0.31921    0.06479  -4.927
   ##                                            Pr(>|z|)    
   ## (Intercept)                                 < 2e-16 ***
   ## relevel(factor(ethnicity), ref = "WBI")BAN   0.7702    
   ## relevel(factor(ethnicity), ref = "WBI")BLA   0.4540    
   ## relevel(factor(ethnicity), ref = "WBI")BLC   0.4370    
   ## relevel(factor(ethnicity), ref = "WBI")CHI   0.0308 *  
   ## relevel(factor(ethnicity), ref = "WBI")IND   0.1509    
   ## relevel(factor(ethnicity), ref = "WBI")MIX   0.5717    
   ## relevel(factor(ethnicity), ref = "WBI")OAS   0.1220    
   ## relevel(factor(ethnicity), ref = "WBI")OBL   0.9807    
   ## relevel(factor(ethnicity), ref = "WBI")OTH   0.8450    
   ## relevel(factor(ethnicity), ref = "WBI")PAK   0.9256    
   ## relevel(factor(ethnicity), ref = "WBI")WHO   0.5741    
   ## scale(age)                                 8.35e-07 ***
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1 
   ## 
   ## Number of iterations in BFGS optimization: 30 
   ## Log-likelihood: -5657 on 25 Df
