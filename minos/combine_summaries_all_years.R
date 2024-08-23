
library(here)
library(tidyverse)
library(data.table)


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
      group_by(run_id, year) %>%
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
      group_by(run_id, year) %>%
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
      group_by(run_id, year) %>%
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
      group_by(run_id, year) %>%
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
    summarise(count = n(),
              prop = count / sum(count))
}

men_illness_risk_families_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    filter(nkids > 0) %>%
    mutate(mental_health_risk = (SF_12 < 45.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n(),
              prop = count / sum(count))
}

UC_men_illness_risk_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0,
           universal_credit == 1) %>%
    mutate(mental_health_risk = (SF_12 < 45.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n()) %>%
    ungroup() %>%
    group_by(run_id) %>%
    mutate(prop = count / sum(count))
}

UC_men_illness_risk_families_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0,
           universal_credit == 1,
           nkids > 0) %>%
    mutate(mental_health_risk = (SF_12 < 45.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n()) %>%
    ungroup() %>%
    group_by(run_id) %>%
    mutate(prop = count / sum(count))
}

UC_men_illness_risk_higher_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0,
           universal_credit == 1) %>%
    mutate(mental_health_risk = (SF_12 < 46.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n()) %>%
    ungroup() %>%
    group_by(run_id) %>%
    mutate(prop = count / sum(count))
}

UC_men_illness_risk_higher_families_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0,
           universal_credit == 1,
           nkids > 0) %>%
    mutate(mental_health_risk = (SF_12 < 46.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n()) %>%
    ungroup() %>%
    group_by(run_id) %>%
    mutate(prop = count / sum(count))
}

UC_men_illness_risk_lower_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0,
           universal_credit == 1) %>%
    mutate(mental_health_risk = (SF_12 < 44.6)) %>%  # IS THIS VALUE CORRECT??
    group_by(run_id, mental_health_risk) %>%
    summarise(count = n()) %>%
    ungroup() %>%
    group_by(run_id) %>%
    mutate(prop = count / sum(count))
}

UC_men_illness_risk_lower_families_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0,
           universal_credit == 1,
           nkids > 0) %>%
    mutate(mental_health_risk = (SF_12 < 44.6)) %>%  # IS THIS VALUE CORRECT??
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

#### UC SUMMARIES ####

