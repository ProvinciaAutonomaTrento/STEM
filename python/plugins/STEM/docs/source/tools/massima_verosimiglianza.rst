Massima verosimiglianza
================================

Il modulo effettua la classificazione di immagini o vettori usando l'algoritmo di classificazione supervisionata Massima Verosimiglianza. Il classificatore a massima verosimilglianza é un classificatore parametrico supervisionato che assume una distribuzione gaussiana dei valori dei pixel all'interno di una classe. La classificazione avverrà in tre passaggi: 1) partendo dalle aree di training il classificatore stima la media e la varianza di ogni classe.  Nel caso di dati multidimensionali si avrà un vettore di medie 1xN (con N = numero di bande) e una matrice di covarainza (NxN) per ogni classe.; ii) una funzione di tipo gaussiano viene definita per ogni classe partendo dalle medie e dalle varianze stimate al passaggio precedente; e iii) per ogni pixel dell'immagine da classificare si ottiene un valore della funzione gaussiana di ogni classe e si sceglie la classe che fornisce il valore più alto.
Gli input al classificatore sono un file vettoriale contente una colonna con l'indicazione della classe in formato numerico (1,2,...,N) e un immagine raster da classificare.
L'utente potrà anche inserire un vettoraile da usare nella fase di validazione (la colonna con le classi deve avere lo stesso nome di quella del vettoriale di training).

.. warning::

  Ogni classe deve avere un numero di pixel superiore al numero totale di feature. Se questo vincolo non è soddisfatto il classificatore si blocca a acusa della non invertibilità della matrice di covarianza della classe il cui numero di campioni è limitato. Questo problema si può evitare riducendo il numero di feature o aumentando il numero di campioni.

.. only:: latex

  .. image:: ../_static/tool_images/massima_verosimiglianza.png


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

**Numero fold cross validation** (opzionale): inserire il numero di subset in cui verrà diviso il training set nella cross validation. Deve essere maggiore o uguale a 2. Dato N il numero di fold, il classificatore a rotazione verrà allenato con N-1 subsets e validato sul subset rimanente. L'accuratezza finale sarà la media delle N accuratezze.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output in formato ".tif". 

**Output info modello**: inserire il percorso di un file .txt per le informazioni del modello di classificazione.

**Output Metriche accuratezza**: inserire il percorso di un file .txt per le metriche di accuratezza.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
