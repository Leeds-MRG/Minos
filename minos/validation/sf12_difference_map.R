library(argparse)
source("minos/validation/minos_SF12_maps.R")

main <- function(){
  if (argparse::detects_python()) {
    
    parser <- ArgumentParser(description="Plot a map of some MINOS geojson.")
    parser$add_argument("-f", "--geojson_file_name1", dest='file1', type="string", help="What geojson to use.")
    parser$add_argument("-g", "--geojson_file_name2", dest='file2', type="string", help="What geojson to use.")
    parser$add_argument("-d", "--plot_destination", dest='destination', type="string", help="Where to save a plot.")
    parser$add_argument("-m", "--mode", type="string", dest='mode', help="What spatial region to use. sheffield, manchester, scotland(not yet)")
    parser$add_argument("-v", "--v", type="string", dest='var', help="What variable to map.")
    
    args <- parser$parse_args()
    geojson_file_name1 <- args$file1
    geojson_file_name2 <- args$file2
    plot_destination <- args$destination
    mode <- args$mode
    v <- args$var
    
  }
  main.diff(geojson_file1, geojson_file2, plot_destination, mode, v)
}

main()
main.diff("output/baseline/2016.geojson", 
          "output/povertyUplift/2016.geojson",
          "output/baseline/sf12_baseline_povertyUplift_diff_map.pdf", 
          "sheffield", 
          "SF_12")