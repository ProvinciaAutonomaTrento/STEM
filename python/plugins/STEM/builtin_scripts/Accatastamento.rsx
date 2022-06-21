##Pre elaborazione=group
##Elenco_path_raster=string
##Formato_di_output=selection GTiff;ENVI
##Definisci_valori_NA=optional number
##Definisci_EPSG=string
##Definisci_Resolution=number
##Definisci_Metodo=string
##Selezione_bande=optional string
##Percorso_output=output file

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("rgdal")
install.packages("gdalUtils")
install.packages("raster")

library(rgdal)
library(gdalUtils)
library(raster)

print("Versione Packages:")
paste("gdalUtils:", packageVersion("gdalUtils"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))

gdal_setInstallation(verbose = TRUE)
print(getOption("gdalUtils_gdalPath"))

valid_install <- !is.null(getOption("gdalUtils_gdalPath"))


if(Formato_di_output==0){
Formato_di_output <- "GTiff"
} else {
Formato_di_output <- "ENVI"
}

proj <- "EPSG:"
proj_EPSG <- paste(proj, Definisci_EPSG, sep="")

if(is.null(Definisci_valori_NA)== TRUE){
Definisci_valori_NA = -9999
} 


percorsi<- strsplit(Elenco_path_raster, ";")[[1]]
align_raster <- as.list(percorsi)

for(i in 1:length(percorsi)){
    
    print("Leggo percorso")
    print(percorsi[i])
    
 
  #gdalwarp(percorsi[i],dstfile= paste("C:\\temp\\STEM\\",as.character(i),"_TMP.tif"),t_srs='EPSG:25832',output_Raster=TRUE,overwrite=TRUE,verbose=TRUE)
  align_raster[i] <- align_rasters(verbose = TRUE, unaligned = percorsi[i], reference = percorsi[1], output_Raster = TRUE ,projres_only = TRUE, r = Definisci_Metodo, tr = c(Definisci_Resolution,Definisci_Resolution))
 
}

lista <- c(NA)
for(i in 1:length(percorsi)){

  lista[i] <- align_raster[[i]]@file@name
  
}


if(Selezione_bande == ""){
mosaic_rasters(gdalfile = c(lista), dst_dataset = Percorso_output, output_Raster = TRUE, separate = TRUE, force_ot = "Float32", a_nodata = Definisci_valori_NA, of = Formato_di_output, a_srs = proj_EPSG)
} else {
selezione_bande <- strsplit(Selezione_bande, " ")[[1]]
bande <- c(selezione_bande)
mosaic_rasters(gdalfile = c(lista), dst_dataset = Percorso_output, output_Raster = TRUE, separate = TRUE, force_ot = "Float32", a_nodata = Definisci_valori_NA, of = Formato_di_output, b = bande, a_srs = proj_EPSG)
}



