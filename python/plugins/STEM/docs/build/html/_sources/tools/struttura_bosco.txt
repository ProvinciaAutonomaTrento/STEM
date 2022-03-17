Struttura bosco
================================

Il modulo permette di stimare la tipologia di struttura del bosco (monoplana, biplana o multiplana) a partire da file .las del Canopy Height Model (ottenuto in uscita dal modulo "Estrazione CHM"). L'algoritmo si basa su un metodo di clustering e su una serie di soglie sulla distribuzione di altezza dei punti LIDAR in celle di dimensione 4x4 m. Successivamente il risultato é aggregato su aree di maggiore dimensione fornite dall'utente.

.. only:: latex

  .. image:: ../_static/tool_images/struttura_bosco.png


Input
------------

**File LAS di input**: selezionare il file .las di input.

Parametri
------------

**XXX**:

Output
------------

**Risultato**: inserire il percorso e il nome del file las di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
