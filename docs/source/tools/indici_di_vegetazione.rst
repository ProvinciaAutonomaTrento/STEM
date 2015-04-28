Indici di vegetazione
================================

Questo modulo estrae da un'immagine multibanda raster i più utilizzati indici di vegetazione presenti in letteratura. Tali indici possono essere utilizzati poi come input nella fase di classificazione o di stima. La maggioranza degli indici é stat sviluppata per immagini satellitari, quindi se ne consiglia l'uso con immagini acquisite da satellite. Si può usare comunque anche con dati da aereo.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `i.vi <http://grass.osgeo.org/grass70/manuals/i.vi.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/indici_di_vegetazione.png


Input
------------

**Dati di input**: nella finestra compaiono i raster attualmente aperti in QGIS. Selezionare il raster multibanda da utilizzare.

**Selezionare la banda per il canale rosso**: tra le bande disponibili selezionare quella corrispondente al canale spettrale del rosso.

**Selezionare la banda per il canale verde**: tra le bande disponibili selezionare quella corrispondente al canale spettrale del verde.

**Selezionare la banda per il canale blu**: tra le bande disponibili selezionare quella corrispondente al canale spettrale del blu.

**Selezionare la banda per il canale infrarosso**: tra le bande disponibili selezionare quella corrispondente al canale spettrale dell'infrarosso.


Parametri
------------

**Seleziona l'indice di vegetazione**: selezionare l'indice di vegetazione da calcolare.

	* *arvi*:  Atmospheric Resistant Vegetation Index. L'indice ARVI è un indice resistente agli effetti atmosferici (in confronto all'NDVI) ed è realizzato mediante un processo di autocorrezione per l'effetto atmosferico nel canale del rosso, utilizzando la differenza di luminosità tra il canale del blu e il canale rosso. Si calcola nel modo seguente:

		ARVI = [infrarosso - (2.0 * rosso - blu)] / [infrarosso + (2.0 * rosso - blu)]

	* *dvi*: Difference Vegetation Index. Si calcola nel modo seguente:

		DVI = (infrarosso - rosso)

	* *evi*: Enhanced Vegetation Index. L'indice EVI è un indice ottimizzato progettato per evidenziare la vegetazione con una migliore sensibilità in regioni ad alta biomassa e migliorando il controllo della vegetazione attraverso un disaccoppiamento del segnale di background della canopy e una riduzione dell'influenza dell'atmosfera. Si calcola nel modo seguente:

		EVI = 2.5 * (infrarosso - rosso) / (infrarosso + 6.0 * rosso - 7.5 * blu + 1.0)

	* *evi2*: Enhanced Vegetation Index 2. Indice EVI a 2 bande senza la banda blu. Fornisce valori molto simili all'EVI a 3 bande quando gli effetti atmosferici sono insignificanti e la qualità dei dati è buona. Si calcola nel modo seguente:

		EVI2 = 2.5 * (infrarosso - rosso) / (infrarosso + 2.4 * rosso + 1.0)

	* *gari*: Green Atmospherically Resistant Vegetation Index. Si calcola nel modo seguente:

		GARI = (infrarosso - (verde - (blu - rosso))) / (infrarosso + (verde - (blu - rosso)))

	* *gemi*: Global Environmental Monitoring Index. Si calcola nel modo seguente:

		GEMI = (((2 * ((infrarosso * infrarosso) - (rosso * rosso)) + 1.5 * infrarosso + 0.5 * rosso) / (infrarosso + rosso + 0.5)) * (1 - 0.25 * (2 * ((infrarosso * infrarosso) - (rosso * rosso)) + 1.5 * infrarosso + 0.5 * rosso) / (infrarosso + rosso + 0.5))) - ((rosso - 0.125) / (1 - rosso))

	* *ipvi*: Infrared Percentage Vegetation Index. Si calcola nel modo seguente:

		IPVI = infrarosso / (rosso + infrarosso)

	* *ndvi*: Normalized Difference Vegetation Index. Si calcola nel modo seguente:

		NDVI = (infrarosso - rosso) / (infrarosso + rosso)

	* *savi*:  Soil Adjusted Vegetation Index. Si calcola nel modo seguente:

		SAVI = ((1.0 + 0.5) * (infrarosso - rosso)) / (infrarosso + rosso +0.5)

	* *sr*: Simple Ratio. Si calcola nel modo seguente:

		SR = (infrarosso / rosso)

	* *vari*: Visible Atmospherically Resistant Index. L'indice VARI è stato studiato per introdurre un'autocorrezione degli effetti atmosferici. Si calcola nel modo seguente:

		VARI = (verde - rosso) / (verde + rosso - blu)

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
