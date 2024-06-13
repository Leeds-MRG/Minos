
library(here)
library(tidyverse)
library(data.table)
require(parallelly)
require(future)
require(future.apply)

# Suppress summarise info
options(dplyr.summarise.inform = FALSE)

###################### HELPER FUNCTIONS  ######################

get_latest_runtime_subdirectory <- function(path) {
  # first select only the path (not filenames)
  out.folders <- list.files(path)
  
  # if more than 1, take the most recent
  if(length(out.folders) == 1) {
    path = paste0(path, '/', out.folders[1], '/')
  }
  else if(length(out.folders) > 1) {
    out.folders.date <- as.POSIXlt(out.folders, format='%Y_%m_%d_%H_%M_%S')
    
    max.date <- max(out.folders.date)
    
    # Collecting these objects here as they have to be formatted
    yr <- max.date$year + 1900 # year is years since 1900
    month <- formatC(max.date$mon + 1, width=2, flag='0') # months are zero indexed (WHY??)
    day <- formatC(max.date$mday, width=2, flag='0')
    hour <- formatC(max.date$hour, width=2, flag='0')
    min <- formatC(max.date$min, width=2, flag='0')
    sec <- formatC(max.date$sec, width=2, flag='0')
    
    str.date <- paste0(yr, '_',
                       month, '_',
                       day, '_',
                       hour, '_',
                       min, '_',
                       sec)
    
    path <- paste0(path, '/', str.date, '/')
  }
  return(path)
}

# extract run_id from filepath string, so it can be attached to each output file
extract_run_id <- function(filepath) {
  # Extracts the run_id using a regular expression
  run_id <- gsub(".*/(\\d+)_run_id_\\d+\\.csv$", "\\1", filepath)
  return(run_id)
}

# remove any dead people from each run
drop_dead <- function(data) {
  data <- data %>%
    filter(alive != 'dead') %>%
    select(-alive)
  return(data)
}

drop_zero_weight <- function(data) {
  # Drop zero weight or missing weight individuals
  data <- data %>%
    filter(weight != 0) %>%
    filter(weight > 0)
  return(data)
}

drop_unnecessary_cols <- function(data, scen) {
  # Only keep specific columns to reduce memory requirements
  
  # cols we always need
  keep.cols <- c('pidp', 'hidp', 'time', 'alive', 'weight', 'sex', 'age', 'ethnicity', 
                 'child_ages', 'S7_labour_state', 'hh_income', 'SF_12', 'nkids',
                 'nkids_ind', 'init_relative_poverty', 'init_absolute_poverty', 
                 'universal_credit', 'income_quintile')
  
  # cols only needed in intervention summaries
  int.cols <- c('boost_amount', 'income_boosted')
  
  # if not baseline, we need intervention cols
  if (stringr::str_detect(scen, 'baseline', negate = TRUE)) {
    keep.cols <- c(keep.cols, int.cols)
  }
  
  # , 'simd_quintile'
  
  data <- data %>%
    select(all_of(keep.cols))
  
  return(data)
}

create.if.not.exists <- function(path) {
  if(!file.exists(path)) {
    dir.create(path = path)
  }
}

###################### SUMMARISE FUNCTIONS  ######################

whole_pop_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

whole_pop_confint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

whole_pop_income_quint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(run_id, time) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      ungroup() %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(run_id, time) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      ungroup() %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

whole_pop_income_quint2_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

whole_pop_income_quintile_confint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      group_by(income_quintile) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      group_by(income_quintile) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

families_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

families_confint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

families_income_quint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      group_by(run_id, time) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      ungroup() %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      group_by(run_id, time) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      ungroup() %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

families_income_quint2_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      group_by(run_id, income_quintile) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

families_income_quint_confint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      group_by(income_quintile) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      filter(nkids > 0) %>%
      mutate(income_quintile = ntile(hh_income, 5)) %>%  # Create income quintiles
      group_by(income_quintile) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

