library(VIM)
library(ggmice)
library(here)
library(dplyr)
library(ggplot2)
library(viridis)
library(tidyr)

source("minos/utils_datain.R")
source("minos/transitions/utils.R")


categorical_missing_different_plot <- function(data, v1, v2) {
  
  data <- replace.missing(data)
  #browser()
  plot.data <- data %>%
    mutate(is_missing = factor(is.na(!!sym(v1)), labels = c("observed height", "missing height"))) %>%
    group_by(is_missing, !!sym(v2)) %>% 
    summarise(count = n()) %>% 
    drop_na() %>%
    mutate(perc = count/sum(count)) 
  
  categorical_lonely_sf12_plot <- ggmice(plot.data, aes(x=!!sym(v2), y=perc)) +
    geom_bar(aes(fill=factor(!!sym(v2)), color='black'), stat='identity') +
    facet_wrap(~ is_missing)
  ggsave(paste0("plots/", v1, "_vs_", v2, "_missing_dist.pdf"))
}

main <- function() {
  
  # load in all post LOCFcorrected data? maybe composite?
  # MICE impuation from notebook
  # save to individual waves.
  # get composite/complete case this data instead. I.E. slot into current pipeline and makes. 
  start.data <- read.csv("data/composite_US/2019_US_cohort.csv") 
  after.data <- read.csv("data/mice_US/2020_US_cohort.csv") 
  
  mice_columns <- c("age",
                    "region",
                    #"heating",
                    "job_sec",
                    "ncigs",
                    "education_state",
                    "ethnicity",
                    "loneliness",
                    "sex",
                    "SF_12",
                    #"SF_12p",
                    #"smoker",
                    "nkids",
                    "behind_on_bills",
                    "financial_situation",
                    "future_financial_situation",
                    "likely_move",
                    "ghq_depression",
                    "ghq_happiness",
                    "clinical_depression",
                    "scsf1",
                    "health_limits_social",
                    #"hhsize",
                    #"housing_tenure",
                    #"urban",
                    "housing_quality",
                    "hh_income",
                    "neighbourhood_safety",
                    "S7_labour_state",
                    "yearly_energy",
                    "nutrition_quality"
                    #"hh_comp",
                    #"marital_status"
                    )
  
  # mice_columns <- c("age",
  #                   "region", 
  #                   #"heating", 
  #                   "job_sec", 
  #                   "ncigs",
  #                   "education_state",            
  #                   "ethnicity",
  #                   "loneliness",
  #                   "sex", 
  #                   "SF_12",
  #                   #"SF_12p",
  #                   #"smoker",
  #                   "nkids",       
  #                   "behind_on_bills",
  #                   "financial_situation",
  #                   "future_financial_situation",
  #                   "likely_move",
  #                   "ghq_depression",
  #                   "ghq_happiness",
  #                   "clinical_depression", 
  #                   "scsf1",
  #                   "health_limits_social",
  #                   #"hhsize",
  #                   #"housing_tenure",
  #                   #"urban", 
  #                   "housing_quality",
  #                   "hh_income",
  #                   "neighbourhood_safety",
  #                   "S7_labour_state",
  #                   "yearly_energy",
  #                   "nutrition_quality"
  #                   #"hh_comp", 
  #                   #"marital_status"
  # )
  
  # mice_columns <- c("age", 
  #                   "region", 
  #                   "job_sec", 
  #                   "ncigs",
  #                   "education_state",            
  #                   "ethnicity",
  #                   "loneliness",
  #                   "sex", 
  #                   "SF_12",
  #                   #"SF_12p",
  #                   #"smoker",
  #                   "nkids",       
  #                   "behind_on_bills",
  #                   "financial_situation",
  #                   "future_financial_situation",
  #                   "likely_move",
  #                   "ghq_depression",
  #                   "ghq_happiness",
  #                   "clinical_depression", 
  #                   "scsf1",
  #                   "health_limits_social",
  #                   'heating',
  #                   #"hhsize",
  #                   #"housing_tenure",
  #                   #"urban", 
  #                   "housing_quality",
  #                   "hh_income",
  #                   "neighbourhood_safety",
  #                   "S7_labour_state",
  #                   "yearly_energy",
  #                   "nutrition_quality",
  #                   "housing_tenure",
  #                   "marital_status",
  #                   'hourly_wage',
  #                   'auditc',
  #                   'active',
  #                   'SF_12_PCS',
  #                   'smoker',#,
  #                   "number_of_rooms")
  #                   
  key_columns <- c("age", 
                   "region", 
                   #"heating", 
                   "ncigs",
                   "education_state",            
                   "ethnicity",
                   #"loneliness",
                   "sex", 
                   "SF_12",
                   #"SF_12p",
                   #"hhsize",
                   "housing_tenure",
                   "housing_quality",
                   "hh_income",
                   "neighbourhood_safety",
                   "S7_labour_state",
                   #"yearly_energy",
                   "nutrition_quality",
                   "hh_comp", 
                   "marital_status"
  )
  
  #other.data <- start.data[, !names(start.data) %in% mice_columns]
  #mice.data <- start.data[, c(mice_columns)]
  mice.data <- replace.missing(start.data)

  pdf("plots/ssm_key_variable_missing_structure.pdf")
  aggr(mice.data[, mice_columns], cex.axis = .7, oma = c(10,5,5,0))
  dev.off()
  
  #spineMiss(mice.data[, c("SF_12", "loneliness")])
  
  # shows a few correlations.
  # wrt loneliness only sf-12 and marital status. 
  # 
  
  
  correlation_plot <- plot_corr(mice.data[, mice_columns]) + 
    scale_fill_continuous_diverging(palette="Tropic", mid=0) +
    theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))
  ggsave("plots/correlation_plot.pdf")
  
  categorical_missing_different_plot(mice.data, "marital_status", "loneliness") 
  categorical_missing_different_plot(mice.data, "SF_12", "loneliness")
  categorical_missing_different_plot(mice.data, "SF_12", "ghq_depression")
}

main()


# load before and after imputation missingness structures
# ggmice for correlation and cross coverage. 