UC_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    group_by(universal_credit, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

UC_rel_pov_summarise <- function(data) {
  
  hh_rep_income <- data %>%
    filter(weight > 0) %>%
    group_by(hidp) %>%
    slice(1) %>%
    ungroup()
  
  hh_median_income <- median(hh_rep_income$hh_income)
  
  data <- data %>%
    filter(weight > 0) %>%
    group_by(hidp) %>%
    mutate(relative_poverty = hh_income < (hh_median_income * 0.6)) %>%
    ungroup() %>%
    group_by(universal_credit, relative_poverty, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

UC_init_rel_pov_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    group_by(universal_credit, init_relative_poverty, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

UC_kids_rel_pov_summarise <- function(data) {
  
  hh_rep_income <- data %>%
    filter(weight > 0) %>%
    group_by(hidp) %>%
    slice(1) %>%
    ungroup()
  
  hh_median_income <- median(hh_rep_income$hh_income)
  
  data <- data %>%
    filter(weight > 0,
           nkids > 0) %>%
    group_by(hidp) %>%
    mutate(relative_poverty = hh_income < (hh_median_income * 0.6)) %>%
    ungroup() %>%
    group_by(universal_credit, relative_poverty, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

UC_kids_init_rel_pov_summarise <- function(data) {
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
  return(data)
}

UC_abs_pov_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    mutate(absolute_poverty = hh_income < 955.54) %>%
    group_by(universal_credit, absolute_poverty, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

UC_init_abs_pov_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    group_by(universal_credit, init_absolute_poverty, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

UC_kids_abs_pov_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0,
           nkids > 0) %>%
    mutate(absolute_poverty = hh_income < 955.54) %>%
    group_by(universal_credit, absolute_poverty, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
  return(data)
}

UC_kids_init_abs_pov_summarise <- function(data) {
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
  return(data)
}

UC_gender_summarise <- function(data) {
  data <- data %>%
    filter(weight > 0) %>%
    group_by(universal_credit, sex, run_id) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  #TODO: Add number households affected by interventions and other stats
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

priority_lone_parent_summarise <- function(data) {
  data <- data %>%
    group_by(hidp, run_id) %>%
    mutate(
      num_adults = n(),  # Calculate the total number of individuals in the household
      lone_parent_flag = ifelse(num_adults == 1 & nkids > 0, 1, 0) # Lone parent flag
    ) %>%
    ungroup()
  
  # Summarize data disaggregated by lone parent status
  data <- data %>%
    group_by(lone_parent_flag) %>%
    summarise(
      count = n(),
      hh_income = weighted.mean(hh_income, w = weight, na.rm = TRUE),
      SF_12 = weighted.mean(SF_12, w = weight, na.rm = TRUE),
      total_cost = sum(boost_amount, na.rm = TRUE),
      mean_cost = mean(boost_amount, na.rm = TRUE)
    )
  
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

# Step 3: Combine Summaries Across Years
combine_summaries_across_years <- function(summary_funcs, save.path1, save.path2) {
  for (summary_name in names(summary_funcs)) {
    print(sprintf('About to combine summaries for %s', summary_name))
    combined_summary <- NULL
    for (year in start.year:end.year) {
      summary_filename <- sprintf("%s/summary_%s_%d.csv", save.path2, summary_name, year)
      year_summary <- read.csv(summary_filename)
      
      # Check if the file is empty (only header or no data)
      if (nrow(year_summary) == 0) {
        message(sprintf("Skipping empty file: %s", summary_filename))
        next  # Skip to the next iteration
      }
      
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
save.path1 <- here::here(save.path.base, args[3])
save.path2 <- here::here(save.path1, 'intermediates')
scen <- args[[3]]


# Create named list of summary functions to go through
summary_funcs <- c(whole_pop = whole_pop_summarise,
                   whole_pop_income_quint = whole_pop_income_quint_summarise,
                   families = families_summarise,
                   families_income_quint = families_income_quint_summarise,
                   UC = UC_summarise,
                   UC_rel_pov = UC_rel_pov_summarise,
                   UC_init_rel_pov = UC_init_rel_pov_summarise,
                   UC_kids_rel_pov = UC_kids_rel_pov_summarise,
                   UC_kids_init_rel_pov = UC_kids_init_rel_pov_summarise,
                   UC_abs_pov = UC_abs_pov_summarise,
                   UC_init_abs_pov = UC_init_abs_pov_summarise,
                   UC_kids_abs_pov = UC_kids_abs_pov_summarise,
                   UC_kids_init_abs_pov = UC_kids_init_abs_pov_summarise,
                   UC_gender = UC_gender_summarise,
                   priority_any = priority_any_summarise,
                   men_illness_risk = men_illness_risk_summarise,
                   men_illness_risk_families = men_illness_risk_families_summarise,
                   UC_men_illness_risk = UC_men_illness_risk_summarise,
                   UC_families_men_illness_risk = UC_men_illness_risk_families_summarise,
                   UC_men_illness_risk_lower = UC_men_illness_risk_lower_summarise,
                   UC_families_men_illness_risk_lower = UC_men_illness_risk_lower_families_summarise,
                   UC_men_illness_risk_higher = UC_men_illness_risk_higher_summarise,
                   UC_families_men_illness_risk_higher = UC_men_illness_risk_higher_families_summarise,
                   priority_lone_parent = priority_lone_parent_summarise
)

# summary_funcs <- c(whole_pop = whole_pop_summarise,
#                    whole_pop_income_quint = whole_pop_income_quint_summarise,
#                    families = families_summarise,
#                    families_income_quint = families_income_quint_summarise,
#                    treated_relative = treated_relative_summarise,
#                    treated_absolute = treated_absolute_summarise,
#                    priority_any = priority_any_summarise,
#                    priority_num = priority_num_summarise,
#                    men_illness_risk = men_illness_risk_summarise,
#                    men_illness_risk_families = men_illness_risk_families_summarise
# )

# families_income_quint2 = families_income_quint2_summarise,
# whole_pop_income_quint2 = whole_pop_income_quint2_summarise,
# whole_pop_confint = whole_pop_confint_summarise,
# whole_pop_income_quint_confint = whole_pop_income_quintile_confint_summarise,
# families_confint = families_confint_summarise,
# families_income_quint_confint = families_income_quint_confint_summarise,
# priority_any_confint = priority_any_confint_summarise,
# priority_num_confint = priority_num_confint_summarise,



# Combine summaries across years for each type of summary
combine_summaries_across_years(summary_funcs, save.path1, save.path2)

# Remove intermediates folder and its contents
unlink(save.path2, recursive = TRUE)
