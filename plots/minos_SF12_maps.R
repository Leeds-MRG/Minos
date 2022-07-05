# This file aims to transpose minos outputs onto Chris' spatially weighted GB data
library(geojsonio)
library(ggplot2)
library(broom)
library(sp)
# grab data 
poly_data <- geojson_read("/Users/robertclay/data/LSOA_with_SF12.geojson"
                           ,what='sp')
# TODO take subset of LSOAs as necessary. E.g. group by those in sheffield or by latlong

yorkshire_lsoas <- read_excel("/Users/robertclay/data/yorkshire_lsoas.xlsx",
                              skip=12, header=F)
yorkshire_lsoas <- data.frame(yorkshire_lsoas)[-c(1:11),c(5,4)]
colnames(yorkshire_lsoas) <- c("ONS", "metro_area")
unique_lsoas <- unique(yorkshire_lsoas$ONS)
yorkshire_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$ONS%in%unique_lsoas),]

sheffield_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$metro_area=="Sheffield"),]

sheff_polys <- subset(poly_data, LSOA11CD %in% sheffield_lsoas$ONS)
sheff_polys_sf<- st_as_sf(sheff_polys)

sheff_polys_tb <- as_tibble(sheff_polys_sf)
#sheff_polys_tb <- tidy(sheff_polys_sf)
print("data cleaned. plotting..")

SF12.map <- ggplot(data = sheff_polys_tb, aes(geometry = geometry, fill=SF_12)) + 
            geom_sf() +
            scale_fill_viridis_c(alpha = .8) 
SF12.map
