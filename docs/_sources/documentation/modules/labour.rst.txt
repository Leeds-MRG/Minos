======
Labour
======


Labour
======

Labour state is a measure of what an individual does. There are 8
distinctive categories including employment, unemployment, and retired.
The encodings of these states can be found
[here]](https://leeds-mrg.github.io/Minos/documentation/data_tables.html).

.. figure:: ./figure/labour_barchart-1.png
   :alt: plot of chunk labour_barchart

   plot of chunk labour_barchart

Methods
-------

Labour state is a complex categorical data type. Single layer neural
network is a simple way to estimate this state. Use multinom function
from R’s nnet package. Formula for weights included given as.

.. math:: labour\_state\_next = sex + ethnicity + age + education\_state + SF\_12 + housing\_quality + labour\_state + job\_sec + hh\_income + alcohol\_spending

Data
----

Variables used in this model. Encodings for discrete variables found in
data tables.

-  sex. Biological sex male/female.
-  ethnicity. Ethnicity e.g. white british. XXXX cite.
-  age in years. XXXX cite.
-  education. Highest qualification attained. XXXX cite
-  sf12. Mental well-being score. XXXX cite
-  housing quality. Number of household appliances. Ordinal 1-3. XXXX
   cite
-  labour_state. Previous labour state. XXXX cite. Probably remove this.
   dominates prediction..
-  nssec. Socioeconomic code of job. Indicates job quality with 1-9
   ordinal variable. XXXX cite
-  household income. Monthly disposable income of individuals household.
   XXXX cite.
-  alcohol spending. How much is spent on alcohol. XXXX cite. remove.

Results
-------

-  hard to determine goodness of fit.
-  use confusion matrix to estimate quality of fit.
-  employed/retired well predicted. unemployed/student volatile socially
   and expectedly hard to predict.
-  some deterministic replacement needed for categories like student
   that have specific time frames. e.g. three years for a degree.

::

   ## Call:
   ## multinom(formula = factor(y) ~ (factor(sex) + factor(ethnicity) + 
   ##     age + factor(education_state) + SF_12 + factor(housing_quality) + 
   ##     factor(labour_state) + hh_income + alcohol_spending), data = data, 
   ##     weights = weight, model = T, MaxNWts = 10000, maxit = 10000)
   ## 
   ## Coefficients:
   ##                 (Intercept) factor(sex)Male factor(ethnicity)BLA factor(ethnicity)BLC factor(ethnicity)CHI
   ## Family Care       -5.427838     -1.36857506           -0.6854990          -1.61967630           -0.1168765
   ## Maternity Leave   -4.174710     -4.32161486          -23.1671344         -20.22088647          -16.8218525
   ## PT Employed       -1.814235     -0.92564199           -0.8120645          -0.77909500           -1.2961382
   ## Retired          -15.216159     -0.08983041           -0.6573547          -0.01085643           -1.5971170
   ## Self-employed     -4.788733      0.26504673           -1.0965227          -0.66715948            0.3675381
   ## Sick/Disabled     -4.914758     -0.23076341            0.1400658          -0.30508870          -17.9304311
   ## Student            1.633007     -0.36372813           -0.4278495          -0.50463144           -0.4346266
   ## Unemployed        -1.265769      0.27796978           -1.2455510           0.30113430           -1.7425558
   ##                 factor(ethnicity)IND factor(ethnicity)MIX factor(ethnicity)OAS factor(ethnicity)OBL
   ## Family Care              -0.08170559           -1.6425998          -0.83297883           0.25500914
   ## Maternity Leave          -0.10550090           -0.2270516         -19.87848320         -16.77600590
   ## PT Employed              -0.28362777           -1.0626890          -1.42013438         -18.45672870
   ## Retired                   0.21490745           -0.6083682          -0.01333375          -2.03725076
   ## Self-employed             1.07615647            0.3597318          -2.02401797          -0.03832563
   ## Sick/Disabled            -0.31695873           -0.3590320          -1.96524134           1.70411172
   ## Student                  -0.34367785           -0.7904874          -0.52019509           1.99386593
   ## Unemployed               -0.16273349           -0.6285184          -0.64270988         -12.97353289
   ##                 factor(ethnicity)OTH factor(ethnicity)PAK factor(ethnicity)WBI factor(ethnicity)WHO          age
   ## Family Care              -0.89505200           1.36791557           -0.4621093          -1.39726289  0.031752630
   ## Maternity Leave           2.70763648         -19.42822346            0.8050632           1.28558528 -0.074786069
   ## PT Employed               0.40751410          -0.31051958           -0.5859156          -0.77982293  0.018568577
   ## Retired                   0.09228302           1.76187406            0.5119257          -0.04689624  0.195398226
   ## Self-employed             1.66354992           1.08453761           -0.4272246           0.01478191  0.015759164
   ## Sick/Disabled            -0.38961378           0.49030224            0.5332637           0.35976890  0.035474558
   ## Student                   0.59860185          -0.22471416           -0.9321785          -1.60536744 -0.146478667
   ## Unemployed               -0.88988177           0.06394131           -0.6285829          -0.77625025  0.004275371
   ##                 factor(education_state)1 factor(education_state)2 factor(education_state)3 factor(education_state)5
   ## Family Care                   0.83527379               0.64198978                0.6193079              0.350489819
   ## Maternity Leave               1.82944596              -0.46533069                0.8926128              0.287960794
   ## PT Employed                  -0.02224803               0.16201937                0.3500865             -0.025950157
   ## Retired                      -0.40534713              -0.01191589                0.2842306              0.154118192
   ## Self-employed                -0.26657306              -0.02998956               -0.1797569             -0.390600894
   ## Sick/Disabled                 0.27379541              -0.15330549               -0.7222727              0.073203488
   ## Student                      -0.24770936              -0.16164739                0.1141930             -0.006217061
   ## Unemployed                   -0.03089045               0.04474756               -0.1149388             -0.360550704
   ##                 factor(education_state)6 factor(education_state)7         SF_12 factor(housing_quality)2
   ## Family Care                  -0.08149697             -0.061919449 -0.0149230757                0.4422199
   ## Maternity Leave               0.19148931              0.714918763  0.0176925914                0.9982074
   ## PT Employed                  -0.16168292             -0.075174142 -0.0058728033               -0.5890025
   ## Retired                      -0.03885064              0.004699173  0.0002808132                0.3268997
   ## Self-employed                -0.37149139             -0.281546857  0.0005757246                0.2173479
   ## Sick/Disabled                -0.89726317             -1.652084951 -0.0423454912                0.2051458
   ## Student                      -0.35988915              0.331056396 -0.0056564699               -0.5094467
   ## Unemployed                   -0.70481604             -0.472356909 -0.0211076243               -0.6497516
   ##                 factor(housing_quality)3 factor(labour_state)Family Care factor(labour_state)Maternity Leave
   ## Family Care                    0.6057731                        6.560573                         2.801650857
   ## Maternity Leave                1.0727501                      -27.050365                         0.855041149
   ## PT Employed                   -0.5639443                        2.029644                         2.183333136
   ## Retired                        0.2992377                        3.669181                       -11.670117758
   ## Self-employed                  0.1621438                        2.496280                         1.798705071
   ## Sick/Disabled                 -0.4121029                        4.189506                        -7.422299110
   ## Student                       -0.5559980                       -7.175352                        -0.008006713
   ## Unemployed                    -1.2712642                        3.825683                         1.416516254
   ##                 factor(labour_state)PT Employed factor(labour_state)Retired factor(labour_state)Self-employed
   ## Family Care                            1.528821                    4.857081                         2.5617401
   ## Maternity Leave                        1.125087                    3.448937                         0.9534827
   ## PT Employed                            3.557821                    2.693552                         1.8331160
   ## Retired                                1.614635                    6.636309                         2.2120142
   ## Self-employed                          1.452299                    3.460900                         6.3530827
   ## Sick/Disabled                          1.127642                    4.989487                         1.4990161
   ## Student                                2.674685                   -9.164293                         2.5631426
   ## Unemployed                             1.399081                    3.501194                         2.1409753
   ##                 factor(labour_state)Sick/Disabled factor(labour_state)Student factor(labour_state)Unemployed
   ## Family Care                              4.466846                    1.678199                       3.829434
   ## Maternity Leave                          2.904895                   -2.257192                     -19.550671
   ## PT Employed                              2.255641                    2.406895                       1.529357
   ## Retired                                  4.541592                  -18.866016                       2.342506
   ## Self-employed                            3.173077                    1.790859                       2.241078
   ## Sick/Disabled                            8.208586                    1.008471                       3.874616
   ## Student                                  3.218337                    4.501494                       2.469657
   ## Unemployed                               4.877558                    2.785955                       4.089258
   ##                     hh_income alcohol_spending
   ## Family Care     -5.771935e-05    -1.928691e-05
   ## Maternity Leave  2.009409e-04    -5.651168e-03
   ## PT Employed     -3.284892e-05    -1.495630e-04
   ## Retired          3.129454e-05     6.816018e-04
   ## Self-employed    1.017149e-04     3.447984e-04
   ## Sick/Disabled   -3.880891e-05    -8.945572e-04
   ## Student         -5.723791e-05     7.672958e-04
   ## Unemployed      -9.100369e-05    -1.868479e-03
   ## 
   ## Std. Errors:
   ##                  (Intercept) factor(sex)Male factor(ethnicity)BLA factor(ethnicity)BLC factor(ethnicity)CHI
   ## Family Care     3.599990e-04    5.183946e-04         7.577712e-05         8.242053e-06         1.875153e-05
   ## Maternity Leave 1.604664e-05    1.737667e-06         1.358760e-16         1.031065e-15         2.995950e-14
   ## PT Employed     1.042258e-03    1.421046e-03         1.088879e-04         5.112275e-05         1.593181e-05
   ## Retired         7.925086e-05    1.850908e-03         1.289113e-05         1.506194e-05         5.717021e-06
   ## Self-employed   2.929192e-04    1.826746e-03         9.684570e-05         3.433277e-05         3.389267e-05
   ## Sick/Disabled   4.203337e-04    1.077658e-03         3.424897e-05         3.544523e-05         5.986399e-14
   ## Student         3.869903e-04    1.518819e-03         1.239351e-04         3.612408e-05         1.228684e-05
   ## Unemployed      7.412049e-04    1.528355e-03         8.613568e-05         9.945933e-05         7.147975e-06
   ##                 factor(ethnicity)IND factor(ethnicity)MIX factor(ethnicity)OAS factor(ethnicity)OBL
   ## Family Care             8.836709e-05         1.138355e-05         1.241400e-04         9.078023e-06
   ## Maternity Leave         2.068933e-06         1.478327e-06         7.065474e-15         3.908089e-15
   ## PT Employed             2.073072e-04         1.186170e-04         8.544246e-05         3.930693e-13
   ## Retired                 5.428162e-05         9.932918e-06         3.448674e-05         1.816830e-06
   ## Self-employed           3.043581e-04         1.049072e-04         1.093481e-04         5.890649e-06
   ## Sick/Disabled           4.733190e-05         3.145531e-05         4.583401e-06         9.622405e-06
   ## Student                 1.721469e-04         2.128175e-04         1.171347e-04         8.581789e-06
   ## Unemployed              2.645788e-04         1.545851e-04         1.284842e-04         2.134065e-11
   ##                 factor(ethnicity)OTH factor(ethnicity)PAK factor(ethnicity)WBI factor(ethnicity)WHO          age
   ## Family Care             9.585206e-06         1.668627e-04         0.0009689715         0.0003104709 7.771488e-05
   ## Maternity Leave         5.435843e-06         2.400686e-15         0.0000484338         0.0000383771 1.862969e-04
   ## PT Employed             3.357588e-05         1.081069e-04         0.0013187616         0.0008978079 4.727082e-05
   ## Retired                 7.807769e-06         3.801897e-05         0.0002860321         0.0001059179 7.364582e-05
   ## Self-employed           6.768732e-05         1.332946e-04         0.0014847507         0.0005444977 6.848791e-05
   ## Sick/Disabled           8.408838e-06         3.282260e-05         0.0006146231         0.0001243856 7.531224e-05
   ## Student                 2.244485e-05         1.605749e-04         0.0014272502         0.0004181797 1.370782e-04
   ## Unemployed              3.499568e-05         2.404168e-04         0.0015018359         0.0005405674 5.586679e-05
   ##                 factor(education_state)1 factor(education_state)2 factor(education_state)3 factor(education_state)5
   ## Family Care                 1.030369e-04             1.498075e-03             2.724664e-04             1.963428e-04
   ## Maternity Leave             6.970519e-06             1.824675e-05             5.916121e-05             3.785673e-05
   ## PT Employed                 3.468506e-05             1.250300e-03             1.541783e-03             1.787870e-03
   ## Retired                     6.468724e-05             1.770359e-03             2.343066e-04             2.882314e-04
   ## Self-employed               6.995343e-05             1.445002e-03             4.822518e-04             2.867011e-04
   ## Sick/Disabled               5.154466e-05             1.203295e-03             1.448427e-04             1.578403e-04
   ## Student                     1.102772e-05             1.480586e-03             1.275723e-03             1.251753e-04
   ## Unemployed                  4.202708e-05             1.501612e-03             1.075742e-03             1.868384e-04
   ##                 factor(education_state)6 factor(education_state)7        SF_12 factor(housing_quality)2
   ## Family Care                 3.598006e-04             0.0001897791 7.695239e-05             1.239252e-03
   ## Maternity Leave             4.442776e-05             0.0000514736 1.326199e-04             5.763622e-05
   ## PT Employed                 1.441987e-03             0.0016964304 5.215361e-05             8.709305e-04
   ## Retired                     7.632435e-04             0.0004408949 8.604771e-05             1.105561e-03
   ## Self-employed               1.783756e-03             0.0009938443 6.555011e-05             1.067965e-03
   ## Sick/Disabled               1.555724e-04             0.0001123603 8.015271e-05             9.284825e-04
   ## Student                     2.131216e-04             0.0001417418 7.548853e-05             1.216606e-03
   ## Unemployed                  5.095567e-04             0.0003075911 5.371171e-05             1.106591e-03
   ##                 factor(housing_quality)3 factor(labour_state)Family Care factor(labour_state)Maternity Leave
   ## Family Care                 1.153711e-03                    1.672145e-03                        5.357447e-05
   ## Maternity Leave             5.621207e-05                    9.553555e-18                        1.504999e-05
   ## PT Employed                 9.330019e-04                    3.077129e-04                        2.215877e-04
   ## Retired                     1.061355e-03                    2.406723e-04                        2.481804e-12
   ## Self-employed               9.693579e-04                    1.301847e-04                        5.793731e-05
   ## Sick/Disabled               6.717642e-04                    3.698338e-04                        8.977211e-10
   ## Student                     1.156117e-03                    2.710250e-09                        5.393807e-06
   ## Unemployed                  1.052262e-03                    7.918922e-04                        2.986506e-05
   ##                 factor(labour_state)PT Employed factor(labour_state)Retired factor(labour_state)Self-employed
   ## Family Care                        2.228520e-04                4.573180e-04                      1.295523e-04
   ## Maternity Leave                    5.319895e-05                1.397646e-05                      2.211520e-05
   ## PT Employed                        1.286473e-03                3.768409e-04                      4.115961e-04
   ## Retired                            9.220664e-04                1.696325e-03                      3.854377e-04
   ## Self-employed                      4.064363e-04                2.566427e-04                      1.731318e-03
   ## Sick/Disabled                      9.386838e-05                4.559525e-04                      2.805343e-05
   ## Student                            5.277678e-04                4.025272e-12                      6.839712e-05
   ## Unemployed                         3.590046e-04                2.467990e-04                      2.462873e-04
   ##                 factor(labour_state)Sick/Disabled factor(labour_state)Student factor(labour_state)Unemployed
   ## Family Care                          1.301395e-04                4.688722e-05                   6.863905e-04
   ## Maternity Leave                      1.017169e-05                3.965230e-06                   2.352938e-14
   ## PT Employed                          6.196837e-05                9.714964e-04                   4.395201e-04
   ## Retired                              4.075096e-04                8.452563e-15                   1.492057e-04
   ## Self-employed                        6.684261e-05                1.237549e-04                   2.859285e-04
   ## Sick/Disabled                        1.522054e-03                1.580962e-05                   7.267649e-04
   ## Student                              1.753183e-05                1.327969e-03                   2.786079e-04
   ## Unemployed                           1.027338e-03                9.703733e-04                   1.642992e-03
   ##                    hh_income alcohol_spending
   ## Family Care     6.609737e-07     1.511865e-05
   ## Maternity Leave 7.600733e-07     4.152949e-05
   ## PT Employed     4.900454e-07     9.096333e-06
   ## Retired         5.906249e-07     1.340972e-05
   ## Self-employed   6.284636e-07     1.147906e-05
   ## Sick/Disabled   8.443992e-07     2.001233e-05
   ## Student         9.691558e-07     1.500951e-05
   ## Unemployed      4.748604e-07     1.473291e-05
   ## 
   ## Residual Deviance: 52532654 
   ## AIC: 52533182

.. figure:: ./figure/labour_output-1.png
   :alt: plot of chunk labour_output

   plot of chunk labour_output

References
----------
