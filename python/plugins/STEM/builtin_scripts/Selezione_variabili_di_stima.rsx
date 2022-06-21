##Stima dei parametri=group
##Dati_di_input_vettoriale_di_training=vector polygon
##Seleziona_colonna_con_indicazione_del_parametro_da_stimare=Field Dati_di_input_vettoriale_di_training
##Colonna_da_non_considerare_nella_selezione=optional string
##load_vector_using_rgdal
##Risultato=output file
##Variabili_significative=output file

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("rgdal")
install.packages("olsrr")

library(sp)
library(rgdal)
library(olsrr)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("rgdal:", packageVersion("rgdal"))
paste("olsrr:", packageVersion("olsrr"))

df <- data.frame(Dati_di_input_vettoriale_di_training@data)

variabili_out <- strsplit(Colonna_da_non_considerare_nella_selezione, ", ")[[1]]
df[variabili_out] = NULL

df = na.omit(df)
colnames(df)[colnames(df) == Seleziona_colonna_con_indicazione_del_parametro_da_stimare] <- "variabile"

MultiLinearRegression = lm(variabile ~ ., data = df)
step_pvalue <- ols_step_both_p(MultiLinearRegression, pent = .05, prem = .05, details = TRUE)

report <- list(step_pvalue, step_pvalue$model)

capture.output(report, file = Risultato)
write.table(t(step_pvalue$predictors), file = Variabili_significative, col.names=F,row.names=F,sep=" ",quote=F)