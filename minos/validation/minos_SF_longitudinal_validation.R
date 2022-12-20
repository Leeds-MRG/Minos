source("minos/transitions/utils.R")
library(TraMineR)

years <- seq(2012, 2016)
source <- 'output/test_output/simulation_data/'

US_file_names <- get_US_file_names(source, years, ".csv")

data <- get_US_data(US_file_names)

data <- data[, c("pidp", "time", "labour_state")]
data[order(data$pidp, data$time),]

data_seqdef <- seqdef(data, var="labour_state")