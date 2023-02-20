"This file contains functions used in R notebook outputs for the sphinx website.

It is generally much tidier than having large blocks of code 
lying around to call one line from here.
"
library(ggplot2)
source("minos/transitions/utils.R")
real_data <- read.csv("data/final_US/2019_US_Cohort.csv")

#source("minos/transitions/utils.R")
#real_data <- read.csv("data/final_US/2018_US_Cohort.csv")

# Prevent spamming of package load messages when compiling with sphinx.
# model stuff.
suppressMessages(require(pscl))
suppressMessages(require(nnet))
suppressMessages(require(ordinal))
suppressMessages(require(tidyverse))
# plot stuff.
suppressMessages(require(ggplot2))
suppressMessages(require(stringr))
suppressMessages(require(shadowtext))


notebook_setwd<- function(){
  workingDir <- "../../.." # points to docsrc/ from the docsrc/documentation/notebooks folder where this file is run.
  knitr::opts_knit$set(root.dir = workingDir)
}

# general data visualisation

continuous_density <- function(path, v){
  obs <- readRDS(path)[[v]]
  quants = quantile(obs, c(.001, .999)) # cutting off huge outliers for better plots.
  plot(density(obs, from=quants[1], to=quants[2]), main='', xlab=v)
}

counts_density <- function(path, v){
  obs <- readRDS(path)$y
  quants = quantile(obs, c(.001, .999))
  plot(density(obs, from=0, to=quants[2]), main='', xlab=v)
}

discrete_barplot <- function(path, v){
  obs <- readRDS(path)[[v]]
  counts <- table(obs)
  barplot(counts, horiz=F, cex.names=.7, las=2)
}

# ols models #############################################################################

ols_histogram <- function(data_path, v, mode="both"){
  ols.model <- readRDS(data_path)
  if (mode == "obs")
  { # just plot observations
    obs <- ols.model$model[, c(v)]
    plot(density(obs, from=min(obs), to=max(obs)))
  }
  else if (mode == "preds")
  { # just plot preditions.
    plot(density(predict(ols.model)))
  }
  else
  { # plot both together.
    obs <- ols.model$model[, c(v)]
    preds <- predict(ols.model)
    quants = quantile(obs, c(.001, .999))
    d1 <- density(obs, from=quants[1], to=max(quants[2]))
    d2 <- density(preds,  from=quants[1], to=max(quants[2]))
    height <- max(max(d1$y), max(d2$y))
    
    plot(d1, col='red', ylim=c(0, 1.02*height), main='', xlab=v)
    lines(d2, col='blue', lty=2)
    legend('topleft', legend=c("Observed", "Predicted"), col=c("red", "blue"), lty=1:2)
  }
}

ols_output <- function(data_path){
  ols<- readRDS(data_path)
  print(summary(ols))
  # any diagnostic plots for tobacco.
  plot(ols)
}

# clm models ###################################################################

clm_barplot <- function(data_path, v){
  clm_model<- readRDS(data_path)
  #column_index <- paste0("factor(", v)
  #column_index <- paste0(column_index, ")")
  #obs <- clm_model$model[, c(column_index)]
  obs <- clm_model[[v]]
  preds <- clm_model$class_preds
  
  obs <- as.data.frame(table(obs))
  colnames(obs) <- c("value", "freq")
  obs$source <- "Observed"
  preds <-  as.data.frame(table(preds))
  colnames(preds) <- c("value", "freq")
  preds$source <- "Predicted"
  
  df <- rbind(obs, preds)
  
  clm_plot <- ggplot(data=df, aes(x=value, y=freq, fill=source)) + 
              geom_bar(stat='identity', position=position_dodge()) +
              labs(fill='Source.', x = v, y = "Freq.") + 
              theme(legend.position='top', 
                    legend.justification='left',
                    legend.direction='horizontal')
  print(clm_plot)
}

clm_output <- function(data_path){
  clm_model<- readRDS(data_path)
  print(summary(clm_model))
  # any diagnostic plots for tobacco.
}

# glm models ###################################################################

glm_barplot <- function(data_path){
  # for binary data plot a split barchart given observed and predicted counts.
  glm_model<- readRDS(data_path)
  obs <- ols.model$model[, c(v)]
  preds <- predict(glm_model)
  df <- cbind(c(obs, preds))
  colnames(df) <- c("Observed", "Predicted")
  barplot(df, 
          col=c("red", "blue") , 
          border="white", 
          beside=T, 
          legend=colnames(df), 
          xlab="")
}

glm_output <- function(data_path){
  glm_model<- readRDS(data_path)
  print(summary(glm_model))
  # any diagnostic plots for tobacco.
}

# nnet models ######################################################################

