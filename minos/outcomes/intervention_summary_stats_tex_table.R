library(xtable)
library(ggplot2)

process_cost_stats_files <- function(file.name) {
  data <- read.csv(file.name)
  data[1, is.na(data[1, ])] <- "mean"
  
  # parsing mean and standard deviation statistics for each health outcome.
  # sf12 auc, intervention cost, number of people boosted, total population size and prct below 45.6
  data_std <- data[, which(data[1,] == "std")]
  data_std$tag <- data$tag
  # data$year <- data
  
  data <- data[, which(data[1,] != "std")]
  data$X <- NULL
  
  # removing first row that contains string of "mean" and "std".
  data_std <- data_std[-c(1), ]
  data <- data[-c(1), ]
  
  # reset row index for each data frame after removing first row.
  row.names(data) <- NULL
  row.names(data_std) <- NULL
  
  data$SF_12_AUC <- as.numeric(data$SF_12_AUC)
  data$intervention_cost <- as.numeric(data$intervention_cost)
  data$number_boosted <- as.numeric(data$number_boosted)
  data$population_size <- as.numeric(data$population_size)
  data$prct_below_45.6 <- as.numeric(data$prct_below_45.6)
  data[which(is.na(data$prct_below_45.6)), "prct_below_45.6"] <- 0
  
  data[which(data$tag!="Baseline"), "SF_12_AUC"] <- data[which(data$tag!="Baseline"), "SF_12_AUC"] + data[1, "SF_12_AUC"]
  data[which(data$prct_below_45.6==0.0), "prct_below_45.6"] <- data[1, "prct_below_45.6"]
  
  if (file.name == "plots/baselineenergyDownliftenergyDownliftNoSupport_counts_over_time.csv")
  {
    data$prct_below_45.6_baseline <- data$prct_below_45.6[33:48]
    data$prct_below_45.6_diff <- data$prct_below_45.6 - data$prct_below_45.6[33:48]
  } else {
    data$prct_below_45.6_baseline <- data$prct_below_45.6[1:16]
    data$prct_below_45.6_diff <- data$prct_below_45.6 - data$prct_below_45.6[1:16]
  }
  
  data$absolute_below_45.6_diff <- data$population_size * abs(data$prct_below_45.6_diff)
  # scale to number of UK working age adults in 2020.
  # according to https://statswales.gov.wales/catalogue/population-and-migration/population/estimates/nationallevelpopulationestimates-by-year-age-ukcountry
  # have 52790493 adults over 16 years old by 2020 mid year estimate.
  #population_scale_factor <- 52.790493 * (10**6) / sum(data$inverse_weights)
  
  data$absolute_below_45.6_diff_scaled_estimate <- data$absolute_below_45.6_diff * (52.790493 * (10**6)) / data$population_size # * data$number_boosted 
  # scale to cost of 275 GBP per individual moved above 45.6 threshold.
  
  # Richards, D.A., Bower, P., Chew-Graham, C., Gask, L., Lovell, K., Cape, J., Pilling
  # S., Araya, R., Kessler, D., Barkham, M. and Bland, J.M., 2016. 
  # Clinical effectiveness and cost-effectiveness of collaborative care 
  # for depression in UK primary care (CADET): a cluster randomised controlled trial.
  # Health Technology Assessment (Winchester, England), 20(14), p.1.
  # for a person with a depressive disorder, the economic analysis was this:
  # Our estimated mean cost per participant for the delivery of the collaborative care intervention was £272.50. 
  # This cost estimate includes care manager costs at £232 and clinical supervision costs of £40.50. 
  # Our probabilistic analyses used to explore uncertainty around the main cost component, 
  # drawing from the distribution of contact time for care managers, showed that in 95% of simulations 
  # (cost estimates) the estimated cost of collaborative care was between £101 and 
  # £592 per participant (median £249 per participant).
  # 

  data$cost_45.6_diff_scaled_estimate <- data$absolute_below_45.6_diff_scaled_estimate * 232
  
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
  
  
  
  # uplift_rp_data <- process_cost_stats_files("plots/baseline25RelativePoverty50RelativePoverty_counts_over_time.csv")
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
                                           "prct_below_45.6_diff",
                                           "absolute_below_45.6_diff_scaled_estimate",
                                           "cost_45.6_diff_scaled_estimate")]
  
  
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
                                           "prct_below_45.6_diff",
                                           "absolute_below_45.6_diff_scaled_estimate",
                                           "cost_45.6_diff_scaled_estimate")]
  
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
                                  "Difference.", 
                                  "Estimated Total Adults Moved above the 45.6 threshold",
                                  "Estimated NHS Cost/Savings")
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