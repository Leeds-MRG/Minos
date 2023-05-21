library(argparse)
source("minos/outcomes/minos_SF12_maps.R")


get_geojson_file_name <- function(mode, intervention, region, year) {
  geojson_file_source <- paste0("output", "/", mode, "/", intervention, "/")
  geojson_file_extension <- paste0(region, "_", "nanmean", "_", "SF_12", "_", year, ".geojson")
  out.files <- list.files(geojson_file_source)
  
  if(length(out.files) == 1) {
    geojson_file_name <- paste0(geojson_file_source, out.files[1], '/', geojson_file_extension)
  }
  else if(length(out.files) > 1) {
    out.files.date <- as.POSIXlt(out.files, format='%Y_%m_%d_%H_%M_%S')
    max.date <- max(out.files.date)
    
    # Collecting these objects here as they have to be formatted
    yr <- max.date$year + 1900 # year is years since 1900
    month <- formatC(max.date$mon + 1, width=2, flag='0') # months are zero indexed (WHY??)
    day <- formatC(max.date$mday, width=2, flag='0')
    hour <- formatC(max.date$hour, width=2, flag='0')
    min <- formatC(max.date$min, width=2, flag='0')
    sec <- formatC(max.date$sec, width=2, flag='0')
    # generate the string runtime directory so we can add to the path
    str.date <- paste0(yr, '_',
                       month, '_',
                       day, '_',
                       hour, '_',
                       min, '_',
                       sec)
    geojson_file_name <- paste0(geojson_file_source, str.date, '/', geojson_file_extension)
  }
  return (geojson_file_name)
}

main <- function(){

  parser <- ArgumentParser(description="Plot a map of some MINOS geojson.")
  parser$add_argument("-m", "--mode", dest='mode', help="What source to use. e.g. defualt_config")
  parser$add_argument("-i", "--int", dest='intervention', help="What inteverntion to map. usually baseline. ")
  parser$add_argument("-j", "--int2", dest='second_intervention', help="What inteverntion to compare against. e.g. livingWageIntervention")
  parser$add_argument("-r", "--region", dest='region', help="What spatial region to use. sheffield, manchester, scotland(not yet)")
  parser$add_argument("-d", "--destination", dest='destination', help="Where to save to.")
  parser$add_argument("-y", "--year", dest='year', help="What year of MINOS data to map.")


  args <- parser$parse_args()

  mode <- args$mode
  intervention1 <- args$intervention
  intervention2 <- args$second_intervention
  region <- args$region
  year <- args$year
  destination_file_name <- args$destination
  
  # mode <- "default_config"
  # intervention2 <- "EBSS"
  # intervention1 <- "EPCG"
  # region <- "glasgow"
  # year <- 2025
  # v <- "SF_12"

  geojson_file_name1 <- get_geojson_file_name(mode, intervention1, region, year)
  geojson_file_name2 <- get_geojson_file_name(mode, intervention2, region, year)
  print(geojson_file_name1)
  print(geojson_file_name2)
  main.diff(geojson_file_name1, geojson_file_name2, destination_file_name)
}

main()
#main.diff("output/baseline/nanmean_SF_12_2018.geojson", 
#          "output/povertyUplift/nanmean_SF_12_2018.geojson",
#          "output/baseline/sf12_baseline_povertyUplift_diff_map.pdf", 
#          "sheffield", 
#          "SF_12")