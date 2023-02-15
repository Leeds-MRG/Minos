=================
Mental Well-Being
=================


Mental Well-Being
=================

Introductory fluff. Why do we need this module? test reference (Nelson
1987).

Methods
-------

What methods are used? Justification due to output data type.
explanation of model output.

|plot of chunk neighbourhood_barchart| ### Data

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

   ## 
   ## Call:
   ## lm(formula = formula, data = data, weights = weight)
   ## 
   ## Weighted Residuals:
   ##      Min       1Q   Median       3Q      Max 
   ## -11929.0    -51.1      0.0    268.9   5850.7 
   ## 
   ## Coefficients:
   ##                                      Estimate Std. Error t value Pr(>|t|)    
   ## (Intercept)                         34.485409   1.634733  21.095  < 2e-16 ***
   ## factor(sex)Male                      0.575984   0.222052   2.594 0.009498 ** 
   ## factor(ethnicity)BLA                 6.590234   1.660414   3.969 7.25e-05 ***
   ## factor(ethnicity)BLC                 4.690490   1.865502   2.514 0.011936 *  
   ## factor(ethnicity)CHI                 6.343840   2.171633   2.921 0.003491 ** 
   ## factor(ethnicity)IND                 4.194507   1.549387   2.707 0.006792 ** 
   ## factor(ethnicity)MIX                 3.753619   1.634865   2.296 0.021690 *  
   ## factor(ethnicity)OAS                 6.334935   1.689290   3.750 0.000177 ***
   ## factor(ethnicity)OBL                 7.008550   4.382247   1.599 0.109773    
   ## factor(ethnicity)OTH                 5.704026   2.218579   2.571 0.010149 *  
   ## factor(ethnicity)PAK                 4.016367   1.639869   2.449 0.014328 *  
   ## factor(ethnicity)WBI                 4.207545   1.409282   2.986 0.002835 ** 
   ## factor(ethnicity)WHO                 3.073975   1.469116   2.092 0.036419 *  
   ## age                                  0.113208   0.009517  11.895  < 2e-16 ***
   ## factor(education_state)1            -0.416676   0.836934  -0.498 0.618590    
   ## factor(education_state)2             0.296434   0.307868   0.963 0.335632    
   ## factor(education_state)3             0.660260   0.401769   1.643 0.100324    
   ## factor(education_state)5             1.370757   0.433957   3.159 0.001588 ** 
   ## factor(education_state)6             0.447677   0.340639   1.314 0.188789    
   ## factor(education_state)7             0.638411   0.390018   1.637 0.101676    
   ## factor(labour_state)Family Care     -2.007455   0.632196  -3.175 0.001499 ** 
   ## factor(labour_state)Maternity Leave -2.802892   1.299391  -2.157 0.031014 *  
   ## factor(labour_state)PT Employed     -0.749076   0.380365  -1.969 0.048929 *  
   ## factor(labour_state)Retired         -1.750428   0.400997  -4.365 1.28e-05 ***
   ## factor(labour_state)Self-employed   -0.820380   0.412457  -1.989 0.046717 *  
   ## factor(labour_state)Sick/Disabled   -9.331572   0.612816 -15.227  < 2e-16 ***
   ## factor(labour_state)Student         -0.308230   0.518760  -0.594 0.552409    
   ## factor(labour_state)Unemployed      -0.695720   0.584918  -1.189 0.234287    
   ## scale(hh_income)                     0.401025   0.105104   3.816 0.000136 ***
   ## scale(SF_12)                         6.392215   0.139857  45.705  < 2e-16 ***
   ## factor(housing_quality)2             0.696491   0.699976   0.995 0.319741    
   ## factor(housing_quality)3             1.522001   0.714000   2.132 0.033050 *  
   ## ---
   ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
   ## 
   ## Residual standard error: 700.4 on 15911 degrees of freedom
   ## Multiple R-squared:  0.1855, Adjusted R-squared:  0.1839 
   ## F-statistic: 116.9 on 31 and 15911 DF,  p-value: < 2.2e-16

|plot of chunk housing_output|\ |image1|\ |image2|\ |image3|

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.

.. |plot of chunk neighbourhood_barchart| image:: ./figure/neighbourhood_barchart-1.png
.. |plot of chunk housing_output| image:: ./figure/housing_output-2.png
.. |image1| image:: ./figure/housing_output-3.png
.. |image2| image:: ./figure/housing_output-4.png
.. |image3| image:: ./figure/housing_output-5.png
