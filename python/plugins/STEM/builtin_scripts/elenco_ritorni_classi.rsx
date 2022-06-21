##Pre elaborazione=group
##FileLas= file
##Ritorni=Output table
##Classi=Output table
install.packages("lidR")
library(lidR)

print("Versione Packages:")
paste("lidR:", packageVersion("lidR"))

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

file <- readLAS(FileLas)

elenco_ritorni <- data.frame(sort(unique(file@data$ReturnNumber)))
elenco_classi <- data.frame(sort(unique(file@data$Classification)))

Ritorni <- elenco_ritorni
Classi <- elenco_classi