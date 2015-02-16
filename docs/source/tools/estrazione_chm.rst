Estrazione CHM
================================

Il modulo effettua la generazione del Canopy Height Model, ossia la nuvola di punti delle chiome "normalizzate" rispetto alla quota del suolo.
Il CHM è un file las in cui sono memorizzati i punti la cui quota è data dalla differenza fra i punti del file .las di input e la quota del Digital Terrain Model - DTM (fornita in formato raster).

.. only:: latex

  .. image:: ../_static/tool_images/estrazione_chm.png


Input
------------

**File LAS di input**: opzione per caricare i file .las a cui sottrarre la quota del suolo.

**Input DTM**: opzione per caricare il file raster del Digital Terrain Model (DTM).


Parametri
------------

**Soglia terreno**: Poichè potrebbero susssistere minime differenze fra quote dei punti al suolo nel file .las e quote corrispondenti nel DTM, si pone una soglia (pari a 1-2 m) per eliminare i punti con valori....???


Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
