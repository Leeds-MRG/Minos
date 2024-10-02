library(here)


data1 <- read.csv(here::here("plots", "QALYs_manchester_synthetic_baseline_GBIS_2025_diffmap.pdfregression_data.csv"))
data2 <- read.csv(here::here("plots", "QALYs_manchester_synthetic_baseline_EPCG_2025_diffmap.pdfregression_data.csv"))

  
  
data1$diff <- as.numeric(data1$diff) - as.numeric(data2$diff)

m1 <- lm(scale(diff)~factor(urban_rural_code) + factor(LAName.y) + scale(intervention_cost.y), data=data1)
m2 <- lm(scale(diff)~factor(urban_rural_code) + factor(LAName.y) + scale(intervention_cost.y) + factor(super_output_area_classifiers)+
           scale(Participation_in_Paid_Employment) + 
           scale(Skills_and_Qualifications) + 
           scale(Involuntary_Exclusion_from_the_Labour_Market) + 
           scale(Digital_Connectivity) + 
           scale(Wealth_Inequality) + 
           scale(Physical_Connectivity) + 
           scale(Earnings_Inequality) + 
           scale(Housing_Affordability) + 
           scale(Poverty) + 
           scale(Cost_of_Living) + 
           scale(Decent_Pay) + 
           scale(Decision_Making_Inclusion) + 
           scale(Job_Security) , data=data1)

print(summary(m1))
print(summary(m2))



print(xtable(summary(m1), type = "latex"), file = here::here("plots", "diffs_on_diffs.tex"))
print(xtable(summary(m2), type = "latex"), file = here::here("plots", "diffs_on_diffs_bigger.tex"))

# ie_indicator_data <- read.csv(here::here("persistent_data", "spatial_data", "ward_ie_indicators.csv"))
# ie_columns <- c("WD22CD", "LAD22NM", "indicator_1a", "indicator_1b", "indicator_2a", "indicator_2b", "indicator_3a", "indicator_3b", "indicator_4a", "indicator_4b", "indicator_5a", "indicator_5b", "indicator_6a", "indicator_6b", "indicator_7a")
# ie_column_names <- c("ward_code", "LA_code", "Participation_in_Paid_Employment", 
#                      "Skills_and_Qualifications", 
#                      "Involuntary_Exclusion_from_the_Labour_Market", 
#                      "Digital_Connectivity", 
#                      "Wealth_Inequality", 
#                      "Physical_Connectivity", 
#                      "Earnings_Inequality", 
#                      "Housing_Affordability", 
#                      "Poverty", 
#                      "Cost_of_Living", 
#                      "Decent_Pay", 
#                      "Decision_Making_Inclusion", 
#                      "Job_Security")
# 
# gmca_la_names <- c("Bolton", "Bury", "Rochdale", "Oldham", "Tameside", "Stockport", "Manchester", "Trafford", "Salford", "Wigan")
# 
# 
# ie_indicator_data <- ie_indicator_data[ie_indicator_data$LAD22NM %in% gmca_la_names, ]
# ie_indicator_data <- ie_indicator_data[, c(ie_columns)]
# colnames(ie_indicator_data) <- ie_column_names
# la_grouped_IE <- aggregate(ie_indicator_data, by=list(ie_indicator_data$LA_code), mean)
# la_grouped_IE$ward_code <- NULL
# la_grouped_IE$LA_code <- NULL
# 
# colnames(la_grouped_IE)[1] <- "Local Authority"
# write.csv(la_grouped_IE, here::here("plots","LA_IE_means.csv"), row.names=F)
