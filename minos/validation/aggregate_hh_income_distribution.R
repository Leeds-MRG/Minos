
library(here)
library(ggridges)
library(ggplot2)
library(tidyverse)

source(here::here('minos', 'utils_datain.R'))
#source(here::here('minos', 'utils_validation_vis.R'))
#source(here::here('minos', 'validation', 'utils.r'))


two_interventions_continuous_plots <- function(mode, intervention1, intervention2, tag1, tag2, v) {
  # load in data
  # subset using dplyer
  # draw ridgeline plot for income over time for baseline and 25 relative poverty.
  print(paste0("Starting for:", intervention1, " ", intervention2, " ", v, "."))
  
  out.path <- here::here('output', mode, "/")
  
  intervention1.data <- read_singular_local_out(out.path, intervention1, drop.dead = TRUE)
  intervention1.data$Intervention <- tag1
  
  intervention2.data <- read_singular_local_out(out.path, intervention2, drop.dead = TRUE)
  intervention2.data$Intervention <- tag2
  
  intervention1.data <- intervention1.data[, c(v, "time", "Intervention")]
  intervention2.data <- intervention2.data[, c(v, "time", "Intervention")]
  
  plot_data <- rbind(intervention1.data, intervention2.data)


  plot.dir <- paste0('plots/', "handovers_", intervention1, "_", intervention2, "_", v)
  
  if (v == "ncigs") {
    comparison_density_plot <- ggplot(plot_data, aes(x=!!sym(v), y=factor(time), color=Intervention, linetype=Intervention, fill=Intervention)) +
      geom_density_ridges(alpha=0.4) +
      xlab(v) + # for the x axis label
      ylab("Year") +
      scale_x_continuous(limits=c(0,30))
    ggsave(paste0(plot.dir, "_ridgelines.pdf"), last_plot())
  }
  
  else {
      comparison_density_plot <- ggplot(plot_data, aes(x=!!sym(v), y=factor(time), fill=Intervention)) +
        geom_density_ridges(alpha=0.4) +
        xlab(v) + # for the x axis label
        ylab("Year")
      ggsave(paste0(plot.dir, "_ridgelines.pdf"), last_plot())
  }
  
  if (v == "ncigs") {
    plot_data <- plot_data[which(plot_data$ncigs<30),]
    boxplot<- ggplot(data = plot_data, aes(x = time, y = !!sym(v),  group = interaction(time, Intervention), fill= Intervention)) +
      geom_boxplot(notch=TRUE) +
      xlab("Year") + # for the x axis label
      ylab(v)
    ggsave(paste0(plot.dir, "_boxplots.pdf"), last_plot())
    print(paste0("Saved to:",paste0(plot.dir, "_boxplots.pdf")))
  }
  else {
    boxplot<- ggplot(data = plot_data, aes(x = time, y = !!sym(v),  group = interaction(time, Intervention), fill= Intervention)) +
      geom_boxplot(notch=TRUE) +
      xlab("Year") + # for the x axis label
      ylab(v)
    ggsave(paste0(plot.dir, "_boxplots.pdf"), last_plot())
    print(paste0("Saved to:",paste0(plot.dir, "_boxplots.pdf")))
  }

}

main <- function(){
 
  
  two_interventions_continuous_plots("default_config", "baseline", "livingWageIntervention", "Baseline", "Living Wage Intervention","ncigs")
  
  two_interventions_continuous_plots("default_config", "baseline", "25RelativePoverty", "Baseline", "£25 Relative Poverty", "hh_income")
  two_interventions_continuous_plots("default_config", "baseline", "50RelativePoverty", "Baseline", "£50 Relative Poverty", "hh_income")
  two_interventions_continuous_plots("default_config", "baseline", "25UniversalCredit", "Baseline", "£25 Universal Credit", "hh_income")
  two_interventions_continuous_plots("default_config", "baseline", "50UniversalCredit", "Baseline", "£50 Universal Credit", "hh_income")
  
  two_interventions_continuous_plots("default_config", "baseline", "livingWageIntervention", "Baseline", "Living Wage Intervention", "hh_income")
  
  two_interventions_continuous_plots("default_config", "baseline", "energyDownlift", "Baseline", "Energy Downlift", "hh_income")
  two_interventions_continuous_plots("default_config", "baseline", "energyDownliftNoSupport", "Baseline", "Energy Downlift No Support", "hh_income")
 
  two_interventions_continuous_plots("default_config", "baseline", "25RelativePoverty", "Baseline", "£25 Relative Poverty", "nutrition_quality")
  two_interventions_continuous_plots("default_config", "baseline", "50RelativePoverty", "Baseline", "£50 Relative Poverty", "nutrition_quality")
  two_interventions_continuous_plots("default_config", "baseline", "25UniversalCredit", "Baseline", "£25 Universal Credit", "nutrition_quality")
  two_interventions_continuous_plots("default_config", "baseline", "50UniversalCredit", "Baseline", "£50 Universal Credit", "nutrition_quality")
  
  two_interventions_continuous_plots("default_config", "baseline", "livingWageIntervention", "Baseline", "Living Wage Intervention","nutrition_quality")
  
  two_interventions_continuous_plots("default_config", "baseline", "energyDownlift", "Baseline", "Energy Downlift","nutrition_quality")
  two_interventions_continuous_plots("default_config", "baseline", "energyDownliftNoSupport", "Baseline", "Energy Downlift No Support", "nutrition_quality") 
  
  two_interventions_continuous_plots("default_config", "baseline", "25RelativePoverty", "Baseline", "£25 Relative Poverty", "SF_12")
  two_interventions_continuous_plots("default_config", "baseline", "50RelativePoverty", "Baseline", "£50 Relative Poverty", "SF_12")
  two_interventions_continuous_plots("default_config", "baseline", "25UniversalCredit", "Baseline", "£25 Universal Credit", "SF_12")
  two_interventions_continuous_plots("default_config", "baseline", "50UniversalCredit", "Baseline", "£50 Universal Credit", "SF_12")
  
  two_interventions_continuous_plots("default_config", "baseline", "livingWageIntervention", "Baseline", "Living Wage Intervention","SF_12")
  
  two_interventions_continuous_plots("default_config", "baseline", "energyDownlift", "Baseline", "Energy Downlift", "SF_12")
  two_interventions_continuous_plots("default_config", "baseline", "energyDownliftNoSupport", "Baseline", "Energy Downlift No Support" ,"SF_12") 
  
  two_interventions_continuous_plots("default_config", "baseline", "25RelativePoverty", "Baseline", "£25 Relative Poverty", "ncigs")
  two_interventions_continuous_plots("default_config", "baseline", "50RelativePoverty", "Baseline", "£50 Relative Poverty", "ncigs")
  two_interventions_continuous_plots("default_config", "baseline", "25UniversalCredit", "Baseline", "£25 Universal Credit", "ncigs")
  two_interventions_continuous_plots("default_config", "baseline", "50UniversalCredit", "Baseline", "£50 Universal Credit", "ncigs")
  
  two_interventions_continuous_plots("default_config", "baseline", "livingWageIntervention", "Baseline", "Living Wage Intervention","ncigs")
  
  two_interventions_continuous_plots("default_config", "baseline", "energyDownlift", "Baseline", "Energy Downlift", "ncigs")
  two_interventions_continuous_plots("default_config", "baseline", "energyDownliftNoSupport", "Baseline", "Energy Downlift No Support" ,"ncigs") 
}

main()