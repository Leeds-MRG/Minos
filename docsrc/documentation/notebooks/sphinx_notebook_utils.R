"This file contains functions used in R notebook outputs for the sphinx website.

It is generally much tidier than having large blocks of code 
lying around to call one line from here.
"

source("minos/transitions/utils.R")
#source("../../../minos/transitions/utils.R")
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

real_data <- read.csv("data/final_US/2018_US_Cohort.csv")
#real_data <- read.csv("../../../data/final_US/2019_US_Cohort.csv")


notebook_setwd<- function(){
  workingDir <- "../../.." # points to docsrc/ from the docsrc/documentation/notebooks folder where this file is run.
  knitr::opts_knit$set(root.dir = workingDir)
}

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
    height <- max(max(d1$obs), max(d2$obs))
    
    plot(d1, col='red', ylim=c(0, 1.02*height))
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

clm_output <- function(data_path){
  clm.model<- readRDS(data_path)
  print(summary(clm.model))
  # any diagnostic plots for tobacco.
}

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


nnet_confusion_matrix <- function(data_path, mode, v){
  
  # each column is people actually in a state.
  # each row is people predicted a state.
  # E.g. row 3 column 2 is the percentage of people actually in family care
  # predicted as sick/disabled (~7%).
  if (mode == "multinom"){
    multinom_model<- readRDS(data_path)
    obs <- multinom_model$model[, c(v)]
    preds <- predict(multinom_model)
  }
  else if (mode == "ordinal"){
    ordinal_model<- readRDS(data_path)
    real_data[,c(v)] <- replace.missing(real_data)[, c(v)]
    obs <- real_data[, c(v)]
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
    scale_y_discrete(labels=rev(row_names)) +
    scale_x_discrete(labels=col_names)
  plot(confusion_plot)
}

nnet_output <- function(data_path){
  multinom_model<- readRDS(data_path)
  print(summary(multinom_model))
}




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
  obs <- zip_model$model[, c(v)]
  # predict probability of zero value and counts of non-zero value..
  probs <- predict(zip_model, type='zero')
  counts <- predict(zip_model, type='count')
  # randomly assign 0 values to individuals based on probability of zero status.
  preds <- (runif(length(probs)) < probs) * counts
  # density plot for obs and preds lines.
  plot(density(preds, from=0), xlim=c(0, 20), lty=1, col='red')
  lines(density(obs, from=0), col='blue', xlim=c(0, 20), lty=2)
  legend('topright', legend=c("Predicted", "Real"), col=c("red", "blue"), lty=1:2)
}

zip_output <- function(data_path){
  zip_model <- readRDS(data_path)
  print(summary(zip_model))
}

#TODO utility functions for education and replenishment. 


#nnet_confusion_matrix("data/transitions/test/labour_nnet_2018_2019.rds", "multinom", "factor(y)")

nnet_confusion_matrix("data/transitions/test/loneliness_clm_2018_2019.rds", "ordinal", 'loneliness') 


