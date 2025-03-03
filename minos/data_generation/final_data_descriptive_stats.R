# This file reports simple summary statistics for key variabels used in the SSM paper

require(xtable)
library(Hmisc)

library(dplyr)
library(reshape2)

income_main <- function() {
  
  # load in final data for 2020.
  final.data <- read.csv("data/final_US/2020_US_cohort.csv")
  
  # get key variables
  key_columns <- c("age",
                   "nkids",
                   "sex", 
                   "ethnicity", 
                   "region", 
                   "education_state", 
                   "housing_quality",
                   "neighbourhood_safety",
                   "marital_status",
                   "hh_comp",
                   "hh_income",
                   "job_sector",
                   "job_sec",
                   "nutrition_quality",
                   "SF_12_MCS",
                   "loneliness")
  
  key_continuous_columns <- c("age",
                             "hh_income",
                             "nutrition_quality",
                             "SF_12_MCS")
  
  key_discrete_columns <- c(
                   "nkids",
                   "sex", 
                   "ethnicity", 
                   "region", 
                   "education_state", 
                   "housing_quality",
                   "neighbourhood_safety",
                   "marital_status",
                   "hh_comp",
                   "job_sector",
                   "job_sec",
                   "loneliness")
  # get input statistics
  summary.table <- summary(final.data[, c(key_continuous_columns)])
  
  # xtable to convert to tex table and save.ne
  continuous.table <- xtable(summary.table, 
         caption = "Summary statistics for key continous variables in the MINOS model.",
         label = "tab: key_continuous_variable_summaries",
         type='tex')
  align(continuous.table) <- "|l|l|l|l|l|"
  print(continuous.table, file = "plots/income_key_continuous_variables_table.tex",
        include.rownames=FALSE)
  
  melted_discrete_vars <- melt(final.data[, c(key_discrete_columns)],measure.vars=c(key_discrete_columns))
  
  discrete.counts.data <- melted_discrete_vars %>%
    group_by(variable, value) %>%
    summarise (n = n()) %>%
    mutate(freq = n / sum(n))
  
  
  #make an 'export' variable
  discrete.counts.data$export <- with(discrete.counts.data, sprintf("%i (%.1f%%)", n, freq*100))
  
  #reshape again
  output <- dcast(variable+value~1, value.var="export", data=discrete.counts.data, fill="missing") #use drop=F to prevent silent missings 
  #'silent missings'
  output$variable <- as.character(output$variable)
  #make 'empty lines' 
  hline_spots <-which(!duplicated(output$variable))
  hline_spots <- c(hline_spots, hline_spots-1, c(-1))
  output[which(duplicated(output$variable)), "variable"] <- ""
  
  discrete.table <- xtable(output,
         caption = "Summary statistics for key discrete variables in the MINOS model.",
         label = "tab: key_discrete_variable_summaries",
         type='tex')
  align(discrete.table) <- "|l|l|l|l|"
  print(discrete.table, 
        file = "plots/income_key_discrete_variables_table.tex", 
        tabular.environment = "longtable",
        hline.after = hline_spots, 
        include.rownames=FALSE)
}


energy_main <- function() {
  
  # load in final data for 2020.
  final.data <- read.csv("data/final_US/2020_US_cohort.csv")
  
  # get key variables
  key_columns <- c("age",
                   "nkids",
                   "sex", 
                   "ethnicity", 
                   "region", 
                   "education_state", 
                   "housing_quality",
                   "neighbourhood_safety",
                   "marital_status",
                   "net_hh_income",
                   "hh_income",
                   "hh_comp",
                   "hh_net_income",
                   "job_sector",
                   "job_sec",
                   "nutrition_quality",
                   "SF_12_MCS",
                   "SF_12_PCS",
                   "auditc",
                   "FP10",
                   "loneliness",
                   "hh_rent",
                   "hh_mortgage",
                   "yearly_energy",
                   "active",
                   "financial_situation",
                   "behind_on_bills",
                   "council_tax",
                   "ncars",
                   "ncigs",
                   "number_of_bedrooms",
                   "housing_tenure"
                   #"housing_sector"
  )
  
  key_continuous_columns <- c("age",
                              "net_hh_income",
                              "hh_income",
                              "nutrition_quality",
                              "council_tax",
                              "SF_12_MCS",
                              "SF_12_PCS",
                              "hh_rent",
                              "hh_mortgage",
                              "hh_comp",
                              "ncars",
                              "ncigs",
                              "yearly_energy")
  
  key_discrete_columns <- c(
    "nkids",
    "sex", 
    "ethnicity", 
    "region", 
    "education_state", 
    "housing_quality",
    "neighbourhood_safety",
    "marital_status",
    "job_sector",
    "job_sec",
    "loneliness",
    "FP10",
    "active",
    "financial_situation",
    "behind_on_bills",
    "marital_status",
    "number_of_bedrooms",
    "auditc",
    "housing_tenure"
    #"housing_sector"
    )
  # get input statistics
  summary.table <- t(summary(final.data[, c(key_continuous_columns)]))
  #colnames(summary.table) <- key_continuous_columns
  
  # xtable to convert to tex table and save.ne
  continuous.table <- xtable(summary.table, 
                             caption = "Summary statistics for key continous variables in the MINOS model.",
                             label = "tab: key_continuous_variable_summaries",
                             type='tex')
  align(continuous.table) <- "|l|l|l|l|l|l|l|"#l|l|l|l|l|l|l|"
  print(continuous.table, file = "plots/energy_key_continuous_variables_table.tex",
        include.rownames=T)
  
  melted_discrete_vars <- melt(final.data[, c(key_discrete_columns)],measure.vars=c(key_discrete_columns))
  
  discrete.counts.data <- melted_discrete_vars %>%
    group_by(variable, value) %>%
    summarise (n = n()) %>%
    mutate(freq = n / sum(n))
  
  
  #make an 'export' variable
  discrete.counts.data$export <- with(discrete.counts.data, sprintf("%i (%.1f%%)", n, freq*100))
  
  #reshape again
  #output <- dcast(variable+value~1, value.var="export", data=discrete.counts.data, fill="missing") #use drop=F to prevent silent missings 
  output <- discrete.counts.data
  #'silent missings'
  output$variable <- as.character(output$variable)
  #make 'empty lines' 
  hline_spots <-which(!duplicated(output$variable))
  hline_spots <- c(hline_spots, hline_spots-1, c(-1))
  output[which(duplicated(output$variable)), "variable"] <- ""
  
  discrete.table <- xtable(output,
                           caption = "Summary statistics for key discrete variables in the MINOS model.",
                           label = "tab: key_discrete_variable_summaries",
                           type='tex')
  align(discrete.table) <- "|l|l|l|l|l|l|"
  print(discrete.table, 
        file = "plots/energy_key_discrete_variables_table.tex", 
        tabular.environment = "longtable",
        hline.after = hline_spots, 
        include.rownames=FALSE)
}


income_main()
energy_main()