nnet_confusion_matrix <- function(data_path, mode, v){
  
  # each column is people actually in a state.
  # each row is people predicted a state.
  # E.g. row 3 column 2 is the percentage of people actually in family care
  # predicted as sick/disabled (~7%).
  if (mode == "multinom"){
    multinom_model<- readRDS(data_path)
    #obs <- multinom_model$model[, c(v)]
    obs <- as.data.frame(multinom_model[v])[,c(v)]
    preds <- predict(multinom_model)
  }
  else if (mode == "ordinal"){
    ordinal_model<- readRDS(data_path)
    obs <- as.data.frame(multinom_model[v])[,c(v)]
    preds <- predict(ordinal_model, type='class', real_data)$fit
  }

  confusion_matrix <- table(obs, preds)
  
  # row and column names for confusion matrix. 
  col_names <- colnames(confusion_matrix)
  row_names <- paste0(col_names, " [")
  row_names <- paste0(row_names,  as.character(rowSums(confusion_matrix)))
  row_names <- paste0(row_names, "]")
  row_names <- str_wrap(row_names, width = 12)
  col_names <- str_wrap(colnames(confusion_matrix), 10) # do col names again with string wrap.
  
  # scale confusion matrix rows to between 0 and 1. 
  # convert to long data frame and rounding frequencies for neatness.
  confusion_matrix <- confusion_matrix/rowSums(confusion_matrix)
  confusion_frame <- as.data.frame(confusion_matrix) # convert to data frame
  confusion_frame$Freq <-round(confusion_frame$Freq, 3) # round to 2dp
  colnames(confusion_frame) <- c("x", "y", "Freq")
  
  confusion_plot<- ggplot(confusion_frame, aes(y, rev(x), fill= Freq)) +
    scale_fill_viridis_c("% of state")+ # colour fill with viridis scheme.
    geom_tile() + # creates grid of coloured tiles.
    geom_shadowtext(aes(label=Freq)) + # white text with black shadow. readable on any colour background. 
    labs(y = "True State [population in state]",x = "Predicted State (no units)") + # label axes and ticks.
    scale_y_discrete(labels=rev(row_names), expand=c(0, 0)) + # Expand removes whitespace between axes and grid.
    scale_x_discrete(labels=col_names, expand=c(0, 0)) +
    theme_minimal() # remove black border and axes ticks.
  plot(confusion_plot)
}

nnet_output <- function(data_path){
  multinom_model<- readRDS(data_path)
  print(summary(multinom_model))
}


# ZIP models #########################################

zip_density <- function (data_path, v){
  # Density plot for zip models.
  # zip model outputs two sets of predictors.
  #
  # First is probability of non-zero event. 
  # For sample n this is a length n vector of values between 0 and 1 containing probabilities.
  # E.g. probability a person smokes anything. 
  #
  # Second is count values given non-zero event.
  # E.g. if a person smokes what is their predicted consumption.
  #
  # Combine these two together to get an estimated count density for the whole population.
  # Randomly sample if individuals have a non-zero even using probabilities.
  # If they have an event assign them the corresponding count else 0.
  
  # get obs/preds
  zip_model <- readRDS(data_path)
  obs <- zip_model[[v]]
  # predict probability of zero value and counts of non-zero value..
  probs <- predict(zip_model, type='zero')
  counts <- predict(zip_model, type='count')
  # randomly assign 0 values to individuals based on probability of zero status.
  preds <- (runif(length(probs)) >= probs) * counts
  # density plot for obs and preds lines.
  plot(density(preds, from=0), lty=1, col='red')
  lines(density(obs, from=0), col='blue', lty=2)
  legend('topright', legend=c("Predicted", "Real"), col=c("red", "blue"), lty=1:2)
}

zip_output <- function(data_path){
  zip_model <- readRDS(data_path)
  print(summary(zip_model))
}

#TODO utility functions for education and replenishment. 

test_main <-function()
{
  
  # labour
  discrete_barplot("data/transitions/labour_state/nnet/labour_state_2018_2019.rds", 'next_labour_state')
  nnet_confusion_matrix("data/transitions/labour_state/nnet/labour_state_2018_2019.rds", "multinom", "next_labour_state")
  
  #loneliness
  discrete_barplot("data/transitions/loneliness/clm/loneliness_2018_2019.rds", 'next_loneliness')
  clm_barplot("data/transitions/loneliness/clm/loneliness_2018_2019.rds", "next_loneliness") 
  clm_output("data/transitions/loneliness/clm/loneliness_2018_2019.rds")
  
  # household income
  continuous_density("data/transitions/hh_income/ols/hh_income_2018_2019.rds", "next_hh_income")  
  ols_output("data/transitions/hh_income/ols/hh_income_2018_2019.rds")
  ols_histogram("data/transitions/hh_income/ols/hh_income_2018_2019.rds", "next_hh_income")
  
  # housing
  discrete_barplot("data/transitions/housing_quality/clm/housing_quality_2018_2019.rds", 'next_housing_quality')
  clm_barplot("data/transitions/housing_quality/clm/housing_quality_2018_2019.rds", "next_housing_quality") 
  clm_output("data/transitions/housing_quality/clm/housing_quality_2018_2019.rds")
  
  # MWB
  continuous_density("data/transitions/SF_12/OLS/SF_12_2018_2019.rds", "next_SF_12")  
  ols_output("data/transitions/SF_12/OLS/SF_12_2018_2019.rds")
  ols_histogram("data/transitions/SF_12/OLS/SF_12_2018_2019.rds", "next_SF_12")
  
  #neighbourhood
  discrete_barplot("data/transitions/neighbourhood_safety/clm/neighbourhood_safety_2014_2017.rds", 'next_neighbourhood_safety')
  clm_barplot("data/transitions/neighbourhood_safety/clm/neighbourhood_safety_2014_2017.rds", "next_neighbourhood_safety") 
  clm_output("data/transitions/neighbourhood_safety/clm/neighbourhood_safety_2014_2017.rds")  
  
  # tobacco
  counts_density("data/transitions/ncigs/zip/ncigs_2018_2019.rds", "y")
  zip_output("data/transitions/ncigs/zip/ncigs_2018_2019.rds")
  zip_density("data/transitions/ncigs/zip/ncigs_2018_2019.rds", 'y')
  
  }

#test_main()
