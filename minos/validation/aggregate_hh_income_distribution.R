
library(here)
library(ggridges)
library(ggplot2)
library(tidyverse)

source(here::here('minos', 'utils_datain.R'))
source(here::here('minos', 'utils_validation_vis.R'))
source(here::here('minos', 'validation', 'utils.r'))


main <- function() {
  # load in data
  # subset using dplyer
  # draw ridgeline plot for income over time for baseline and 25 relative poverty.
  
  out.path <- here::here('output', 'default_config/')
  base.data <- read_singular_local_out(out.path, 'baseline', drop.dead = TRUE)
  base.data$Intervention <- "Baseline"
  
  out.path <- here::here('output', 'default_config/')
  living.wage.data <- read_singular_local_out(out.path, 'livingWageIntervention', drop.dead = TRUE)
  living.wage.data$Intervention = "Living Wage"
  
  base.data <- base.data[, c("hh_income", "time", "Intervention")]
  living.wage.data <- living.wage.data[, c("hh_income", "time", "Intervention")]
  
  plot_data <- rbind(base.data, living.wage.data)

  comparison_density_plot <- ggplot(plot_data, aes(x=hh_income, y=factor(time), fill=Intervention)) +
    geom_density_ridges(alpha=0.4) +
    xlab("Household Disposable Income") + # for the x axis label
    ylab("Year")
  ggsave("plots/living_wage_vs_baseline_income_ridgelines.pdf", last_plot())
    
  boxplot<- ggplot(data = plot_data, aes(x = time, y = hh_income,  group = interaction(time, Intervention), fill= Intervention)) +
    geom_boxplot(notch=TRUE) +
    xlab("Household Disposable Income") + # for the x axis label
    ylab("Year")
  ggsave("plots/living_wage_vs_baseline_income_boxplots.pdf", last_plot())

}

main()