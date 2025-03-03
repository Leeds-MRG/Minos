

library(here)
library(VIM)


source(here::here("minos", "utils_datain.R"))
source(here::here('minos', 'utils_validation_vis.R'))
source(here::here('minos', 'transitions', 'utils.R'))



aggr_data <- read_all_UKHLS_waves("data/composite_US/", "")
print(colnames(aggr_data))


aggr_data <- aggr_data[which(aggr_data$time>2018), ]

aggr_columns <- c("SF_12_MCS", "SF_12_PCS", "hh_income", "auditc",
                  "housing_quality", "heating", 
                  "loneliness", "age", "sex", "job_sec", "ncigs", 
                  "financial_situation", "housing_tenure", "urban",
                  "ncars", "universal_credit", "number_of_bedrooms", "net_hh_income",
                  "yearly_energy", "FP10", "active")#, "neighbourhood_safety","nutrition_quality")

aggr_data2<- aggr_data[, c(aggr_columns)]
aggr_data2 <- replace.missing(aggr_data2)


pdf("test_missing_structure.pdf")
aggr(aggr_data2, combined=F, sortVars=T, cex.lab=1.2, cex.axis=0.5, plot=T)
dev.off()