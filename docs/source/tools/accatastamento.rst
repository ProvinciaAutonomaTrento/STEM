Accatastamento
================================

Il modulo crea un nuovo raster multibanda a partire da più file mono o multibanda aventi estensione, proiezione e dimensioni uguali tra loro. L'output sarà un nuovo file multibanda.

.. only:: latex

  .. image:: ../_static/tool_images/accatastamento.png


Input
------------

**Dati di input**: nella finestra compaiono i raster attualmente aperti in QGIS. Selezionare i raster da accatastare.

.. warning::

  L'ordine dei raster è importante soprattutto per definire l'estensione
  dell'output. Il primo raster, dall'alto verso il basso, selezionato
  sarà quello dal quale si otterrà l'estensione dell'output

Parametri
------------

**Formato di output**: selezionare il formato per l'output del comando

  * *ENVI*: formato ENVI (file binario + header).
  * *GTIFF*: formato GeoTiff.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
