Feature geometriche
================================

Il modulo effettua l'estrazione delle feature geometriche sull'immagine.
Il processo di estrazione delle feature geometriche avviene su ciascuna banda delle immagine analizzata, su un intervallo (definito dall'utente) di segmentazione delle immagini.
Per ogni banda e per ogni livello di smoothing, è eseguita una segmentazione (vedi modulo segmentazione) che tiene conto sia delle informazioni spettrali sia della geometria dei singoli segmenti presi in considerazione durante il processo di region growing.
Il risultato finale di questo processo è una serie (scala) di immagini accatastate per ogni banda in un unico file di output.
Nota che questo modulo è stato ottimizzato per utilizzare immagini multispettrali (4 bande).

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `i.segment <http://grass.osgeo.org/grass70/manuals/i.segment.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/feature_geometriche.png


Input
------------

**Dati di input**: nella finestra compaiono i raster attualmente aperti in QGIS.
Selezionare i raster su cui eseguire l'estrazione delle feature geometriche.

**Selezionare la banda per il canale rosso**: selezionare dall'immagine di input la banda corrispondente al rosso.

**Selezionare la banda per il canale verde**: selezionare dall'immagine di input la banda corrispondente al verde.

**Selezionare la banda per il canale blu**: selezionare dall'immagine di input la banda corrispondente al blu.

**Selezionare la banda per il canale infrarosso**: selezionare dall'immagine di input la banda corrispondente al infrarosso.


Parametri
------------

**Seleziona il threshold minimo**: definisci il threshold minimo da cui eseguire iniziare il processo di estrazione delle feature geometriche. Tale valore estrime il threshold minimo della segmentazione dell'immagine.

**Seleziona il threshold massimo**: definisci il threshold massimo da cui eseguire iniziare il processo di estrazione delle feature geometriche. Tale valore estrime il threshold massimo della segmentazione dell'immagine.

**Seleziona il valore incrementale del threshold**: definisci di quanto incrementare il valore di segmentazione all'interno di ciascuna scala. Da questo valore dipente il numero di feature che verrà estratto per ogni banda dell'immagine.

**Inserire il valore di memoria da utilizzare in MB**: esprime il valore in MB di RAM da utilizzare per il processo  in corso.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
