# Data Discovery

All variables here are from Understanding Society unless otherwise stated

[Link to variable search](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation)

Although at first glance lots of variables are only asked intermittently, I think we will be able to derive lots of useful information from those that are asked more often. E.g. MRS social class in psychosocial is only included on two non-consecutive waves, however RG Social Class: present job was asked at every wave with good detail, which can be used to derive MRS.

## **Wage/Income**

[Individual income variables](https://www.understandingsociety.ac.uk/documentation/mainstage/user-guides/main-survey-user-guide/individual-income-variables) - this page details the six components of individual net income, and which variables in BHPS or US that relate to these components.

Only going to list labour income variables, as there are lots of others that are unrelated to this work. A living wage will only affect labour income.

**N.B.** The top variable here (fimnlabnet\_dv) is a derived variable, which is the sum of three earnings components:

- `paynu_dv`: net usual pay
- `seearnnet_dv`: net self-employment income
- `j2paynet_dv`: net pay in second job

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| **LABOUR** | **INCOME** ||||
| [fimnlabnet\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fimnlabnet_dv) | amount income component 1: net labour income |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11|Derived variable, sum of the next three variables in this table.<br/>Labour income, component 1 out of 6 of individual income.|
| [fimnlabgrs\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fimnlabgrs_dv) | Total monthly labour gross income |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Gross monthly pay rather than net.|
| [fihhmnlabgrs\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fihhmnlabgrs_dv) | Total gross household labour income: month before interview |hhresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11|Gross monthly household income. <br />Calculated from fimnlabgrs\_dv, calculating sum for household.|
| [paynu\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/paynu_dv) | Usual net pay per month: current job |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Component of labour income.<br />Response of &#39;inapplicable&#39; hovering around 40-50% across every wave. Don&#39;t understand this, not obvious from the variable page. Could this be unemployed, disabled, or retired? Seems a large proportion to be in that group.|
| [seearnnet\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/seearnnet_dv) | Self employment earnings - net |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11|Component of labour income|
| [j2pay\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/j2pay_dv) | Pay in second job |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Component of labour income.<br />Not sure if this is net income, the variable mentioned on the page about individual income is _j2paynet\_dv_, but this doesn&#39;t seem to exist in the variable search.|
| [basrate](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/basrate) | Basic pay hourly rate |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
| [jbhrs](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/jbhrs) | No. of hours normally worked per week |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||




## **Psychosocial - Improvement in social status/esteem, financial independence**

(including from benefit stigma etc.)

Come back to this, unfinished. Mostly collected variables that refer to social status/esteem (social class, NSSEC etc.). Financial independence is more complex as there are LOTS of variables related to benefits.

Financial independence is a persons ability to support themselves financially. This relates to welfare/benefits, as well as extra support from family members (i.e. childcare from family members) as well as dependence for other reasons (i.e. victims of abuse).

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| **Social** | **Status/Esteem** ||||
| [opcls2](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/opcls2) | Subjective social class membership |indresp|bh01, bh06, bh10, bh15|Ordinal variable, outcomes in the form &#39;lower working class&#39;, &#39; upper middle class&#39; etc.|
| [jbmrs](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/jbmrs) | MRS social class |indresp|bh08, bh15|Approximated social grade with 6 categories, produced by ONS by applying an algorithm developed by MRS Census &amp; Geodemographics group. See [link](https://ukgeographics.co.uk/blog/social-grade-a-b-c1-c2-d-e) for more info.Based on occupation.|
| [mrssci](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/mrssci) | MRS Social Class Individual |indresp|bh05|Similar to jbmrs above, distinction from household MRS|
| [mrssch](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/mrssch) | MRS Social Class Household |indresp|bh05|See above|
| [jbgold](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/jbgold) | Goldthorpe Social Class: present job |indresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|11 level occupational classification. Think this has been superceded by NS-SEC, also doesn&#39;t seem to have all the job types in NS-SEC (missing managerial unless I&#39;m being daft).|
| [jbrgsc\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/jbrgsc_dv) | RG Social Class: present job |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Runs for every wave of BHPS and US.<br />Note about derived variable:<br/>_Registrar General&#39;s Social Class (SC) of current job. Uses the coding frame from the BHPS. Current job refers to being in paid employment during the last week, even if respondent was away from work in that week. This standard classification has been replaced by the NS-SEC. Derived from look-up file SOC2000 to RGSC provided on the CAMSIS project website. From Wave 2 onwards this is includes RGSC codes fed forward from the previous interview._|
| [mrjnssec8\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/mrjnssec8_dv) | Occupation of most recent job: NSSEC 8 categories |indresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Full length of BHPS 8 category NSSEC.|
| [j1nssec8\_dv](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/j1nssec8_dv) | Own first job: NSSEC 8 classes |indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Complete NSSEC of first job, most of BHPS &amp; all of US. Also a 2nd job NSSEC var if necessary.Derived variable note:_National Statistics Socio-economic Classification (NS-SEC) of respondent&#39;s first job: Condensed 8-category version. Note that this indicator is constructed on the basis of less information than the respondent&#39;s current or last job NSSEC: Information on establishment size and managerial duties is not considered. For a detailed look-up file between SOC 2000 and the 5-category NSSEC see_[_bit.ly/1RzyUfR_](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/bit.ly/1RzyUfR)|
| [**f132**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/f132) | Income: income support (IS) |indresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Whether someone receives income support, if they were to come off it then might have an impact on financial esteem.|
| [**benbase1**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/benbase1) | Income Support |indresp|6, 7, 8, 9, 10, 11|Income support as above but in US instead of BHPS|
| **Financial** | **Independence** ||||


## **Behaviour - Nutrition**

(food security, hunger, better quality food)

Variables related to food and nutrition are somewhat lacking in US. Some variables included here are not very strongly related or at best incomplete in capturing the topic.

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| **Food** | **Security** ||||
| [foodbank](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/foodbank) | Food banks usage |hhresp|11|Only in wave 11, might be useful as a component of a constructed/aggregated variable|
| [hscane](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hscane) | Eat meat on alternate days |hhresp|bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Think this can fit in both hunger or food security. As the last time this was asked was in BHPS wave 18 (2008), I don&#39;t think the answers would be related to health or environmental reasons. Comes under index terms for financial management: problems and financial management: material wellbeing so we can be confident this is a financial decision.|
| [lacte](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/lacte) | How often: eat out |indresp|bh06, bh08, bh10, bh12, bh14, bh16, bh18|Comes under index terms for time use and leisure activities, however we could investigate how income/wealth is related to those who answered never/almost never.Clutching at straws a little here as theres not much to go on.|
| **Hunger** |  ||||
| [breakfst](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/breakfst) | Days eats breakfast |indresp|7, 9, 11|Could be for many reasons other than lack of access to food, however included this as there are not many variables that can relate to hunger.|
| [**pdepa2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/pdepa2) | filling meal a day: no, no money for this |hhresp|4, 6, 8, 10|Household question, only asked if there is a pensioner in the house.|
| **Food** | **Quality** ||||
| [wkfruit](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/wkfruit) | Days each week eat fruit |indresp|2, 5, 7, 9, 11|Including tinned, frozen, dried and fresh.Question asks for usual week.Categories: Never, 1-3d, 4-6d, everyday|
| [wkvege](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/wkvege) | Days each week eat vegetables |indresp|2, 5, 7, 9, 11|Including tinned, frozen and fresh.Does not include potatoes, crisps, or chips.Same categories as above.|
| [cdepdo5](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/cdepdo5) | Eat fruit and veg every day |hhresp|4, 6, 8, 10|Only asked if there is at least one child (age 0-15) living in the household.|


## **Behaviour - Alcohol and Tobacco Consumption**

(increase/decrease?)

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| **Alcohol** |||||
| [scalcl7d](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/scalcl7d) |Drank alcohol last 7 days|indresp|2, 5|Binary, only asked if answered previous question stating that respondent has had an alcoholic drink in last 12 months. Also only asked in self-completion or telephone interviews.|
| [auditc1](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/auditc1) |Past 12 months alcoholic drink|indresp|7, 9, 11|Binary|
| [auditc3](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/auditc3) |Alcohol frequency past 12 months|indresp|7, 9, 11|Ordinal, 5 categories ranging from Never, monthly or less, …, up to 4+ times per week.|
| [evralc](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/evralc) |Ever had an alcoholic drink|indresp|3, 4, 6, 8, 10|Only asked for young adults aged 16-21.|
| [fivealcdr](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fivealcdr) |Frequency of 5 plus alcoholic drinks|indresp|3, 4, 6, 8, 10|Again only asked for young adults aged 16-21. One drink is defined as one pint/bottle/can of beer or cider, 2 alcopops, one small glass of wine, a single measure of spirits.|
| [hlprbj](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hlprbj) |Health problems: Alcohol or drugs|indresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Binary, positive response indicates problem with either alcohol or drugs.Very low relative frequency of positive response but could still be useful.|
| [xpaltob\_g3](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xpaltob_g3) |Total amount spent on alcohol|hhresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11|Household spending in past 4 weeks. Includes all alcohol (supermarkets/shops, pubs, restaurants, other venues).|
| [dklm](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/dklm) |Past month: how many alcoholic drinks?|indresp|3, 4, 6, 8, 10|Ordinal, question specifies how many **times** in the past month, not how many drinks.<br /> Answers range; most days, once or twice a week, 2 or 3 times, once only, never.Also youth version of this question asked.|
| [scfalcdrnk](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/scfalcdrnk) |How often have you had an alcoholic drink during the last 12 months?|indresp|2, 5|Ordinal variable with 8 categories. Almost every day, …, once or twice a week, …, once or twice a year, not at all in last 12 months.|
| **Tobacco** |||||
| [smoker](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/smoker) |Smoker|indresp|6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Simple binary, &#39;_do you smoke cigarettes?_'|
| [smever](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/smever) |Ever smoked cigarettes?|indresp|2, 5, bh09|Cigarette, cigar, or pipe.|
| [smnow](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/smnow) |Smoke nowadays|indresp|2, 5, bh09|Asked if smever == 1|
| [smcigs](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/smcigs) |Smoking history|indresp|2, 5, bh09, bh12|**Text:** _Have you ever smoked cigarettes regularly, that is at least one cigarette a day, or did you smoke them only occasionally?_If smever == 1 (yes) &amp;&amp; smnow == 2 (does no smoke nowadays).<br />Find it a bit weird that this question relies on answers to 2 other questions that were not asked in BH12.|
| [ncigs](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ncigs) |Usual no. of cigarettes smoked per day|indresp|2, 5, 6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|Asked if smoker == 1<br />Continuous outcome.<br />Bit weird before wave BH09. Doesn&#39;t seem to be a continuous variable however that could just be an error in the way it&#39;s reported in the variable search.|
| [smncigs](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/smncigs) |Number of cigarettes smoked in past|indresp|2, 5, bh09|If smever == 1 (ever smoked)&amp;&amp; smnow == 2 (does not smoke now)&amp;&amp; smcigs == 1 (used to smoke regularly)<br />Continuous for wave 2 &amp; 5, unknown for wave BH09.|
| [ecigs1](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ecigs1) |Uses electronic cigarettes|indresp|9, 10, 11|Ordinal.<br />Captures both whether respondent has or has not used ecigs, as well as the frequency.Frequency: only used once or twice -\&gt; at least once a week with steps in between.|



## **Housing Quality**

(decent homes = less damp, warmer, housing security)

Still to do: Look for more vars related to housing security.

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| [lfsat3](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/lfsat3) | Satisfaction with: house/flat | indresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Ordinal, 7 categories from:Not satisfied at all -\&gt; Completely satisfied |
| [matdepd](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/matdepd) | Material deprivation: house | hhresp | 1, 2, 4, 6, 8, 10 | Question Text:_Enough money to keep your house in a decent state of repair?_<br />Ordinal, 4 levels including: Yes, Can&#39;t afford it, Don&#39;t need it now, Does not apply |
| [xphsdb](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsdb) | Problems paying for housing | hhresp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | _Many people find it hard to keep up with their housing payments. In the last twelve months, have you ever found yourself behind with your rent/mortgage?_<br />Binary, applies to both rented and mortgaged accommodation. |
| [hsprbj](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbj) | Accom: not enough light | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsprbk](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbk) | Accom: lack of adequate heating | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsprb](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbli) | Accom: condensation | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsprbm](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbm) | Accom: leaky roof | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsprbn](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbn) | Accom: damp walls, floors etc. | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsprbo](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbo) | Accom: rot in windows, floors | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [**pdepf2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/pdepf2) | home good state of repair: no, no money for this | hhresp | 4, 6, 8, 10 | Specifically about pensioners and only asked if pensioner in the house. |
| [**pdeph2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/pdeph2) | damp-free home: no, no money for this | hhresp | 4, 6, 8, 10 | Again pensioners only |
| [**pdepi2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/pdepi2) | home kept warm: no, no money for this | hhresp | 4, 6, 8, 10 | Pensioner |
| [**hheat**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hheat) | keep accommodation warm enough | hhresp | 1, 2, 4, 6, 8, 9, 10, 11 | Asked of everyone, specifically about keeping the house warm enough in winter. |

