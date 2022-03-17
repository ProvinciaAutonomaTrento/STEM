Spectral Angle Mapper
======================

Il modulo esegue la classificazione di immagini utilizzando l'algoritmo Spectral Angle Mapper (SAM). SAM è un classificatore spettrale che utilizza un angolo n-dimensionale per abbinare i pixel dell'immagine a degli spettri di riferimento. L'algoritmo determina la somiglianza spettrale fra due spettri calcolando l'angolo tra gli spettri e trattandoli come vettori in uno spazio con dimensionalità pari al numero di banda. Questa tecnica , se utilizzata su dati di riflettanza calibrati, è relativamente insensibile ad effetti di illuminazione e albedo.

.. only:: latex

  .. image:: ../_static/tool_images/spectral_angle_mapper.png


Input
------------

**Dati di input**: immagine raster da classificare.

**Seleziona le bande da utilizzare cliccandoci sopra** (opzionale): selezionare le bande da utilizzare. Se non si seleziona nulla vengono usate tutte le bande.


Parametri
------------

**File di selezione delle matrici**: file contenete le matrici delle firme spettrali.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
