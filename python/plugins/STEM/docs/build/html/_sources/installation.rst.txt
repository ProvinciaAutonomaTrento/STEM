Come installare il plugin
==============================

Il plugin supporta la versione **QGIS 3.10 LTR** con **GRASS GIS 7.8**.

**STEP**: installazione dipendenze:

	1.	Provvedere a configurare **GRASS** (in termini di LOCATION) correttamente, lanciando direttamente l'applicazione e seguendo le istruzioni mostrate a video per la creazione della LOCATION.
	2.	Installare il motore di calcolo R, scaricandolo direttamente dal sito https://cran.r-project.org/. Il plugin supporta la versione 4.0.3.
	3.	Installare il plugin **Processing R Provider** e configurarlo alla voce ``Impostazioni -> Opzioni -> Processing -> Programmi -> R``.
		Per verificare la corretta installazione, si consiglia di provare uno degli script già presenti nella installazione del plugin.
	4.	Verificare che in ``Strumenti di Processing`` sia presente la voce **R** e le cartelle ``Pre Elaborazione, Classificazione Supervisionata, Stima dei Parametri, ...)``. 
	5.	Verificare che in Impostazioni -> Opzioni -> Processing -> Generale -> Percorso della cartella temporanea in uscita le barre del percorso siano “/” e non “\”


Installazione pacchetti aggiuntivi GRASS GIS
--------------------------------------------------
Il modulo per calcolare lo Spectral Angle Mapper richiede un modulo aggiuntivo
per GRASS GIS (denominati `Addons <https://grass.osgeo.org/grass70/manuals/addons/>`_).
In special modo bisogna installare l'addons `i.spec.sam <https://grass.osgeo.org/grass70/manuals/addons/i.spec.sam.html>`_,
per fare ciò bisogna:

* lanciare GRASS GIS
* andare in ``Impostazioni -> Estensioni (addons) aggiuntive -> Installa estensione dagli addons``
* cliccare su ``imagery -> i.spec.sam`` all'interno della ``Lista delle estensioni``
* cliccare sul bottone ``Installa``

A questo punto l'estensione è installata. Per controllare la corretta installazione
si può digitare ``i.spec.sam`` nel ``Layer Manager`` all'interno della
``Console dei programmi``; se tutto è andato a buon fine si aprirà la finestra
del comando.
