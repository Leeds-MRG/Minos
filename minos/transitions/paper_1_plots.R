library(ggplot2)
library(sjPlot)
library(ggplot2)
library(ggpattern)
library(visreg)
library(ggridges)

source("minos/transitions/utils.R")
source("minos/transitions/transition_model_functions.R")

# forest plot for lm models. 
forest_plot_lm <- function(model, file_name){
  
  sf12_coefs <- summary(model)$coefficients
  sf12_coefs <- cbind(sf12_coefs, sf12_coefs[, 4])
  colnames(sf12_coefs)[5] <- "p.stars"
  what_ns <- which(sf12_coefs[, "Pr(>|t|)"] > 0.05)
  what_one_star <- which(sf12_coefs[, "Pr(>|t|)"] <= 0.05)
  what_two_star <- which(sf12_coefs[, "Pr(>|t|)"] <= 0.01)
  what_three_star <- which(sf12_coefs[, "Pr(>|t|)"] <= 0.001)
  
  sf12_coefs[what_ns, 'p.stars'] <- ""
  sf12_coefs[what_one_star, 'p.stars'] <- "*"
  sf12_coefs[what_two_star, 'p.stars'] <- "**"
  sf12_coefs[what_three_star, 'p.stars'] <- "***"
  p.stars<- sf12_coefs[, 5]
  #browser()
  pdf(file_name)
  p <- plot_model(model, transform=NULL,
                  title = "") + aes(shape=p.stars)
  p$data$p.stars[which(p$data$p.stars == "")] <- 'n.s.'
  p <- p +  scale_shape_manual(name='Significance Level',
                               limits=c("n.s.", "*", "**", "***"),
                               breaks=c("n.s.", "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  plot(p)
  dev.off()
}


forest_plot_glmm <- function(model, file_name){
  
  
  
  sf12_coefs <- summary(model)$coefficients
  sf12_coefs <- cbind(sf12_coefs, sf12_coefs[, 4])
  
  # shift coefficients by exponential scale
  
  
  # shift standard errors according to formula.
  
  colnames(sf12_coefs)[5] <- "p.stars"
  what_ns <- which(sf12_coefs[, "Pr(>|z|)"] > 0.05)
  what_one_star <- which(sf12_coefs[, "Pr(>|z|)"] <= 0.05)
  what_two_star <- which(sf12_coefs[, "Pr(>|z|)"] <= 0.01)
  what_three_star <- which(sf12_coefs[, "Pr(>|z|)"] <= 0.001)
  
  sf12_coefs[what_ns, 'p.stars'] <- ""
  sf12_coefs[what_one_star, 'p.stars'] <- "*"
  sf12_coefs[what_two_star, 'p.stars'] <- "**"
  sf12_coefs[what_three_star, 'p.stars'] <- "***"
  p.stars<- sf12_coefs[, 5]
  pdf(file_name)
  p <- plot_model(model, transform="exp",
                  title = "") + aes(shape=p.stars)
  p$data$p.stars[which(p$data$p.stars == "")] <- 'n.s.'
  p <- p +  scale_shape_manual(name='Significance Level',
                               limits=c("n.s.", "*", "**", "***"),
                               breaks=c("n.s.", "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  plot(p)
  dev.off()
}



# for glmm gamma
forest_plot <- function(model, file_name, limits=NULL){
  pdf(file_name)
  p <- plot_model(model,
                  title = "") + aes(shape=p.stars)
  p$data$p.stars[p$data$p.stars == ""] <- "n.s." # force empty shape strings to n.s. so they show up in legend.
  p <- p +  scale_shape_manual(name='Significance Level',
                               breaks=c('n.s.', "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  if (!is.null(limits)){
    p <- p + scale_y_log10(limits = limits)
  }
  plot(p)
  dev.off()
}

residual_density_plot <- function(res, file_name, guide=NULL){
  # res - residuals of plotted model
  # guide - expected residual distribution. usually standard normal. 
  pdf(file_name)
  hist(scale(res), breaks=1000, freq=F)
  if (guide=="normal"){
    x <- seq(-4, 4, 1/10000) # reference normal line in red.
    lines(x, dnorm(x), col='red')
  }
  dev.off()
  print("saved residual density plot to")
  print(file_name)
}


qq_plot <- function(res, file_name){
  pdf(file_name)
  print(qqnorm(scale(res)))
  print(qqline(scale(res)))
  dev.off()
  print("saved qq plot to")
  print(file_name)
}

fitted_residual_plot <- function(fitted_residuals, file_name){
  residual_fitted_plot <- ggplot(fitted_residuals, aes(fitted, sqrt_residuals)) +
    geom_point(shape=1) +
    geom_smooth(colour="red") +
    #geom_line(aes(y=rollmean(sqrt_residuals, 10000, na.pad=TRUE)), col='red') +
    theme_bw()
  pdf(file_name)
  print(residual_fitted_plot)
  dev.off()
  print("saved fitted-residual plot to")
  print(file_name)
}

get_tex_table_caption <- function(dependent, mod_type) {
  
  # intro sentence of fluff describing the model.
  output_string <- paste0("Table of coefficients for ", mod_type, " model for variable ", dependent, ". ")
  
  # any additional info required for the model type. 
  if (mod_type == "glmm" || mod_type == "lmm")
  {
    output_string <- paste0(output_string, "Variables with prefix `var:` provide information for random intercepts. ")
  } 
  else if (mod_type == "clm")
  {
    output_string <- paste0(output_string, "Variables with pipe operators e.g. `1|2' mark the thresholds between ordinal states.")
  } 
  else if (mod_type == "zip")
  {
    output_string <- paste0(output_string, "Variables with the `Count model:`
                            prefix are used to estimate number of cigarettes consumed per week if a person does smoke.
                            Variables with prefix `Zero model: ` are used to estimate if a person smokes 0 cigarettes. ")
  }  
  else if (mod_type == "ols" || mod_type == "logit")
  {
    output_string <- paste0(output_string, "") # no extra info needed here?
  }  
  return (output_string)
}



density_ridges <- function(data, v, save=FALSE, save.path=NULL, filename.tag=NULL)
{
  data_plot <- data[, c("time", v)]
  # Remove missing values
  #data_plot <- data_plot %>%
   # filter(!data_plot[[v]] %in% miss.values)
  if (min(data_plot$time) < 2020) {
    handover <- TRUE
  }
  
  data_plot$time <- factor(data_plot$time)
  data_plot <- data_plot[order(data_plot$time),]
  output_plot <- ggplot(data_plot, aes(x=!!sym(v), y=time)) +
    geom_density_ridges(aes(y=time, color=time, linetype=time), alpha=0.6) +
    #scale_color_viridis_d() +
    scale_color_cyclical(values=c("#F8766D", "#00BA38","#619CFF")) +
    scale_linetype_cyclical(values=c(1, 2, 3)) +
    xlim(0, 80)
  
  if(save) {
    if(is.null(save.path)) {
      stop('ERROR: save.path must be defined when saving the plot')
    }
    # add handover to filename if handover
    if (handover) {
      save.filename <- paste0('density_ridges_handover_', v, '.png')
    } else {
      save.filename <- paste0('density_ridges_output_', v, '.png')
    }
    # add tag to filename if provided
    if (!is.null(filename.tag)) {
      save.filename <- paste0(filename.tag, '_', save.filename)
    }
    
    ggsave(filename = save.filename,
           plot = output_plot,
           path = save.path)
  }
  return(output_plot)
}


handover_boxplots <- function(raw, baseline, var, save_path, save=T) {
  raw.var <- raw %>%
    dplyr::select(pidp, time, all_of(var))
  raw.var$source <- 'Real Data'
  
  baseline.var <- baseline %>%
    dplyr::select(pidp, time, all_of(var))
  baseline.var$source <- 'Predicted Data.'
  
  combined <- rbind(raw.var, baseline.var)
  combined$time <- as.factor(combined$time)
  combined <- drop_na(combined)
  combined <- filter(combined, .data[[var]] != -9)
  
  if (var %in% c('hh_income', 'equivalent_income')) {
    combined <- filter(combined, .data[[var]] < quantile(.data[[var]], 0.99), .data[[var]] > quantile(.data[[var]], 0.01))
  } else if (var == 'ncigs') {
    #combined <- filter(combined, .data[[var]] < quantile(.data[[var]], 0.99))
    combined <- filter(combined, .data[[var]] < quantile(.data[[var]], 0.99), !.data[[var]] == 0)
  }
  
  boxplot<- ggplot(data = combined, aes(x = time, y = .data[[var]],  group = interaction(time, source), fill= source)) +
    geom_boxplot(notch=TRUE) +
    labs(title = paste0(var, ': Yearly box plots'))
  if (save) {
    ggsave(paste0(save_path, ".pdf"))
  }
}
