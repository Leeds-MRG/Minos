#file for initial ideas on longitudinal visualisation of single minos model runs
library(ggplot2) # plots plots plots plots plots
library(tidyr) #data manipulation
library(dplyr) # data manipulation
library(stringr) # for nice formatting of axes labels.
library(viridis) # for nice colour palettes

get_latest_file <-function(path){
  # find last file lexigraphically in a given path.
  # This will find the latest chronologically MINOS run output in this path. 
  files = Sys.glob(path)
  files = sort(files)
  file = tail(files,1)[1]
  return(file)
}

violin_plot <- function(data, v)
{
  # plot violins (similar to boxplots) over time for continuous variable v
  # data: list Some dataset to plot. Needs v, time and pidp variables.
  # v : some continuous variable to plot. 
  data <- data[, c("time", "pidp", v)]
  data <- data[order(data$pidp, data$time),]
  data$time <- factor(data$time)
  
  violin_long <- ggplot(data, aes_string(x = 'time', y = v)) +
    geom_violin() +
    geom_boxplot(width = 0.1, outlier.colour = "blue") +
    theme_classic() + 
    scale_y_continuous(limits = quantile(data[, c(v)], c(0.001, 0.999)))
  return(violin_long)
}

spaghetti_plot <- function(data, v)
{
  # spaghetti plot displaying trajectories over time for continuous variable v
  # data: list Some dataset to plot. Needs v, time and pidp variables.
  # v : some continuous variable to plot. 
  #TODO convert this to pure ggplot2 as with joint spaghetti plot below. Far more flexible and doesnt need stupid wide format conversion. 
  data_plot <- data[, c("time", "pidp", v)]
  output_plot <- ggplot(data_plot, aes(x = time, y = !!sym(v), group = pidp)) + 
                 ggplot2::labs(x = "time", y = v) + 
                 ggplot2::theme_classic() + 
                 ggplot2::theme(text = ggplot2::element_text(size = 12)) + 
                 ggplot2::scale_colour_viridis_d()+ 
                 #ggplot2::geom_smooth(colour="blue") +
                 ggplot2::geom_line(colour="blue", alpha=0.2) +
                 ggplot2::geom_point() +
                 ggplot2::geom_smooth()
    
  return (output_plot)
}

joint_violin_plot <- function(data1, data2, v, label1, label2){
  data <- data[, c("time", "pidp", v)]
  data2 <- data2[, c("time", "pidp", v)]
  #data_wide <- reshape(data, idvar='pidp', timevar='time', direction = 'wide') # needs wide formatting.
  #data2_wide <- reshape(data2, idvar='pidp', timevar='time', direction = 'wide') 
  #var_list <- tail(colnames(data_wide), -1) # ignore only the first variable (pidp). 
  
  data$group <- label1
  data2$group <- label2
  
  #data_wide <- rbind(data_wide, data2_wide)
  #data_wide <- as.data.frame(data_wide)
  data <- rbind(data, data2)
  data$time <- factor(data$time)
  output_plot <- ggplot(data, aes(fill=group, y=.data[[v]], x=time)) + 
    geom_violin()
  return(output_plot)
}

joint_spaghetti_plot <- function(data, data2, v, label1, label2)
{
  # plot violins (similar to boxplots) for two interventions over time for continuous variable v
  # data, data2: list Some dataset to plot. Needs v, time and pidp variables.
  # v : some continuous variable to plot. 
  # label1, label1: string. Name of intervention groups to add to legend.
  # Probably should move this out of the function and make it a requirement for the dataset. 
  
  data <- data[, c("time", "pidp", v)]
  data2 <- data2[, c("time", "pidp", v)]
  data$group <- label1
  data2$group <- label2
  # TODO take a subsample? Doesnt seem worth it. 
  data_plot <- rbind(data, data2)
  output_plot <- ggplot(data_plot, aes(x = time, y = !!sym(v), group = pidp, colour = factor(group))) + 
                ggplot2::labs(x = "time", y = v) + 
                ggplot2::theme_classic() + 
                ggplot2::theme(text = ggplot2::element_text(size = 12)) + 
                #ggplot2::scale_colour_viridis_d()+ 
                ggplot2::geom_line(alpha=0.2) +
                ggplot2::geom_point(alpha=0.4, size=0.1)
  
  print(output_plot)
  return (output_plot)
}

percent_barplot<- function(data, v, title){
  # getting required columns and count entries by categories of v and time
  sub_data <- data %>%
    select(pidp, time, (!!sym(v))) %>%
    group_by(time, (!!sym(v))) %>%
    count()
  
  sub_data2 <- sub_data %>%
    group_by(time) %>%
    mutate(total = sum(n)) %>%
    mutate(prct = (n / total))
  
  output_plot <-  ggplot(sub_data2, aes(x = time, y = prct, fill=(!!(sym(v))))) +
    geom_bar(stat="identity") +
    scale_fill_viridis() +
    ggtitle(title) +
    theme(axis.text.x = element_text(angle = 60, hjust=1))
  return(output_plot)
}


