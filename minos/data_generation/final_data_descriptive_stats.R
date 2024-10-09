# This file reports simple summary statistics for key variabels used in the SSM paper

require(xtable)
library(Hmisc)

library(dplyr)
library(reshape2)

main <- function() {
  
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
  print(continuous.table, file = "plots/key_continuous_variables_table.txt",
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
        file = "plots/key_discrete_variables_table.txt", 
        tabular.environment = "longtable",
        hline.after = hline_spots, 
        include.rownames=FALSE)
}


main()