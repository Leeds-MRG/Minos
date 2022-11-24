# This file aims to transpose minos outputs onto Chris' spatially weighted GB data
#library(geojsonio) # geojsons in R. not used any more it sucks to install.
library(geojsonsf)
library(ggplot2) # plots
library(broom) # spatial data manipulation
library(sp) # ^
library(sf) # ^ Also sucks to install. 
library(tibble) # ^
# library(ggrepel) # for geom_text_repel labels
library(argparse) # for argument parsing from bash shell.

load_geojson <- function(geojson_file_name){
  # Load geojson object
  #data2 <- geojson_read(geojson_file_name, what='sp')
  #data <- FROM_GeoJson(url_file_string = geojson_file_name)
  data <- geojson_sf(geojson_file_name)
  return(data)
}

subset_geojson <- function(data, subset_function){
  # Subset national MINOS geoJSON output by some subset function.
  # For now this just takes LSOAs in certain areas (Sheff,Manc,Scot) 
  # Also converts geojson to a tibble dataframe that ggplot can use.
  data <- subset_function(data)
  data <- st_as_sf(data)
  data_tibble <-  as_tibble(data)
  return(data_tibble)
}

sheffield_lsoa_subset_function <- function(data){
  lsoas <- read.csv("persistent_data/sheffield_lsoas.csv")
  lsoas <- lsoas$x # just take needed lsoa column
  return(subset(data, ZoneID %in% lsoas))
}

manchestser_lsoa_subset_function <- function(data){
  lsoas <- read.csv("persistent_data/manchester_lsoas.csv")
  lsoas <- lsoas$x # just take needed lsoa column.
  return(subset(data, ZoneID %in% lsoas))
}

scotland_data_zone_subset_function <- function(data){
  datazones <- read.csv("persistent_data/scotland_data_zones.csv")
  datazones <- datazones$DZ2011_Code
  return(subset(data, ZoneID %in% datazones))
}

glasgow_data_zone_subset_function <- function(data){
  datazones <- read.csv("persistent_data/glasgow_data_zones.csv")
  datazones <- datazones$lsoa11cd
  return(subset(data, ZoneID %in% datazones))
}
choose_lsoa_function <- function(mode){
  
  if (mode == "sheffield"){
    subset_function <- sheffield_lsoa_subset_function
  }
  else if (mode == "manchester"){
    subset_function <- manchestser_lsoa_subset_function
  }
  else if (mode == "scotland"){
    subset_function <- scotland_data_zone_subset_function
  }
  else if (mode == "glasgow"){
    subset_function <- glasgow_data_zone_subset_function
  }
  else {
    print("Warning no subset specified. Defaulting to Sheffield..")
    subset_function <- sheffield_lsoa_subset_function
  }
  return(subset_function)
}

calculate_diff <-function(data1, data2, v){
  # for two data frames with some shared column v.
  # add data1$v - data2$v to data1 as diff.
  data1$diff <- data1[[v]] - data2[[v]]
  return(data1)
}

minos_map <- function(data, v, destination_name, do_save=T){
  # plot map of minos results from a geojson data.  
  
  minos.map <- ggplot(data = data, aes_string(geometry = "geometry", fill=v)) + 
    #geom_sf() + # black outlines on borders for clarity.
    geom_sf(color=NA) + # black outlines on borders for clarity.
    scale_fill_viridis_c(alpha = 1.0, direction=-1) + # use viridis colour scale and reverse it  so brighter is better.
    labs(fill='SF12 Score')  + # colour bar label. 
    theme(aspect.ratio=9/16) + # change plot to widescreen dimensions. 
    xlab("Longitude") + # axis labels
    ylab("Latitude")
  
  if(do_save){
    pdf(paste0(destination_name, '.pdf')) # need to do this or R won't save pdf from variable.
    print(minos.map) # note need to print maps when running R scripts outside of console or they're blank.
    dev.off()
  }
  else {
    print(minos.map)
  }
  
  # SCRAP THAT MAY BE USEFUL
  # Adds labels at geojson shape centroids if specified.
  # E.g. adding names of sheffield political wards makes more/less inclusive
  # areas more identifiable.
  #
  #geom_text_repel(data=sheff_wards, aes(geometry=geometry, label=WD13NM)
  #                 , stat='sf_coordinates', inherit.aes = F, min.segment.length = 0,
  #                bg.color='white',alpha=0.3) +
  # # Highlight worst n performing LSOAs
  # geom_sf(colour = data$worst_highlighted_col, lwd=data$worst_highlighted) +
  #
  # TITLE
  # ggtitle("SF12 Difference") +
}

