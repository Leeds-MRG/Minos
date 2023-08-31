
source("minos/validation/minos_SF12_maps.R")
library(geojsonio)
library(ggplot2)
library(broom)
library(sp)
library(readxl)
library(sf)
library(tibble)
library(ggrepel) # for geom_text_repel


manchester_subset_function <- function(data){
  gma_lsoas <- read.csv("/Users/robertclay/minos/persistent_data/KNN_LSOA_clusters.csv")$X
  return(subset(data, LSOA11CD %in% gma_lsoas))
}


manc_sf12_diff_map <- function(data, f_name){
  plot = T
  c.min <- min(data$SF12_diff)
  c.max <- max(data$SF12_diff)
  c <- max(abs(c.min), abs(c.max))
  SF12.map <- ggplot(data = data, aes(geometry = geometry,fill=SF12_diff)) + 
    geom_sf(lwd=0.1) +
    #scale_fill_viridis_c(alpha = .8) + 
    # Symmetric colourmap to highlight positive/negative values. 
    # Has limited colour schemes relative to matplotlib. Purple orange (puor) seems
    # like best avaiable. 
    scale_fill_distiller(palette = "PuOr", limits=c(-c, c), direction=-1) + 
    #scale_fill_stepsn(colors=c('#0000FF','#FFFFFF','#ff0000'), 
    #                  n.breaks=20, limits=c(-c.max, c.max),) + 
    labs(fill='SF12 Score')  +
    theme(aspect.ratio=9/16) +
    #ggtitle("Difference in SF12 spatial distribution for minos vs real US data in Sheffield.") +
    xlab("Longitude") +
    ylab("Latitude")
  
  if(plot == T){
    pdf(paste(f_name, '.pdf'))
    print(SF12.map)
    dev.off()
  }else{
    print(SF12.map)
  }
}

main <- function(real_data_file, minos_data_file, f_name){
  real_data <- format_geojson(real_data_file, manchester_subset_function)

  minos_data <- format_geojson(minos_data_file, manchester_subset_function)
  minos_data <- calculate_diff(minos_data, real_data)

  manc_sf12_diff_map(minos_data, f_name)
}

baseline_data <- "/Users/robertclay/minos/output/baseline/2016.geojson"
living_wage_data <- "/Users/robertclay/minos/output/livingWage/2016.geojson"
knn_living_wage_data <- "/Users/robertclay/minos/output/knnClusterLivingWage/2016.geojson"

main(baseline_data, living_wage_data, "plots/LivingWage")
main(baseline_data, knn_living_wage_data, "plots/knnLivingWage")
main(living_wage_data, knn_living_wage_data, "plots/livingWageDiffs")
