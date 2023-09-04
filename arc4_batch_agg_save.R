

require(tidyverse)
require(here)

workingDir <- normalizePath('.')
setwd(workingDir)


source(here::here('minos', 'utils_datain.R'))



S7.var.list <- c('hh_income', 'equivalent_income',  # Income variables
                 'S7_housing_quality', 'S7_neighbourhood_safety', 'S7_physical_health', 'S7_mental_health', 'S7_labour_state', 'loneliness',  # SIPHER 7 variables
                 'ethnicity', 'age', 'region', 'job_sec', 'education_state', 'nkids_ind', 'housing_tenure', 'urban')
out.path.batch <- here::here('output', 'SIPHER7_batch/')

base.batch <- read_batch_out_all_years(out.path.batch, 'baseline', start.year = 2021, var.list = S7.var.list, verbose=FALSE)
write.csv(base.batch, file = 'output/baseline_batch_aggregated.csv')
rm(base.batch)
wage.batch <- read_batch_out_all_years(out.path.batch, 'livingWageIntervention', start.year = 2021, var.list = c('income_boosted', S7.var.list), verbose=FALSE)
write.csv(wage.batch, file = 'output/wage_batch_aggregated.csv')
rm(wage.batch)
energy.batch <- read_batch_out_all_years(out.path.batch, 'energyDownlift', start.year = 2021, var.list = c('income_boosted', S7.var.list), verbose=FALSE)
write.csv(energy.batch, file = 'output/energy_batch_aggregated.csv')
rm(energy.batch)
child.batch <- read_batch_out_all_years(out.path.batch, 'hhIncomeChildUplift', start.year = 2021, var.list = c('income_boosted', S7.var.list), verbose=FALSE)
write.csv(child.batch, file = 'output/child_batch_aggregated.csv')
rm(child.batch)
pov.batch <- read_batch_out_all_years(out.path.batch, 'hhIncomePovertyLineChildUplift', start.year = 2021, var.list = c('income_boosted', S7.var.list), verbose=FALSE)
write.csv(pov.batch, file = 'output/pov_batch_aggregated.csv')
rm(pov.batch)

