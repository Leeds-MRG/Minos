
# take some housing quality percentage over time data for minos runs from make_lineplots.py requires finding latest timestamp for dta.
# take mean.
# group overall 


library(here)
library(ggplot2)
library(dplyr)

source(here::here('minos', 'utils_datain.R'))

main<- function() {
  
  data.path <- here::here("output", "default_config", "livingWageIntervention")
  data.path <- get_latest_runtime_subdirectory(data.path)
  data.path <- paste0(data.path, "/housing_quality_aggregation_using_aggregate_percentage_counts.csv")
  data <- read.csv(data.path)
  
  for (tag in unique(data$tag)) {
    data2 <- data[which(data$tag == tag),]
    data2$housing_quality <- factor(data2$housing_quality, levels = c("High", "Medium", "Low"))
    if (length(unique(data2$id)) == 1) {
      print ("Warning! Only one model run being used to calculate standard errors. Plots will have no uncertainty bars.")
      data3 <- data2 %>%
      group_by(time, housing_quality) %>%
      summarise(mean = mean(prct, na.rm = TRUE))
      
      barplot <-ggplot(data = data3, mapping = aes(x = time, y = mean, fill=housing_quality)) +
        geom_bar(stat = 'identity') +
        geom_vline(xintercept=2020, linetype='dotted') +
        labs(title = paste0("Housing Quality over time for ", tag)) +
        xlab('Year') +
        ylab('Proportion')
    
      ggsave(paste0(here::here(), "/plots/housing_quality.pdf"), plot = last_plot())
      print(barplot)
    }
    
    else {
      
      data3 <- data2 %>%
        group_by(time, housing_quality) %>%
        summarise(mean = mean(prct, na.rm = TRUE),
                  std = sd(prct, na.rm = TRUE),
                  n = n()) %>%
        mutate(se = std / sqrt(n), # grab CIs
               lower.ci = mean - qt(1 - (0.05 / 2), n - 1) * se,
               upper.ci = mean + qt(1 - (0.05 / 2), n - 1) * se)
      
      
      barplot <-ggplot(data = data3, mapping = aes(x = time, y = mean, fill=housing_quality)) +
        geom_bar(stat = 'identity') +
        geom_errorbar(aes(ymin= lower.ci, ymax= upper.ci)) +
        geom_vline(xintercept=2020, linetype='dotted') +
        labs(title = paste0("Housing Quality over time for ", tag)) +
        xlab('Year') +
        ylab('Proportion')
      
      ggsave(paste0(here::here(), "/plots/housing_quality.pdf"), plot = last_plot())
    }
    #print(barplot)
  }

}

main()