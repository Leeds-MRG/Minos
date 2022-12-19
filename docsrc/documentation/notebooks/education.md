## Education

### Purpose

This module has been added currently for the sole purpose of solving a problem created by our 
current method of replenishing the population. Briefly, this is that 16 year olds are added to the 
model before finishing their studies, and so some will increase their highest level of education
throughout their lives. We needed to find a way to predict what the highest level of education 
would be for each individual, and then manage their trajectory towards achieving that level in a 
sensible timeframe. 

### Levels

Each qualification type as reported in Understanding Society has been mapped to a level, details of
which are [provided by the government](https://www.gov.uk/what-different-qualification-levels-mean/list-of-qualification-levels):
- None of the above : 0
- Other School Certification : 1
- GCSE/O level : 2
- Standard/o/lower : 2
- CSE : 2
- AS level : 3
- A level : 3
- International Baccalaureate : 3
- Welsh Baccalaureate : 3
- Scottish Highers : 3
- Cert 6th year studies : 3
- Nursing/other med qual : 5
- Diploma in HE : 5
- Teaching qual not PGCE : 6
- 1st Degree or equivalent : 6
- Higher degree : 7
- Other higher degree : 7

### Method

During the data generation pipeline, a neural net model is estimated to predict the highest
level of education a person will attain based on their sex, ethnicity, and region of the UK. 
At present this model is not particularly effective at predicting the correct maximum education 
level, and more variables from Understanding Society would most likely improve this, but it is
passable for a first iteration. The model is estimated on a sample of the population over the age of
30, at which point we assume that the vast majority of people have reached their highest level 
of qualification. This model is then used to predict the maximum education level for the entire replenishing 
population of 16 year olds.

Then, at each wave of the simulation after the replenishing population is added for that wave, we
run the education module. In simple terms, the education module checks the age of each simulant
(between 16 and 26), and then checks to see if the max education level is higher than the current.
If yes, and the simulant is at an age where a new qualification would be achieved, the current
education level is modified. See section below for a list of ages where qualifications are 
achieved. Note that we assume that everybody achieves equivalent levels of education at exactly
the same age, which is not correct for the real world.

N.B. we do not vary these trends over time, so the distribution of
education states will remain roughly static into the future. This is inadequate, but again 
decisions were made to get something reasonable for the first iteration that can be improved
upon in time - the important part was the framework for how we update education state for 
replenishing populations over time.

### Attainment Ages

Each new qualification is added the year after it would be achieved, because some people 
completed the survey before the end of the school year (i.e. someone could be 18 in the first 
month of the academic year, so it made more sense to wait until the next year to apply the change).

- Level 2 is equivalent to GCSE level, which everyone should have achieved by the age of 17
  - No need to check the maximum education level for this one, everyone should stay in school until at least age 18 now
- Level 3 is equivalent to A-level, so make this change by age 19 if max_educ is 3 or larger
- Level 5 is nursing/medical and HE diploma, so make this change by age 22 if max_educ is 5
- Level 6 is 1st degree or teaching qual (not PGCE), so make this change by age 22 if max_educ is 6 or larger
- Level 7 is higher degree (masters/PhD), so make this change by age 25 if max_educ is 7

Currently there is no mechanism for those who achieve less than GCSE (level 0-1).
