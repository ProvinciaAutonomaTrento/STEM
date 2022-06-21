##Pre elaborazione=group
##Seleziona_vettore=optional vector
##Seleziona_la_maschera=vector polygon
##Definisci_tipologia_di_ritaglio=selection interno;esterno
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
paste("rgeos",packageVersion("rgeos"))

if(is.null(Seleziona_vettore)==FALSE){
if(Definisci_tipologia_di_ritaglio== 0){
   inside <- intersect(Seleziona_vettore, Seleziona_la_maschera)
   Output_vettore <- inside
} else if(Definisci_tipologia_di_ritaglio== 1){
   diff <- gDifference(Seleziona_vettore, Seleziona_la_maschera)
   outside <- Seleziona_vettore[diff, ]
   Output_vettore <- outside
}
}
