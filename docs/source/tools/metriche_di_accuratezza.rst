Metriche di accuratezza
================================

Il modulo serve per calcolare iuna serie di metriceh di accuratezza su di un'immagine classificata. Calcola la matrice di confusione dell'immagine di input rispetto all'immagine/vettore di riferimento. Viene calcolata inoltre la kappa accuracy (e la sua varianza), l'errore di omissione e commisisone, il numero totale di pixels classificati correttamente, la superficie totale in numero di pixel e percentuale di pixels correttamente classificati.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.kappa <http://grass.osgeo.org/grass70/manuals/r.kappa.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/metriche_di_accuratezza.png


Input
------------

**Mappa classificata**: mappa classificata in formato raster.

**Input mappa training area (sia raster che vettoriale)**: mapa delle aree di riferimento. Puo' essere sia in formato raster che vettoriale.

Parametri
------------

**Seleziona la colonna da considerare per le statistiche**: nel caso l'input sia un vettoriale indicare la colonna contente le classi di riferimento..

Output
------------

**Risultato**: file di testo contenente le metriche di accuratezza.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
