
library(here)
library(tidyverse)
library(data.table)

###################### SUMMARY FUNCTIONS ####################

treated_summary <- function(data) {
  boosted.pidps <- data %>%
    filter(scenario == 'intervention') %>%
    filter(income_boosted == 'TRUE') %>%
    select(pidp)
  
  output <- data %>%
    inner_join(boosted.pidps, by = 'pidp') %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  
  return(output)
}

whole_pop_income_quint_summary <- function(data) {
  income_quints <- data %>%
    filter(scenario == 'baseline') %>%
    mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
    select(pidp, income_quintile)
  
  output <- data %>%
    inner_join(income_quints, by = 'pidp') %>%
    group_by(run_id, scenario, income_quintile) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  
  return(output)
}

families_income_quint_summary <- function(data) {
  income_quints <- data %>%
    filter(scenario == 'baseline') %>%
    filter(nkids > 0) %>%
    mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
    select(pidp, income_quintile)
  
  output <- data %>%
    inner_join(income_quints, by = 'pidp') %>%
    group_by(run_id, scenario, income_quintile) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  
  return(output)
}





# Step 3: Combine Summaries Across Years
combine_summaries_across_years <- function(summary_funcs, save.path1, save.path2) {
  for (summary_name in names(summary_funcs)) {
    print(sprintf('About to combine summaries for %s', summary_name))
    combined_summary <- NULL
    for (year in start.year:end.year) {
      if((summary_name == 'treated') & (year == 2020)) {
        # no treated pops in first year
        next
      }
      summary_filename <- sprintf("%s/summary_%s_%d.csv", save.path2, summary_name, year)
      year_summary <- read.csv(summary_filename)
      year_summary$year <- year
      combined_summary <- rbind(combined_summary, year_summary)
    }
    combined_summary_filename <- sprintf("%s/combined_summary_%s.csv", save.path1, summary_name)
    write.csv(combined_summary, file = combined_summary_filename, row.names = FALSE)
  }
}

###################### RUN THIS STUFF! ######################

args <- commandArgs(trailingOnly=TRUE)
#args <- list('default_config', 'cpr_summary_out_test', 'ChildPovertyReductionRELATIVE_2_batch')

# constants
start.year <- 2020
end.year <- 2035

out.path <- here::here('output', args[1])
#out.path <- '/home/luke/Documents/WORK/MINOS/Minos/output/default_config/'
save.path.base <- here::here(out.path, args[2])
save.path1 <- here::here(save.path.base, paste0(args[3], '_together'))
save.path2 <- here::here(save.path1, 'intermediates')
scen <- args[[3]]


# Create named list of summary functions to go through
summary_funcs <- c(treated = treated_summary,
                   whole_pop_income_quint_together = whole_pop_income_quint_summary,
                   families_income_quint_together = families_income_quint_summary)



# Combine summaries across years for each type of summary
combine_summaries_across_years(summary_funcs, save.path1, save.path2)

# Remove intermediates folder and its contents
#unlink(save.path2, recursive = TRUE)
