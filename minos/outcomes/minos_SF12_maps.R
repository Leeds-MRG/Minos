# This file aims to transpose minos outputs onto Chris' spatially weighted GB data
#library(geojsonio) # spatial_data in R. not used any more it sucks to install.
#library(geojsonsf)
library(ggplot2) # plots
library(broom) # spatial data manipulation
library(sp) # ^
#library(sf) # ^ Also sucks to install. no longer used for geojsonio. 
library(tibble) # converting spatial objects to data frames.
# library(ggrepel) # for geom_text_repel labels
library(argparse) # for argument parsing from bash shell.
library(geojsonio) # lightweight geojson loader.

get_latest_file <-function(path){
  # find last file lexicographically in a given path.
  # This will find the latest chronologically MINOS run output in this path. 
  files = Sys.glob(path)
  files = sort(files)
  file = tail(files,1)[1]
  return(file)
}


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

minos_map <- function(data, destination_file, do_save=T){
  # plot map of minos results from a geojson data.  
  browser()
  minos.map <- ggplot(data = data, aes(geometry = geometry, fill=SF_12)) + 
    #geom_sf() + # black outlines on borders for clarity.
    geom_sf(color=NA) + # black outlines on borders for clarity.
    scale_fill_viridis_c(alpha = 1.0, direction=-1) + # use viridis colour scale and reverse it  so brighter is better.
    labs(fill='SF12 Score')  + # colour bar label. 
    theme(aspect.ratio=9/16) + # change plot to widescreen dimensions. 
    xlab("Longitude") + # axis labels
    ylab("Latitude")
  
  if(do_save){
    pdf(destination_file) # need to do this or R won't save pdf from variable.
    print(minos.map) # note need to print maps when running R scripts outside of console or they're blank.
    dev.off()
    print("Saved to:")
    print(destination_file)
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

minos_diff_map <- function(data, destination_file_name, do_save=T){
  # similar to minos map above but compares results from two interventions.
  # uses a different purple-orange colour scale centered about 0 to better 
  # show off positive/negative values.
  c.min <- min(data$diff) # calculate range of data for colour maps and scale.
  c.max <- max(data$diff)
  scale_limit <- max(abs(c.min), abs(c.max)) 
  diff.map <- ggplot(data = data, aes(geometry = geometry, fill=diff)) + 
    #geom_polygon() +
    geom_sf(color='black', lwd=0.01) + # add black borders to lsoas for clarity
    # Add split colour scheme.
    scale_fill_viridis_c(alpha = 1.0, direction=-1) + # use viridis colour scale and reverse it  so brighter is better.
    #scale_fill_distiller(palette = "PuOr", limits=c(-scale_limit, scale_limit), direction=-1) + 
    labs(fill='Absolute Difference')  + # label colour bar
    theme(aspect.ratio=9/16) +
    #ggtitle("Difference in SF12 spatial distribution for minos vs real US data in Sheffield.") +
    xlab("Longitude") + # axis labels
    ylab("Latitude")

  if(do_save == T){
    pdf(destination_file_name)
    print(diff.map)
    dev.off()
    print("saved to: ")
    print(destination_file_name)
  }
  else {
    print(diff.map)
  }
}



# map of locally or nationally scaled multiple deprevation index (MDI) useful comparison with SF_12 due to high correlation >0.8. 
imd_map <- function(){
  lsoas <- read.csv("persistent_data/spatial_data/glasgow_data_zones.csv")
  
  mdi_data <- st_as_sf(geojson_sf('/Users/robertclay/minos/persistent_data/spatial_data/SG_DataZone_Bdry_2011.json'))
  mdi_data <- as_tibble(mdi_data)
  mdi_data <- mdi_data[, c("DataZone", "geometry")]
  mdi_data <- subset(mdi_data, DataZone %in% lsoas$lsoa11cd)
  
  imd_ranks <- read.csv("persistent_data/spatial_data/scotland_simd_to_data_zones.csv")
  imd_ranks <- subset(imd_ranks, DZ %in% lsoas$lsoa11cd)
  imd_ranks <- imd_ranks[, c("DZ", "SIMD2020v2_Rank")]
  colnames(imd_ranks) <- c("DataZone", "IMDRank")
  
  mdi_data <- merge(mdi_data, imd_ranks, by=c("DataZone"))
  mdi_data$local_rank <- rank(mdi_data$IMDRank)
  
  mdi.map <- ggplot(data = mdi_data, aes(geometry = geometry, fill=local_rank)) + 
    #geom_sf(color='black', lwd=0.00001) +
    scale_fill_viridis_c(alpha = 1.0, direction=-1) +
    labs(fill='SIMD Rank')  +
    theme(aspect.ratio=9/16) +
    #ggtitle("Multiple Deprivation Index Ranks for Sheffield") +
    xlab("Longitude") +
    ylab("Latitude")
  pdf('plots/glasgow_simd_map.pdf')
  print(mdi.map)
  dev.off()
}

#imd_map()

geojson_to_tibble <- function(data) {
  data <- st_as_sf(data)
  data_tibble <-  as_tibble(data)
  return (data_tibble)
}

main.single <- function(geojson_file_name, destination_file_name){
  # Not doing subsetting anymore. just generate geojsons at desired spatial level beforehand. 
  # load data. subset it. plot as map.
  #lsoa_subset_function <- choose_lsoa_function(mode)
  data <- geojson_read(geojson_file_name, what='sp')
  #data <- load_geojson(geojson_file_name)
  data <- geojson_to_tibble(data)
  #data <- subset_geojson(data, lsoa_subset_function)
  #data[which(data$SF_12 %in% head(sort(data$SF_12), 10)),] # ten worst performing areas by SF12.
  minos_map(data, destination_file_name)
}

main.diff <- function(geojson_file1, geojson_file2, destination_file_name){
  # load 2 data sets. subset. find difference in v. plot difference as map. 
  #lsoa_subset_function <- choose_lsoa_function(mode)

  data1 <- geojson_read(geojson_file1, what='sp')
  data2 <- geojson_read(geojson_file2, what='sp')
  data1 <- geojson_to_tibble(data1)
  data2 <- geojson_to_tibble(data2)

  #data1 <- load_geojson(geojson_file1)
  #data2 <- load_geojson(geojson_file2)
  #data1 <- subset_geojson(data1, lsoa_subset_function)
  #data2 <- subset_geojson(data2, lsoa_subset_function)
  #data1 <- geojson_to_tibble(data1)
  #data2 <- geojson_to_tibble(data2)
  
  data1 <- calculate_diff(data1, data2, "SF_12")
  minos_diff_map(data1, destination_file_name)
  
  # imd_ranks <- read.csv("persistent_data/spatial_data/scotland_simd_to_data_zones.csv")
  # imd_ranks <- subset(imd_ranks, DZ %in% data1$ZoneID)
  # imd_ranks <- imd_ranks[, c("DZ", "SIMD2020v2_Rank")]
  # colnames(imd_ranks) <- c("ZoneID", "IMDRank")
  # imd_ranks$local_IMD_Ranks <- rank(imd_ranks$IMDRank)
  # 
  # data1 <- merge(data1, imd_ranks, by=(c("ZoneID")))
  # data1$local_sf12_ranks <- rank(data1$SF_12)
  # print(corr(data1$local_sf12_ranks, data1$local_IMD_ranks))
}