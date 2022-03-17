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
  list(
  Max=(if(0%in%Seleziona_le_statistiche_da_calcolare){
     Max = max(n)
   }),
  Mean=(if(1%in%Seleziona_le_statistiche_da_calcolare){
    Mean = mean(n)
  }),
  Mode=(if(2%in%Seleziona_le_statistiche_da_calcolare){
    Mode = mfv1(n)
    print("Mode:-----")
    print(Mode)
  }),
  CoefVar=(if(3%in%Seleziona_le_statistiche_da_calcolare){
    CoefVar = ((sd(n)/mean(n))*100)
  }),
  p10=(if(4%in%Seleziona_le_statistiche_da_calcolare){
    p10 = quantile(n, 0.10)
  }),
  p20=(if(5%in%Seleziona_le_statistiche_da_calcolare){
    p20 = quantile(n, 0.20)
  }),
  p30=(if(6%in%Seleziona_le_statistiche_da_calcolare){
    p30 = quantile(n, 0.30)
  }),
  p40=(if(7%in%Seleziona_le_statistiche_da_calcolare){
    p40 = quantile(n, 0.40)
  }),
  p50=(if(8%in%Seleziona_le_statistiche_da_calcolare){
    p50 = quantile(n, 0.50)
  }),
  p60=(if(9%in%Seleziona_le_statistiche_da_calcolare){
    p60 = quantile(n, 0.60)
  }),
  p70=(if(10%in%Seleziona_le_statistiche_da_calcolare){
    p70 = quantile(n, 0.70)
  }),
  p80=(if(11%in%Seleziona_le_statistiche_da_calcolare){
    p80 = quantile(n, 0.80)
  }),
  p90=(if(12%in%Seleziona_le_statistiche_da_calcolare){
    p90 = quantile(n, 0.90)
  })
  )
}

if(Seleziona_la_dimensione==0){
    fileLas <- readLAS(File_LAS_di_input, select = "z")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Z))
     })
} else if(Seleziona_la_dimensione==1){
    fileLas <- readLAS(File_LAS_di_input, select = "x")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(X))
     })
} else if(Seleziona_la_dimensione==2){
    fileLas <- readLAS(File_LAS_di_input, select = "y")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Y))
     })
} else if(Seleziona_la_dimensione==3){
    fileLas <- readLAS(File_LAS_di_input, select = "i")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Intensity))
     })
} else if(Seleziona_la_dimensione==4){
    fileLas <- readLAS(File_LAS_di_input, select = "r")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(ReturnNumber))
     })
} else if(Seleziona_la_dimensione==5){
    fileLas <- readLAS(File_LAS_di_input, select = "n")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(NumberOfReturns))
     })
} else if(Seleziona_la_dimensione==6){
    fileLas <- readLAS(File_LAS_di_input, select = "d")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(ScanDirectionFlag))
     })
} else if(Seleziona_la_dimensione==7){
    fileLas <- readLAS(File_LAS_di_input, select = "e")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(EdgeOfFlightLine))
     })
} else if(Seleziona_la_dimensione==8){
    fileLas <- readLAS(File_LAS_di_input, select = "c")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Classification))
     })
} else if(Seleziona_la_dimensione==9){
    fileLas <- readLAS(File_LAS_di_input, select = "a")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(ScanAngleRank))
     })
} else if(Seleziona_la_dimensione==10){
    fileLas <- readLAS(File_LAS_di_input, select = "u")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(UserData))
     })
} else if(Seleziona_la_dimensione==11){
    fileLas <- readLAS(File_LAS_di_input, select = "p")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(PointSourceId))
     })
} else if(Seleziona_la_dimensione==12){
    fileLas <- readLAS(File_LAS_di_input, select = "t")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(GpsTime))
     })
} else if(Seleziona_la_dimensione==13){
    fileLas <- readLAS(File_LAS_di_input, select = "R")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Red))
     })
} else if(Seleziona_la_dimensione==14){
    fileLas <- readLAS(File_LAS_di_input, select = "G")
    seg_cloud <- clip_roi(fileLas, Dati_di_input)
    metrics <- lapply(seg_cloud, function(seg_cloud) {
    cloud_metrics(seg_cloud, func = ~funct(Green))
     })
} else if(Seleziona_la_dimensione==15){
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
