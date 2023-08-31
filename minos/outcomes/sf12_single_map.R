library(argparse)
source("minos/outcomes/minos_SF12_maps.R")
  

get_geojson_file_name <- function(mode, intervention, region, year) {
  geojson_file_source <- paste0("output", "/", mode, "/", intervention, "/")
  geojson_file_extension <- paste0(region, "_", "nanmean", "_", "SF_12", "_", year, ".geojson")
  out.files <- list.files(geojson_file_source)
  
  if(length(out.files) == 1) {
    geojson_file_name <- paste0(dirname(geojson_file_source), out.files[1], '/', geojson_file_source)
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
  parser$add_argument("-i", "--intervention", dest='intervention', help="What inteverntion to map. e.g. livingWageIntervention")
  parser$add_argument("-r", "--region", dest='region', help="What spatial region to use. sheffield, manchester, scotland(not yet)")
  parser$add_argument("-y", "--year", dest='yearr', help="What year of MINOS data to map.")
  parser$add_argument("-d", "--destination", dest='destination', help="Where to save to.")
  
  args <- parser$parse_args()
  
  mode <- args$mode
  intervention <- args$intervention
  region <- args$region
  year <- args$year 
  destination_file_name <- args$destination

  #mode <- "default_config"
  #intervention <- "baseline"
  #region <- "manchester"
  #year <- 2025
  #v <- "SF_12"
  
  ## handle runtime subdirectory
  # first select only the path (not filename)
  geojson_file_name <- get_geojson_file_name(mode, intervention, region, year)
  print(geojson_file_name)
  main.single(geojson_file_name, destination_file_name)
}

main()