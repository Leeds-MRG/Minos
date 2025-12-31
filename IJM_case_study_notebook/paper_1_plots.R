library(ggplot2)


miss.values <- c(-10, -9, -8, -7, -3, -2, -1,
                 -10., -9., -8., -7., -3., -2., -1.)


# Forest plot for lognormal OLS coefficients.
ols.exponential.sf12.mcs.forest.plot <- function(model, plot.file.name){
  
  # Define labels for coefficients in final graph. improve readibility.
  coefficient.term.labels <- c("Sex: Male vs Female",
                   "Ethnicity: BAN vs WBI",
                   "Ethnicity: BLA vs WBI",
                   "Ethnicity: BLC vs WBI",
                   "Ethnicity: CHI vs WBI",
                   "Ethnicity: IND vs WBI",
                   "Ethnicity: MIX vs WBI",
                   "Ethnicity: OAS vs WBI",
                   "Ethnicity: OBL vs WBI",
                   "Ethnicity: OTH vs WBI",
                   "Ethnicity: PAK vs WBI",
                   "Ethnicity: WHO vs WBI",
                   "Age",
                   "Education State: 1 vs 0",
                   "Education State: 2 vs 0",
                   "Education State: 3 vs 0",
                   "Education State: 5 vs 0",
                   "Education State: 6 vs 0",
                   "Education State: 7 vs 0",
                   "Labour State: FT Education vs Family Care",
                   "Labour State: FT Employment vs Family Care",
                   "Labour State: Job Seeking vs Family Care",
                   "Labour State: Not Working vs Family Care",
                   "Labour State: PT Employed vs Family Care",
                   "NSSEC: 0 vs. 1",
                   "NSSEC: 2 vs. 1",
                   "NSSEC: 3 vs. 1",
                   "NSSEC: 4 vs. 1",
                   "NSSEC: 5 vs. 1",
                   "NSSEC: 6 vs. 1",
                   "NSSEC: 7 vs. 1",
                   "NSSEC: 8 vs. 1",
                   "Region: East Midlands vs London",
                   "Region: East of England vs London",
                   "Region: North East vs London",
                   "Region: North West vs London",
                   "Region: Northern Ireland vs London",
                   "Region: Scotland vs London",
                   "Region: South East vs London",
                   "Region: South West vs London",
                   "Region: Wales vs London",
                   "Region: West Midlands vs London",
                   "Region: Yorkshire \\& Humber vs London",
                   "Household Income")
  coefficient.term.labels <- factor(coefficient.term.labels, levels=unique(rev(coefficient.term.labels)))
  
  pdf(plot.file.name)
  # make forest plot using sjPlot package.
  p <- plot_model(model, transform="exp",
                  title = "", vline.color='black') + aes(shape=p.stars)
  p$data$p.stars[p$data$p.stars == ""] <- "n.s." # force empty shape strings to n.s. so they show up in legend.
  p$data$term <- coefficient.term.labels
  p <- p +  scale_shape_manual(name='Significance Level',
                               breaks=c('n.s.', "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  p <- p + ylab("Coefficient Estimates")
  p <- p + ylim(c(0.7, 1.5))
  
  plot(p)
  dev.off()
  # print again so it displays in notebook and saves to pdf.
  print(p)
  
}


# Forest plot for lognormal OLS SF-12 MCS model using MICE imputation.
mice.ols.sf12.mcs.forest.plot <- function(model, plot.file.name){
  
  # Redefine coefficient names in graph for readibility.
  coefficient.term.labels <- c("Sex: Male vs Female",
                   "Ethnicity: BAN vs WBI",
                   "Ethnicity: BLA vs WBI",
                   "Ethnicity: BLC vs WBI",
                   "Ethnicity: CHI vs WBI",
                   "Ethnicity: IND vs WBI",
                   "Ethnicity: MIX vs WBI",
                   "Ethnicity: OAS vs WBI",
                   "Ethnicity: OBL vs WBI",
                   "Ethnicity: OTH vs WBI",
                   "Ethnicity: PAK vs WBI",
                   "Ethnicity: WHO vs WBI",
                   "Age",
                   "Education State: 1 vs 0",
                   "Education State: 2 vs 0",
                   "Education State: 3 vs 0",
                   "Education State: 5 vs 0",
                   "Education State: 6 vs 0",
                   "Education State: 7 vs 0",
                   "Labour State: FT Education vs Family Care",
                   "Labour State: FT Employment vs Family Care",
                   "Labour State: Job Seeking vs Family Care",
                   "Labour State: Not Working vs Family Care",
                   "Labour State: PT Employed vs Family Care",
                   "NSSEC: 0 vs. 1",
                   "NSSEC: 2 vs. 1",
                   "NSSEC: 3 vs. 1",
                   "NSSEC: 4 vs. 1",
                   "NSSEC: 5 vs. 1",
                   "NSSEC: 6 vs. 1",
                   "NSSEC: 7 vs. 1",
                   "NSSEC: 8 vs. 1",
                   "Region: East Midlands vs London",
                   "Region: East of England vs London",
                   "Region: North East vs London",
                   "Region: North West vs London",
                   "Region: Northern Ireland vs London",
                   "Region: Scotland vs London",
                   "Region: South East vs London",
                   "Region: South West vs London",
                   "Region: Wales vs London",
                   "Region: West Midlands vs London",
                   "Region: Yorkshire \\& Humber vs London",
                   "Household Income",
                   "Household Income Squared",
                   "Housing Quality: High vs Low",
                   "Housing Quality: Medium vs Low",
                   "Neighbourhood Safety: 2 vs 1",
                   "Neighbourhood Safety: 3 vs 1",
                   "Loneliness: 2 vs 1",
                   "Loneliness: 3 vs 1",
                   "Nutrition Quality",
                   "Number of Cigarettes"
  )
  coefficient.term.labels <- factor(coefficient.term.labels, levels=unique(rev(coefficient.term.labels)))
  
  pdf(plot.file.name)
  # plot coefficients using sjPlot.
  p <- plot_model(model, transform="exp", 
                  title = "", vline.color='black') + aes(shape=p.stars)
  p <- p + ylim(c(0.2, 1.5))
  
  p$data$term <- coefficient.term.labels
  p$data$p.stars[p$data$p.stars == ""] <- "n.s." # force empty shape strings to n.s. so they show up in legend.
  p <- p +  scale_shape_manual(name='Significance Level',
                               breaks=c('n.s.', "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  p <- p + ylab("Coefficient Estimates")
  plot(p)
  dev.off()
  
  plot(p) # plot again so shows up in notebook.
  
}


# Forest plot for GLMM Gamma model for SF-12 MCS.
gamma.forest.plot <- function(model, save.path, plot.file.name){
  
  # Redefine coefficient names for readibility.
  coefficient.term.labels <- c("SF-12 MCS Last", 
                               "Sex: Male vs Female",
                               "Ethnicity: BAN vs WBI",
                               "Ethnicity: BLA vs WBI",
                               "Ethnicity: BLC vs WBI",
                               "Ethnicity: CHI vs WBI",
                               "Ethnicity: IND vs WBI",
                               "Ethnicity: MIX vs WBI",
                               "Ethnicity: OAS vs WBI",
                               "Ethnicity: OBL vs WBI",
                               "Ethnicity: OTH vs WBI",
                               "Ethnicity: PAK vs WBI",
                               "Ethnicity: WHO vs WBI",
                               "Age",
                               "Education State: 1 vs 0",
                               "Education State: 2 vs 0",
                               "Education State: 3 vs 0",
                               "Education State: 5 vs 0",
                               "Education State: 6 vs 0",
                               "Education State: 7 vs 0",
                               "Labour State: FT Education vs Family Care",
                               "Labour State: FT Employment vs Family Care",
                               "Labour State: Job Seeking vs Family Care",
                               "Labour State: Not Working vs Family Care",
                               "Labour State: PT Employed vs Family Care",
                               "NSSEC: 0 vs. 1",
                               "NSSEC: 2 vs. 1",
                               "NSSEC: 3 vs. 1",
                               "NSSEC: 4 vs. 1",
                               "NSSEC: 5 vs. 1",
                               "NSSEC: 6 vs. 1",
                               "NSSEC: 7 vs. 1",
                               "NSSEC: 8 vs. 1",
                               "Region: East Midlands vs London",
                               "Region: East of England vs London",
                               "Region: North East vs London",
                               "Region: North West vs London",
                               "Region: Northern Ireland vs London",
                               "Region: Scotland vs London",
                               "Region: South East vs London",
                               "Region: South West vs London",
                               "Region: Wales vs London",
                               "Region: West Midlands vs London",
                               "Region: Yorkshire \\& Humber vs London",
                               "Household Income",
                               "Household Income Squared",
                               "Housing Quality: High vs Low",
                               "Housing Quality: Medium vs Low",
                               "Neighbourhood Safety: 2 vs 1",
                               "Neighbourhood Safety: 3 vs 1",
                               "Loneliness: 2 vs 1",
                               "Loneliness: 3 vs 1",
                               "Nutrition Quality",
                               "Number of Cigarettes",
                               "Time"
  )
  coefficient.term.labels <- factor(coefficient.term.labels, levels=unique(rev(coefficient.term.labels)))
  
  pdf(plot.file.name)
  # plot coefficients using sjPlot.
  p <- plot_model(model, transform="exp", sort.set=NULL, grid.breaks=10,
                  title = "", coefficient.term.labels=coefficient.term.labels) + aes(shape=p.stars)
  p$data$term <- coefficient.term.labels
  p <- p + geom_hline(yintercept=1)
  #p <- p + ylim(c(0.993, 1.1))
  p <- p + ylim(c(0.915, 1.01))
  p$data$p.stars[p$data$p.stars == ""] <- "n.s." # force empty shape strings to n.s. so they show up in legend.
  p <- p +  scale_shape_manual(name='Significance Level',
                               breaks=c('n.s.', "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  p <- p + ylab("Coefficient Estimates")
  plot(p)
  dev.off()
  
  plot(p) # plot again so shows in notebook.
  
}

# plotting densities for residuals against standard normal guide function. similar to qq plot.
residual.density.plot <- function(res, plot.file.name, guide=NULL){

  # res - residuals of plotted model.
  # plot.file.name - where to save plot
  # guide - expected residual distribution. usually standard normal. 
  pdf(plot.file.name)
  plot(density(scale(res)), xlab="SF-12 MCS", ylab = "Residual Probability Density.", main="")
  if (guide=="normal"){
    x <- seq(-4, 4, 1/10000) # reference normal line in red.
    lines(x, dnorm(x), col='red', lty=2)
    legend("topleft", legend=c("Residuals", "Standard Normal Guide"), 
           col = c("black","red"), lty=c(1,2))
  }
  dev.off()
  print("saved residual density plot to")
  print(plot.file.name)
  
  # plotting in notebook as well as saving..
  plot(density(scale(res)), xlab="SF-12 MCS", ylab = "Residual Probability Density.", main="")
  if (guide=="normal"){
    x <- seq(-4, 4, 1/10000) # reference normal line in red.
    lines(x, dnorm(x), col='red', lty=2)
    legend("topleft", legend=c("Residuals", "Standard Normal Guide"), 
           col = c("black","red"), lty=c(1,2))
  }
  
}


qq.plot <- function(res, plot.file.name){
  
  pdf(plot.file.name)
  qqnorm(scale(res), xlab="SF-12 MCS Theoretical Quantities")
  qqline(scale(res))
  dev.off()
  print("saved qq plot to")
  print(plot.file.name)
  
  # outputting plot in notebook as well as saving..
  qqnorm(scale(res), xlab="SF-12 MCS Theoretical Quantities")
  qqline(scale(res))
  
}

# Standard fitted-residual plot for OLS/ regression models checking for heterogeneity.
fitted.residual.plot <- function(fitted.residuals, plot.file.name){
  
  residual.fitted.plot <- ggplot(fitted.residuals, aes(fitted, sqrt_residuals)) +
    geom_point(shape=1) +
    geom_smooth(colour="red") +
    #geom_line(aes(y=rollmean(sqrt_residuals, 10000, na.pad=TRUE)), col='red') +
    theme_bw() +
    xlab("SF-12 MCS Fitted Values") +
    ylab("Residual Square Roots")
  pdf(plot.file.name)
  print(residual.fitted.plot)
  dev.off()
  print("saved fitted-residual plot to")
  print(plot.file.name)
  
  print(residual.fitted.plot) # print in notebook as well as saving.
  
}


# Plot boxplots used in nowcasting comparing fitted and true SF-12 MCS populations.
handover.boxplots <- function(raw, baseline, var, save.path, filename.prefix) {
  raw.var <- raw %>%
    dplyr::select(pidp, time, all_of(var))
  raw.var$Dataset <- 'Real UKHLS Data'
  
  baseline.var <- baseline %>%
    dplyr::select(pidp, time, all_of(var))
  baseline.var$Dataset <- 'Model Prediction'
  
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
  
  p <- ggplot(data = combined, aes(x = time, y = .data[[var]],  group = interaction(time, Dataset), fill= Dataset)) +
    geom_boxplot(notch=TRUE) +
    labs(title = paste0(var, ': Yearly box plots'))
  
  ggsave(filename = paste0(filename.prefix, ".pdf"),
         plot=p,
         path=save.path)
  
  print(p)
}



# Ridgeline density plots comparing SF-12 MCS real and predicted populations when nowcasting.
density.ridges <- function(data, v, save=FALSE, save.path=NULL, filename.tag=NULL)
{
  
  # Get data for plotting. 
  data.plot <- data[, c("time", v)]
  # Remove missing values
  data.plot <- data.plot %>%
    filter(!data.plot[[v]] %in% miss.values)
  if (min(data.plot$time) <= 2020) {
    handover <- TRUE
  } else {
    handover <- FALSE
  }
  
  data.plot$time <- factor(data.plot$time)
  data.plot <- data.plot[order(data.plot$time),]
  
  # plot using ridgeline plot.
  output.plot <- ggplot(data.plot, aes(x=!!sym(v), y=time)) +
    geom_density_ridges(aes(y=time, color=time, linetype=time), alpha=0.6) +
    scale_color_cyclical(values=c("#F8766D", "#00BA38","#619CFF")) +
    scale_linetype_cyclical(values=c(1, 2, 3)) +
    xlim(c(0, 70)) + 
    ylab("SF-12 MCS Densities Over Time") +
    xlab("SF-12 MCS")
  
  if(save) {
    if(is.null(save.path)) {
      stop('ERROR: save.path must be defined when saving the plot')
    }
    # add handover to filename if handover
    if (handover) {
      save.filename <- paste0('density_ridges_', v, '.pdf')
    } else {
      save.filename <- paste0('density_ridges_', v, '.pdf')
    }
    # add tag to filename if provided
    if (!is.null(filename.tag)) {
      save.filename <- paste0(filename.tag, '_', save.filename)
    }
    
    ggsave(filename = save.filename,
           plot = output.plot,
           path = save.path)
  }
  return(output.plot)
}


# format captions for latex tables depending on model type and dependent variable.
get.tex.table.caption <- function(variable, mod.type) {
  
  output <- paste0("Model ", mod.type)
  output <- paste0(output, " coefficients for estimation of variable: ")
  output <- paste0(output, variable)
  output <- paste0(output, ".")
  
}


# updating some column names for understanding society data. useful for more readable plots.
update.column.names <- function(data) {
  
  data.colnames <- colnames(data)
  data.colnames[which( data.colnames=="job_sec" )] <- "NSSEC"
  data.colnames[which( data.colnames=="hh_netinc" )] <- "hh_income"
  data.colnames[which( data.colnames=="labour_state_raw" )] <- "labour_state"
  data.colnames[which( data.colnames=="S7_labour_state" )] <- "labour_state"
  colnames(data) <- data.colnames
  
  return(data)
}

# Function for getting root mean squared error for GLMM models.
rmse2 <- function(preds, obs){
  
  obs.minus.preds.squared <- (preds - obs)**2
  out <- sqrt(sum(obs.minus.preds.squared/length(preds)))
  
  return (out)
}


mice.missingness.structure.aggr.plot <- function(mice.data, save.path, aggr.columns, file.name)
{
  #create aggr plot for missing data structure.
  pdf(paste0(save.path, file.name))
  aggr(mice.data[,aggr.columns], sortVars=T, prop=T, combined=F,varheight=T, oma=c(10,5,1,2), gap=0, 
       ylabs=c("Percentage of Missing Values", "Combinations of Missing Values"), labels=aggr.labels)
  dev.off()
  # run again so it prints in notebook.
  aggr(mice.data[,aggr.columns], sortVars=T, prop=T, combined=F,varheight=T, oma=c(10,5,1,2), gap=0, 
       ylabs=c("Percentage of Missing Values", "Combinations of Missing Values"), labels=aggr.labels)
  
}

mice.convergence.trace.plot <- function(imputed.mice.populations, save.path, file.name) {
  # Make MICE convergence plot. checking variance and mean SF-12 MCS values for each imputed population and MICE iteration for stability.
  pdf(paste0(paste0(save.path, file.name)))
  MICE.trace.plot <- plot_trace(imputed.mice.populations, "SF_12_MCS") + theme(legend.position="none")
  MICE.trace.plot$data$vrb <- "SF-12 MCS"
  plot(MICE.trace.plot)
  dev.off()
  plot(MICE.trace.plot) # run twice so prints in notebook.
}


sf12.mcs.cv.lasso.plot <- function(sf12.mcs.cv.lasso, save.path, file.name) {
  pdf(paste0(save.path, file.name))
  plot(sf12.mcs.cv.lasso, xlab="L1 Regularisation Constraint (log(lambda))", ylab="Mean Squared Error")
  dev.off()
}



sf12.mcs.randomised.coefficients.plot <- function(randomised.mice.model.data, save.path, file.name) {
  # Plot SF-12 MCS predicted distributions for each of the 100 models with randomised coefficients.
  p <- ggplot(randomised.mice.model.data, aes(x=SF_12_MCS, y=Density, group=factor(run_id))) +
    geom_line(alpha=0.1) + ylim(0, 0.15) + xlim(15,60) + xlab("SF-12 MCS") + ylab("Probabilities Densities")
  ggsave(paste0(save.path, "/",  file.name))
  print(p) # print so shows  up in notebook.
}  



########################################
# Code for generating model latex tables
########################################

# Coefficient names for models using MICE imputed data and model formula.#
# Used multiple times so global variable.
mice.sf12.mcs.coefficients.names <- c("Intercept", "Sex: Male vs Female",
                                      "Ethnicity: BAN vs WBI",
                                      "Ethnicity: BLA vs WBI",
                                      "Ethnicity: BLC vs WBI",
                                      "Ethnicity: CHI vs WBI",
                                      "Ethnicity: IND vs WBI",
                                      "Ethnicity: MIX vs WBI",
                                      "Ethnicity: OAS vs WBI",
                                      "Ethnicity: OBL vs WBI",
                                      "Ethnicity: OTH vs WBI",
                                      "Ethnicity: PAK vs WBI",
                                      "Ethnicity: WHO vs WBI",
                                      "Age",
                                      "Education State: 1 vs 0",
                                      "Education State: 2 vs 0",
                                      "Education State: 3 vs 0",
                                      "Education State: 5 vs 0",
                                      "Education State: 6 vs 0",
                                      "Education State: 7 vs 0",
                                      "Labour State: FT Education vs Family Care",
                                      "Labour State: FT Employment vs Family Care",
                                      "Labour State: Job Seeking vs Family Care",
                                      "Labour State: Not Working vs Family Care",
                                      "Labour State: PT Employed vs Family Care",
                                      "NSSEC: 0 vs. 1",
                                      "NSSEC: 2 vs. 1",
                                      "NSSEC: 3 vs. 1",
                                      "NSSEC: 4 vs. 1",
                                      "NSSEC: 5 vs. 1",
                                      "NSSEC: 6 vs. 1",
                                      "NSSEC: 7 vs. 1",
                                      "NSSEC: 8 vs. 1",
                                      "Region: East Midlands vs London",
                                      "Region: East of England vs London",
                                      "Region: North East vs London",
                                      "Region: North West vs London",
                                      "Region: Northern Ireland vs London",
                                      "Region: Scotland vs London",
                                      "Region: South East vs London",
                                      "Region: South West vs London",
                                      "Region: Wales vs London",
                                      "Region: West Midlands vs London",
                                      "Region: Yorkshire \\& Humber vs London",
                                      "Household Income",
                                      "Household Income Squared",
                                      "Housing Quality: High vs Low",
                                      "Housing Quality: Medium vs Low",
                                      "Neighbourhood Safety: 2 vs 1",
                                      "Neighbourhood Safety: 3 vs 1",
                                      "Loneliness: 2 vs 1",
                                      "Loneliness: 3 vs 1",
                                      "Nutrition Quality",
                                      "Number of Cigarettes")

OLS.make.latex.tables <- function(ols.model){
  
  texreg.file <- paste0(save.path, 'table_2_SF12_MCS_OLS_coefficients.txt')
  tex.label <- paste0("table: baseline_SF12_MCS_OLS_coefficients") 
  tex.headers <- c(texreg::names2latex("Baseline SF-12 MCS OLS"))
  tex.caption <- texreg::names2latex(get.tex.table.caption("SF-12 MCS", "OLS"))
  ols.coef.names <- c("Intercept", "Sex: Male vs Female",
                      "Ethnicity: BAN vs WBI",
                      "Ethnicity: BLA vs WBI",
                      "Ethnicity: BLC vs WBI",
                      "Ethnicity: CHI vs WBI",
                      "Ethnicity: IND vs WBI",
                      "Ethnicity: MIX vs WBI",
                      "Ethnicity: OAS vs WBI",
                      "Ethnicity: OBL vs WBI",
                      "Ethnicity: OTH vs WBI",
                      "Ethnicity: PAK vs WBI",
                      "Ethnicity: WHO vs WBI",
                      "Age",
                      "Education State: 1 vs 0",
                      "Education State: 2 vs 0",
                      "Education State: 3 vs 0",
                      "Education State: 5 vs 0",
                      "Education State: 6 vs 0",
                      "Education State: 7 vs 0",
                      "Labour State: FT Education vs Family Care",
                      "Labour State: FT Employment vs Family Care",
                      "Labour State: Job Seeking vs Family Care",
                      "Labour State: Not Working vs Family Care",
                      "Labour State: PT Employed vs Family Care",
                      "NSSEC: 0 vs. 1",
                      "NSSEC: 2 vs. 1",
                      "NSSEC: 3 vs. 1",
                      "NSSEC: 4 vs. 1",
                      "NSSEC: 5 vs. 1",
                      "NSSEC: 6 vs. 1",
                      "NSSEC: 7 vs. 1",
                      "NSSEC: 8 vs. 1",
                      "Region: East Midlands vs London",
                      "Region: East of England vs London",
                      "Region: North East vs London",
                      "Region: North West vs London",
                      "Region: Northern Ireland vs London",
                      "Region: Scotland vs London",
                      "Region: South East vs London",
                      "Region: South West vs London",
                      "Region: Wales vs London",
                      "Region: West Midlands vs London",
                      "Region: Yorkshire \\& Humber vs London",
                      "Household Income")
  texreg(ols.model, # what model to save coefs for. 
         file=texreg.file,  # where to save.
         custom.model.names = tex.headers, # title of table.
         custom.coef.names = ols.coef.names,
         stars = c(0.001, 0.01, 0.05), # p-value significance symbols. 
         digits=4, # p values significant figures.
         caption=tex.caption, # \caption command option. 
         label = tex.label, # \label command option. 
         dcolumn=T,# nice column alignment. 
         booktabs=T, # nice hlines. (recommended)
         tabular=T,# tabular env.
         single.row = T, # nicer one row formatting.
         longtable=T, # allows tables to wrap over pages
         use.packages=F, # don't add \usepackage commands to allow for direct importing of files as inputs
         fontsize='small',# tiny font
         center = FALSE # no centering
         ) 
}




# Writing pooled MICE OLS model coefficients to a LATEX table.
SF12.MCS.OLS.MICE.make.latex.tables <- function(final.ols.sf12.mcs.pool) {
  
  texreg.file <- paste0(save.path, 'table_5_SF12_MICE_pool_OLS_coefficients.txt')
  tex.label <- paste0("table: MICE_pool_OLS_coefficients") 
  tex.headers <- c(texreg::names2latex("MICE SF-12 MCS OLS Pool"))
  tex.caption <- texreg::names2latex(get.tex.table.caption("SF-12 MCS", "MICE OLS"))    
  texreg(final.ols.sf12.mcs.pool, # what model to save coefs for. 
         file=texreg.file,  # where to save.
         custom.model.names = tex.headers, # title of table.
         custom.coef.names = mice.sf12.mcs.coefficients.names,
         stars = c(0.001, 0.01, 0.05), # p-value significance symbols. 
         digits=4, # p values significant figures.
         caption=tex.caption, # \caption command option. 
         label = tex.label, # \label command option. 
         dcolumn=T,# nice column alignment. 
         booktabs=T, # nice hlines. (recommended)
         tabular=T,# tabular env.
         single.row = T, # nicer one row formatting.
         longtable=T, # allows tables to wrap over pages
         use.packages=F, # don't add \usepackage commands to allow for direct importing of files as inputs
         fontsize='small',# tiny font
         center = FALSE # no centering
  )
}


sf12.mcs.ols.crossval.coefficients <- function(mice.crossval.sf12.mcs.old.model)
{
  
  texreg.file <- paste0(save.path, 'table_6_SF12_cross_val_OLS_coefficients.txt')
  tex.label <- paste0("table: sf12_mcs_ols_cross_val_coefficients") 
  tex.headers <- c(texreg::names2latex("5-Fold Cross Validated SF-12 MCS OLS"))
  tex.caption <- texreg::names2latex(get.tex.table.caption("Cross-validated SF-12 MCS", "OLS"))    
  texreg(summary(mice.crossval.sf12.mcs.old.model), # what model to save coefs for. 
         file=texreg.file,  # where to save.
         custom.model.names = tex.headers, # title of table.
         custom.coef.names = mice.sf12.mcs.coefficients.names,
         stars = c(0.001, 0.01, 0.05), # p-value significance symbols. 
         digits=4, # p values significant figures.
         caption=tex.caption, # \caption command option. 
         label = tex.label, # \label command option. 
         dcolumn=T,# nice column alignment. 
         booktabs=T, # nice hlines. (recommended)
         tabular=T,# tabular env.
         single.row = T, # nicer one row formatting.
         longtable=T, # allows tables to wrap over pages
         use.packages=F, # don't add \usepackage commands to allow for direct importing of files as inputs
         fontsize='small',# tiny font
         center = FALSE # no centering
  )
}


sf12.mcs.lasso.coefficients.table <- function(lasso.min, lasso.1se, lasso.min.coefs, lasso.1se.coefs){
  
  mice.sf12.mcs.coefficients.names <- c("Intercept", "Sex: Male vs Female",
                                        "Ethnicity: BAN vs WBI",
                                        "Ethnicity: BLA vs WBI",
                                        "Ethnicity: BLC vs WBI",
                                        "Ethnicity: CHI vs WBI",
                                        "Ethnicity: IND vs WBI",
                                        "Ethnicity: MIX vs WBI",
                                        "Ethnicity: OAS vs WBI",
                                        "Ethnicity: OBL vs WBI",
                                        "Ethnicity: OTH vs WBI",
                                        "Ethnicity: PAK vs WBI",
                                        "Ethnicity: WHO vs WBI",
                                        "Age",
                                        "Education State: 1 vs 0",
                                        "Education State: 2 vs 0",
                                        "Education State: 3 vs 0",
                                        "Education State: 5 vs 0",
                                        "Education State: 6 vs 0",
                                        "Education State: 7 vs 0",
                                        "Labour State: FT Education vs Family Care",
                                        "Labour State: FT Employment vs Family Care",
                                        "Labour State: Job Seeking vs Family Care",
                                        "Labour State: Not Working vs Family Care",
                                        "Labour State: PT Employed vs Family Care",
                                        "NSSEC: 0 vs. 1",
                                        "NSSEC: 2 vs. 1",
                                        "NSSEC: 3 vs. 1",
                                        "NSSEC: 4 vs. 1",
                                        "NSSEC: 5 vs. 1",
                                        "NSSEC: 6 vs. 1",
                                        "NSSEC: 7 vs. 1",
                                        "NSSEC: 8 vs. 1",
                                        "Region: East Midlands vs London",
                                        "Region: East of England vs London",
                                        "Region: North East vs London",
                                        "Region: North West vs London",
                                        "Region: Northern Ireland vs London",
                                        "Region: Scotland vs London",
                                        "Region: South East vs London",
                                        "Region: South West vs London",
                                        "Region: Wales vs London",
                                        "Region: West Midlands vs London",
                                        "Region: Yorkshire \\& Humber vs London",
                                        "Household Income",
                                        "Household Income Squared",
                                        "Housing Quality: High vs Low",
                                        "Housing Quality: Medium vs Low",
                                        "Neighbourhood Safety: 2 vs 1",
                                        "Neighbourhood Safety: 3 vs 1",
                                        "Loneliness: 2 vs 1",
                                        "Loneliness: 3 vs 1",
                                        "Nutrition Quality",
                                        "Number of Cigarettes")
  
  # Save to LATEX text file.
  texreg.file <- paste0(save.path, 'table_8_SF12_MCS_Lasso_coefficients.txt')
  tex.label <- paste0("table: sf12_mcs_lasso_coefficients") 
  tex.headers <- c(texreg::names2latex("Minimum Error"), texreg::names2latex("First Standard Error"))
  tex.caption <- texreg::names2latex(get.tex.table.caption("SF-12 MCS", "lasso"))    
  lasso.min <-createTexreg(coef.names=mice.sf12.mcs.coefficients.names, coef = lasso.min.coefs)
  lasso.1se <-createTexreg(coef.names=mice.sf12.mcs.coefficients.names, coef = lasso.1se.coefs)
  texreg(c(lasso.min, lasso.1se), # what model to save coefs for. 
         file=texreg.file,  # where to save.
         custom.model.names = tex.headers, # title of table.
         caption=tex.caption, # \caption command option. 
         label = tex.label, # \label command option. 
         digits=4, # p values significant figures.
         dcolumn=T,# nice column alignment. 
         booktabs=T, # nice hlines. (recommended)
         tabular=T,# tabulr env.
         single.row = T, # nicer one row formatting.
         longtable=T, # allows tables to wrap over pages
         use.packages=F, # don't add \usepackage commands to allow for direct importing of files as inputs
         fontsize='small',# tiny font
         center = FALSE # no centering
  )
}



sf12.mcs.weighted.ols.latex.coefficients.table <- function(sf12.mcs.ols.weighted.2013, sf12.mcs.ols.weighted.2018) {
  
  # Write two model coefficients to LATEX text file.
  texreg.file <- paste0(save.path, 'table_7_projected_weights_coefficients.txt')
  tex.label <- paste0("table: sf12_projected_weights_coefficients") 
  tex.headers <- c(texreg::names2latex("SF-12 MCS 2018 With 2013 Extrapolated Weights"), texreg::names2latex("SF-12 MCS 2018 With Weights"))
  tex.caption <- texreg::names2latex(get.tex.table.caption("SF-12 MCS", "OLS models with current and projected sample weights."))    
  texreg(list(sf12.mcs.ols.weighted.2013, sf12.mcs.ols.weighted.2018), # what model to save coefs for. 
         file=texreg.file,  # where to save.
         custom.model.names = tex.headers, # title of table.
         custom.coef.names = mice.sf12.mcs.coefficients.names,
         stars = c(0.001, 0.01, 0.05), # p-value significance symbols. 
         digits=4, # p values significant figures.
         caption=tex.caption, # \caption command option. 
         label = tex.label, # \label command option. 
         dcolumn=T,# nice column alignment. 
         booktabs=T, # nice hlines. (recommended)
         tabular=T,# tabular env.
         single.row = T, # nicer one row formatting.
         longtable=T, # allows tables to wrap over pages
         use.packages=F, # don't add \usepackage commands to allow for direct importing of files as inputs
         fontsize='small',# tiny font
         center = FALSE # no centering
  )
}


# save GLMM pooled coefficients to LATEX text file.
sf12.mcs.glmm.coefficients.latex.table <- function(sf12.glmm.pool)
{
  
  texreg.file <- paste0(save.path, 'table_9_SF_12_GLMM_coefficients.txt')
  tex.label <- paste0("table: GLMM_SF_12_coefficients") 
  tex.headers <- c(texreg::names2latex("SF-12 MCS GLMM"))
  tex.caption <- texreg::names2latex(get.tex.table.caption("SF-12 MCS", "glmm"))    
  texreg(sf12.glmm.pool, # what model to save coefs for. 
         file=texreg.file,  # where to save.
         custom.model.names = tex.headers, # title of table.
         custom.coef.names = c("SF-12 MCS Last", mice.sf12.mcs.coefficients.names, "time"),
         stars = c(0.001, 0.01, 0.05), # p-value significance symbols. 
         digits=4, # p values significant figures.
         caption=tex.caption, # \caption command option. 
         label = tex.label, # \label command option. 
         dcolumn=T,# nice column alignment. 
         booktabs=T, # nice hlines. (recommended)
         tabular=T,# tabular env.
         single.row = T, # nicer one row formatting.
         longtable=T, # allows tables to wrap over pages
         use.packages=F, # don't add \usepackage commands to allow for direct importing of files as inputs
         fontsize='small',# tiny font
         center = FALSE # no centering
  ) 
}
