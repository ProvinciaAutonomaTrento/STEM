Minima distanza
================================

Il modulo effettua la classificazione di immagini usando l'algoritmo di classificazione supervisionata non-parametrico Minima Distanza. 
Gli input al classificatore sono un file raster da classificare e un vettoriale di training contente una colonna con l'indicazione delle classi da classificare in formato numerico (1,2,...,N).
L'utente potrà anche inserire un vettoriale da usare nella fase di validazione (la colonna con le classi deve avere lo stesso nome di quella del vettoriale di training).
L'algoritmo partendo dai dati di training definisce il centroide delle classi nello spazio delle feature ed assegna ad ogni pixel dell'immagine la classe corrispondente al centroide più vicino nello spazio delle feature.

.. only:: latex

  .. image:: ../_static/tool_images/minima_distanza.png


Input
------------

**File raster**: immagine raster da classificare.

**Training aree**: file vettoriale contente le aree di training e l'indicazione delle classi.

**Seleziona la colonna con codice classe**: selezionare tra le colonne del file vettoriale quella che indica le classi.

**Aree di validazione** (opzionale): file vettoriale contente le aree di validazione e l'indicazione delle classi (la colonna con le classi deve avere lo stesso nome di quella del vettoriale di training). Se non si hanno aree di validazione selezionare nuovamente Training aree.

Parametri
------------

**Creazione mappa**: se la casella è spuntata verrà generata la mappa in formato '.tif'. 

**Elenco features** (opzionale): digitare manualmente il numero identificativo delle features (bande) da utilizzare. Ciascun numero deve essere separato da uno spazio. Esempio: 30 52 16 9 6.

**File features** (opzionale): opzionalmente può essere dato in input il file .txt ottenuto mediante il modulo di 'Selezione feature per classificazione' alla voce "Output features" che elenca le feature da utilizzare.


**Numero di neighbors** (opzionale): numero di pixel di training vicini al pixel da classificare da considerare per la classificazione.

**Numero fold cross validation** (opzionale): inserire il numero di subset in cui verrà diviso il training set nella cross validation. Deve essere maggiore o uguale a 2. Dato N il numero di fold, il classificatore a rotazione verrà allenato con N-1 subsets e validato sul subset rimanente. L'accuratezza finale sarà la media delle N accuratezze.


Output
------------

**Risultato**: inserire il percorso e il nome del file di output in formato ".tif".

**Output info modello**: inserire il percorso di un file .txt per le informazioni del modello di classificazione.

**Output Metriche accuratezza**: inserire il percorso di un file .txt per le metriche di accuratezza.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
