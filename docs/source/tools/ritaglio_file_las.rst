Ritaglio file LAS
================================

Il modulo permette di ritagliare un file .las in base a un rettangolo con coordinate fissate dall'utente o in base ad uno shpaefile poligonale. L'output é un file .las contente i punti ritagliati.

.. only:: latex

  .. image:: ../_static/tool_images/ritaglio_file_LAS.png


Input
------------

**File LAS di input**: selezionare il file .las da ritagliare.

**Shapefile dell'area di interesse**: selezionare lo shapefile da usare per ritagliare il file .las. Lo shapefile deve essere stato precedentemente aperto in Qgis. Input opzionale

**Coordinate della bounding box**: input opzionale. Non serve se viene dato in input uno shapefile.

	* *Max North*: coordinata Y dell'angolo in alto a sinistra della bounding box.

	* *Min North*: coordinata Y dell'angolo in basso a sinistra della bounding box.

	* *Max East*: coordinata X dell'angolo in basso a destra della bounding box.

	* *Min East*: coordinata X dell'angolo in alto a sinistra della bounding box.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
