Support Vector Machines
================================

Il modulo effettua la classificazione di immagini o vettori usando l'algoritmo di classificazione supervisionata non-parametrico Support Vector Machine (SVM). L'algoritmo SVM si basa sul principio che lo spazio delle feature di partenza può essere trasformato in uno spazio a più alta dimensionalità in cui le classi sono linearmente separabili. La trasformazione è effettuata utilizzando una funzione kernel di tipo gaussiano Radial Basis Function.
Gli input al classificatore sono un file vettoriale contente una colonna con l'indicazione della classe in formato numerico (1,2,...,N) e un immagine raster da classificare.
L'utente potrà anche inserire un vettoriale da usare nella fase di validazione (la colonna con le classi deve avere lo stesso nome di quella del vettoriale di training).

.. only:: latex

  .. image:: ../_static/tool_images/support_vector_machines.png


Input
------------

**File raster**: immagine raster da classificare.

**Training aree**: file vettoriale contente le aree di training e l'indicazione delle classi.

**Seleziona la colonna con codice classe**: selezionare tra le colonne del file vettoriale quella che indica le classi.

**Aree di validazione** (opzionale): file vettoriale contente le aree di validazione e l'indicazione delle classi (la colonna con le classi deve avere lo stesso nome di quella del vettoriale di training). Se non si hanno aree di validazione selezionare nuovamente Training aree.

Parametri
------------

**Creazione mappa**: se la casella è spuntata verrà generata la mappa in formato '.tif'. 

**Elenco features** (opzionale): digitare manualmente il numero identificativo delle features da utilizzare. Ciascun numero deve essere separato da uno spazio. Esempio: 30 52 16 9 6.

**File features** (opzionale): selezionare il file .txt ottenuto mediante il modulo di 'Selezione feature per classificazione' alla voce "Output features".

**Valore C** (opzionale): parametro di regolarizzazione.

**Valore di sigma** (opzionale): parametro del kernel RBF.

**Numero fold cross validation** (opzionale): inserire il numero di subset in cui verrà diviso il training set nella cross validation. Deve essere maggiore o uguale a 2. Dato N il numero di fold, il classificatore a rotazione verrà allenato con N-1 subsets e validato sul subset rimanente. L'accuratezza finale sarà la media delle N accuratezze.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output in formato ".tif".

**Output info modello**: inserire il percorso di un file .txt per le informazioni del modello di classificazione.

**Output Metriche accuratezza**: inserire il percorso di un file .txt per le metriche di accuratezza.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
