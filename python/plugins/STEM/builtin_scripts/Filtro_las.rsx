##Pre-elaborazione Lidar=group
##FileLas=file 
##Seleziona_ritorno=optional string
##Inserire_valore_minimo__X=optional number
##Inserire_valore_massimo__X=optional number
##Inserire_valore_minimo__Y=optional number
##Inserire_valore_massimo__Y=optional number
##Inserire_valore_minimo__Z=optional number
##Inserire_valore_massimo__Z=optional number
##Inserire_valore_minimo_intensita=optional number
##Inserire_valore_massimo_intensita=optional number
##Inserire_valore_minimo_angolo_scansion=optional number
##Inserire_valore_massimo_angolo_scansion=optional number
##Inserire_valore_di_classificazione=optional number
##Output=output file

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("raster")
install.packages("lidR")

library(sp)
library(raster)
library(lidR)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("lidR:", packageVersion("lidR"))


paste("Seleziona_ritorno:",Seleziona_ritorno )


las_path <-file.path(FileLas)
 
fileLas <- readLAS(las_path)

if (is.null(Inserire_valore_massimo__X) == FALSE){
  fileLas = filter_poi(fileLas, X <= Inserire_valore_massimo__X)
}
if (is.null(Inserire_valore_minimo__X) == FALSE){
  fileLas = filter_poi(fileLas, X >= Inserire_valore_minimo__X)
}
if (is.null(Inserire_valore_massimo__Y) == FALSE){
  fileLas = filter_poi(fileLas, Y <= Inserire_valore_massimo__Y)
}
if (is.null(Inserire_valore_minimo__Y) == FALSE){
  fileLas = filter_poi(fileLas, Y >= Inserire_valore_minimo__Y)
}
if (is.null(Inserire_valore_minimo__Z) == FALSE){
  fileLas = filter_poi(fileLas, Z >= Inserire_valore_minimo__Z)  
}  
if (is.null(Inserire_valore_massimo__Z) == FALSE){
  fileLas = filter_poi(fileLas, Z <= Inserire_valore_massimo__Z)
}
if (is.null(Inserire_valore_massimo_intensita) == FALSE){
  fileLas = filter_poi(fileLas, Intensity <= Inserire_valore_massimo_intensita)
}
if (is.null(Inserire_valore_minimo_intensita) == FALSE){
  fileLas = filter_poi(fileLas, Intensity >= Inserire_valore_minimo_intensita)
}
if (is.null(Inserire_valore_massimo_angolo_scansion) == FALSE){
  fileLas = filter_poi(fileLas, ScanAngleRank <= Inserire_valore_massimo_angolo_scansion)
}
if (is.null(Inserire_valore_minimo_angolo_scansion) == FALSE){
  fileLas = filter_poi(fileLas, ScanAngleRank >= Inserire_valore_minimo_angolo_scansion)
}
if (is.null(Inserire_valore_di_classificazione) == FALSE){
  fileLas = filter_poi(fileLas, Classification == Inserire_valore_di_classificazione)
}

if(Seleziona_ritorno == "99"){
    fileLas = filter_poi(fileLas, ReturnNumber == NumberOfReturns)
} else {
Seleziona_ritorno <- strsplit(Seleziona_ritorno, " ")[[1]]
ritorni <- c(Seleziona_ritorno)
fileLas = filter_poi(fileLas, ReturnNumber %in% ritorni)
} 

writeLAS(fileLas, file = Output)
 