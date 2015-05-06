Struttura bosco
================================

Il modulo permette di stimare la tipologia di struttura del bosco (monoplana, biplana o multiplana) a partire da file .las del Canopy Height Model (ottenuto in uscita dal modulo "Estrazione CHM"). L'algoritmo si basa su un metodo di clustering e su una serie di soglie sulla distribuzione di altezza dei punti LIDAR in celle di dimensione prefissata. Successivamente il risultato é aggregato su aree di maggiore dimensione fornite dall'utente (file shp). L'algoritmo fornisce in uscita un file .shp modificato in cui viene aggiunta la colonna con l'informazione riguardante la struttura e un file .las modificato in cui l'informazione sulla strutturta e' contenuta nel campo "sourceID".

.. only:: latex

  .. image:: ../_static/tool_images/struttura_bosco.png


Input
------------

**File LAS di input**: selezionare il file .las di input realtivo al CHM.

**Shapefile di input**: selezionare il file .shp con le aree su cui stimare la struttura.

Parametri
------------

**Soglia**: soglia per rimuovere i punti considerati terreno o arbusti (default 1 m).

Output
------------

**Risultato**: inserire il percorso e il nome del file .las di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