minos_diff_map <- function(data, destination_name, do_save=T){
  # similar to minos map above but compares results from two interventions.
  # uses a different purple-orange colour scale centered about 0 to better 
  # show off positive/negative values.
  c.min <- min(data$diff) # calculate range of data for colour maps and scale.
  c.max <- max(data$diff)
  c <- max(abs(c.min), abs(c.max)) 
  diff.map <- ggplot(data = data, aes_string(geometry = "geometry", fill="diff")) + 
    geom_sf() + # add black borders to lsoas for clarity
    # Add split colour scheme.
    scale_fill_distiller(palette = "PuOr", limits=c(-c, c), direction=-1) + 
    labs(fill='Absolute Difference')  + # label colour bar
    theme(aspect.ratio=9/16) +
    ggtitle("Difference in SF12 spatial distribution for minos vs real US data in Sheffield.") +
    xlab("Longitude") + # axis labels
    ylab("Latitude")

  if(do_save == T){
    pdf(paste0(destination_name, '.pdf'))
    print(diff.map)
    dev.off()
  }
  else {
    print(diff.map)
  }
}

main.single <- function(geojson_file_name, plot_destination_file, mode, v){
  # load data. subset it. plot as map.
  lsoa_subset_function <- choose_lsoa_function(mode)
  data <- load_geojson(geojson_file_name)
  data <- subset_geojson(data, lsoa_subset_function)
  #data[which(data$SF_12 %in% head(sort(data$SF_12), 10)),] # ten worst performing areas by SF12.
  minos_map(data, v, plot_destination_file)
}

main.diff <- function(geojson_file1, geojson_file2, plot_destination_file, mode, v){
  # load 2 data sets. subset. find difference in v. plot difference as map. 
  lsoa_subset_function <- choose_lsoa_function(mode)
  data1 <- load_geojson(geojson_file1)
  data2 <- load_geojson(geojson_file2)
  data1 <- subset_geojson(data1, lsoa_subset_function)
  data2 <- subset_geojson(data2, lsoa_subset_function)
  data1 <- calculate_diff(data1, data2, v)
  minos_diff_map(data1, plot_destination_file)
}

#main.single("output/baseline/nanmean_SF_12_2018.geojson", "output/baseline/scotland_sf12_map", "scotland", "SF_12")

###########################
# Deprecated Stuff. Ignore.
###########################

# old main. replaced with better ones that can be run in shell with argparse.
#main <- function(real_data_file, minos_data_file, diff, f_name){
#  #real_data_file <- "/Users/robertclay/minos/output/baseline/2016.geojson"
#  #minos_data_file <- "/Users/robertclay/data/SF12_LSOAS_0.0_75.0_2016.geojson"
#  #real_data_file <- "/Users/robertclay/data/SF12_LSOAS_10000.0_75.0_2016.geojson"
#  
#  #minos_data_file <- "output/ex1/0.0_25.0_2016.geojson"
#  #real_data_file <- "output/ex1/0.0_50.0_2016.geojson"
#  
#  #minos_data_file <- "/Users/robertclay/minos/output/povertyUplift/2016.geojson"
#  #real_data_file <-  "/Users/robertclay/data/real_LSOA_with_SF12_2016.geojson"
#  real_data <- format_geojson(real_data_file, sheffield_subset_function)
#  
#  minos_data <- format_geojson(minos_data_file, sheffield_subset_function)
#  minos_data <- calculate_diff(minos_data, real_data)
#  # find 5 worst performing lsoas and highlight them red. 
#  five_worst <- head(sort(minos_data$SF_12), 5)
#  minos_data$worst_highlighted <- minos_data$SF_12%in%five_worst
#  minos_data$worst_highlighted_col <- minos_data$SF_12%in%five_worst
#  minos_data$worst_highlighted_col[which(minos_data$worst_highlighted==F)] <- 'black'
#  minos_data$worst_highlighted_col[which(minos_data$worst_highlighted==T)] <- 'red'
#  minos_data$worst_highlighted <- minos_data$worst_highlighted + 0.1
#  
#  if (diff){
#    sf12_diff_map(minos_data, f_name)
#  } else{
#    sf12_map(minos_data, f_name)
#  }
#  }

