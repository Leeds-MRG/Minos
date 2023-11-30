library(ggplot2)


miss.values <- c(-10, -9, -8, -7, -3, -2, -1,
                 -10., -9., -8., -7., -3., -2., -1.)

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



# for glmm gamma
forest_plot <- function(model, file_name){
  pdf(file_name)
  p <- plot_model(model,
                  title = "") + aes(shape=p.stars)
  p$data$p.stars[p$data$p.stars == ""] <- "n.s." # force empty shape strings to n.s. so they show up in legend.
  p <- p +  scale_shape_manual(name='Significance Level',
                               breaks=c('n.s.', "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  plot(p)
  dev.off()
}

# for glmm gamma
gamma_forest_plot <- function(model, file_name){
  pdf(file_name)
  p <- plot_model(model, transform=NULL, 
                  title = "") + aes(shape=p.stars)
  p$data$p.stars[p$data$p.stars == ""] <- "n.s." # force empty shape strings to n.s. so they show up in legend.
  p <- p +  scale_shape_manual(name='Significance Level',
                               breaks=c('n.s.', "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  #p <- p + ylim(0.1, 1.9)
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


handover_boxplots <- function(raw, baseline, var, save.path, filename.prefix) {
  raw.var <- raw %>%
    dplyr::select(pidp, time, all_of(var))
  raw.var$source <- 'final_US'
  
  baseline.var <- baseline %>%
    dplyr::select(pidp, time, all_of(var))
  baseline.var$source <- 'baseline_output'
  
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
  
  ggplot(data = combined, aes(x = time, y = .data[[var]],  group = interaction(time, source), fill= source)) +
    geom_boxplot(notch=TRUE) +
    labs(title = paste0(var, ': Yearly box plots'))
}

# summarise(summary_var = weighted.mean(x = .data[[var]], w = weight)) %>%
handover_lineplots <- function(raw, base, var) {
  # GENERALISE THIS AND DOCSTRING
  raw.means <- raw %>% 
    dplyr::select(pidp, time, var) %>%
    group_by(time) %>%
    summarise(summary_var = mean(.data[[var]], na.rm = TRUE)) %>%
    mutate(source = 'final_US')
  
  base.means <- base %>%
    dplyr::select(pidp, time, var) %>%
    group_by(time) %>%
    summarise(summary_var = mean(!!sym(var))) %>%
    mutate(source = 'baseline_output')
  
  # merge before plot
  combined <- rbind(raw.means, base.means)
  
  # Now plot
  ggplot(data = combined, aes(x = time, y = summary_var, group = source, color = source)) +
    geom_line() +
    geom_vline(xintercept=start.year, linetype='dotted') +
    labs(title = var, subtitle = 'Full Sample') +
    xlab('Year') +
    ylab(var) +
    ggsave(filename = paste0(save.path, "/", filename.prefix))
}



handover_boxplots <- function(raw, baseline, var, save.path, filename.prefix) {
  raw.var <- raw %>%
    dplyr::select(pidp, time, all_of(var))
  raw.var$source <- 'Raw Data'
  
  baseline.var <- baseline %>%
    dplyr::select(pidp, time, all_of(var))
  baseline.var$source <- 'Predicted Data'
  
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
  
  ggplot(data = combined, aes(x = time, y = .data[[var]],  group = interaction(time, source), fill= source)) +
    geom_boxplot(notch=TRUE) +
    labs(title = paste0(var, ': Yearly box plots'))
}



# summarise(summary_var = weighted.mean(x = .data[[var]], w = weight)) %>%
handover_lineplots <- function(raw, base, var) {
  # GENERALISE THIS AND DOCSTRING
  raw.means <- raw %>% 
    dplyr::select(pidp, time, var) %>%
    group_by(time) %>%
    summarise(summary_var = mean(.data[[var]], na.rm = TRUE)) %>%
    mutate(source = 'Raw Data')
  
  base.means <- base %>%
    dplyr::select(pidp, time, var) %>%
    group_by(time) %>%
    summarise(summary_var = mean(!!sym(var))) %>%
    mutate(source = 'Predicted Data')
  
  # merge before plot
  combined <- rbind(raw.means, base.means)
  
  # Now plot
  ggplot(data = combined, aes(x = time, y = summary_var, group = source, color = source)) +
    geom_line() +
    geom_vline(xintercept=start.year, linetype='dotted') +
    labs(title = var, subtitle = 'Full Sample') +
    xlab('Year') +
    ylab(var) +
    ggsave(filename = paste0(save.path, "/", filename.prefix))
}



density_ridges <- function(data, v, save=FALSE, save.path=NULL, filename.tag=NULL)
{
  data_plot <- data[, c("time", v)]
  # Remove missing values
  data_plot <- data_plot %>%
    filter(!data_plot[[v]] %in% miss.values)
  if (min(data_plot$time) <= 2020) {
    handover <- TRUE
  } else {
    handover <- FALSE
  }
  
  data_plot$time <- factor(data_plot$time)
  data_plot <- data_plot[order(data_plot$time),]
  output_plot <- ggplot(data_plot, aes(x=!!sym(v), y=time)) +
    geom_density_ridges(aes(y=time, color=time, linetype=time), alpha=0.6) +
    #scale_color_viridis_d() +
    scale_color_cyclical(values=c("#F8766D", "#00BA38","#619CFF")) +
    scale_linetype_cyclical(values=c(1, 2, 3))
  
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

get_tex_table_caption <- function(variable, mod.type) {
  
  output <- paste0("Model ", mod.type)
  output <- paste0(output, " coefficients for estimation of variable: ")
  output <- paste0(output, variable)
  output <- paste0(output, ".")
  
}


