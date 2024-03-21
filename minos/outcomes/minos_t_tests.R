library(ggplot2)

# load in real data and comparison data.
# real data may be individuals or aggregates depending on what is available.
# if aggregates then can only compare means and variances directly using t-tests
# rather than stacked histograms.

c1 <- rgb(56, 180, 251,max = 255, alpha = 90, names = "lt.blue")
c2 <- rgb(255, 91, 0, max = 255, alpha = 70, names = "lt.orange")
c3 <- rgb(80, 200, 120, max = 255, alpha = 70, names = "lt.green")

get.sf12.data <- function(real_source, minos_source, year){
  #real.file.name <- paste0(real_source, 1)
  real.file.name <- paste0(real_source, year)
  real.file.name <- paste0(real.file.name, "_US_Cohort.csv")
  minos.file.name <- paste0(minos_source, '_')
  minos.file.name <- paste0(minos.file.name, year)
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

minos.split.hist2 <- function(d1, d2, var, labels, cols, title){
  v1 <- d1[, c(var)]
  v2 <- d2[, c(var)]

  l = min(min(v1), min(v2))
  u = max(max(v1), max(v2))
  
  ax <- base::pretty((l-1):(u+1), n=100) # calculate number of hist bins. geojsonio masks pretty.
  
  hgA <- hist(v1, breaks=ax, plot=F)
  hgA$counts <- hgA$counts/sum(hgA$counts)
  hgB <- hist(v2, breaks=ax, plot=F)
  hgB$counts <- hgB$counts/sum(hgB$counts)
  
  yupper <- max(max(hgA$counts), max(hgB$counts))
  
  plot(hgA, col=cols[1], xlab="SF_12_MCS", xlim=c(20,80), ylim = c(0, yupper+0.005), ylab="Density", main=title)
  plot(hgB, col=cols[2], add = T)
  legend("topleft", labels, fill=cols)
}

minos.split.hist3 <- function(d1, d2, d3, var, labels, cols, title){
  v1 <- d1[, c(var)]
  v2 <- d2[, c(var)]
  v3 <- d3[, c(var)]
  
  l = min(min(v1), min(v2), min(v3))
  u = max(max(v1), max(v2), max(v3))
  
  ax <- base::pretty((l-1):(u+1), n=100) # calculate number of hist bins. geojsonio masks pretty.
  
  hgA <- hist(v1, breaks=ax, plot=F)
  hgA$counts <- hgA$counts/sum(hgA$counts)
  hgB <- hist(v2, breaks=ax, plot=F)
  hgB$counts <- hgB$counts/sum(hgB$counts)
  hgC <- hist(v3, breaks=ax, plot=F)
  hgC$counts <- hgC$counts/sum(hgC$counts)
  yupper <- max(max(hgA$counts), max(hgB$counts), max(hgC$counts))
  plot(hgA, col=cols[1], xlab="SF_12_MCS", xlim=c(20,80), ylab="Density", ylim = c(0, yupper+0.005), main=title)
  plot(hgB, col=cols[2], add = T)
  plot(hgC, col=cols[3], add = T)
  legend("topleft", labels, fill=cols)
}

test_title <- "Projected vs Real SF_12_MCS distribution for 2016 UK Population."

main <- function(year){
  real_source <- 'data/final_US/'
  minos_source <- 'output/baseline/'
  #datasets <- get.sf12.data(real_source, minos_source, year)
  #d2 <- datasets$d2
  #d1 <- datasets$d1
  d1 <- read.csv('data/final_US/2016_US_Cohort.csv')
  d2 <- read.csv('output/baseline/run_id_0_2016.csv')

  minos.t.test(d1, d2, "SF_12_MCS")
  minos.split.hist2(d1, d2, "SF_12_MCS", c("Real", "Minos"), c(c1, c2), "Minos SF12 Prediction VS Real Data.")
  
  
  minos_baseline<-get.sf12.data(real_source, 'output/baseline', year)$d2
  minos_poverty<-get.sf12.data(real_source, 'output/povertyUplift', year)$d2
  minos_all<-get.sf12.data(real_source, 'output/childUplift', year)$d2
    
  minos.t.test(minos0, minos20, "SF_12_MCS")
  minos.t.test(minos20, minos100, "SF_12_MCS")
  
  minos.split.hist2(minos0, minos20, "SF_12_MCS", c("0", "20"), c(c1, c2), "£0 vs £20 Uplift")
  minos.split.hist2(minos0, minos100, "SF_12_MCS",  c("0", "100"), c(c1, c3), "£0 vs £100 Uplift")
  minos.split.hist3(minos0, minos20, minos100, "SF_12_MCS",  c("0", "20", "100"), c(c1, c2, c3), "All Three Income Strategies")
}

main(2016)