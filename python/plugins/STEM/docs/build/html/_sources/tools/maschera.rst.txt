Maschera
================================

Il modulo maschera serve per preprocessare i layer (vettoriali e raster) sui quali si intende lancire i moduli STEM. Una volta lanciata l'elaborazione, dei nuovi layer vengono aggiunti nella TOC  conformi alla forma della maschera. La maschera é passata al software tramite uno shapefile M-poligonale. Il poligono può essere usato anche come maschera inversa, ovvero l'area all'interno del poligono non é utilizzabile nelle elaborazioni successive.

.. only:: latex

  .. image:: ../_static/tool_images/maschera.png


Input
------------

**Dati di input**: selezionare i layer da usare come maschera. Per rimoverle un dataset, selezionarlo e cancellare il layer tramite il tasto "canc".

**Layer maschera**: selezionare lo shapefile da usare come maschera.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
