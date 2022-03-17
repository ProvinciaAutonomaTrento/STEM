Estrazione CHM
================================

Il modulo può estrarre il CHM da un singolo file oppure da una serie di file LiDAR (LASCatalog). Il modulo "normalizza" rispetto alla quota del suolo la Z delle coordinate dei punti LiDAR all'interno di un file .las. Se il file .las ricopre un'area forestale si avrà in uscita il Canopy Height Model.
L'algoritmo sottrae alla Z di ogni punto del file .las di input la quota del DTM in quel punto.
Il CHM in uscita è un file .las in cui sono memorizzati i punti la cui quota è data dalla differenza fra i punti del file .las di input e la quota del Digital Terrain Model - DTM (fornito in formato raster).

Per maggiori informazioni si veda la documentazione R del metodo  `normalize_height <https://>`_.


.. only:: latex

  .. image:: ../_static/tool_images/estrazione_chm.png


Input
------------

**Seleziona la sorgente**: scegliere tra l'utilizzo del modulo su un singolo file oppure su più file (LASCatalog) contenuti in una cartella.

**File LAS di input**: scegliere il file .las a cui sottrarre la quota del suolo.

**File DTM di input**: scegliere il file raster del Digital Terrain Model (DTM).

oppure 

**Cartella dei file LAS**: scegliere la cartella dei file .las (LASCatalog).

**Cartella dei file DTM**: scegliere la cartella dei raster del Digital Terrain Model (DTM).

Output
------------

**Risultato**: inserire il percorso e il nome del file .las (o .laz) di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
