
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

#### INDICES OF INEQUALITY ####

calculate_indices <- function(sub_data) {
  
  # Calculate income quintiles from baseline run
  income_quints <- data %>%
    filter(scenario == 'baseline') %>%
    filter(nkids > 0) %>%
    mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
    select(pidp, income_quintile)
  
  # Calculate SF12 mid-point of each quintiles cumulative proportion
  income_dist <- data %>%
    inner_join(income_quints, by = 'pidp') %>%
    group_by(income_quintile) %>%
    summarise(mean_SF12 = weighted.mean(SF_12, w = weight), .groups = 'drop') %>%
    mutate(
      population_proportion = n() / nrow(data),
      cumulative_proportion = cumsum(population_proportion) - (population_proportion / 2)
    )
  
  # Fit linear regression model
  model <- lm(mean_SF12 ~ cumulative_proportion, data = income_distribution)
  
  # Calculate SII
  SII <- coef(model)[2]
  # Calulate RII
  predicted_lowest <- predict(model, newdata = data.frame(cumulative_population = min(income_distribution$cumulative_population)))
  predicted_highest <- predict(model, newdata = data.frame(cumulative_population = max(income_distribution$cumulative_population)))
  RII <- predicted_highest / predicted_lowest
  
  return(c(SII = SII, RII = RII))
}

indices_of_inequality <- function(data) {
  results <- data %>%
    group_by(run_id, scenario) %>%
    do(as.data.frame(t(calculate_indices(.)))) %>%
    ungroup()
  
  summary_results <- results %>%
    group_by(scenario) %>%
    summarise(
      mean_SII = mean(SII),
      sd_SII = sd(SII),
      mean_RII = mean(RII),
      sd_RII = sd(RII)
    )
  
  return(summary_results)
}


##################### PRIORITY SUBGROUPS ###################

priority_summarise_ethnicity <- function(data) {
  data <- data %>%
    filter(ethnicity != 'WBI') %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

priority_summarise_child_under_one <- function(data) {
  data <- data %>%
    filter(substr(child_ages, 1, 1) == 0) %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

priority_summarise_three_plus_children <- function(data) {
  data <- data %>%
    filter(nkids >= 3) %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

priority_summarise_mother_under_25 <- function(data) {
  data <- data %>%
    filter((age < 25) & (nkids_ind > 0)) %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

priority_summarise_disabled <- function(data) {
  data <- data %>%
    group_by(hidp, run_id, scenario) %>%
    mutate(disabled_flag = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE)) %>%
    ungroup() %>%
    filter(disabled_flag == TRUE) %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

priority_any_summarise <- function(data) {
  data <- data %>%
    group_by(run_id, hidp, scenario) %>%
    mutate(priority_ethnic = ifelse(any(ethnicity != 'WBI'), TRUE, FALSE),
           priority_child_under_one = ifelse(any(substr(child_ages, 1, 1) == 0), TRUE, FALSE),
           priority_three_plus_children = ifelse(any(nkids >= 3), TRUE, FALSE),
           priority_mother_under_25 = ifelse(any((age < 25) & (nkids_ind > 0)), TRUE, FALSE),
           priority_disabled = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE),
           num_priority_groups = sum(c(priority_ethnic, priority_child_under_one,
                                       priority_three_plus_children, priority_mother_under_25,
                                       priority_disabled)),
           priority_any = ifelse(num_priority_groups > 0, TRUE, FALSE)
    ) %>%
    ungroup() %>%
    filter(priority_any == TRUE) %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  return(data)
}

priority_any_confint_summarise <- function(data) {
  data <- data %>%
    group_by(run_id, hidp, scenario) %>%
    mutate(priority_ethnic = ifelse(any(ethnicity != 'WBI'), TRUE, FALSE),
           priority_child_under_one = ifelse(any(substr(child_ages, 1, 1) == 0), TRUE, FALSE),
           priority_three_plus_children = ifelse(any(nkids >= 3), TRUE, FALSE),
           priority_mother_under_25 = ifelse(any((age < 25) & (nkids_ind > 0)), TRUE, FALSE),
           priority_disabled = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE),
           num_priority_groups = sum(c(priority_ethnic, priority_child_under_one,
                                       priority_three_plus_children, priority_mother_under_25,
                                       priority_disabled)),
           priority_any = ifelse(num_priority_groups > 0, TRUE, FALSE)
    ) %>%
    ungroup() %>%
    filter(priority_any == TRUE) %>%
    group_by(scenario) %>%
    summarise(count = n(),
              SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  return(data)
}

priority_num_summarise <- function(data) {
  data <- data %>%
    group_by(run_id, hidp, scenario) %>%
    mutate(priority_ethnic = ifelse(any(ethnicity != 'WBI'), TRUE, FALSE),
           priority_child_under_one = ifelse(any(substr(child_ages, 1, 1) == 0), TRUE, FALSE),
           priority_three_plus_children = ifelse(any(nkids >= 3), TRUE, FALSE),
           priority_mother_under_25 = ifelse(any((age < 25) & (nkids_ind > 0)), TRUE, FALSE),
           priority_disabled = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE)
    ) %>%
    ungroup() %>%
    mutate(num_priority_groups = (rowSums(select(., starts_with("priority_"))))) %>%
    mutate(num_priority_groups = case_when(
      num_priority_groups == 0 ~ 0,
      num_priority_groups == 1 ~ 1,
      num_priority_groups >= 2 ~ 2)) %>%
    group_by(num_priority_groups, run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  return(data)
}

priority_num_confint_summarise <- function(data) {
  data <- data %>%
    group_by(run_id, hidp, scenario) %>%
    mutate(priority_ethnic = ifelse(any(ethnicity != 'WBI'), TRUE, FALSE),
           priority_child_under_one = ifelse(any(substr(child_ages, 1, 1) == 0), TRUE, FALSE),
           priority_three_plus_children = ifelse(any(nkids >= 3), TRUE, FALSE),
           priority_mother_under_25 = ifelse(any((age < 25) & (nkids_ind > 0)), TRUE, FALSE),
           priority_disabled = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE)
    ) %>%
    ungroup() %>%
    mutate(num_priority_groups = (rowSums(select(., starts_with("priority_"))))) %>%
    mutate(num_priority_groups = case_when(
      num_priority_groups == 0 ~ 0,
      num_priority_groups == 1 ~ 1,
      num_priority_groups == 2 ~ 2)) %>%
    group_by(num_priority_groups, scenario) %>%
    summarise(count = n(),
              SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  return(data)
}


###################### RUN THIS STUFF! ######################


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
                   families_income_quint_together = families_income_quint_summary,
                   priority_any = priority_any_summarise,
                   priority_num = priority_num_summarise,
                   priority_ethnicity = priority_summarise_ethnicity,
                   priority_child_under_one = priority_summarise_child_under_one,
                   priority_mother_under_25 = priority_summarise_mother_under_25,
                   priority_three_plus_children = priority_summarise_three_plus_children
                   )

# indices_of_inequality = indices_of_inequality

# disable summary not working for some reason
# priority_disabled = priority_summarise_disabled,



# Combine summaries across years for each type of summary
combine_summaries_across_years(summary_funcs, save.path1, save.path2)

# Remove intermediates folder and its contents
unlink(save.path2, recursive = TRUE)
