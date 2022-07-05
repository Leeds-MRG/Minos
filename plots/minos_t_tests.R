

# load in real data and comparison data.
# real data may be individuals or aggregates depending on what is available.
# if aggregates then can only compare means and variances directly using t-tests
# rather than stacked histograms.

c1 <- rgb(56, 180, 251,max = 255, alpha = 80, names = "lt.blue")
c2 <- rgb(255, 91, 0, max = 255, alpha = 80, names = "lt.orange")

real_UK_data <- read.csv("data/final_US/2016_US_Cohort.csv")
minos_data <- read.csv("output/test_output/simulation_data/5.csv")
real_SF12 <- real_UK_data$SF_12
minos_SF12 <- minos_data$SF_12

t <- t.test(real_SF12, minos_SF12)
print(t)

l = min(min(real_SF12), min(minos_SF12))
u = max(max(real_SF12), max(minos_SF12))

ax <- base::pretty((l-1):(u+1), n=100) # calculate number of hist bins. geojsonio masks pretty.

hgA <- hist(real_SF12, breaks=ax, plot=F)
hgA$counts <- hgA$counts/sum(hgA$counts)
hgB <- hist(minos_SF12, breaks=ax, plot=F)
hgB$counts <- hgB$counts/sum(hgB$counts)

plot(hgA, col=c1, xlab="SF_12", ylab="Density", main="Projected vs Real SF_12 distribution for 2016 UK Population.")
plot(hgB, col=c2, add = T)
legend("topleft", c("Actual", "Minos"), fill=c(c1,c2))