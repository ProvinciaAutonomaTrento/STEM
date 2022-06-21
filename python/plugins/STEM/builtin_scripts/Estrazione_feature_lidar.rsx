##Pre-elaborazione Lidar=group
##Dati_di_input=vector
##File_LAS_di_input=file
##Seleziona_le_statistiche_da_calcolare=string
##Seleziona_la_dimensione=selection Z;X;Y;Intensity;ReturnNumber;NumberOfReturns;ScanDirectionFlag;EdgeOfFlightLine;Classification;ScanAngleRank;UserData;PointSourceId;GpsTime;Red;Green;Blue
##Risultato=output vector
##load_vector_using_rgdal

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("rgdal")
install.packages("raster")
install.packages("lidR")
install.packages("modeest")
install.packages("rlist")

library(sp)
library(rgdal)
library(raster)
library(lidR)
library(modeest)
library(rlist)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))
paste("lidR:", packageVersion("lidR"))
paste("modeest:", packageVersion("modeest"))
paste("rlist:", packageVersion("rlist"))

Seleziona_le_statistiche_da_calcolare = strsplit(Seleziona_le_statistiche_da_calcolare, ", ")[[1]]
Seleziona_le_statistiche_da_calcolare = as.numeric(Seleziona_le_statistiche_da_calcolare)

funct <- function(n){ # user-defined fucntion
    prova <-list() 

  (if(0%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(Max = max(n))
    prova<-c(prova, loc)
  })

  (if(1%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(Mean = mean(n))
    prova<-c(prova, loc)
  })
  
  (if(2%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(Mode = mfv1(n))
    prova<-c(prova, loc)
  })
  
    
  (if(3%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(CoefVar = ((sd(n)/mean(n))*100))
    prova<-c(prova, loc)
  })
  
  (if(4%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p10 = quantile(n, 0.10))
    prova<-c(prova, loc)
  })
  
  (if(5%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p20 = quantile(n, 0.20))
    prova<-c(prova, loc)
  })
  
  (if(6%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p30 = quantile(n, 0.30))
    prova<-c(prova, loc)
  })
  
  (if(7%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p40 = quantile(n, 0.40))
    prova<-c(prova, loc)
  })
  
  (if(8%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p50 = quantile(n, 0.50))
    prova<-c(prova, loc)
  })
  
  (if(9%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p60 = quantile(n, 0.60))
    prova<-c(prova, loc)
  })
  
  (if(10%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p70 = quantile(n, 0.70))
    prova<-c(prova, loc)
  })
  
  (if(11%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p80 = quantile(n, 0.80))
    prova<-c(prova, loc)
  })
  
  (if(12%in%Seleziona_le_statistiche_da_calcolare){
    loc <- list(p90 = quantile(n, 0.90))
    prova<-c(prova, loc)
  })
 return(prova)
}

if(Seleziona_la_dimensione==0){
    fileLas <- readLAS(File_LAS_di_input, select = "z")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Z))
     })
} 
if(Seleziona_la_dimensione==1){
    fileLas <- readLAS(File_LAS_di_input, select = "x")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(X))
     })
} 
if(Seleziona_la_dimensione==2){
    fileLas <- readLAS(File_LAS_di_input, select = "y")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Y))
     })
} 
if(Seleziona_la_dimensione==3){
    fileLas <- readLAS(File_LAS_di_input, select = "i")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Intensity))
     })
} 
if(Seleziona_la_dimensione==4){
    fileLas <- readLAS(File_LAS_di_input, select = "r")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(ReturnNumber))
     })
} 
if(Seleziona_la_dimensione==5){
    fileLas <- readLAS(File_LAS_di_input, select = "n")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(NumberOfReturns))
     })
} 
if(Seleziona_la_dimensione==6){
    fileLas <- readLAS(File_LAS_di_input, select = "d")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(ScanDirectionFlag))
     })
} 
if(Seleziona_la_dimensione==7){
    fileLas <- readLAS(File_LAS_di_input, select = "e")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(EdgeOfFlightLine))
     })
} 
if(Seleziona_la_dimensione==8){
    fileLas <- readLAS(File_LAS_di_input, select = "c")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Classification))
     })
} 
if(Seleziona_la_dimensione==9){
    fileLas <- readLAS(File_LAS_di_input, select = "a")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(ScanAngleRank))
     })
} 
if(Seleziona_la_dimensione==10){
    fileLas <- readLAS(File_LAS_di_input, select = "u")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(UserData))
     })
} 
if(Seleziona_la_dimensione==11){
    fileLas <- readLAS(File_LAS_di_input, select = "p")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(PointSourceId))
     })
} 
if(Seleziona_la_dimensione==12){
    fileLas <- readLAS(File_LAS_di_input, select = "t")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(GpsTime))
     })
} 
if(Seleziona_la_dimensione==13){
    fileLas <- readLAS(File_LAS_di_input, select = "R")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Red))
     })
} 
if(Seleziona_la_dimensione==14){
    fileLas <- readLAS(File_LAS_di_input, select = "G")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Green))
     })
} 
if(Seleziona_la_dimensione==15){
    fileLas <- readLAS(File_LAS_di_input, select = "B")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Blue))
     })
}

metrics <- lapply(metrics, function(metrics) {
  list.clean(metrics, fun= "is.null")
})
metrics <- data.table::rbindlist(metrics)

id <- Dati_di_input@data$id
metrics <- cbind(metrics, id = id) 

Dati_di_input@data = merge(Dati_di_input@data, metrics)

Risultato <- Dati_di_input
