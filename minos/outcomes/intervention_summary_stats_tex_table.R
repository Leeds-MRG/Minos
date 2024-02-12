library(xtable)
library(ggplot2)

process_cost_stats_files <- function(file.name) {
  data <- read.csv(file.name)
  data[which(data$tag!="Baseline"), "SF_12_AUC"] <- data[which(data$tag!="Baseline"), "SF_12_AUC"] + data[1, "SF_12_AUC"]
  
  
  if (file.name == "plots/baselineenergyDownliftenergyDownliftNoSupport_counts_over_time.csv")
  {
    data$prct_below_45.6_baseline <- data$prct_below_45.6[33:48]
    data$prct_below_45.6_diff <- data$prct_below_45.6 - data$prct_below_45.6[33:48]
  } else {
    data$prct_below_45.6_baseline <- data$prct_below_45.6[1:16]
    data$prct_below_45.6_diff <- data$prct_below_45.6 - data$prct_below_45.6[1:16]
  }
  
  data$SF_12_AUC <- (data$SF_12_AUC - data$SF_12_AUC[1:16])
  #data$SF_12_AUC <- (data$SF_12_AUC - data$SF_12_AUC[1:16]) * 100 / data$SF_12_AUC[1:16]
  data$SF_12_AUC <- data$SF_12_AUC/data$number_boosted # 6100000
  #data$SF_12_AUC_scaled <- data$SF_12_AUC/data$number_boosted
  #ggplot(data, aes(x=year, y=SF_12_AUC_scaled, group=tag, color=tag, )) + geom_line()
  #ggplot(data, aes(x=year, y=SF_12_AUC, group=tag, color=tag)) + geom_line()
  data <- data[which(data$tag!="Baseline"), ]
  data <- data[which(data$tag!="No Support"), ]
  return (data)
}

main <- function() {
  
  # get year column
  
  
  
  uplift_rp_data <- process_cost_stats_files("plots/baseline25RelativePoverty50RelativePoverty_counts_over_time.csv")
  uplift_uc_data <- process_cost_stats_files("plots/baseline25UniversalCredit50UniversalCredit_counts_over_time.csv")
  living_wage_data <- process_cost_stats_files("plots/baselinelivingWageIntervention_counts_over_time.csv")
  energy_downlift_data <- process_cost_stats_files("plots/baselineenergyDownliftenergyDownliftNoSupport_counts_over_time.csv")
  
  
  final_table_data <- rbind(uplift_uc_data, 
                            #uplift_rp_data, 
                            living_wage_data, 
                            energy_downlift_data)
  final_table_data <- final_table_data[, c("year", 
                                           #"tag", 
                                           "intervention_cost",
                                           "number_boosted", 
                                           "population_size",
                                           "prct_below_45.6_baseline",
                                           "prct_below_45.6", 
                                           "prct_below_45.6_diff")]
  
  
  final_table_data$percentage_uplifted <- 100*final_table_data$number_boosted/final_table_data$population_size
  final_table_data$intervention_cost <- abs(final_table_data$intervention_cost)
  final_table_data$cost_per_head <- final_table_data$intervention_cost/final_table_data$number_boosted
  final_table_data$prct_below_45.6 <- 100 * final_table_data$prct_below_45.6
  final_table_data$prct_below_45.6_baseline <- 100 * final_table_data$prct_below_45.6_baseline
  final_table_data$prct_below_45.6_diff <- 100 * final_table_data$prct_below_45.6_diff
  
  final_table_data <- final_table_data[, c("year", 
                                           #"tag",
                                           #"number_boosted",
                                           #"population_size", 
                                           "percentage_uplifted", 
                                           #"intervention_cost", 
                                           "cost_per_head",
                                           "prct_below_45.6_baseline",
                                           "prct_below_45.6", 
                                           "prct_below_45.6_diff")]
  
  final_table_data[duplicated(final_table_data$tag), "tag"] <- " "
  
  n.digits <- 0
  #final_table_data$number_boosted <- as.integer(final_table_data$number_boosted)
  #final_table_data$population_size <- as.integer(final_table_data$population_size)
  final_table_data$percentage_uplifted <- round(final_table_data$percentage_uplifted, digits=2)
  #final_table_data$intervention_cost <- as.integer(final_table_data$intervention_cost)
  final_table_data$cost_per_head <- round(final_table_data$cost_per_head, digits=2)
  final_table_data$prct_below_45.6 <- round(final_table_data$prct_below_45.6, digits=2)
  final_table_data$prct_below_45.6_baseline <- round(final_table_data$prct_below_45.6_baseline, digits=2)
  final_table_data$prct_below_45.6_diff <- round(final_table_data$prct_below_45.6_diff, digits=2)
  
  colnames(final_table_data) <- c("Year", 
                                  #"Tag", 
                                  #"Intervention Population Size", 
                                  #"Total Population", 
                                  "Intervened Population Percentage", 
                                  #"Total Intervention Cost", 
                                  "Cost Per Capita",                                  
                                  "Baseline Percentage Below 45.6.",
                                  "Treated Percentage Below 45.6.",
                                  "Difference.")
  # wide table looks crap. 
  #final_table_data <- reshape(final_table_data, 
  #                            idvar='Tag', 
  #                            direction="wide", 
  #                            v.names = c("Total Intervention Cost", "Population Boosted", "Total Population", "Percentage Boosted", "Cost Per Head"),
  #                            sep=' ')
  
  final_table_data <- final_table_data[final_table_data$Year %in% c(2021, 2025, 2030, 2035), ]
  
  output.table <- xtable(final_table_data, 
                         caption = "Statistics for Policy Cost and the Number of People Who Receive Support.",
                         label = "tab: intervention_statistics")
  
  print.xtable(output.table, file="plots/sf12_intervention_statistics.tex",
               include.rownames=FALSE,
               hline.after = c(-1, 0, 4, 8, 12, 16))
  #hline.after = c(-1, 0, 16, 32, 48, 64))
  
  #uplift_25_file <- uplift_25_file[, c("population_size", "number_boosted", "SF_12_AUC")]
  
  # get intervention
  # get cumulative MCS population uplift amount intervention cost.
  # bind into one subtable for each intervention
  # put together
  # make into table with xtable?
  
}

main()