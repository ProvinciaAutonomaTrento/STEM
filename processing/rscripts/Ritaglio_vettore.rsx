##Pre elaborazione=group
##Seleziona_vettore=optional vector
##Seleziona_la_maschera=vector polygon
##Definisci_tipologia_di_ritaglio=selection interno;esterno
##Definisci_EPSG=string
##Output_vettore=output vector
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

if(is.null(Seleziona_vettore)==FALSE){
  Seleziona_la_maschera <- spTransform(Seleziona_la_maschera, crs(Seleziona_vettore))
if(Definisci_tipologia_di_ritaglio== 0){
   inside <- intersect(Seleziona_vettore, Seleziona_la_maschera)
   inside <- spTransform(inside, CRSobj = a_crs_object_epsg)
   Output_vettore <- inside
} else if(Definisci_tipologia_di_ritaglio== 1){
   diff <- gDifference(Seleziona_vettore, Seleziona_la_maschera)
   outside <- Seleziona_vettore[diff, ]
   outside <- spTransform(outside, CRSobj = a_crs_object_epsg)
   Output_vettore <- outside
}
}
