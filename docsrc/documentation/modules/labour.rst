======
Labour
======


Labour
======

Introductory fluff. Why do we need this module? test reference (Nelson
1987).

Methods
-------

What methods are used? Justification due to output data type.
explanation of model output.

Data
----

What variables are included? Why is this output chosen. What explanatory
variables are used and why are they chosen

Results
-------

What are the results. Coefficients tables. diagnostic plots. measures of
goodness of fit.

::

   ## Call:
   ## multinom(formula = factor(y) ~ (factor(sex) + factor(ethnicity) + 
   ##     age + factor(education_state) + SF_12 + factor(housing_quality) + 
   ##     factor(labour_state) + factor(job_sec) + hh_income + alcohol_spending), 
   ##     data = data, weights = weight, MaxNWts = 10000, maxit = 10000)
   ## 
   ## Coefficients:
   ##                 (Intercept) factor(sex)Male factor(ethnicity)BLA factor(ethnicity)BLC factor(ethnicity)CHI
   ## Family Care      -2.9497345     -1.36541687           -0.7948968           -1.6277063           0.11817892
   ## Maternity Leave  -3.5820257     -4.44527918          -11.7371518          -14.5349570          -9.92827393
   ## PT Employed      -2.0448978     -0.92764147           -0.9306805           -0.9331177          -1.40619415
   ## Retired         -12.8295628     -0.08102316           -0.9429840           -0.3920822          -1.16563853
   ## Self-employed    -4.0093586      0.25315997           -1.4027270           -0.8531256          -0.02967332
   ## Sick/Disabled    -1.9664480     -0.36764454           -0.3290371           -0.5739203          -8.23754301
   ## Student           1.8892772     -0.34221553           -0.4584254           -0.4811614          -0.29158755
   ## Unemployed        0.2799377      0.24892489           -1.4686023            0.1650021          -1.58511178
   ##                 factor(ethnicity)IND factor(ethnicity)MIX factor(ethnicity)OAS factor(ethnicity)OBL
   ## Family Care               0.14030977           -1.5509210           -0.8945242            0.2519840
   ## Maternity Leave          -0.30264122           -0.4033260          -13.3046146          -15.0408827
   ## PT Employed              -0.51132272           -1.1165830           -1.5637029          -30.0231856
   ## Retired                   0.01581089           -0.5724423           -0.4387145           -2.3985793
   ## Self-employed             0.70942239            0.1098976           -2.5231531           -0.3128006
   ## Sick/Disabled            -0.50565692           -0.6655297           -2.2586774            1.4285698
   ## Student                  -0.32663740           -0.7408731           -0.3964799            1.8573672
   ## Unemployed               -0.16819318           -0.6845342           -0.7946784          -24.5867351
   ##                 factor(ethnicity)OTH factor(ethnicity)PAK factor(ethnicity)WBI factor(ethnicity)WHO          age
   ## Family Care               -1.6345895           1.24418171           -0.4067465           -1.4172374  0.035376075
   ## Maternity Leave            2.3924637         -12.10388834            0.5926260            1.0201013 -0.080272476
   ## PT Employed                0.2693373          -0.50732873           -0.7221293           -0.9717529  0.020186477
   ## Retired                    0.8772435           1.39822587            0.2204762           -0.2300769  0.194189896
   ## Self-employed              1.4927405           0.57414890           -0.7972023           -0.4008622  0.012225839
   ## Sick/Disabled             -0.5659292           0.09443374            0.3455181            0.1379029  0.037682591
   ## Student                    0.6866963          -0.35259251           -0.9668251           -1.7488775 -0.144099422
   ## Unemployed                -0.6127510          -0.18341167           -0.7577150           -0.8377109  0.008186388
   ##                 factor(education_state)1 factor(education_state)2 factor(education_state)3 factor(education_state)5
   ## Family Care                   0.74281014               0.52131484              0.596315923              0.384622621
   ## Maternity Leave               1.36589408              -0.48892543              0.905280375              0.107928538
   ## PT Employed                   0.01132911               0.07981087              0.311845118              0.040625580
   ## Retired                      -0.48440358              -0.01572557              0.267113484              0.102445363
   ## Self-employed                -0.63219523              -0.04237620             -0.135584555             -0.331883602
   ## Sick/Disabled                 0.27535789              -0.10294973             -0.558452297              0.316274693
   ## Student                      -0.26800074              -0.20411862              0.161242861              0.008156958
   ## Unemployed                   -0.03018320               0.06864482             -0.003671677             -0.240458470
   ##                 factor(education_state)6 factor(education_state)7        SF_12 factor(housing_quality)2
   ## Family Care                  -0.07609724              0.087652654 -0.013810509                0.5922054
   ## Maternity Leave              -0.10104216              0.435330665  0.017592620                1.2082372
   ## PT Employed                  -0.07433417              0.058489111 -0.005160245               -0.5429169
   ## Retired                      -0.11644864             -0.006395467  0.002690721                0.1882706
   ## Self-employed                -0.28381293             -0.125804959  0.001887230                0.0554855
   ## Sick/Disabled                -0.72358208             -1.254921747 -0.040867556                0.1536673
   ## Student                      -0.29540605              0.377481315 -0.004174788               -0.4718893
   ## Unemployed                   -0.50220911             -0.253726649 -0.020076719               -0.6316680
   ##                 factor(housing_quality)3 factor(labour_state)Family Care factor(labour_state)Maternity Leave
   ## Family Care                   0.69240451                      3.79090641                          3.58710344
   ## Maternity Leave               1.19095258                     -0.05666984                          1.16444014
   ## PT Employed                  -0.48220328                      2.19612785                          2.17277135
   ## Retired                       0.13319220                      1.87652818                         -6.89971549
   ## Self-employed                -0.01169744                      2.27586925                          1.59875575
   ## Sick/Disabled                -0.39742215                      1.19298909                       -260.62780461
   ## Student                      -0.52794690                    -10.73850272                         -0.01132441
   ## Unemployed                   -1.20564260                      2.17230699                          1.57974732
   ##                 factor(labour_state)PT Employed factor(labour_state)Retired factor(labour_state)Self-employed
   ## Family Care                            1.516738                    2.120639                         1.7819615
   ## Maternity Leave                        1.295354                    3.309351                         0.7815352
   ## PT Employed                            3.426520                    2.661703                         1.7489819
   ## Retired                                1.831565                    4.771644                         2.1743918
   ## Self-employed                          1.543264                    3.226062                         5.2843949
   ## Sick/Disabled                          1.417359                    2.027793                         0.2700767
   ## Student                                2.522705                   -4.368500                         1.6741382
   ## Unemployed                             1.292714                    1.792941                         1.9979514
   ##                 factor(labour_state)Sick/Disabled factor(labour_state)Student factor(labour_state)Unemployed
   ## Family Care                              1.935282                  -0.8837657                      1.1063835
   ## Maternity Leave                          2.601701                  -2.5521503                    -14.7375055
   ## PT Employed                              2.287280                   2.3489924                      1.7425244
   ## Retired                                  2.883320                 -12.6548198                      0.4179273
   ## Self-employed                            2.927572                   1.4983159                      2.1937774
   ## Sick/Disabled                            5.641920                  -1.6945415                      0.9691273
   ## Student                                  2.745633                   4.0794835                      1.9894943
   ## Unemployed                               3.422059                   1.3017956                      2.3535479
   ##                 factor(job_sec)1 factor(job_sec)2 factor(job_sec)3 factor(job_sec)4 factor(job_sec)5 factor(job_sec)6
   ## Family Care          -14.4751942      -3.45519640      -3.69872191       -3.2317550      -1.39655762      -2.87498594
   ## Maternity Leave       -0.1171488      -0.13099896       0.10179132       -1.2738393      -0.04224619      -0.13833148
   ## PT Employed           -0.8752487      -0.38142249       0.05475755        0.2410632       0.56945373       0.15998216
   ## Retired               -1.9746011      -2.54572438      -2.10441341       -2.1218438      -1.54366683      -1.50534412
   ## Self-employed         -0.5102614      -0.09063855      -0.12740650       -0.7183060       1.96288755      -0.03350326
   ## Sick/Disabled        -17.9271127      -2.71692686      -3.97168935       -5.0736450      -0.72462714      -2.68418075
   ## Student              -12.5475088      -1.82691729      -0.41485274       -0.6318453       1.40921165      -1.05780877
   ## Unemployed            -1.8752435      -2.75788822      -2.55311932       -1.7592651      -1.22182163      -2.02281948
   ##                 factor(job_sec)7 factor(job_sec)8     hh_income alcohol_spending
   ## Family Care          -2.99004929      -2.24253800 -2.997223e-05     6.199353e-04
   ## Maternity Leave      -0.93112652       0.03554928  1.872417e-04    -4.635891e-03
   ## PT Employed           0.49340171       0.54900127 -8.909814e-07     6.946914e-05
   ## Retired              -2.61530352      -2.53350837  5.833198e-05     1.082706e-03
   ## Self-employed        -0.85359953      -0.37689126  1.313467e-04     1.608024e-04
   ## Sick/Disabled        -3.22156526      -3.18921149  2.133250e-06     2.303288e-04
   ## Student              -0.02686193      -0.38769200 -3.042457e-05     9.604474e-04
   ## Unemployed           -1.45315740      -1.47282109 -6.663903e-05    -1.103043e-03
   ## 
   ## Std. Errors:
   ##                  (Intercept) factor(sex)Male factor(ethnicity)BLA factor(ethnicity)BLC factor(ethnicity)CHI
   ## Family Care     4.342442e-04    5.623153e-04         7.809779e-05         8.805471e-06         1.671869e-05
   ## Maternity Leave 1.804763e-05    2.439986e-06         1.879394e-11         3.585074e-13         5.917406e-11
   ## PT Employed     1.154584e-03    1.459168e-03         1.181447e-04         5.361772e-05         1.743577e-05
   ## Retired         8.478321e-05    1.852017e-03         1.338332e-05         1.408630e-05         3.247547e-06
   ## Self-employed   3.329921e-04    1.840927e-03         9.024914e-05         3.829343e-05         3.455447e-05
   ## Sick/Disabled   4.835214e-04    1.061065e-03         3.902344e-05         4.113404e-05         6.626953e-10
   ## Student         3.872745e-04    2.026454e-03         1.542764e-04         4.248369e-05         1.780322e-05
   ## Unemployed      8.679271e-04    1.606898e-03         9.869143e-05         1.044638e-04         7.557315e-06
   ##                 factor(ethnicity)IND factor(ethnicity)MIX factor(ethnicity)OAS factor(ethnicity)OBL
   ## Family Care             1.078441e-04         1.117251e-05         1.303290e-04         9.577063e-06
   ## Maternity Leave         2.652242e-06         1.304866e-06         7.521860e-12         3.010032e-14
   ## PT Employed             1.952642e-04         1.273906e-04         8.906847e-05         5.452938e-18
   ## Retired                 5.303829e-05         1.134785e-05         3.455446e-05         1.705537e-06
   ## Self-employed           3.005222e-04         1.356333e-04         9.744535e-05         6.073181e-06
   ## Sick/Disabled           6.519363e-05         3.757706e-05         5.426632e-06         9.895064e-06
   ## Student                 2.152227e-04         2.750316e-04         1.463397e-04         1.119009e-05
   ## Unemployed              3.037847e-04         1.729166e-04         1.438581e-04         2.653400e-16
   ##                 factor(ethnicity)OTH factor(ethnicity)PAK factor(ethnicity)WBI factor(ethnicity)WHO          age
   ## Family Care             9.175514e-06         1.743482e-04         1.065500e-03         3.290276e-04 7.789890e-05
   ## Maternity Leave         5.580979e-06         7.130926e-12         5.320196e-05         4.505423e-05 1.922297e-04
   ## PT Employed             3.497209e-05         1.061181e-04         1.334246e-03         1.076443e-03 4.802763e-05
   ## Retired                 1.518061e-05         3.907925e-05         3.043353e-04         1.151972e-04 7.514448e-05
   ## Self-employed           8.790333e-05         1.302100e-04         1.528607e-03         5.729616e-04 7.151329e-05
   ## Sick/Disabled           1.031165e-05         3.504362e-05         7.245953e-04         1.404643e-04 7.772225e-05
   ## Student                 2.635773e-05         2.018670e-04         1.733217e-03         4.710982e-04 1.415025e-04
   ## Unemployed              4.406198e-05         2.600604e-04         1.540329e-03         5.794466e-04 5.636969e-05
   ##                 factor(education_state)1 factor(education_state)2 factor(education_state)3 factor(education_state)5
   ## Family Care                 1.071588e-04             1.457235e-03             2.976536e-04             1.717052e-04
   ## Maternity Leave             6.608865e-06             2.242433e-05             6.192421e-05             3.424644e-05
   ## PT Employed                 3.759206e-05             1.335557e-03             1.595889e-03             1.783358e-03
   ## Retired                     5.966897e-05             1.775871e-03             2.057461e-04             2.760753e-04
   ## Self-employed               5.908347e-05             1.353200e-03             4.038160e-04             2.323421e-04
   ## Sick/Disabled               5.022223e-05             1.210784e-03             1.752387e-04             1.519234e-04
   ## Student                     1.075098e-05             1.493713e-03             1.303170e-03             1.319873e-04
   ## Unemployed                  4.351493e-05             1.533300e-03             1.420826e-03             1.934243e-04
   ##                 factor(education_state)6 factor(education_state)7        SF_12 factor(housing_quality)2
   ## Family Care                 3.281584e-04             1.866491e-04 7.653249e-05             1.260793e-03
   ## Maternity Leave             4.386918e-05             5.909469e-05 1.360279e-04             6.742856e-05
   ## PT Employed                 1.476272e-03             1.663749e-03 5.399319e-05             8.932971e-04
   ## Retired                     8.124449e-04             5.171476e-04 8.760085e-05             1.109532e-03
   ## Self-employed               1.754936e-03             1.482655e-03 6.831498e-05             1.096710e-03
   ## Sick/Disabled               1.446236e-04             9.819000e-05 8.188384e-05             9.654297e-04
   ## Student                     2.501431e-04             1.629361e-04 7.628102e-05             1.220661e-03
   ## Unemployed                  5.580456e-04             3.655798e-04 5.532430e-05             1.126556e-03
   ##                 factor(housing_quality)3 factor(labour_state)Family Care factor(labour_state)Maternity Leave
   ## Family Care                 1.180723e-03                    1.602808e-03                        8.985609e-05
   ## Maternity Leave             6.763619e-05                    5.799370e-06                        1.986301e-05
   ## PT Employed                 9.857155e-04                    2.766135e-04                        3.185640e-04
   ## Retired                     1.068212e-03                    2.634625e-04                        3.084222e-10
   ## Self-employed               1.001123e-03                    1.338237e-04                        4.769826e-05
   ## Sick/Disabled               6.917951e-04                    3.167163e-04                       1.092114e-119
   ## Student                     1.158887e-03                    1.082084e-10                        5.150664e-06
   ## Unemployed                  1.113581e-03                    8.208203e-04                        3.574125e-05
   ##                 factor(labour_state)PT Employed factor(labour_state)Retired factor(labour_state)Self-employed
   ## Family Care                        2.247457e-04                4.815378e-04                      1.233455e-04
   ## Maternity Leave                    6.895016e-05                1.225137e-05                      1.758022e-05
   ## PT Employed                        1.306760e-03                3.577849e-04                      3.699376e-04
   ## Retired                            9.682588e-04                1.626870e-03                      4.497132e-04
   ## Self-employed                      3.971318e-04                2.539942e-04                      1.477054e-03
   ## Sick/Disabled                      1.142338e-04                4.248092e-04                      3.658187e-05
   ## Student                            7.477603e-04                1.149476e-09                      7.314916e-05
   ## Unemployed                         4.929702e-04                2.417982e-04                      2.064404e-04
   ##                 factor(labour_state)Sick/Disabled factor(labour_state)Student factor(labour_state)Unemployed
   ## Family Care                          1.098583e-04                4.934618e-05                   7.015585e-04
   ## Maternity Leave                      8.321274e-06                6.350274e-06                   4.180367e-12
   ## PT Employed                          6.100748e-05                9.933094e-04                   4.144204e-04
   ## Retired                              3.455040e-04                3.455623e-11                   1.383670e-04
   ## Self-employed                        4.991741e-05                1.525295e-04                   3.324166e-04
   ## Sick/Disabled                        1.509525e-03                1.617104e-05                   8.086136e-04
   ## Student                              1.316903e-05                1.467587e-03                   3.456711e-04
   ## Unemployed                           1.122855e-03                9.933811e-04                   1.566308e-03
   ##                 factor(job_sec)1 factor(job_sec)2 factor(job_sec)3 factor(job_sec)4 factor(job_sec)5 factor(job_sec)6
   ## Family Care         3.039978e-10     4.127454e-05     1.315257e-04     9.998751e-05     9.747108e-05     4.862156e-05
   ## Maternity Leave     4.028923e-06     2.475044e-05     6.024942e-05     1.875085e-05     8.330642e-06     8.073375e-06
   ## PT Employed         1.038607e-04     5.610007e-04     1.378038e-03     1.494413e-03     2.428316e-04     4.715531e-04
   ## Retired             5.326735e-05     1.260184e-04     7.238485e-04     2.714788e-04     3.242490e-04     1.464736e-04
   ## Self-employed       7.952528e-05     7.935532e-04     1.720729e-03     1.596218e-04     1.040548e-03     1.802849e-04
   ## Sick/Disabled       6.393871e-12     3.176662e-05     4.420321e-05     7.781330e-06     4.480147e-05     5.893138e-05
   ## Student             1.127809e-10     2.577772e-05     2.388133e-04     1.245008e-04     6.319745e-05     3.688589e-05
   ## Unemployed          5.608839e-05     5.692383e-05     2.343427e-04     2.097156e-04     1.271489e-04     8.469653e-05
   ##                 factor(job_sec)7 factor(job_sec)8    hh_income alcohol_spending
   ## Family Care         1.432280e-04     1.296934e-04 7.263170e-07     1.469334e-05
   ## Maternity Leave     2.623497e-05     4.357722e-05 7.977769e-07     3.959363e-05
   ## PT Employed         1.326299e-03     1.607418e-03 5.546498e-07     9.172823e-06
   ## Retired             2.775361e-04     1.947507e-04 6.155210e-07     1.326850e-05
   ## Self-employed       1.861835e-04     1.762337e-04 6.036379e-07     1.272284e-05
   ## Sick/Disabled       7.939485e-05     4.973675e-05 9.413016e-07     1.682318e-05
   ## Student             8.216236e-04     1.783408e-04 1.033192e-06     1.544872e-05
   ## Unemployed          6.949220e-04     3.753802e-04 5.745550e-07     1.406929e-05
   ## 
   ## Residual Deviance: 51171549 
   ## AIC: 51172205

References
----------

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-1987:nelson

      Nelson, Edward. 1987. *Radically Elementary Probability Theory*.
      Princeton University Press.
