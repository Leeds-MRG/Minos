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

   counts_density("data/transitions/ncigs/zip/ncigs_2018_2019.rds", "y")

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

age. persons age. generally older people and very young smoke. SF_12_MCS.
wellbeing estimates number of cigarettes smoked. labour_state. whether a
person is employed or not. ethnicity. certain ethnicities more likely to
smoke cigarettes. education_state. highest qualification. job_sec job
quality hh_income household income ncigs previous number consumed.

Variables that predict whether a person smokes

ethnicity. certain ethnicities more likely to smoke cigarettes.
labour_state. whether a person is employed or not. age SF_12_MCS. wellbeing
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
   ## zeroinfl(formula = formula, data = dat.subset, weights = weight, dist = "pois", link = "logit")
   ## 
   ## Pearson residuals:
   ##      Min       1Q   Median       3Q      Max 
   ## -0.22590 -0.02780 -0.01848  0.00000  3.90660 
   ## 
   ## Count model coefficients (poisson with log link):
   ##                                                Estimate Std. Error z value Pr(>|z|)
   ## (Intercept)                                   1.826e+00         NA      NA       NA
   ## age                                           1.364e-02         NA      NA       NA
   ## factor(sex)Male                               5.071e-02         NA      NA       NA
   ## relevel(factor(education_state), ref = "3")0  3.819e-02         NA      NA       NA
   ## relevel(factor(education_state), ref = "3")1  3.870e-01         NA      NA       NA
   ## relevel(factor(education_state), ref = "3")2  9.921e-02         NA      NA       NA
   ## relevel(factor(education_state), ref = "3")5 -3.817e-02         NA      NA       NA
   ## relevel(factor(education_state), ref = "3")6 -2.838e-01         NA      NA       NA
   ## relevel(factor(education_state), ref = "3")7  2.962e-01         NA      NA       NA
   ## SF_12_MCS                                        -3.491e-03         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")1          8.265e-02         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")2          7.372e-01         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")4          1.603e-01         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")5          1.904e-01         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")6          1.211e-01         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")7          1.474e-01         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")8          2.507e-01         NA      NA       NA
   ## hh_income                                     4.793e-05         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")BAN   -5.872e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")BLA   -5.784e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")BLC   -5.287e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")CHI   -4.005e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")IND   -5.132e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")MIX   -2.855e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")OAS   -4.219e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")OBL   -7.849e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")OTH    7.849e-02         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")PAK   -6.763e-01         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")WHO   -3.410e-02         NA      NA       NA
   ## 
   ## Zero-inflation model coefficients (binomial with logit link):
   ##                                              Estimate Std. Error z value Pr(>|z|)
   ## (Intercept)                                 1.3968641         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")BAN -0.0665143         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")BLA  0.7077274         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")BLC -0.8377246         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")CHI  0.2628890         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")IND  1.4577262         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")MIX -0.2970005         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")OAS  1.0415864         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")OBL  0.3374910         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")OTH -0.8345472         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")PAK -0.0972652         NA      NA       NA
   ## relevel(factor(ethnicity), ref = "WBI")WHO -0.2608373         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")1        0.4389168         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")2        0.5864644         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")4       -0.1661200         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")5       -0.2828293         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")6       -0.8209764         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")7       -0.7934972         NA      NA       NA
   ## relevel(factor(job_sec), ref = "3")8       -0.7788828         NA      NA       NA
   ## hh_income                                   0.0002134         NA      NA       NA
   ## SF_12_MCS                                       0.0179618         NA      NA       NA
   ## 
   ## Number of iterations in BFGS optimization: 90 
   ## Log-likelihood: -84.87 on 50 Df

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
