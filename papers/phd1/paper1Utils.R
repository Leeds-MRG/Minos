source("papers/phd1/utils.R")

format_baseline_data <- function(source, years){
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
  #columns <- c("pidp", "SF_12", "job_sec","education_state", "sex",
  #             "depression_change", "depression", "labour_state",
  #             "region", "ethnicity", "age", "time", "gross_hh_income")
  columns <- c("pidp", "SF_12", "job_sec","education_state", "sex",
               "labour_state", "region", "ethnicity", "age", 
               "time", "gross_hh_income")
  
  data <- data[, columns]
  for(co in columns){
    i <- which(data[,co]%in%missing)
    data[,co] <- replace(data[,co], i, NA)
  }
  
  return(data)  
}



format_transition_data <- function(source, years, v){
  main_data <- c()
  for (year in years){
  print(year)
  print(year+1)
  data_source<- source
  data_files <- get_US_files(data_source, year, year+1)
  data <- data_files$data1
  data2 <- data_files$data2
  columns <- c( "pidp",
                "time",
                  "sex",
                  "ethnicity", 
                  "age",
                  "education_state",
                  "labour_state",
                  "job_sec",
                  "region",
                  "gross_hh_income",
                  "SF_12")
  
  data <- data[, columns]
  data2 <- data2[, columns]
  
  data <- replace.missing(data)
  data2 <- replace.missing(data2)
  

  # only look at individuals with data in both waves.
  common <- intersect(data$pidp, data2$pidp)
  data <- data[which(data$pidp %in% common), ]
  data2 <- data2[which(data2$pidp %in% common), ]
  
  data2 <- data2[, c("pidp", v)]
  colnames(data2) <- c("pidp", "y")
  data <- merge(data, data2,"pidp")
  main_data <- rbind(main_data, data)
  }
  return(main_data)
}

get_US_files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1, "_US_cohort.csv")
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2, "_US_cohort.csv")
  data2 <- get_US_data(file_name2)
  data_files <- list("data1" = data, "data2" = data2)
  return(data_files)
}


get_US_data <- function(file_names){
  first_time <- T
  for(file in file_names){
    new_data <- read.csv(file)
    if (first_time==T){
      first_time <- F
      data <- new_data
    }
    else{
      data<- rbind(data, new_data)
    }
  }
  return(data)
}

get_US_file_names <- function(source, years, extension){
  file_names = c()
  for(year in years){
    # loop over years and load in files.
    file_name <- concat(source, str(year))
    file_name <- paste0(concat(file_name, extension))
    file_names <- append(file_names, file_name)
  }
  return(file_names)
}

missing.str <- c("-1", "-2", "-7", "-8", "-9")
missing.int <- c(-1, -2, -7, -8, -9)
missing.float <- c(-1., -2., -7., -8., -9.)
replace.missing <- function(data){
  data <- lapply(data, function(x) replace(x, x %in% missing.str, NA))
  data <- lapply(data, function(x) replace(x, x %in% missing.int, NA))
  data <- lapply(data, function(x) replace(x, x %in% missing.float, NA))
  return(as.data.frame(data))
}


compare_densities_plot <- function(preds, real, v){
  preds <- as.data.frame(preds)
  real <- as.data.frame(real)
  preds$type <- c("Predicted")
  real$type <- c("Real")
  colnames(preds) <- c(v, 'type')
  colnames(real) <- c(v, 'type')
  hist.data <- rbind(preds,real)
  v <- ensym(v)
  # !! notation allows for general argument v. see aes_string deprecation note.
  ols.densities <- ggplot(hist.data) +
    geom_density_pattern(aes(x=!!v, pattern_fill = as.factor(type), pattern_type = as.factor(type)),
                         alpha=0.1,
                         pattern = 'polygon_tiling',
                         pattern_key_scale_factor = 1.2,
                         pattern_alpha=0.4)+        
    scale_pattern_type_manual(values = c("hexagonal", "rhombille"))+
    theme_bw(18) +
    theme(legend.key.size = unit(1.5, 'cm'))
  return(ols.densities)
}

