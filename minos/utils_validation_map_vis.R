library(ggplot2) # plots
library(broom) # spatial data manipulation
library(sp) # ^
library(sf) # ^ Also sucks to install. no longer used for geojsonio.
library(tibble) # converting spatial objects to data frames.
# library(ggrepel) # for geom_text_repel labels
library(here)

source(here::here("minos", "outcomes", "minos_SF12_maps.R"))

get_geojson_data <- function(file){
  return(st_read(file))
}

get_subsetted_lsoa_geojson_data <- function(region) {
  lsoa_geojson_data <- get_geojson_data(here::here("persistent_data", "spatial_data", "UK_super_outputs.geojson"))
  lsoa_geojson_data <- subset_geojson(lsoa_geojson_data, choose_lsoa_function(region))
  return(lsoa_geojson_data)
}

get_subsetted_la_geojson_data <- function(region) {
  la_geojson_data <- get_geojson_data(here::here("persistent_data", "spatial_data", "UK_LADs.geojson"))
  la_geojson_data <- subset_geojson(la_geojson_data, choose_la_function(region))
  return(la_geojson_data)
}


map_la_and_lsoa_level_variable <- function(data, v){
  test.synth.data <- scotland_synth_data %>%
    group_by(ZoneID) %>%
    summarise(lsoa_mean = mean(!!sym(v)))
  
  test.lsoa<- merge(test.synth.data, lsoas, by= "ZoneID")
  minos_map(test.lsoa, "test_lsoa", "lsoa_mean", do_save=F)
  
  test.la <- test.lsoa
  test.la$geometry <- NULL
  
  test.la <- test.la %>%
    group_by(LAName) %>%
    summarise(LA_mean = mean(lsoa_mean))
  
  test.la <- merge(test.la, las, by.x = "LAName", by.y = "LAD21NM")
  minos_map(test.la, "test_la", "LA_mean", do_save=F)
}
