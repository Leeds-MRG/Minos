"This file contains functions used in R notebook outputs for the sphinx website.

It is generally much tidier than having large blocks of code 
lying around to call one line from here.
"

notebook_setwd<- function(){
  workingDir <- "../../.." # points to docsrc/ from the docsrc/documentation/notebooks folder where this file is run.
  knitr::opts_knit$set(root.dir = workingDir)
  suppressMessages(require(tidyverse))
}

zip_output <- function(data_path){
  suppressMessages(require(pscl))
  notebook_setwd()
  zip_model <- readRDS(data_path)
  print(summary(zip_model))
  # any diagnostic plots for tobacco.
  #plot(zip_model)
  # TODO density plot.
}

ols_output <- function(data_path){
  notebook_setwd()
  ols<- readRDS(data_path)
  print(summary(ols))
  # any diagnostic plots for tobacco.
  plot(ols)
}

clm_output <- function(data_path){
  
  suppressMessages(require(ordinal))
  notebook_setwd()
  clm.model<- readRDS(data_path)
  print(summary(clm.model))
  # any diagnostic plots for tobacco.
}

glm_output <- function(data_path){
  notebook_setwd()
  suppressMessages(require(lme4))
  glm.model<- readRDS(data_path)
  print(summary(glm.model))
  # any diagnostic plots for tobacco.
}

nnet_output <- function(data_path){
  notebook_setwd()
  suppressMessages(require(nnet)) # disable annoying startup message.
  multinom.model<- readRDS(data_path)
  print(summary(multinom.model))
}



#TODO utility functions for education and replenishment. 