# finding largest discrepancies between estimated and real SF12. 
#five_largest <- tail(sort(sheff_polys_minos_tb$SF12_diff), 5)
#five_largest_lsoas <- sheff_polys_minos_tb[which(sheff_polys_minos_tb$SF12_diff%in%five_largest),]
# most over estimated areas.
# broomhill student area, greystones posh, northern general hospital ,woodhouse badger estate very uninclusive, direct city centre. 
# all seem to be volatile places. Many possible reasons why this is. 

#run_all <- function(){
#  # use main multiple times with different source data.
#
#  # load political wards of sheffield for name labels.
#  sheff_wards <- st_as_sf(geojson_read('/Users/robertclay/data/sheffield_wards.geojson', what='sp'))
#  sheff_wards <- as_tibble(st_centroid(sheff_wards, byid=T))
#  
#  real_data <- "/Users/robertclay/data/real_LSOA_with_SF12_2016.geojson"
#  baseline_data <- "/Users/robertclay/minos/output/baseline/2016.geojson"
#  poverty_data <- "/Users/robertclay/minos/output/povertyUplift/2016.geojson"
#  all_data <- "/Users/robertclay/minos/output/childUplift/2016.geojson"
#  twentyfive_data <- "/Users/robertclay/minos/output/twentyFivePovertyUplift/2016.geojson"
#  living_wage_data <- "/Users/robertclay/minos/output/childUplift/2016.geojson"
#  
#  main(real_data, baseline_data, F, 'plots/SF12_map')
#
#}


# map of locally or nationally scaled multiple deprevation index (MDI) useful comparison with SF_12 due to high correlation >0.8. 
#mdi_map <- function(){
#  mdi_data <- st_as_sf(geojson_read('/Users/robertclay/data/Lower_Super_Output_Area_(LSOA)_IMD_2019__(OSGB1936).geojson', what='sp'))
#  mdi_data <- as_tibble(mdi_data)
#  yorkshire_lsoas <- read_excel("/Users/robertclay/data/yorkshire_lsoas.xlsx",
#                                skip=11)
#  yorkshire_lsoas <- data.frame(yorkshire_lsoas)[-c(1:11),c(5,4)]
#  colnames(yorkshire_lsoas) <- c("ONS", "metro_area")
#  unique_lsoas <- unique(yorkshire_lsoas$ONS)
#  yorkshire_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$ONS%in%unique_lsoas),]
#  sheffield_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$metro_area=="Sheffield"),]
#  mdi_data <- subset(mdi_data, lsoa11cd %in% sheffield_lsoas$ONS)
#  mdi_data$local_rank <- rank(mdi_data$IMDRank)
#  SF12.map <- ggplot(data = mdi_data, aes(geometry = geometry, fill=IMDRank)) + 
#    geom_sf() +
#    scale_fill_viridis_c(alpha = 1.0, direction=-1) +
#    labs(fill='MDI Rank')  +
#    theme(aspect.ratio=9/16) +
#    #ggtitle("Multiple Deprivation Index Ranks for Sheffield") +
#    xlab("Longitude") +
#    ylab("Latitude")
#  pdf('plots/mdi_map.pdf')
#  SF12.map
#  dev.off()
#}