treated_relative_summarise <- function(data) {
  if (('boost_amount' %in% names(data)) & (mean(data$time) != 2020)) {
    data <- data %>%
      filter(weight > 0) %>%
      filter((init_relative_poverty == 1) & (nkids > 0)) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      filter((init_relative_poverty == 1) & (nkids > 0)) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

treated_absolute_summarise <- function(data) {
  if (('boost_amount' %in% names(data)) & (mean(data$time) != 2020)) {
    data <- data %>%
      filter(weight > 0) %>%
      filter((init_absolute_poverty == 1) & (nkids > 0)) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      filter((init_absolute_poverty == 1) & (nkids > 0)) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

men_illness_risk_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    mutate(mental_health_risk = (SF_12 < 45.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n()) %>%
    ungroup() %>%
    group_by(run_id) %>%
    mutate(prop = count / sum(count))
}

men_illness_risk_families_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    filter(nkids > 0) %>%
    mutate(mental_health_risk = (SF_12 < 45.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n()) %>%
    ungroup() %>%
    group_by(run_id) %>%
    mutate(prop = count / sum(count))
}

#mutate(kids = (nkids > 0)) %>%
#group_by(kids)

group_summarise <- function(data, group.var) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(.data[[group.var]], run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(.data[[group.var]], run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

simd_generate_quintiles <- function(data) {
  data[['simd_quintile']] <- round(data[['simd_decile']] / 2)
  return(data)
}

UC_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_rel_pov_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, init_relative_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, init_relative_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_kids_rel_pov_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0,
             nkids > 0) %>%
      group_by(universal_credit, init_relative_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0,
             nkids > 0) %>%
      group_by(universal_credit, init_relative_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_abs_pov_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, init_absolute_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, init_absolute_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_kids_abs_pov_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0,
             nkids > 0) %>%
      group_by(universal_credit, init_absolute_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0,
             nkids > 0) %>%
      group_by(universal_credit, init_absolute_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_gender_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, sex, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(weight > 0) %>%
      group_by(universal_credit, sex, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

###################### PRIORITY SUBGROUPS ######################

priority_summarise_ethnicity <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(ethnicity != 'WBI') %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(ethnicity != 'WBI') %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_child_under_one <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(substr(child_ages, 1, 1) == 0) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(substr(child_ages, 1, 1) == 0) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_three_plus_children <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(nkids >= 3) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(nkids >= 3) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_mother_under_25 <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter((age < 25) & (nkids_ind > 0)) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(nkids >= 3) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_disabled <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(hidp, run_id) %>%
      mutate(disabled_flag = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE)) %>%
      filter(disabled_flag == TRUE) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(hidp, run_id) %>%
      mutate(disabled_flag = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE)) %>%
      filter(disabled_flag == TRUE) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_any_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(run_id, hidp) %>%
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
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
  } else {
    data <- data %>%
      group_by(run_id, hidp) %>%
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
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_any_confint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(run_id, hidp) %>%
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
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
  } else {
    data <- data %>%
      group_by(run_id, hidp) %>%
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
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_num_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(run_id, hidp) %>%
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
        num_priority_groups == 2 ~ 2,
        num_priority_groups >= 3 ~ 3)) %>%
      group_by(num_priority_groups, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    
  } else {
    data <- data %>%
      group_by(run_id, hidp) %>%
      mutate(priority_ethnic = ifelse(any(ethnicity != 'WBI'), TRUE, FALSE),
             priority_child_under_one = ifelse(any(substr(child_ages, 1, 1) == 0), TRUE, FALSE),
             priority_three_plus_children = ifelse(any(nkids >= 3), TRUE, FALSE),
             priority_mother_under_25 = ifelse(any((age < 25) & (nkids_ind > 0)), TRUE, FALSE),
             priority_disabled = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE)
      ) %>%
      ungroup() %>%
      mutate(num_priority_groups = (rowSums(select(., starts_with("priority_"))))) %>%
      mutate(num_priority_groups = case_when(
        num_priority_groups == 1 ~ 1,
        num_priority_groups == 2 ~ 2,
        num_priority_groups >= 3 ~ 3)) %>%
      group_by(num_priority_groups, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_num_confint_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(run_id, hidp) %>%
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
        num_priority_groups == 2 ~ 2,
        num_priority_groups >= 3 ~ 3)) %>%
      group_by(num_priority_groups) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    
  } else {
    data <- data %>%
      group_by(run_id, hidp) %>%
      mutate(priority_ethnic = ifelse(any(ethnicity != 'WBI'), TRUE, FALSE),
             priority_child_under_one = ifelse(any(substr(child_ages, 1, 1) == 0), TRUE, FALSE),
             priority_three_plus_children = ifelse(any(nkids >= 3), TRUE, FALSE),
             priority_mother_under_25 = ifelse(any((age < 25) & (nkids_ind > 0)), TRUE, FALSE),
             priority_disabled = ifelse(any(S7_labour_state == 'disabled'), TRUE, FALSE)
      ) %>%
      ungroup() %>%
      mutate(num_priority_groups = (rowSums(select(., starts_with("priority_"))))) %>%
      mutate(num_priority_groups = case_when(
        num_priority_groups == 1 ~ 1,
        num_priority_groups == 2 ~ 2,
        num_priority_groups >= 3 ~ 3)) %>%
      group_by(num_priority_groups) %>%
      summarise(count = n(),
                SF_12_margin = qnorm(0.975) * (sd(SF_12) / sqrt(count)),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

###################### READ FUNCTIONS  ######################

# Step 1: Load Data for One Year
load_data_for_year <- function(scen.path, year, scen) {
  
  # Create file strings using year from args
  file_pattern <- sprintf("*_run_id_%d.csv", year)
  file_list <- list.files(path = scen.path,
                          pattern = file_pattern,
                          full.names = TRUE)
  
  # no_cores <- availableCores(omit=1)
  # plan(multisession, workers = no_cores)  # Set up parallel plan
  
  # Use future_lapply with file_paths and fread
  #data_list <- future_lapply(file_list, fread, stringsAsFactors = TRUE)
  
  #data_list <- lapply(file_list, read.csv)
  data_list <- lapply(file_list, fread)
  data_list <- lapply(data_list, as.data.frame)
  
  # Keep only certain columns (check function above for list)
  data_list <- lapply(data_list, drop_unnecessary_cols, scen)
  
  # Now drop dead and zero weight
  data_list <- lapply(data_list, drop_dead)
  data_list <- lapply(data_list, drop_zero_weight)
  
  # Add run_id to each dataframe
  for (i in seq_along(data_list)) {
    run_id <- extract_run_id(file_list[i])
    data_list[[i]]$run_id <- as.numeric(str_remove(run_id, "^0+"))
  }
  
  return(data_list)
}

# Step 2: Generate Summary CSVs
generate_summary_csv <- function(data_list, year, summary_funcs, save.path) {
  for (summary_name in names(summary_funcs)) {
    summary_func <- summary_funcs[[summary_name]]
    summary_filename <- sprintf("%s/summary_%s_%d.csv", save.path, summary_name, year)
    summary_data <- lapply(data_list, summary_func)
    #rm(data_list)
    combined_summary <- do.call(rbind, summary_data)
    rm(summary_data)
    write.csv(combined_summary, file = summary_filename, row.names = FALSE)
    rm(combined_summary)
  }
}




###################### RUN THIS STUFF! ######################

args <- commandArgs(trailingOnly=TRUE)
#args <- list('default_config', 'cpr_summary_out_test', 'ChildPovertyReductionRELATIVE_2_batch')

# constants
# start.year <- 2020
# end.year <- 2035

out.path <- here::here('output', args[1])
#out.path <- '/home/luke/Documents/WORK/MINOS/Minos/output/default_config/'
save.path.base <- here::here(out.path, args[2])
save.path1 <- here::here(save.path.base, args[3])
save.path2 <- here::here(save.path1, 'intermediates')
scen <- args[[3]]
year <- as.numeric(args[[4]])



create.if.not.exists(save.path.base)
create.if.not.exists(save.path1)
create.if.not.exists(save.path2)

scen.path <- here::here(out.path, scen)
scen.path <- get_latest_runtime_subdirectory(scen.path)

# Create named list of summary functions to go through
summary_funcs <- c(whole_pop = whole_pop_summarise,
                   whole_pop_income_quint = whole_pop_income_quint_summarise,
                   whole_pop_income_quint2 = whole_pop_income_quint2_summarise,
                   families = families_summarise,
                   families_income_quint = families_income_quint_summarise,
                   families_income_quint2 = families_income_quint2_summarise,
                   treated_relative = treated_relative_summarise,
                   treated_absolute = treated_absolute_summarise,
                   priority_any = priority_any_summarise,
                   priority_num = priority_num_summarise,
                   men_illness_risk = men_illness_risk_summarise,
                   men_illness_risk_families = men_illness_risk_families_summarise
)

# whole_pop_confint = whole_pop_confint_summarise,
# whole_pop_income_quint_confint = whole_pop_income_quintile_confint_summarise,
# families_confint = families_confint_summarise,
# families_income_quint_confint = families_income_quint_confint_summarise,
# priority_any_confint = priority_any_confint_summarise,
# priority_num_confint = priority_num_confint_summarise,




# UC = UC_summarise,
# UC_rel_pov = UC_rel_pov_summarise,
# UC_kids_rel_pov = UC_kids_rel_pov_summarise,
# UC_abs_pov = UC_abs_pov_summarise,
# UC_kids_abs_pov = UC_kids_abs_pov_summarise,
# UC_gender = UC_gender_summarise
# priority_any2 = priority_summarise_any2,


# Step 5: Script Execution
# for (year in start.year:end.year) {
#   
# }

print(sprintf('Starting for year %s', year))
data_list <- load_data_for_year(scen.path, year, scen)
generate_summary_csv(data_list, year, summary_funcs, save.path2)
rm(data_list)
print(sprintf('Finished for year %s', year))
