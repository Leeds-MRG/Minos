# This file aims to transpose minos outputs onto Chris' spatially weighted GB data
library(geojsonio)
library(ggplot2)
library(broom)
library(sp)
library(readxl)
library(sf)
library(tibble)
library(ggrepel) # for geom_text_repel

format_geojson <- function(f_name, subset_function){
  data <- geojson_read(f_name, what='sp')
  data <- subset_function(data)
  data <- st_as_sf(data)
  data_tibble <-  as_tibble(data)
  return(data_tibble)
}

sheffield_subset_function <- function(data){
  yorkshire_lsoas <- read_excel("/Users/robertclay/data/yorkshire_lsoas.xlsx",
                                skip=11)
  yorkshire_lsoas <- data.frame(yorkshire_lsoas)[-c(1:11),c(5,4)]
  colnames(yorkshire_lsoas) <- c("ONS", "metro_area")
  unique_lsoas <- unique(yorkshire_lsoas$ONS)
  yorkshire_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$ONS%in%unique_lsoas),]
  sheffield_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$metro_area=="Sheffield"),]
  return(subset(data, LSOA11CD %in% sheffield_lsoas$ONS))
}

calculate_diff <-function(d1, d2){
  d1$SF12_diff <- d1$SF_12 - d2$SF_12
  return(d1)
}

