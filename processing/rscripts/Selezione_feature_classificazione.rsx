##Classificazione Supervisionata=group
##Dati_di_input_vettoriale_di_training=vector polygon
##Colonna_indicazione_classe=Field Dati_di_input_vettoriale_di_training
##Strategia_selezione_feature=selection mean;minimum
##Seleziona_numero_variabili=number
##Dati_di_input_raster=raster
##Output_JM=output file
##Output_features=output file
##load_vector_using_rgdal

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("raster")
install.packages("rgdal")
install.packages("varSel")

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))
paste("varSel",packageVersion("varSel"))
  

print("Session Info:")
sessionInfo()


library(sp)
library(raster)
library(rgdal)
library(varSel)

band_values <- extract(Dati_di_input_raster, Dati_di_input_vettoriale_di_training, na.rm = TRUE)

nomi <- Dati_di_input_vettoriale_di_training[[Colonna_indicazione_classe]]
nomi <- as.list(nomi)

df_all <- mapply(cbind, nomi, band_values, SIMPLIFY = FALSE)

df <- do.call(rbind.data.frame, df_all)

df <- df[complete.cases(df),]

nomi_1 <- df[1]
df[1] <- NULL

df[] <- lapply(df, function(x) as.numeric(x))

df <- cbind(nomi_1, df)

Number <- ncol(df)

if(Strategia_selezione_feature == 0){ 
Strategia_selezione_feature <- "mean"
} else {
Strategia_selezione_feature <- "minimum"
}

n_select = Seleziona_numero_variabili - 1

tryCatch( expr = {
se <- varSelSFFS(g =df$V1, X =df[,c(2:Number)], 
                 strategy = Strategia_selezione_feature, n = n_select)
     print("La selezione e' andata a buon fine.")
},  error = function(e){
    print("Si e' generato un errore. La matrice generata e' singolare, non e' possibile effettuare la selezione.")
    print("Si consiglia di verificare le bande del dato in input nel caso presentassero una possibile singolarita'")
    print("Si consiglia di controllare i poligoni di training. Il numero di campioni di ciascuna classe deve essere maggiore del numero di bande.") 
  },
  finally = {
    print("Funzione terminata.")
  }
    )

bande <- c(se$features[Seleziona_numero_variabili, ])
bande <- bande[complete.cases(bande)]

capture.output(se, file = Output_JM)
write.table(t(bande), file = Output_features,col.names=F,row.names=F,sep=" ",quote=F)