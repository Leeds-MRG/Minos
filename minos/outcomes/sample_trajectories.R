library(ggplot2)
library(dplyr)
library(here)
library(viridis)

source(here::here("minos", "utils_datain.R"))

main <- function() {
  
  # get minos data from baseline and 25 relative poverty
  
  #baseline.data <- read_first_singular_local_out("output/default_config/", "baseline")
  #rp.data <- read_first_singular_local_out("output/default_config/", "25RelativePoverty")
  
  baseline.data <- read_singular_local_out("output/default_config/", "baseline", drop.dead=T)
  rp.data <- read_singular_local_out("output/default_config/", "25RelativePoverty", drop.dead=T)
  
  required_cols <-  c("pidp", "SF_12_MCS", "time", "hh_income")
  baseline.data <- baseline.data[, required_cols]
  rp.data <- rp.data[, required_cols]

  
  # calculate income deciles.
  baseline.data$income_deciles <- ntile(baseline.data$hh_income, 10)
  rp.data$income_deciles <- ntile(rp.data$hh_income, 10)
  
  # get 10 pidps from deciles 1, 5, 10.
  # sample data
  baseline.data.bottom.decile <- baseline.data[which(baseline.data$income_deciles == 1), ]
  baseline.data.middle.decile <- baseline.data[which(baseline.data$income_deciles == 5), ]
  baseline.data.top.decile <- baseline.data[which(baseline.data$income_deciles == 10), ]
  
  rp.data.bottom.decile <- baseline.data[which(rp.data$income_deciles == 1), ]
  rp.data.middle.decile <- baseline.data[which(rp.data$income_deciles == 5), ]
  rp.data.top.decile <- baseline.data[which(rp.data$income_deciles == 10), ]
  
  # sample pidps
  sample_size <- 30
  baseline.bottom.decile.sample.pidps <- sample(unique(baseline.data.bottom.decile$pidp), sample_size, replace = F)
  baseline.middle.decile.sample.pidps <- sample(unique(baseline.data.middle.decile$pidp), sample_size, replace = F)
  baseline.top.decile.sample.pidps <- sample(unique(baseline.data.top.decile$pidp), sample_size, replace = F)
  
  rp.bottom.decile.sample.pidps <- sample(unique(rp.data.bottom.decile$pidp), sample_size, replace = F)
  rp.middle.decile.sample.pidps <- sample(unique(rp.data.middle.decile$pidp), sample_size, replace = F)
  rp.top.decile.sample.pidps  <-sample(unique(rp.data.top.decile$pidp), sample_size, replace = F)
  
  
  # loading in source data for pre-2020 trajectories.
  source.files <- list.files("data/final_US/",
                             pattern = '[0-9]{4}_US_cohort.csv',
                             full.names = TRUE)
  source.data <- do.call(rbind, lapply(source.files, read.csv))
  source.data <- source.data[, required_cols]
  source.data$income_deciles <- 0
  
  baseline.data <- rbind(source.data, baseline.data)
  rp.data <- rbind(source.data, rp.data)
  
  
  baseline.bottom.sample.tracks <- baseline.data[baseline.data$pidp %in% baseline.bottom.decile.sample.pidps, ]
  baseline.middle.sample.tracks <- baseline.data[baseline.data$pidp %in% baseline.middle.decile.sample.pidps, ]
  baseline.top.sample.tracks <- baseline.data[baseline.data$pidp %in% baseline.top.decile.sample.pidps, ]
  baseline.bottom.sample.tracks$group <- "Baseline Bottom Decile"
  baseline.middle.sample.tracks$group <- "Baseline Middle Decile"
  baseline.top.sample.tracks$group <- "Baseline Top Decile"
  
  rp.bottom.sample.tracks <- rp.data[rp.data$pidp %in% rp.bottom.decile.sample.pidps, ]
  rp.middle.sample.tracks <- rp.data[rp.data$pidp %in% rp.middle.decile.sample.pidps, ]
  rp.top.sample.tracks <- rp.data[rp.data$pidp %in% rp.top.decile.sample.pidps, ]
  rp.bottom.sample.tracks$group <- "£25 Relative Poverty Bottom Decile"
  rp.middle.sample.tracks$group <- "£25 Relative Poverty Middle Decile"
  rp.top.sample.tracks$group <- "£25 Relative Poverty Top Decile"
  
  plot.data <- rbind(baseline.bottom.sample.tracks, baseline.middle.sample.tracks, baseline.top.sample.tracks,
                     rp.bottom.sample.tracks, rp.middle.sample.tracks, rp.top.sample.tracks)

  # plot a 3x3 facet grid of these spaghetti plots for SF-12.
  spaghetti.sample.plot <- ggplot(data = plot.data, aes(x=time, y=SF_12_MCS, group = factor(pidp), color=factor(pidp))) +
                           geom_line(alpha=0.5) +
                           facet_wrap( ~ group) +
                           scale_fill_viridis_d() + 
                           theme(legend.position="none")
  ggsave("plots/sf12_spaghetti_grid.pdf")
}


main()