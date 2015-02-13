Correzione Atmosferica
================================

Il modulo esegue la correzione atmosferica sulla mappa raster di input utilizzando l'algoritmo 6S (Seconda Simulazione del segnale satellite nello spettro solare).
Una descrizione dettagliata algoritmo è disponibile presso il sito internet "Land Surface Reflectance Science Computing Facility" (http://modis-sr.ltdri.org/).
Nota importante: le impostazioni della regione corrente vengono ignorate!
La regione viene modificata in modo da coprire la mappa raster ingresso prima che venga eseguita la correzione atmosferica. Le impostazioni precedenti vengono ripristinate dopo.
Si noti inoltre che il tempo di passaggio del satellite deve essere specificato in Greenwich Mean Time (GMT).

.. only:: latex

  .. image:: ../_static/tool_images/correzione_atmosferica.png


Input
------------

**Selezionare file con i parametri 6s**: selezionare il file nel quale sono memorizzati i parametri 6s.
Si ricorda che tale file deve essere formattato utilizzando le informazioni contentue nel sito "Land Surface Reflectance Science Computing Facility" (http://modis-sr.ltdri.org/).

**Dati di input**: nella finestra compaiono i raster attualmente aperti in QGIS.
Selezionare i raster da accatastare.

**Selezionare una sola banda**: selezionare la banda sulla quale eseguire la correzione atmosferica. L'algoritmo processa una banda alla volta.

Parametri
------------

**Selezionare l'algoritmo da utilizzare**: selezionare l'algoritmo con cui effetturare la correzione atmosferica. Al momento è implementato solo l'algoritmo 6s.

**Convertire la mappa in input in riflettanza**: selezionando questa opzione, la mappa viene convertita in immagine di riflettanza. Se non viene selezionata questa opzione, l'immagine è restituita in radianza (default).

**ETM+ precedente al 1 Luglio 2000**: SOLO nel caso di immagini Landsat 7. Selezionare questa opzione se le immagini sono state acquisite prima del 1 Luglio 2000.

**ETM+ successivo al 1 Luglio 2000**: SOLO nel caso di immagini Landsat 7. Selezionare questa opzione se le immagini sono state acquisite dopo il 1 Luglio 2000.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
