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

   ## Warning in sqrt(diag(vc)): NaNs produced

::

   ## Call:
   ## multinom(formula = factor(labour_state_next) ~ factor(sex) + 
   ##     factor(ethnicity) + scale(age) + factor(education_state) + 
   ##     scale(SF_12) + factor(housing_quality) + factor(job_sec) + 
   ##     scale(hh_income) + scale(alcohol_spending), data = data, 
   ##     weights = weight, model = T, MaxNWts = 10000, maxit = 10000)
   ## 
   ## Coefficients:
   ##                 (Intercept) factor(sex)Male factor(ethnicity)BLA factor(ethnicity)BLC factor(ethnicity)CHI
   ## Family Care       2.0700647     -2.60518211           -0.9825768           -3.1575459           -0.1764825
   ## Maternity Leave -38.3320663     -4.54435271          -16.9272681          -23.6746620          -34.5183986
   ## PT Employed       0.5913872     -1.68303171           -0.5361685           -0.6654445           -1.2043192
   ## Retired          -1.5364465     -0.53179641           -0.8914463           -0.6807451           -0.7120798
   ## Self-employed    -1.5257471      0.12555586           -1.0256513           -0.6595954           -1.0410456
   ## Sick/Disabled     0.5963203     -0.49059863            1.0232892            0.6074573           -7.7029250
   ## Student          -5.2482373     -0.71448946           -0.4674698           -0.7731220           -0.8121577
   ## Unemployed        2.4851230     -0.03163507           -1.7616146            0.1735088           -1.6126293
   ##                 factor(ethnicity)IND factor(ethnicity)MIX factor(ethnicity)OAS factor(ethnicity)OBL
   ## Family Care              -0.96730860           -3.0299880           -0.9139955           -1.8968120
   ## Maternity Leave          -0.41657743           -0.1773812          -20.4626167          -28.7748963
   ## PT Employed              -0.19253822           -0.8721669           -0.6298375         -505.1255102
   ## Retired                   0.42407907           -0.3142946           -0.6781151           -1.6194193
   ## Self-employed             0.01005406            0.1984501           -1.5638888            0.1037002
   ## Sick/Disabled             0.41939995            0.7160362           -2.3485362            0.7998032
   ## Student                  -0.52396602           -1.0035423            0.4116776            4.4193991
   ## Unemployed               -0.24450372           -0.3681087           -0.3822971          -24.7735726
   ##                 factor(ethnicity)OTH factor(ethnicity)PAK factor(ethnicity)WBI factor(ethnicity)WHO scale(age)
   ## Family Care               -1.5732255           0.57257107           -1.1728068           -1.5417463  0.6489328
   ## Maternity Leave            2.4250770         -18.92205878            0.7429532            1.1368146 -1.3172818
   ## PT Employed                0.1390558           0.05806469           -0.2300265           -0.5540156  0.4164365
   ## Retired                   -0.3664190           0.77612818            0.4186166           -0.1725794  6.1705704
   ## Self-employed              0.2428048           0.04355558           -0.8833137           -0.8527529  0.5297521
   ## Sick/Disabled            -23.0068627           0.23361161            1.2273323            0.7263442  1.1362123
   ## Student                    0.3462968          -0.13863235           -1.1903906           -1.5296003 -5.0972580
   ## Unemployed                -1.1146447          -0.17349114           -0.6225869           -0.8989643  0.1348663
   ##                 factor(education_state)1 factor(education_state)2 factor(education_state)3 factor(education_state)5
   ## Family Care                  1.093072660               0.71973172               0.61008334               0.44923296
   ## Maternity Leave              2.049828212              -0.31472053               0.85094163               0.35424680
   ## PT Employed                  0.143339097               0.20648634               0.32410217               0.08297149
   ## Retired                     -0.006949523               0.18008193               0.73681273               0.52809290
   ## Self-employed                0.398090157               0.11861133               0.09295622               0.15346389
   ## Sick/Disabled               -0.190058758              -0.23771223              -0.34447954               0.25835992
   ## Student                     -0.477601765              -0.14664982               0.81320851              -0.11253669
   ## Unemployed                  -0.486247506              -0.09034886               0.07266512              -0.28706136
   ##                 factor(education_state)6 factor(education_state)7 scale(SF_12) factor(housing_quality)2
   ## Family Care                   0.24699153               0.44855159 -0.144441123              0.443510917
   ## Maternity Leave               0.20148096               0.65296928  0.222432819              0.920957081
   ## PT Employed                   0.06935358               0.11209176  0.005027363             -0.306799502
   ## Retired                       0.45734189               0.47104110  0.067479718              0.691977184
   ## Self-employed                -0.03670478               0.10539933 -0.004838563              0.017378466
   ## Sick/Disabled                -0.41951285              -0.59188760 -0.724897753              0.380956686
   ## Student                      -0.18984753               0.81610361 -0.023462567              0.005478777
   ## Unemployed                   -0.38663593               0.02375306 -0.329408911             -0.539632524
   ##                 factor(housing_quality)3 factor(job_sec)1 factor(job_sec)2 factor(job_sec)3 factor(job_sec)4
   ## Family Care                   0.72541559       -5.0162729       -4.4110535      -4.86336274       -4.2483521
   ## Maternity Leave               0.92846959       31.7880284       31.9680931      32.03746193       30.8446258
   ## PT Employed                  -0.09450522       -2.4200232       -1.5827890      -1.34206999       -0.8480948
   ## Retired                       0.76829285       -3.3974992       -3.4906164      -3.50476641       -3.5590742
   ## Self-employed                 0.06628421       -0.9871041        0.4864982       0.01380174       -1.1545668
   ## Sick/Disabled                -0.12620777       -5.8211411       -7.5813269      -5.52814828       -5.4873325
   ## Student                       0.20052477      -34.9985025       -4.2069005      -3.15288272       -3.4030008
   ## Unemployed                   -1.07626116       -4.4886201       -4.5505713      -4.93074079       -3.8123314
   ##                 factor(job_sec)5 factor(job_sec)6 factor(job_sec)7 factor(job_sec)8 scale(hh_income)
   ## Family Care           -1.7754635       -4.1081077       -3.9628349       -3.1200753      -0.28288910
   ## Maternity Leave       32.1089308       31.9783016       30.9927914       31.9017445       0.31440560
   ## PT Employed           -0.1552995       -1.2338417       -0.3399387       -0.2822169      -0.06426639
   ## Retired               -2.1234115       -3.5961309       -3.8923096       -3.8057946      -0.19157212
   ## Self-employed          4.6865216       -0.8608097       -1.2978377       -0.7422390       0.19302075
   ## Sick/Disabled         -2.5181672       -4.8686918       -4.4142408       -4.6246899      -0.30003573
   ## Student               -0.3920563       -3.3512038       -2.2652363       -2.6340193      -0.04863215
   ## Unemployed            -2.4456119       -4.5030251       -3.4539974       -3.4577365      -0.32731027
   ##                 scale(alcohol_spending)
   ## Family Care                 -0.15771691
   ## Maternity Leave             -1.23959490
   ## PT Employed                 -0.07481014
   ## Retired                      0.27035021
   ## Self-employed                0.03878633
   ## Sick/Disabled               -0.58869051
   ## Student                      0.05759228
   ## Unemployed                  -0.50116318
   ## 
   ## Std. Errors:
   ##                 (Intercept) factor(sex)Male factor(ethnicity)BLA factor(ethnicity)BLC factor(ethnicity)CHI
   ## Family Care     0.011801919     0.003145390         1.125126e-02         2.591048e-02         1.420599e-02
   ## Maternity Leave 0.044000808     0.017525579         4.436513e-08         2.759018e-11         7.516237e-12
   ## PT Employed     0.008992635     0.001370033         8.606788e-03         9.781844e-03         1.429365e-02
   ## Retired         0.023856403     0.001643519         2.603080e-02         2.496088e-02         3.571191e-02
   ## Self-employed   0.013958646     0.001646926         1.188541e-02         1.338486e-02         1.375771e-02
   ## Sick/Disabled   0.018241661     0.002160640         1.896288e-02         2.058164e-02         1.791085e+00
   ## Student         0.014225020     0.002089478         1.132834e-02         1.437908e-02         2.564983e-02
   ## Unemployed      0.008968934     0.001803575         1.200061e-02         1.012058e-02         2.403214e-02
   ##                 factor(ethnicity)IND factor(ethnicity)MIX factor(ethnicity)OAS factor(ethnicity)OBL
   ## Family Care              0.010600418          0.020194748         1.112360e-02         3.647028e-02
   ## Maternity Leave          0.048469674          0.048705770         1.636808e-09         1.906864e-12
   ## PT Employed              0.008112336          0.009021987         8.978949e-03                  NaN
   ## Retired                  0.023820799          0.025742890         2.559983e-02         6.182739e-02
   ## Self-employed            0.010603019          0.010931312         1.252585e-02         2.401768e-02
   ## Sick/Disabled            0.018940140          0.019897272         3.689741e-02         4.140264e-02
   ## Student                  0.010568490          0.010275903         1.117879e-02         2.894247e-02
   ## Unemployed               0.008595691          0.009223602         9.414690e-03         3.084408e-12
   ##                 factor(ethnicity)OTH factor(ethnicity)PAK factor(ethnicity)WBI factor(ethnicity)WHO   scale(age)
   ## Family Care             2.057506e-02         1.017710e-02          0.008965633          0.009815345 0.0014667522
   ## Maternity Leave         4.634104e-02         3.408405e-09          0.044071532          0.044343476 0.0041950511
   ## PT Employed             1.098652e-02         8.989935e-03          0.007339107          0.007652287 0.0008428856
   ## Retired                 2.966076e-02         2.526053e-02          0.023037239          0.023506220 0.0025722727
   ## Self-employed           1.350553e-02         1.159234e-02          0.010008170          0.010381525 0.0012684613
   ## Sick/Disabled           3.534268e-10         1.944726e-02          0.017251059          0.017866266 0.0015036432
   ## Student                 1.743773e-02         1.067652e-02          0.009090748          0.009826108 0.0049089966
   ## Unemployed              1.682654e-02         9.013297e-03          0.007456084          0.008134753 0.0012411753
   ##                 factor(education_state)1 factor(education_state)2 factor(education_state)3 factor(education_state)5
   ## Family Care                  0.007386593              0.002989435              0.004033542              0.004339459
   ## Maternity Leave              0.015492374              0.009619563              0.008084114              0.009398866
   ## PT Employed                  0.006500464              0.001744080              0.002192053              0.002325999
   ## Retired                      0.006617957              0.002223636              0.003209026              0.003130716
   ## Self-employed                0.007586465              0.002555447              0.003173690              0.003225111
   ## Sick/Disabled                0.008300946              0.002605715              0.004375236              0.003979449
   ## Student                      0.014709279              0.003101081              0.003204578              0.005419518
   ## Unemployed                   0.008731510              0.002323715              0.003072662              0.003930677
   ##                 factor(education_state)6 factor(education_state)7 scale(SF_12) factor(housing_quality)2
   ## Family Care                  0.003890945              0.004496899 0.0012381235              0.007216870
   ## Maternity Leave              0.007799520              0.008216787 0.0034799904              0.021658462
   ## PT Employed                  0.002010534              0.002306398 0.0007914633              0.003541696
   ## Retired                      0.002598689              0.003062832 0.0011137141              0.005440773
   ## Self-employed                0.002609310              0.002739410 0.0011352681              0.005848270
   ## Sick/Disabled                0.004051762              0.005716964 0.0010001796              0.005604822
   ## Student                      0.004325521              0.005165516 0.0011905551              0.006655738
   ## Unemployed                   0.003373234              0.003653115 0.0009390030              0.004102393
   ##                 factor(housing_quality)3 factor(job_sec)1 factor(job_sec)2 factor(job_sec)3 factor(job_sec)4
   ## Family Care                  0.007370642     9.024109e-03      0.006236266      0.004218988      0.004119065
   ## Maternity Leave              0.021792363     1.202693e-02      0.009212211      0.006988583      0.009065849
   ## PT Employed                  0.003611126     5.987426e-03      0.004691615      0.004030588      0.004049563
   ## Retired                      0.005558676     5.014999e-03      0.004505726      0.003629832      0.003947279
   ## Self-employed                0.005905593     9.188986e-03      0.008168875      0.008011167      0.008636658
   ## Sick/Disabled                0.006011891     1.107321e-02      0.021787539      0.004574433      0.005568321
   ## Student                      0.006778787     1.261000e-12      0.010015493      0.004201161      0.004406982
   ## Unemployed                   0.004457970     6.920730e-03      0.005524742      0.003984810      0.003526133
   ##                 factor(job_sec)5 factor(job_sec)6 factor(job_sec)7 factor(job_sec)8 scale(hh_income)
   ## Family Care          0.005086158      0.005711604      0.003782480      0.004079362     0.0009810099
   ## Maternity Leave      0.018068211      0.010378183      0.008940047      0.009223655     0.0012321320
   ## PT Employed          0.005538634      0.004590545      0.003961279      0.004137503     0.0008241614
   ## Retired              0.004655313      0.004673252      0.003799386      0.004139305     0.0008228718
   ## Self-employed        0.008222124      0.008903910      0.008762974      0.008703512     0.0006613299
   ## Sick/Disabled        0.005311654      0.005457641      0.003759818      0.004504582     0.0010146045
   ## Student              0.006967735      0.006180708      0.003295834      0.004008369     0.0017220238
   ## Unemployed           0.005625391      0.005193505      0.003163935      0.003470247     0.0008920096
   ##                 scale(alcohol_spending)
   ## Family Care                 0.003108814
   ## Maternity Leave             0.008744252
   ## PT Employed                 0.001629176
   ## Retired                     0.001983578
   ## Self-employed               0.001938997
   ## Sick/Disabled               0.003711073
   ## Student                     0.002780563
   ## Unemployed                  0.003216640
   ## 
   ## Residual Deviance: 74677760 
   ## AIC: 74678288

.. figure:: ./figure/labour_output-1.png
   :alt: plot of chunk labour_output

   plot of chunk labour_output

References
----------