sf12_map <- function(data, f_name){
  plot = T
  c.min <- min(data$SF12_diff)
  c.max <- max(data$SF12_diff)
  
  SF12.map <- ggplot(data = data, aes(geometry = geometry, fill=SF_12)) + 
    geom_sf() +
    #geom_sf(colour = data$worst_highlighted_col, lwd=data$worst_highlighted) +
    scale_fill_viridis_c(alpha = 1.0, direction=-1) +
    # if you want political ward names by area..
    geom_text_repel(data=sheff_wards, aes(geometry=geometry, label=WD13NM)
                     , stat='sf_coordinates', inherit.aes = F, min.segment.length = 0,
                    bg.color='white',alpha=0.3) +
    # Symmetric colourmap to highlight positive/negative values. 
    # Has limited colour schemes relative to matplotlib. Purple orange (puor) seems
    # like best avaiable. 
    #scale_fill_distiller(palette = "PuOr", limits=c(-c.max,c.max)) + 
    #scale_fill_stepsn(colors=c('#0000FF','#FFFFFF','#ff0000'), 
    #                  n.breaks=20, limits=c(-c.max, c.max),) + 
    labs(fill='SF12 Score')  +
    theme(aspect.ratio=9/16) +
    #ggtitle("SF12 Di") +
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

sf12_diff_map <- function(data, f_name){
  plot = T
  c.min <- min(data$SF12_diff)
  c.max <- max(data$SF12_diff)
  c <- max(abs(c.min), abs(c.max))
  SF12.map <- ggplot(data = data, aes(geometry = geometry,fill=SF12_diff)) + 
    geom_sf() +
    #scale_fill_viridis_c(alpha = .8) + 
    # Symmetric colourmap to highlight positive/negative values. 
    # Has limited colour schemes relative to matplotlib. Purple orange (puor) seems
    # like best avaiable. 
    scale_fill_distiller(palette = "PuOr", limits=c(-c, c), direction=-1) + 
    #scale_fill_stepsn(colors=c('#0000FF','#FFFFFF','#ff0000'), 
    #                  n.breaks=20, limits=c(-c.max, c.max),) + 
    labs(fill='SF12 Score')  +
    theme(aspect.ratio=9/16) +
    ggtitle("Difference in SF12 spatial distribution for minos vs real US data in Sheffield.") +
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

main <- function(real_data_file, minos_data_file, diff, f_name){
  #real_data_file <- "/Users/robertclay/minos/output/baseline/2016.geojson"
  #minos_data_file <- "/Users/robertclay/data/SF12_LSOAS_0.0_75.0_2016.geojson"
  #real_data_file <- "/Users/robertclay/data/SF12_LSOAS_10000.0_75.0_2016.geojson"
  
  #minos_data_file <- "output/ex1/0.0_25.0_2016.geojson"
  #real_data_file <- "output/ex1/0.0_50.0_2016.geojson"
  
  #real_data_file <-  "/Users/robertclay/data/real_LSOA_with_SF12_2016.geojson"
  #minos_data_file <- "/Users/robertclay/minos/output/povertyUplift/2016.geojson"
  real_data <- format_geojson(real_data_file, sheffield_subset_function)
  
  minos_data <- format_geojson(minos_data_file, sheffield_subset_function)
  minos_data <- calculate_diff(minos_data, real_data)
  five_worst <- head(sort(minos_data$SF_12), 5)
  minos_data$worst_highlighted <- minos_data$SF_12%in%five_worst
  minos_data$worst_highlighted_col <- minos_data$SF_12%in%five_worst
  minos_data$worst_highlighted_col[which(minos_data$worst_highlighted==F)] <- 'black'
  minos_data$worst_highlighted_col[which(minos_data$worst_highlighted==T)] <- 'red'
  minos_data$worst_highlighted <- minos_data$worst_highlighted + 0.1
  
  if (diff){
    sf12_diff_map(minos_data, f_name)
  } else{
    sf12_map(minos_data, f_name)
  }
  }

#five_largest <- tail(sort(sheff_polys_minos_tb$SF12_diff), 5)
#five_largest_lsoas <- sheff_polys_minos_tb[which(sheff_polys_minos_tb$SF12_diff%in%five_largest),]
# most over estimated areas.
# broomhill student area, greystones posh, northern general hospital ,woodhouse badger estate rough, direct city centre. 

sheff_wards <- st_as_sf(geojson_read('/Users/robertclay/data/sheffield_wards.geojson', what='sp'))
sheff_wards <- as_tibble(st_centroid(sheff_wards, byid=T))

real_data <- "/Users/robertclay/data/real_LSOA_with_SF12_2016.geojson"
baseline_data <- "/Users/robertclay/minos/output/baseline/2016.geojson"
poverty_data <- "/Users/robertclay/minos/output/povertyUplift/2016.geojson"
all_data <- "/Users/robertclay/minos/output/childUplift/2016.geojson"
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2014.geojson"

#main(real_data, baseline_data, F, 'plots/SF12_map.pdf')
#main(baseline_data, poverty_data, T, 'plots/povertyUpliftmap.pdf')
#main(baseline_data, all_data, T, 'plots/allUpliftmap.pdf')

energy_data <- "/Users/robertclay/minos/output/energyDownlift/2010.geojson"
main(baseline_data, energy_data, T, 'plots/2010energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2011.geojson"
main(baseline_data, energy_data, T, 'plots/2011energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2012.geojson"
main(baseline_data, energy_data, T, 'plots/2012energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2013.geojson"
main(baseline_data, energy_data, T, 'plots/2013energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2014.geojson"
main(baseline_data, energy_data, T, 'plots/2014energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2015.geojson"
main(baseline_data, energy_data, T, 'plots/2015energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2016.geojson"
main(baseline_data, energy_data, T, 'plots/2016energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2017.geojson"
main(baseline_data, energy_data, T, 'plots/2017energyDownliftmap')
energy_data <- "/Users/robertclay/minos/output/energyDownlift/2018.geojson"
main(baseline_data, energy_data, T, 'plots/2018energyDownliftmap')


#box <- matrix(c(-1.6, -1.4, 53.35, 53.45),ncol=2, nrow=2, byrow=T)
#q <- opq(bbox = 'sheffield') %>%
#  add_osm_feature(key = 'boundary', value = 'political') %>%
#  osmdata_sf (quiet = FALSE)
##ggmap(get_map(getbb("Sheffield"), maptype='toner-background'))+
#ggmap(get_map(box, maptype='toner-background'))+
#  #geom_sf(data=q$osm_points, inherit.aes = FALSE)+
#  geom_sf_text(data=sheff_wards, label=sheff_wards$WD13NM, inherit.aes = FALSE)


mdi_map <- function(){
  mdi_data <- st_as_sf(geojson_read('/Users/robertclay/data/Lower_Super_Output_Area_(LSOA)_IMD_2019__(OSGB1936).geojson', what='sp'))
  mdi_data <- as_tibble(mdi_data)
  yorkshire_lsoas <- read_excel("/Users/robertclay/data/yorkshire_lsoas.xlsx",
                                skip=11)
  yorkshire_lsoas <- data.frame(yorkshire_lsoas)[-c(1:11),c(5,4)]
  colnames(yorkshire_lsoas) <- c("ONS", "metro_area")
  unique_lsoas <- unique(yorkshire_lsoas$ONS)
  yorkshire_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$ONS%in%unique_lsoas),]
  sheffield_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$metro_area=="Sheffield"),]
  mdi_data <- subset(mdi_data, lsoa11cd %in% sheffield_lsoas$ONS)
  mdi_data$local_rank <- rank(mdi_data$IMDRank)
  SF12.map <- ggplot(data = mdi_data, aes(geometry = geometry, fill=IMDRank)) + 
    geom_sf() +
    scale_fill_viridis_c(alpha = 1.0, direction=-1) +
    labs(fill='MDI Rank')  +
    theme(aspect.ratio=9/16) +
    #ggtitle("Multiple Deprivation Index Ranks for Sheffield") +
    xlab("Longitude") +
    ylab("Latitude")
  pdf('plots/mdi_map.pdf')
  SF12.map
  dev.off()
  }