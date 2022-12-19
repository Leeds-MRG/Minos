Replenishment
=============

Rationale
---------

In order to run the model beyond the length of the Understanding Society
data (11 waves, currently from 2009 - 2020), we needed to generate a
replenishing population that would maintain the age structure, as well
as being representative of the British population into the future in
terms of sex and ethnicity.

Data Sources
------------

Counts by age, sex, and year were generated for 2008 - 2070 from 2
sources: 1. National Midyear estimates for 2008 - 2020 1. These were
obtained using the `nomisweb data query
tool <https://www.nomisweb.co.uk/>`__ 2. Principal Population
Projections (PPP) for 2021 - 2070 1. `Principal Population
Projections <https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z1zippedpopulationprojectionsdatafilesuk>`__

Counts by ethnic group were obtained from a previous project involving
Nik Lomax called Ethpop. These were counts by ethnic group by age and
LAD, which were summed to generate national level counts of ethnicity by
single year of age. See `this link for more information about
ethpop <https://reshare.ukdataservice.ac.uk/852508/>`__.

Method
------

What we did to ensure that the simulation maintains the age structure of
the data moving into the future, was to begin with a population derived
from a single year of understanding society (we picked 2018). The
replenishing population is also derived from US 2018, but instead takes
just the 16 year olds. Each year in the simulation, every simulant is
transformed and ages by 1 year, which means the 16 year olds at time t
will be 17 at time t+1, meaning there are no 16 year olds in the
simulation. We then take the 16 year olds from the replenishing
population, which have been reweighted to be representative for that
year by sex and age (see below) and add them into the simulation to
replace the 16 year olds that have aged.

Reweighting
-----------

As part of the data generation pipeline, we take the final_US datafiles
(after a number of pre-processing and imputation steps) and use them to
generate both the starting and replenishing populations. The model
begins with a population derived from Understanding Society in 2018
(wave 9), from which the analysis weights provided by the survey are
then modified based on the counts from both the age-sex projections and
the counts by ethnicity. Replenishing populations are also derived from
US wave 9, where we take all 16 year olds from wave 9, duplicate them
for every year from 2009 - 2070, and reweight these populations by age,
sex, and ethnicity. The actual reweighting calculation is very simple:

::

   new_weight = (old_weight * count_by_group) / total_weight_by_group

Complication
------------

A slight complication to this method of replenishing is that education
states now have to be transformed over time in the model. This is
handled by the Education module, which is described on a different page.
