##Pre elaborazione=group
##Seleziona_raster=optional raster
##Seleziona_la_maschera=vector polygon
##Definisci_tipologia_di_ritaglio=selection interno;esterno
##Definisci_EPSG=string
##Definisci_valori_NA=number
##Output_raster=output file
##load_vector_using_rgdal is specified

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

library(sp)
library(raster)
library(rgdal)
library(rgeos)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))
paste("rgeos:", packageVersion("rgeos"))

proj <- "+init=epsg:"
proj_EPSG <- paste(proj, Definisci_EPSG, sep="")
a_crs_object_epsg <- crs(proj_EPSG)

if(is.null(Seleziona_raster)==FALSE){
  Seleziona_la_maschera <- spTransform(Seleziona_la_maschera, crs(Seleziona_raster))
  if(Definisci_tipologia_di_ritaglio== 0){
    inside <- mask(crop(Seleziona_raster, Seleziona_la_maschera), Seleziona_la_maschera)
    inside <- projectRaster(inside, crs = a_crs_object_epsg)
    ritaglio <- inside
  } else {
    outside <- mask(Seleziona_raster, Seleziona_la_maschera, inverse = TRUE)
    outside <- projectRaster(outside, crs = a_crs_object_epsg)
    ritaglio <- outside
  }
}

writeRaster(ritaglio, filename = Output_raster, overwrite = TRUE, NAflag = Definisci_valori_NA)