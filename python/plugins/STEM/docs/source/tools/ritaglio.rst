Ritaglio
================================

Il modulo Ritaglio serve per preprocessare i layer (sia vettoriali che raster) sui quali si intende lanciare i moduli STEM creando dei nuovi dataset coerenti con la forma della maschera. Una volta lanciata l'elaborazione, i nuovi layer vengono aggiunti nella cartella identificata ed, eventualmente, aggiunti alla TOC. La maschera (ritaglio) è di tipo shapefile M-poligonale. Il poligono può essere usato anche come maschera inversa, ovvero l'area all'interno del poligono viene rimossa. I dati presenti nella TOC (sia vettoriali che raster) vengono caricati di default tra quelli utilizzabili come input, mentre i soli vettoriali vengono aggiunti come scelta sulla quale effettuare il ritaglio. E' possibile aggiungere ulteriori dataset tramite il pulsante "Sfoglia".

.. only:: latex

  .. image:: ../_static/tool_images/maschera.png


Input
------------

**Dati di input**: selezionare i layer da usare come maschera. Per rimoverle un dataset, selezionarlo e cancellare il layer tramite il tasto "canc". E' possibile i drag and drop e la scelta multipla.

**Layer maschera**: selezionare lo shapefile da usare come maschera.

**Usa Maschera Inversa**: inverte l'area da rimuovere.

**Cartella output**: cartella dove vengono salvati i dati processati.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
