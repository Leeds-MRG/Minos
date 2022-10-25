# File for common functions across multiple transition techniques.
# Useful for setting all R scripts to the right directory.
# Change as necessary

str<- toString
concat<- function(x, y){return(paste0(x, y))}
invlogit <- function(x){
  # inverse of standard logistic link function
  # note defaults to 1 if x is large enough.
  # R max float size is 1.797693e+308. so if x > log(1.797693e+308) = 709.7827 
  # defaults to 1.
  # Practically any invlogit(x) for x > 100 is close enough to 1 (within 10^-16) 
  # to be indistinguishable. 
  if (x < 100){
  out = 1/(1 + exp(-x))
  }
  else{
    out = 1
  }
  return (out)
}

missing <- c("-1", "-2", "-7", "-8", "-9", 
             -1, -2, -7, -8,- 9,
             -1., -2., -7., -8., -9.)
t_blue<- rgb(56/256,180/256,251/256,0.25)
blue<- rgb(56/256,180/256,251/256,1.0)
t_orange <- rgb(255/256, 91/256, 0, 0.25)
orange <-rgb(255/256, 91/256, 0, 1.0)

format_depression_data <- function(source, years){
  
  first_time = T # if its the first year in the loop create the data frame.
  for(year in years){
    # loop over years and load in files.
    file_name <- concat(source, str(year))
    file_name <- paste0(concat(file_name, "_US_cohort.csv"))
    new_data <- read.csv(file_name)
    if (first_time==T){
      first_time <- F
      data <- new_data
    }
    else{
      data<- rbind(data, new_data)
    }
  }
  columns <- c("pidp", "sex", "age", "time", "education_state", "depression", "depression_change", "labour_state", "job_sec", "ethnicity")
  data<- data[, columns]
  
  who_depressed = which(data$depression == "Depressed")
  who_not_depressed = which(data$depression == "Not Depressed")
  
  data[who_not_depressed,]$depression = "0"
  data[who_depressed,]$depression = "1"
  
  who_1 = which(data$depression_change == "Less than Usual")
  who_2 = which(data$depression_change == "Same")
  who_3 = which(data$depression_change == "More Depressed")
  who_4 = which(data$depression_change == "Much More Depressed")
  
  data[who_1,]$depression_change = 0
  data[who_2,]$depression_change = 0
  data[who_3,]$depression_change = 1
  data[who_4,]$depression_change = 1
  #data[who_1,]$depression_change = 1
  #data[who_2,]$depression_change = 2
  #data[who_3,]$depression_change = 3
  #data[who_4,]$depression_change = 4
  
  # Remove anyone with fewer than 3 entries
  complete_pidps<- strtoi(rownames(data.frame(which(table(data$pidp)>=3))))
  data<- data[which(data$pidp%in%complete_pidps),]
  return(data)  
}

plot_depression_residuals <-function(res, y, colours, markers){
  
  #plot(res, col = colours, pch = 20)
  plot(res, col = colours, pch = markers, xlab= "Individual",  ylab="Probability of Increased Depression Score", ylim=c(0,1))
  legend("topleft", legend=c("Depression", "No Depression"), bg="transparent", col = c("blue", "orange"), lty = 1, cex = 0.8)
  # Horizontal line at 0.5 white with black border for clarity.
  abline(h = 0.5, col = "black", lwd = 6)
  abline(h = 0.5, col = "white", lwd = 3)

  #plot(predict(m2, data2, allow.new.levels = T), col = colours, pch = 20)
  
  res[which(res>0.5)] = T
  res[which(res<0.5)] = F
  
  results_table<- table(y, res)
  print(results_table)
  if (ncol(results_table) == 2 & nrow(results_table) == 2){
  precision <- results_table[2,2]/(results_table[2,1]+results_table[2,2])
  print(precision)
  }
  else{print("Noone predicted in one or more factor states. Small sample size or 
             model is a poor fit.")
    }
}

format_employment_data <- function(source, years){
  
  first_time = T # if its the first year in the loop create the data frame.
  for(year in years){
    # loop over years and load in files.
    file_name <- concat(source, str(year))
    file_name <- paste0(concat(file_name, "_US_cohort.csv"))
    new_data <- read.csv(file_name)
    if (first_time==T){
      first_time <- F
      data <- new_data
    }
    else{
      data<- rbind(data, new_data)
    }
  }
  columns <- c("pidp", "sex", "age", "time", "education_state", "depression_state", "labour_state", "job_sec", "ethnicity")
  final_labour_states<- c("Retired",
                          "Family Care",
                          "Unemployed",
                          "Student",
                          "Sick/Disabled",
                          "Employed",
                          "Self-employed")
  # who is in the desired final labour states
  who_not_omitted<- which(data$labour_state %in% final_labour_states) 
  # remove irrelvalant columns and those in undesired labour states
  data<- data[who_not_omitted, columns]
  
  #Simplify depression state.
  who_decreasing = which(data$depression_state <= 2)
  who_increasing = which(data$depression_state > 2)
  
  data[who_decreasing,]$depression_state = 0
  data[who_increasing,]$depression_state = 1
  
  # Remove anyone with fewer than 3 entries
  complete_pidps<- strtoi(rownames(data.frame(which(table(data$pidp)>=3))))
  data<- data[which(data$pidp%in%complete_pidps),]
  return(data)  
}