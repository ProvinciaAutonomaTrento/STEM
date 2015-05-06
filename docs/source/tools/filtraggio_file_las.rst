Filtraggio file LAS
================================

Il modulo esegue il filtraggio dei file .las in modo da selezionare solo i punti LIDAR che rispettano determinate regole.

.. only:: latex

  .. image:: ../_static/tool_images/filtraggio_file_las.png


Input
------------

**File LAS di input**: selezionare il file .las da filtrare.

Parametri
------------

Tutti i parametri sono opzionali. Se non viene impostato nessun parametro il modulo darà in output lo stesso file .las di input.

**Z max**: valore di Z al di sopra del quali i punti LIDAR vengono rimossi.

**Z min**: valore di Z al di sotto del quali i punti LIDAR vengono rimossi.

**X max**: valore di X al di sopra del quali i punti LIDAR vengono rimossi.

**X min**: valore di X al di sotto del quali i punti LIDAR vengono rimossi.

**Y max**: valore di Y al di sopra del quali i punti LIDAR vengono rimossi.

**Y min**: valore di Y al di sotto del quali i punti LIDAR vengono rimossi.

**Max scan angle**: valore massimo in valore assoluto dell'angolo di scansione al di sopra del quali i punti LIDAR vengono rimossi.

**Ritorni**: valore dei ritorni da mantenere nel file .las di output.


Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
