library(ggplot2)

# load in real data and comparison data.
# real data may be individuals or aggregates depending on what is available.
# if aggregates then can only compare means and variances directly using t-tests
# rather than stacked histograms.

c1 <- rgb(56, 180, 251,max = 255, alpha = 90, names = "lt.blue")
c2 <- rgb(255, 91, 0, max = 255, alpha = 70, names = "lt.orange")

get.sf12.data <- function(real_source, minos_source, year){
  real.file.name <- paste0(real_source, year)
  real.file.name <- paste0(real.file.name, "_US_Cohort.csv")
  minos.file.name <- paste0(minos_source, year)
  minos.file.name <- paste0(minos.file.name, ".csv")
  
  d1 <- read.csv(real.file.name)
  d2 <- read.csv(minos.file.name)
  return(list(d1=d1, d2=d2))
}

minos.t.test<- function(d1, d2, var){
  t <- t.test(d1[,c(var)], d2[,c(var)])
  print(t)
  return(t)
}

minos.split.hist <- function(d1, d2, var){
  v1 <- d1[, c(var)]
  v2 <- d2[, c(var)]
  l = min(min(v1), min(v2))
  u = max(max(v1), max(v2))
  
  ax <- base::pretty((l-1):(u+1), n=100) # calculate number of hist bins. geojsonio masks pretty.
  
  hgA <- hist(v1, breaks=ax, plot=F)
  hgA$counts <- hgA$counts/sum(hgA$counts)
  hgB <- hist(v2, breaks=ax, plot=F)
  hgB$counts <- hgB$counts/sum(hgB$counts)
  
  plot(hgA, col=c1, xlab="SF_12", ylab="Density", main="Projected vs Real SF_12 distribution for 2016 UK Population.")
  plot(hgB, col=c2, add = T)
  legend("topleft", c("Actual", "Minos"), fill=c(c1,c2))
}

main <- function(year){
  real_source <- 'data/final_US/'
  minos_source <- 'output/test_output/simulation_data/'
  datasets <- get.sf12.data(real_source, minos_source, year)
  d1 <- datasets$d1
  d2 <- datasets$d2
  minos.t.test(d1, d2, "SF_12")
  minos.split.hist(d1, d2, "SF_12")
}

main(2015)