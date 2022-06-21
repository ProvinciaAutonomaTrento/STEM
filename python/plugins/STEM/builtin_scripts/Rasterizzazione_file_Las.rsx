##Pre-elaborazione Lidar=group
##File_LAS_di_input= file
##Seleziona_il_ritorno_desiderato=number
##Seleziona_il_metodo_statistico_da_utilizzare=selection n;min;max;range;sum;mean;stddev;variance;coeff_var;median;percentile;skewness;trimmean
##Risoluzione_finale_del_raster=number
##Percentile_valori_supportati_1_100=optional number
##Soglia_trim=optional number
##Classe_o_classi_separate_da_uno_spazio_su_cui_filtrare_il_file_Las=optional string
##Definisci_valori_NA=number
##Definisci_EPSG=string
##Risultato=string

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("lidR")
install.packages("raster")
install.packages("PerformanceAnalytics")

library(lidR)
library(raster)
library(PerformanceAnalytics)

print("Versione Packages:")
paste("raster:", packageVersion("raster"))
paste("lidR:", packageVersion("lidR"))
paste("PerformanceAnalytics:", packageVersion("PerformanceAnalytics"))

las<-readLAS(File_LAS_di_input)

if(Seleziona_il_ritorno_desiderato== 0){
   las <- las
} else if (Seleziona_il_ritorno_desiderato== 99){
   las <- filter_poi(las, ReturnNumber==NumberOfReturns)
} else {
   las <- filter_poi(las, ReturnNumber== Seleziona_il_ritorno_desiderato)
} 


if(Classe_o_classi_separate_da_uno_spazio_su_cui_filtrare_il_file_Las==""){
Classe_o_classi_separate_da_uno_spazio_su_cui_filtrare_il_file_Las=TRUE
} else {
lista_c <- c(1:255)
classe <- strsplit(Classe_o_classi_separate_da_uno_spazio_su_cui_filtrare_il_file_Las, ", ") [[1]]
classe = as.numeric(classe)
c_da_eliminare <- subset(lista_c, !(lista_c %in% classe))
for(i in 1:length(c_da_eliminare)){
  las = filter_poi(las, Classification != c_da_eliminare[i])
}
}

if(Seleziona_il_metodo_statistico_da_utilizzare==0){
   rast <- grid_metrics(las, func = length(unique(Z)), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==1){
   rast <- grid_metrics(las, func = min(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==2){
   rast <- grid_metrics(las, func = max(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==3){
   rast <- grid_metrics(las, func = range(Z), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==4){
   rast <- grid_metrics(las, func = sum(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==5){
   rast <- grid_metrics(las, func = mean(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==6){
   rast <- grid_metrics(las, func = sd(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==7){
   rast <- grid_metrics(las, func = var(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==8){
   rast <- grid_metrics(las, func = (sd(Z, na.rm = TRUE)/mean(Z, na.rm = TRUE))*100, res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==9){
   rast <- grid_metrics(las, func = median(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==10){
   Percentile_valori_supportati_1_100 = Percentile_valori_supportati_1_100/100
   rast <- grid_metrics(las, func = quantile(Z, Percentile_valori_supportati_1_100), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==11){
   rast <- grid_metrics(las, func = skewness(Z, na.rm=TRUE), res = Risoluzione_finale_del_raster)
} else if (Seleziona_il_metodo_statistico_da_utilizzare==12){
   rast <- grid_metrics(las, func = mean(Z, trim = Soglia_trim, na.rm=TRUE), res = Risoluzione_finale_del_raster)
}

proj <- "+init=epsg:"
proj_EPSG <- paste(proj, Definisci_EPSG, sep="")
projection(rast) <- proj_EPSG

writeRaster(rast, filename = Risultato, NAflag = Definisci_valori_NA, overwrite = TRUE)