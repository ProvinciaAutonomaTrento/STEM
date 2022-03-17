Estrazione CHM
================================

Il modulo "normalizza" rispetto alla quota del suolo la Z delle coordinate dei punti LiDAR all'interno di un file .las. Se il file .las ricopre un'area forestale si avrà in uscita il Canopy Height Model.
L'algoritmo sottrae alla Z di ogni punto del file .las di input la quota del DTM in quel punto.
Il CHM in uscita è un file .las in cui sono memorizzati i punti la cui quota è data dalla differenza fra i punti del file .las di input e la quota del Digital Terrain Model - DTM (fornita in formato raster).


.. only:: latex

  .. image:: ../_static/tool_images/estrazione_chm.png


Input
------------

**File LAS di input**: scegliere il file .las a cui sottrarre la quota del suolo.

**Input DTM**: scegliere tra i file raster aperti in Qgis il file raster del Digital Terrain Model (DTM).


Output
------------

**Risultato**: inserire il percorso e il nome del file .las di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
