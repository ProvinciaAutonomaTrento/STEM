Spectral Angle Mapper
======================

Il modulo esegue la classificazione di immagini utilizzando l'algoritmo Spectral Angle Mapper (SAM). SAM è un classificatore spettrale che utilizza un angolo n-dimensionale per abbinare i pixel dell'immagine a degli spettri di riferimento. L'algoritmo determina la somiglianza spettrale fra due spettri calcolando l'angolo tra gli spettri e trattandoli come vettori in uno spazio con dimensionalità pari al numero di banda. Questa tecnica , se utilizzata su dati di riflettanza calibrati, è relativamente insensibile ad effetti di illuminazione e albedo. Nel caso dell'algoritmo implementato in questo modulo gli spettri di riferimento sono estatti dall'immagine passata in input.

.. only:: latex

  .. image:: ../_static/tool_images/spectral_angle_mapper.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione delle classi.

**Seleziona la colonna con indicazione della classe**: selezionare tra le colonne del file vettoriale quella che indica le classi.

**Dati di input raster** (opzionale): immagine da cui estrarre le feature e da classificare (opzionale).

**Seleziona le bande da utilizzare cliccandoci sopra** (opzionale): selezionare le bande da utilizzare. Se non si seleziona nulla vengono usate tutte le bande.


Parametri
------------

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
