
# take some housing quality percentage over time data for minos runs from make_lineplots.py requires finding latest timestamp for dta.
# take mean.
# group overall 


library(here)
library(ggplot2)
library(dplyr)

source(here::here('minos', 'utils_datain.R'))

stack_barplot_with_uncertainty<- function(mode, source, v) {
  
  data.path <- here::here("output", mode, source)
  data.path <- get_latest_runtime_subdirectory(data.path) # calculate latest time folder of data to get runs from.
  data.path <- paste0(data.path, v, "_aggregation_using_aggregate_percentage_counts.csv")
  data <- read.csv(data.path)
  
  if (v == "housing_quality" || v == "neighbourhood_safety" || v == "loneliness"){
    data[, c(v)] <- factor(data[, c(v)], levels = c("High", "Medium", "Low"))
  }
  
  for (tag in unique(data$tag)) {
    data2 <- data[which(data$tag == tag),]
    if (length(unique(data2$id)) == 1) {
      
      print ("Warning! Only one model run being used to calculate standard errors. Plots will have no uncertainty bars.")
      data3 <- data2 %>%
      group_by(time, !!sym(v)) %>%
      summarise(mean = mean(prct, na.rm = TRUE))
      
      barplot <-ggplot(data = data3, mapping = aes(x = time, y = mean, fill=!!sym(v))) +
        geom_bar(stat = 'identity') +
        geom_vline(xintercept=2020, linetype='dotted') +
        labs(title = paste0(v, " over time for ", tag)) +
        xlab('Year') +
        ylab('Proportion')
      
      save.path <- paste0(here::here(), "/plots/", tag, "_", v, "_aggregate_barplot.pdf")
      ggsave(save.path, plot = last_plot())
      print(paste0("Saved to: ", save.path))
      #print(barplot)
    }
    
    else {
      
      data3 <- data2 %>%
        group_by(time, !!sym(v)) %>%
        arrange(time, !!sym(v)) %>% 
        summarise(mean = mean(prct, na.rm = TRUE),
                  std = sd(prct, na.rm = TRUE),
                  n = n()) %>%
        mutate(se = std / sqrt(n), # grab CIs
               cs = cumsum(mean)) %>%
        mutate(lower.ci = 1- (cs + qt(1 - (0.05 / 2), n - 1) * se),
               upper.ci = 1- (cs - qt(1 - (0.05 / 2), n - 1) * se))
      
      #print(data)
      
      barplot <-ggplot(data = data3, mapping = aes(x = time, y = mean, fill=!!symv(v))) +
        geom_bar(stat = 'identity') +
        geom_errorbar(aes(x=time, y = cs, ymin= lower.ci, ymax= upper.ci)) +
        geom_vline(xintercept=2020, linetype='dotted') +
        labs(title = paste0(v, " over time for ", tag)) +
        xlab('Year') +
        ylab('Proportion')
      
      if (tag == "Baseline"){
        save.path <- paste0(here::here(), "/plots/", source, "_", tag, "_", v, "_aggregate_barplot.pdf")
      }
      else {
        save.path <- paste0(here::here(), "/plots/", tag, "_", v, "_aggregate_barplot.pdf")
      }
      
      ggsave(save.path, plot = last_plot())
      print(paste0("Saved to: ", save.path))
      #print(barplot)    
      }
    #print(barplot)
  }

}

main <- function() {
  mode <- "default_config"
  stack_barplot_with_uncertainty(mode, "50UniversalCredit", "housing_quality")
  stack_barplot_with_uncertainty(mode, "50RelativePoverty", "housing_quality")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "housing_quality")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "housing_quality")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "housing_quality")
  
  stack_barplot_with_uncertainty(mode, "50UniversalCredit", "neighbourhood_safety")
  stack_barplot_with_uncertainty(mode, "50RelativePoverty", "neighbourhood_safety")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "neighbourhood_safety")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "neighbourhood_safety")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "neighbourhood_safety")
  
  stack_barplot_with_uncertainty(mode, "50UniversalCredit", "loneliness")
  stack_barplot_with_uncertainty(mode, "50RelativePoverty", "loneliness")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "loneliness")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "loneliness")
  stack_barplot_with_uncertainty(mode, "livingWageIntervention", "loneliness")
}

main()