## **Moving Home**

(could mean less overcrowding, better neighbourhood with more green space, different cultural norms, better recreational and health care facilities, better food outlets, less tobacco and alcohol outlets, less crime and anti-social behaviours)

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| [hsprbg](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbg) | Accom: shortage of space | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsprbh](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation?search_api_views_fulltext=housing&amp;page=1) | Accom: noise from neighbours | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsprbi](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbi) | Accom: street noise | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 | Binary |
| [hsbeds](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsbeds) | Number of bedrooms | hhresp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh01 ||
| [hsgdn](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsgdn) | Accom: has terrace/garden | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 |Should be used alongside [hsgdns](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsgdns), which is _Accom: is terrace/garden shared?_|
| [hsprbp](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsprbp) | Accom: pollution/environmental problems | hhresp | bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 ||
| [hsroom](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsroom) | Number of rooms in accomodation | hhresp | bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 ||
| **Neighbourhood** |  |  |  ||
| [**rescond**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/rescond) | conditions of residential properties | hhsamp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 |Ordinal, 4 levels|
| [vicini1](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/vicini1) | Boarded houses: abandoned buildings: demolished houses or demolished buildings | hhsamp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 |Thought this would relate to the neighbourhood quality.<br />Binary but in the form &#39;Yes mentioned&#39; or &#39;Not mentioned&#39;. Not sure therefore how complete/reliable.|
| [**vicini2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/vicini2) | trash: litter or junk in street/road | hhsamp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ||
| [**vicini3**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/vicini3) | heavy traffic on street/road | hhsamp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ||
| [**nbrcoh\_dv**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nbrcoh_dv) | Neighbourhood Social Cohesion,(Î±= .8) | indresp | 3, 6 |Summary of 4 variables on neighbourhood social cohesion. Ordinal var with range from 4 (no cohesion) to 20 (strong cohesion).|
| [**scopngbhg**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/scopngbhg) | Am similar to others in neighbourhood | indresp | 1, 3, 6, 9 |_I think of myself as similar to the people that live in this neighbourhood._<br />Could mean many different things, like ethnicity, religion, life stage, etc. But could be useful in this context. Relates to the idea of belonging and &#39;fitting in&#39;.There is also a separate var for this in BHPS.|
| [**nbrcoh3**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nbrcoh3) | people in this neighbourhood can be trusted | indresp | 3, 6 ||
| [**nbrsnci\_dv**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nbrsnci_dv) | Buckner&#39;s Neighbourhood Cohesion Instrument, short (alpha ±= .88) | indresp | 1, 3, 6, 9 ||
| [**crburg**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crburg) | extent of: homes broken into | hhresp, indresp | 3, 6, 9, bh07, bh12, bh17 |This and the following 8 vars (labels all start with &#39;extent of: &#39; are more objective measures of the quality of a neighbourhood (still measured subjectively, but asking about specific things).<br />All are ordinal with 4 levels, ranging from Very common to Not at all common. We could use these potentially to create a summary variable, ranging from the worst (9/36) to the best (36/36).|
| [**crcar**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crcar) | extent of: cars stolen/broken into | indresp, hhresp | 3, 6, 9, bh07, bh12, bh17 ||
| [**crdrnk**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crdrnk) | extent of: drunks/tramps on street | hhresp, indresp | 3, 6, 9, bh07, bh12, bh17 ||
| [**crgraf**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crgraf) | extent of: graffiti on walls | indresp, hhresp | 3, 6, 9, bh07, bh12, bh17 ||
| [**crmugg**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crmugg) | extent of: people attacked on street | indresp, hhresp | 3, 6, 9, bh07, bh12, bh17 ||
| [**crrace**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crrace) | extent of: racial insults/attacks | hhresp, indresp | 3, 6, 9, bh07, bh12, bh17 ||
| [**crteen**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crteen) | extent of: teenagers hanging about | indresp, hhresp | 3, 6, 9, bh07, bh12, bh17 ||
| [**crvand**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crvand) | extent of: vandalism | hhresp, indresp | 3, 6, 9, bh07, bh12, bh17 ||
| [**crrubsh**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crrubsh) | extent of: rubbish on street | hhresp | 3, 6, 9 ||
| [**crwora**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crwora) | worry about being affected by crime | indresp | 3, 6, bh07, bh12, bh17 |Binary|
| [**crworb**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crworb) | extent of worry about crime | indresp | 3, 6, bh07, bh12, bh17 |Ordinal, 3 levels|
| [**locchd**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locchd) | Suitability of area for raising children | indresp | bh08, bh13, bh18 ||
| [**hsctax**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/hsctax) | Council tax band of accommodation | hhresp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18 |Don&#39;t know if this is important or not but must have some relationship to neighbourhood?|
| [unsafe1](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe1) | At school | indresp | 3, 5, 7, 9, 11 |This and the following 12 variables all relate to feeling safe in specific places.<br />All binary although in the form &#39;Mentioned/Not Mentioned&#39; so may not be complete.|
| [unsafe2](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe2) | At college/university | indresp | 3, 5, 7, 9, 11 ||
| [unsafe3](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe3) | At work | indresp | 3, 5, 7, 9, 11 ||
| [unsafe4](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe4) | On public transport | indresp | 3, 5, 7, 9, 11 ||
| [unsafe5](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe5) | At/near Bus/train stn | indresp | 3, 5, 7, 9, 11 ||
| [unsafe6](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe6) | In Shopping centres, etc | indresp | 3, 5, 7, 9, 11 ||
| [unsafe7](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe7) | In cinema, cafes | indresp | 3, 5, 7, 9, 11 ||
| [unsafe8](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe8) | At pub/disco/club | indresp | 3, 5, 7, 9, 11 ||
| [unsafe9](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe9) | In car parks | indresp | 3, 5, 7, 9, 11 ||
| [unsafe10](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe10) | Outside, street/park | indresp | 3, 5, 7, 9, 11 ||
| [unsafe11](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe11) | At home | indresp | 3, 5, 7, 9, 11 ||
| [unsafe96](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe96) | Not, in last 12 months | indresp | 3, 5, 7, 9, 11 ||
| [unsafe97](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/unsafe97) | Other places | indresp | 3, 5, 7, 9, 11 ||
| [**crworb**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crworb) | extent of worry about crime | indresp | 3, 6, bh07, bh12, bh17 |Think this var is part of the pathway between the quality of the neighbourhood and mental health. If a person is very worried about crime and in a high crime area then it will likely affect mental health.|
| [**crwora**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/crwora) | worry about being affected by crime | indresp | 3, 6, bh07, bh12, bh17 |See above, in the same vein.|
| **Access To** | **Services** |  |  ||
| [**servacc**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/servacc) | able to access services when need to | indresp | 3, 6 |Bit crap that it only runs for 2 waves, might be able to find a better var for this.|
| [**locchd**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locchd) | Suitability of area for raising children | indresp | bh08, bh13, bh18 ||
| [**locsera**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locsera) | Standard of local services: Schools | indresp | bh08, bh13, bh18 |This and the following are much better variables related to services but still don&#39;t run for very long. Could use them to create a summary variable that relates to the quality of services and access to them in the neighbourhood. This maybe wouldn&#39;t be too useful in longitudinal models but could be interesting to see what relationship it has with mental health. OR on the other hand, we could investigate the relationship between all of these things individually and mental health and try to determine which if any are important.<br />Ordinal, subjective, 4 levels, Poor to Excellent.|
| [**locserap**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locserap) | standard of local services: primary schools | indresp | 3, 6 ||
| [**locseras**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locseras) | standard of local services: secondary schools | indresp | 3, 6 ||
| [**locserb**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locserb) | standard of local services: medical | indresp | 3, 6, bh08, bh13, bh18 ||
| [**locserc**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locserc) | standard of public transport | indresp | 3, 6, bh08, bh13, bh18 ||
| [**locserd**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locserd) | standard of local services: shopping | indresp | 3, 6, bh08, bh13, bh18 ||
| [**locsere**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/locsere) | standard of local services: leisure | indresp | 3, 6, bh08, bh13, bh18 ||
| [**servaccy4**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/servaccy4) | financial reasons | indresp | 3, 6 |**Text:** _What stops you from accessing services such as healthcare, food shops and learning facilities when you need to?_<br />Not useful on its own but could relate to other vars.|




## **More Social Inclusion**

(e.g. more ability to participate in leisure activities e.g. sports, cinema, or pub)

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| [sclonely](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/sclonely) | How often feels lonely | indresp | 9, 10, 11 | Ordinal, 3 levels.<br />Variable note:_The questions used to output levels of loneliness in Understanding Society come from the Government Statistical Service (GSS) harmonised principle of loneliness. This means the outputs are comparable with other surveys that use this principle. The GSS has a guidance page which may be useful to understand what other data can and cannot be compared with this output._ |
| [scisolate](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/scisolate) | How often feels isolated from others | indresp | 9, 10, 11 | See above |
| [sclackcom](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/sclackcom) | How often feels lack of companionship | indresp | 9, 10, 11 ||
| [scleftout](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/scleftout) | How often feels left out | indresp | 9, 10, 11 ||
| [**visfrndsy2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/visfrndsy2) | Financial reasons | indresp | 3, 6, 9 |Text:<br />_What stops you from going out socially or visiting friends when you want to?_<br /><br />Not really an indicator of sorts but we could look at the relationship between this and other social isolation vars.|
| [**pdepb2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/pdepb2) | go out socially: no, no money for this | hhresp | 4, 6, 8, 10 |Household question, specifically asked about pensioners and only if there is a pensioner in the house.|


## **Psychosocial - Financial Security**

(less chronic stress/worry)

| **Variable** | **Label** | **Datafile** | **Waves** | **Notes** |
| --- | --- | --- | --- | --- |
| [**sclfsat2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/sclfsat2) | Satisfaction with income | indresp | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | This is obviously a subjective measure, but I think it&#39;s reasonable to assume that someone would become more satisfied with income if they were moved onto a living wage. The question specifically asks for satisfaction with household income.<br />Might be useful for looking at relationship with mental health or wage etc.<br />Ordinal, 7 levels. |
|**Savings Or**|**Investments**||||
|[**save**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/save)|whether saves|indresp|2, 4, 6, 8, 10, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|This and the following vars are about whether a respondents (or household) has savings. Think we can assume a level of financial security based on the amount / existence of savings.<br />Would be interesting to see the relationship between extent of savings and mental health before we do anything in anger.|
|[**saved**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/saved)|monthly amount saved|indresp|2, 4, 6, 8, 10, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**nvesth**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nvesth)|Savings/investments: savings account|indresp|bh10, bh15||
|[**matdepf**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/matdepf)|regular savings|hhresp|1, 2, 4, 6, 8, 10|Text:_Enough money to make regular savings of £10 a month or more for rainy days or retirement?_<br />Ordinal 4 levels. From I/We have this, Can&#39;t afford it, Don&#39;t need it now, Does not apply.<br />Weird levels in this one, we&#39;d have to make some assumptions about those who say they don&#39;t need it or it doesn&#39;t apply.|
|[**fiyrdia**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fiyrdia)|savings and investments|indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**svackb3**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/svackb3)|Over 10000 in savings|indresp|bh10, bh15||
|[**svackb5**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/svackb5)|Over 20000 in savings|indresp|bh15||
|[**nvestb**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nvestb)|Savings/investments: premium bonds|indresp|bh05, bh10, bh15||
|[**nvestd**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nvestd)|Savings/investments: PEP|indresp|bh05, bh10, bh15||
|[**nveste**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nveste)|Savings/investments: shares|indresp|bh05, bh10, bh15||
|[**nvestg**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nvestg)|Savings/investments: other|indresp|bh05, bh10, bh15||
|[**nvestj**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nvestj)|Savings/investments: tessa/ISA|indresp|bh05, bh10, bh15||
|[**nvestnn**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/nvestnn)|Savings/investments: none|indresp|bh10, bh15||
|[**rtfndb**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/rtfndb)|Retirement income: savings|indresp|bh16||
|[**svack**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/svack)|Total value in savings accounts|indresp|bh10, bh15||
|[**svackb1**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/svackb1)|Over 1000 in savings accounts|indresp|bh10, bh15||
|[**svackb2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/svackb2)|Over 5000 in savings accounts|indresp|bh10, bh15||
|[**svackb4**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/svackb4)|Over 500 in savings accounts|indresp|bh10, bh15||
|[**fiyrinvinc\_dv**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fiyrinvinc_dv)|income from savings and investments, annual|indresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11|Relates more to income but also falls under financial security. Might be unlikely that someone has income below living wage that is propped up by savings/investments but not impossible.|
|[**bankk**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/bankk)|Amount in account(s) - non-reg saving|indresp|bh05||
|[**bankkb1**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/bankkb1)|Savings amount to 1000 or more|indresp|bh05||
|[**bankkb2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/bankkb2)|Savings amount to 5000 or more|indresp|bh05||
|[**bankkb3**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/bankkb3)|Savings amount to 10,000 or more|indresp|bh05||
|[**bankkb4**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/bankkb4)|Savings amount to 500 or more|indresp|bh05||
|[**savekb1**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/savekb1)|Savings amount to 1000 or more|indresp|bh05||
|[**savekb2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/savekb2)|Savings amount to 5000 or more|indresp|bh05||
|[**savekb3**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/savekb3)|Savings amount to 10,000 or more|indresp|bh05||
|[**savekb4**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/savekb4)|Savings amount to 500 or more|indresp|bh05||
|||||**There are MANY more vars related to savings and investments but I&#39;m stopping here and leaving this note.**|
|**Credit**|**and**|**Debt**|||
|[**ccamtjt**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ccamtjt)|outstanding balance, cards in joint names|indresp|4, 8|Joint account debt|
|[**ccamtsole**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/ccamtsole)|balance outstanding, cards in sole name|indresp|4, 8|Sole account debt|
|[**debt**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/debt)|Resp. owe money|indresp|bh05, bh10, bh15|Debt doesn&#39;t always indicate financial insecurity, could be things like buying a car on finance or personal loan for something reasonable. Think the level of debt is important here, or a combination of debt and income to find respondents who are in more debt than is reasonable. Therefore debt to income ratio might be better indicator.<br />See next 5 vars for levels of debt|
|[**debtc1**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/debtc1)|owe 500 or more|indresp|4, 8, bh05, bh10, bh15||
|[**debtc2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/debtc2)|owe 1,500 or more|indresp|4, 8, bh05, bh10, bh15||
|[**debtc3**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/debtc3)|owe 5,000 or more|indresp|4, 8, bh05, bh10, bh15||
|[**debtc4**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/debtc4)|owe 100 or more|indresp|4, 8, bh05, bh10, bh15||
|[**debtc5**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/debtc5)|owe 10,000 or more|indresp|4, 8, bh15||
|[**debty**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/debty)|total amount owed|indresp|4, 8, bh05, bh10, bh15||
|[**deduc**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/deduc)|total hh deductions|hhresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**xphp**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphp)|Repayments on hire purchase or loans|hhresp|bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18|This var and the following to the end are very good indicators of financial security and have great coverage. They could be used to create a summary variable that indicates whether someone has enough money to pay for housing and other bills, or if they have/are having trouble paying.|
|[**xphpdf**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphpdf)|Repayments a burden on household|hhresp|bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**xphsd1**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsd1)|Housing payments required borrowing|hhresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**xphsd2**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsd2)|Housing payments required cutbacks|hhresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**xphsdb**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsdb)|problems paying for housing|hhresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**xphsdb\_bh**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsdb_bh)|Been 2+ months late with housing payment|hhresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**xphsdba**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsdba)|up to date with all bills|hhresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11||
|[**xphsdct**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsdct)|problems paying council tax|hhresp|1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11||
|[**xphsdf**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphsdf)|Problems paying for housing over year|hhresp|bh01, bh02, bh03, bh04, bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
|[**xphp**](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/xphp)|Repayments on hire purchase or loans|hhresp|bh05, bh06, bh07, bh08, bh09, bh10, bh11, bh12, bh13, bh14, bh15, bh16, bh17, bh18||
