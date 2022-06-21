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

install.packages("gdalUtils")
install.packages("raster")
install.packages("rgdal")
install.packages("raster")

library(gdalUtils)
library(raster)
library(rgdal)
library(raster)

print("Versione Packages:")
paste("gdalUtils:", packageVersion("gdalUtils"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))


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
  align_raster[i] <- align_rasters(unaligned = percorsi[i], reference = percorsi[1], output_Raster = TRUE ,projres_only = TRUE, r = Definisci_Metodo, tr = c(Definisci_Resolution,Definisci_Resolution))
}

bande_sel <- strsplit(Selezione_bande, " ")[[1]]
bande_sel <- c(bande_sel)

estensioni <- list(NA)
bande_sel_corretto = as.numeric(bande_sel)

bande_tot <- 0
bande_tot_fin <- 0

for(i in 1:length(align_raster)){
    bande_canc <- 0
    print("inizio ciclo")
    estensioni[i] <- intersect(extent(align_raster[[1]]), extent(align_raster[[(i)]]))
    prova = estensioni[i]
    print(prova)
    if(is.null(prova[[1]])){
      bande_canc = align_raster[[i]]@file@nbands
      for(y in 1:bande_canc){
        if(y+bande_tot_fin %in% bande_sel_corretto){
          print("rimuovi")
          cat("bande_sel_corretto " , bande_sel_corretto, "\n")
          bande_sel_corretto<- bande_sel_corretto[! bande_sel_corretto %in% (y+bande_tot_fin)]
          cat("bande_sel_corretto " , bande_sel_corretto, "\n")
        } 
      } 
      print("ciao thomas")
    } else {
      bande_tot_fin = bande_tot_fin + align_raster[[i]]@file@nbands
    }
    cat("bande_canc ", bande_canc, "\n")
    for (x in 1:length(bande_sel_corretto)){
      if(bande_sel_corretto[x] > bande_tot_fin){
       bande_sel_corretto[x] = bande_sel_corretto[x]-bande_canc
      }
    }
    cat("bande_sel_corretto " , bande_sel_corretto)
    bande_tot = bande_tot + (align_raster[[i]]@file@nbands)
    print(bande_tot)
}


if(max(bande_sel_corretto) > max(align_raster[[1]]@file@nbands)){
Nulli <- c(NA)
Nulli <- vapply(estensioni, is.null, TRUE)
Nulli <- which(Nulli == TRUE)
Nulli <- as.numeric(Nulli)

estensioni[[1]] <- NULL 
estensioni <- estensioni[!sapply(estensioni, is.null)]

if(length(Nulli)>0){
align_raster <- align_raster[- Nulli]
}

if(length(estensioni)> 1){
merge_ext <- do.call(merge, estensioni)
merge_ext_l = c(NA)
for(i in 1:4){
  merge_ext_l[i] <- merge_ext[i]
}
xmin <- merge_ext_l[1]
xmax <- merge_ext_l[2]
ymin <- merge_ext_l[3]
ymax <- merge_ext_l[4]
final_extent <- c(xmin, ymin, xmax, ymax)
} else{
 xmin <- estensioni[[1]][1]
  xmax <- estensioni[[1]][2]
  ymin <- estensioni[[1]][3]
  ymax <- estensioni[[1]][4]
  final_extent <- c(xmin, ymin, xmax, ymax)
}

lista <- c(NA)
for(i in 1:length(align_raster)){
  lista[i] <- align_raster[[i]]@file@name
}

bande <- as.character(c(bande_sel_corretto))
bande <- unique(bande)
mosaic_rasters(gdalfile = c(lista), dst_dataset = Percorso_output, output_Raster = TRUE, 
               separate = TRUE, te = final_extent, force_ot = "Float32", a_nodata = Definisci_valori_NA, of = Formato_di_output, b = bande, a_srs = proj_EPSG, overwrite = TRUE)
} else {
  lista <- c(NA)
  lista <- align_raster[[1]]@file@name
  
  bande <- as.character(c(bande_sel_corretto))
  bande <- unique(bande)
  mosaic_rasters(gdalfile = c(lista), dst_dataset = Percorso_output, output_Raster = TRUE, separate = TRUE, force_ot = "Float32", 
                  a_nodata = Definisci_valori_NA, of = Formato_di_output, b = bande, a_srs = proj_EPSG, overwrite = TRUE)
}
