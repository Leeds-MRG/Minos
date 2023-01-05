library(argparse)
source("minos/validation/minos_SF12_maps.R")

main <- function(){
  
  parser <- ArgumentParser(description="Plot a map of some MINOS geojson.")
  parser$add_argument("-f", "--geojson_file_name", dest='file', help="What geojson to use.")
  parser$add_argument("-d", "--plot_destination", dest='destination', help="Where to save a plot.")
  parser$add_argument("-m", "--mode", dest='mode', help="What spatial region to use. sheffield, manchester, scotland(not yet)")
  parser$add_argument("-v", "--v", dest='var', help="What variable to map.")
  
  args <- parser$parse_args()
  geojson_file_name <- args$file
  plot_destination <- args$destination
  mode <- args$mode
  v <- args$var

  ## handle runtime subdirectory
  # first select only the path (not filename)
  out.files <- list.files(dirname(geojson_file_name))

  if(length(out.files) == 1) {
    geojson_file_name = paste0(dirname(geojson_file_name), '/', out.files[1], '/', basename(geojson_file_name))
  }
  else if(length(out.files) > 1) {
    out.files.date <- as.Date(out.files)
    geojson_file_name <- paste0(dirname(geojson_file_name), '/', str(max(out.files.date)), '/', basename(geojson_file_name))
  }

  print("This is the geojson file name:")
  print(geojson_file_name)
  
  main.single(geojson_file_name, plot_destination, mode, v)
}

main()
#main.single("output/baseline/2016.geojson", "output/baseline/scotland_sf12_map.pdf", "scotland", "SF_12")
