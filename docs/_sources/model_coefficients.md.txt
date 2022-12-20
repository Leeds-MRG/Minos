Call:
lm(formula = y ~ factor(sex) + factor(ethnicity) + age + factor(education_state) + 
    factor(labour_state) + factor(job_sec) + factor(region) + 
    gross_hh_income, data = data)

Residuals:
    Min      1Q  Median      3Q     Max 
-61.516  -4.331   3.903   9.151  38.744 

Coefficients:
                                          Estimate Std. Error t value Pr(>|t|)    
(Intercept)                              3.340e+01  8.539e-01  39.111  < 2e-16 ***
factor(sex)Male                          1.113e+00  1.430e-01   7.787 6.97e-15 ***
factor(ethnicity)BLA                     5.283e+00  8.080e-01   6.538 6.30e-11 ***
factor(ethnicity)BLC                     4.751e+00  8.267e-01   5.747 9.12e-09 ***
factor(ethnicity)CHI                     5.951e+00  1.198e+00   4.967 6.83e-07 ***
factor(ethnicity)IND                     6.138e+00  7.414e-01   8.279  < 2e-16 ***
factor(ethnicity)MIX                     6.845e+00  8.109e-01   8.441  < 2e-16 ***
factor(ethnicity)OAS                     5.362e+00  8.749e-01   6.129 8.90e-10 ***
factor(ethnicity)OBL                     7.467e+00  1.856e+00   4.024 5.74e-05 ***
factor(ethnicity)OTH                     5.058e+00  1.301e+00   3.888 0.000101 ***
factor(ethnicity)PAK                     1.937e+00  7.706e-01   2.514 0.011951 *  
factor(ethnicity)WBI                     7.726e+00  6.401e-01  12.070  < 2e-16 ***
factor(ethnicity)WHO                     7.310e+00  7.082e-01  10.322  < 2e-16 ***
age                                      9.522e-02  6.412e-03  14.850  < 2e-16 ***
factor(education_state)CSE               1.685e-01  3.899e-01   0.432 0.665608    
factor(education_state)Degree            1.029e+00  2.639e-01   3.900 9.62e-05 ***
factor(education_state)GCSE              1.021e-01  2.333e-01   0.438 0.661473    
factor(education_state)HE Diploma        1.847e-01  3.054e-01   0.605 0.545224    
factor(education_state)Higher Degree     1.093e+00  2.851e-01   3.833 0.000127 ***
factor(education_state)Less than GCSE   -1.808e+00  2.538e-01  -7.123 1.07e-12 ***
factor(labour_state)Family Care         -8.296e-01  5.147e-01  -1.612 0.107015    
factor(labour_state)Government Training  9.408e-02  2.958e+00   0.032 0.974631    
factor(labour_state)Maternity Leave     -1.890e+00  8.503e-01  -2.223 0.026216 *  
factor(labour_state)Other               -3.218e+00  1.069e+00  -3.011 0.002606 ** 
factor(labour_state)Retired              1.028e+00  4.963e-01   2.071 0.038384 *  
factor(labour_state)Self-employed       -8.384e-02  3.764e-01  -0.223 0.823735    
factor(labour_state)Sick/Disabled       -1.098e+01  5.629e-01 -19.506  < 2e-16 ***
factor(labour_state)Student              7.602e-02  4.564e-01   0.167 0.867712    
factor(labour_state)Unemployed          -3.498e+00  5.274e-01  -6.632 3.34e-11 ***
factor(job_sec)1                         1.821e+00  5.824e-01   3.127 0.001766 ** 
factor(job_sec)2                         1.508e+00  5.250e-01   2.872 0.004081 ** 
factor(job_sec)3                         1.457e+00  4.609e-01   3.162 0.001568 ** 
factor(job_sec)4                         1.893e+00  4.868e-01   3.889 0.000101 ***
factor(job_sec)5                         1.319e+00  5.731e-01   2.301 0.021403 *  
factor(job_sec)6                         2.204e+00  5.391e-01   4.088 4.37e-05 ***
factor(job_sec)7                         1.719e+00  4.557e-01   3.772 0.000162 ***
factor(job_sec)8                         8.399e-01  4.953e-01   1.696 0.089907 .  
factor(region)East of England           -2.075e-01  3.344e-01  -0.620 0.534998    
factor(region)London                    -1.700e+00  3.398e-01  -5.002 5.71e-07 ***
factor(region)North East                -2.369e-01  4.199e-01  -0.564 0.572554    
factor(region)North West                 2.036e-01  3.237e-01   0.629 0.529297    
factor(region)Northern Ireland          -1.459e+00  3.705e-01  -3.938 8.23e-05 ***
factor(region)Scotland                   7.987e-01  3.323e-01   2.404 0.016238 *  
factor(region)South East                 3.685e-01  3.108e-01   1.185 0.235846    
factor(region)South West                 7.296e-01  3.382e-01   2.157 0.030981 *  
factor(region)Wales                     -1.121e+00  3.522e-01  -3.183 0.001457 ** 
factor(region)West Midlands             -3.593e-01  3.414e-01  -1.052 0.292631    
factor(region)Yorkshire and The Humber  -9.738e-01  3.385e-01  -2.877 0.004016 ** 
gross_hh_income                          5.668e-05  1.465e-05   3.869 0.000110 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

Residual standard error: 15.25 on 51031 degrees of freedom
Multiple R-squared:  0.0599,	Adjusted R-squared:  0.05901 
F-statistic: 67.74 on 48 and 51031 DF,  p-value: < 2.2e-16


