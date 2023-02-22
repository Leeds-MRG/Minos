library(geepack)
source("minos/transitions/utils.R")

residual_density_plot <- function(res, file_name=NULL, guide=NULL){
  # res - residuals of plotted model
  # guide - expected residual distribution. usually standard normal. 
  if (is.null(file_name))
  {
    pdf(file_name)
    plot(density(scale(res)))
    if (guide=="normal"){
      x <- seq(-4, 4, 1/10000) # reference normal line in red.
      lines(x, dnorm(x), col='red')
    }
    dev.off()
    print("saved residual density plot to")
    print(file_name)
  }
  else{
    print(plot(density(scale(res))))
    if (guide=="normal"){
      x <- seq(-4, 4, 1/10000) # reference normal line in red.
      print(lines(x, dnorm(x), col='red'))
    }
  }
}


qq_plot <- function(res, file_name=NULL){
  if (is.null(file_name))
  {
    pdf(file_name)
    dev.off()
    print("saved qq plot to")
    print(file_name)
  }
  else{
    print(qqnorm(res))
    print(qqline(res))    
  }
  
}

fitted_residual_plot <- function(fitted_residuals, file_name=NULL){
  residual_fitted_plot <- ggplot(fitted_residuals, aes(fitted, sqrt_residuals)) +
    geom_point(shape=1) +
    geom_smooth(colour="red") +
    #geom_line(aes(y=rollmean(sqrt_residuals, 10000, na.pad=TRUE)), col='red') +
    theme_bw()
  if (is.null(file_name))
  {
    pdf(file_name)
    print(residual_fitted_plot)
    dev.off()
    print("saved fitted-residual plot to")
    print(file_name)
  }
  print(residual_fitted_plot)
  
}

format_sf12_gee_transition_data <- function(source, years, v){
  
  files <- get_US_file_names(source, years, "_US_cohort.csv")
  print(files)
  columns <- c("pidp",
               "weight",
               "SF_12", 
               "job_sec",
               "education_state",
               "sex",
               "labour_state", 
               #"region", 
               "ethnicity", 
               "age", 
               "time", 
               "hh_income", 
               "housing_quality",
               "loneliness",
               #"yearly_energy",
               #"neighbourhood_safety",
               'financial_situation')
  data <- data.frame()
  for (file in files){
    print(file)
    new_data <- read.csv(file)
    new_data <- new_data[, columns]
    new_data <- replace.missing(new_data)
    data <- rbind(new_data, data)
  }
  data <- drop_na(data)
  return(data)
}

data <- format_sf12_gee_transition_data("data/final_US/", c(2016,2017,2018,2019), "SF_12")
data <- data[order(data$pidp, data$time),]

dep.gee.gamma <- geeglm(I(max(SF_12) - SF_12 + 0.001)  ~ # reflection about maximum makes right skewed non-negative data. also slight addition to make strictly positive values.
                          sex + 
                          ethnicity + 
                          age + 
                          I(age**2) +
                          I(age**3) +
                          #factor(education_state) + 
                          labour_state + 
                          #factor(job_sec) +
                          #region +
                          #scale(hh_income) +
                          #I(scale(hh_income)**2) +
                          #factor(neighbourhood_safety) +
                          #factor(heating) +
                          factor(loneliness) +
                          #yearly_energy +
                          factor(housing_quality) +
                          factor(financial_situation),
                        id = pidp,
                        waves = time,
                        family = Gamma(link='inverse'),
                        data = data,
                        corstr="ar1")

sf12.gee.path <- "data/transitions/SF_12/gee/"
sf12.gee.name <- "sf12_gee.rds"
sf12.gee.filename <- paste(sf12.gee.path, sf12.gee.name)
create.if.not.exists(sf12.gee.path)
saveRDS(dep.gee.gamma, file=sf12.gee.filename)

#r.squaredGLMM(dep.gee.gamma)

#gee.gamma.sum <- summary(dep.gee.gamma)
#print(gee.gamma.sum)
#print(AIC(dep.gee.gamma))
#r.squaredGLMM(dep.gee.gamma)

recent_data <- data[data$time==2019,]
dep.gee.gamma.preds <- predict(dep.gee.gamma, newdata=recent_data, allow.new.levels=T,type='response')
dep.gee.gamma.preds <- max(data$SF_12) - dep.gee.gamma.preds


hist(dep.gee.gamma.preds)
res <- residuals(dep.gee.gamma, type='pearson')
residual_density_plot(res, "plots/residual_density_test.pdf", guide="normal")
qq_plot(res, "plots/qq_plot_test.pdf")

#squareRootRes <- sqrt(abs(scale(resid(dep.gee.gamma, type='pearson'))))
#fitted_residuals <- as.data.frame(cbind(fitted(dep.gee.gamma), squareRootRes))
#colnames(fitted_residuals) <- c("fitted", "sqrt_residuals")
#fitted_residual_plot(fitted_residuals, "plots/fitted_residual_test.pdf")