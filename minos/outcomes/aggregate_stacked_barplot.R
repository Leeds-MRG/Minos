
# take some housing quality percentage over time data for minos runs from make_lineplots.py requires finding latest timestamp for dta.
# take mean.
# group overall 


library(here)
library(ggplot2)

source(here::here('minos', 'utils_datain.R'))

main<- function() {
  
  data.path <- here::here("output", "default_config", "25RelativePoverty/")
  data.path <- get_latest_runtime_subdirectory(data.path)
  data.path <- paste0(data.path, "/housing_quality_aggregation_using_aggregate_percentage_counts.csv")
  
  data <- read.csv(data.path)
  
  for (tag in unique(data$tag)) {
    data2 <- data[which(data$tag == tag),]
    data3 <- data2 %>%
      group_by(time, housing_quality) %>%
      summarise(n = n(),
                mean.var = mean(prct),)
    
    
    barplot <-ggplot(data = data3, mapping = aes(x = time, y = mean.var, fill=housing_quality)) +
      geom_bar(stat = 'identity') +
      geom_vline(xintercept=2020, linetype='dotted') +
      labs(title = paste0("Housing Quality over time for ", tag)) +
      xlab('Year') +
      ylab('Proportion')
    print(barplot)
  }

}

main()