main <- function() {
  # Get the latest MINOS run files chronologically in these paths.
  file_path<-(get_latest_file("output/default_config/baseline/*"))
  #file_path2<-(get_latest_file("output/default_config/baseline/*"))
  #file_path3<-(get_latest_file("output/default_config/livingWageIntervention/*"))
  #file_path4<-(get_latest_file("output/default_config/livingWageIntervention/*"))
  #file_path5<-(get_latest_file("output/default_config/povertyLineChildUplift/*"))
  #file_path6<-(get_latest_file("output/default_config/energyDownlift/*"))
  file_path2<-(get_latest_file("output/default_energy_poverty_config/energyDownlift/*"))
  file_path3<-(get_latest_file("output/default_energy_poverty_config/energyPoverty/*"))
  file_path4<-(get_latest_file("output/default_energy_poverty_config/energyPovertyEfficiency/*"))
  
  # Find all csv files in these directories using glob. Could use more precise regex here but does its job of ignoring YAMLs etc.
  # This is stupid if there are multiple minos runs in one file. Will call hundreds of csvs. Needs fixing.. 
  # Look for files with form id_0_year.csv first?
  # Failing that look for more generic year.csv one with just one run inside.
  files <- sort(Sys.glob(paste0(file_path, "/[0-9]*", ".csv"))) 
  files2 <- sort(Sys.glob(paste0(file_path2, "/[0-9]*", ".csv")))
  files3 <- sort(Sys.glob(paste0(file_path3, "/[0-9]*", ".csv")))
  files4 <- sort(Sys.glob(paste0(file_path4, "/[0-9]*", ".csv")))
  
  # For all files for a given intervention bind them together. 
  data <- do.call(rbind, lapply(files, read.csv))
  data2 <- do.call(rbind, lapply(files2, read.csv))
  data3 <- do.call(rbind, lapply(files3, read.csv))
  data4 <- do.call(rbind, lapply(files4, read.csv))
  
  #data <- data[which(data$time<2020),]
  #data2 <- data2[which(data2$time<2020),]
  
  data$time <- factor(data$time)
  data2$time <- factor(data2$time)
  data3$time <- factor(data3$time)
  data4$time <- factor(data4$time)
  
  # spaghetti and violin plots over time for SF12
  sf12_violin <- violin_plot(data, "SF_12")
  sf12_spag <- spaghetti_plot(data, "SF_12")
  
  sf12_violin2 <- violin_plot(data2, "SF_12")
  sf12_spag2 <- spaghetti_plot(data2, "SF_12")
  
  # joint plots SF12 for two interventions together with colour groupings. 
  joint_spaghetti_plot(data, data2, "SF_12", "baseline", "energy poverty")
  #joint_violin_plot <- joint_violin_plot(data3, data2, "SF_12", "base", 'energy poverty measures')
  
  # Stacked barplots for discrete data. 
  #housing_barplot <- percent_barplot(data, "housing_quality", "Baseline")
  #print(housing_barplot)
  #housing_barplot2 <- percent_barplot(data2, "housing_quality", "Energy Downlift")
  #print(housing_barplot2)
  #housing_barplot3 <- percent_barplot(data3, "housing_quality", "Government Policy")
  #print(housing_barplot3)
  #housing_barplot4 <- percent_barplot(data4, "housing_quality", "Energy Efficiency")
  
  #safety_barplot1 <- percent_barplot(data, "neighbourhood_safety", "Baseline")
  #safety_barplot2 <- percent_barplot(data2, "neighbourhood_safety", "Energy Downlift")
  #labour_barplot <- print(percent_barplot(data2, "labour_state", "Energy Downlift"))
  
  #finsit_barplot1 <- percent_barplot(data, "financial_situation", "Baseline")
  #finsit_barplot2 <- percent_barplot(data2, "financial_situation", "EnergyDownlift")
  #finsit_barplot3 <- percent_barplot(data3, "financial_situation", "EnergyPoverty")
  #finsit_barplot4 <- percent_barplot(data4, "financial_situation", "EnergyPovertyEfficiency")
  
  #heating_barplot1 <- percent_barplot(data, "heating", "Baseline")
  #heating_barplot2 <- percent_barplot(data2, "heating", "EnergyDownlift")
  #heating_barplot3 <- percent_barplot(data3, "heating", "EnergyPoverty")
  #heating_barplot4 <- percent_barplot(data4, "heating", "EnergyPovertyEfficiency")
}

main()