Massima verosimiglianza
================================

Il modulo effettua la classificazione di immagini o vettori usando l'algoritmo di classificazione supervisionata Massima Verosimiglianza. Il classificatore a massima verosimilglianza é un classificatore parametrico supervisionato che assume una distribuzione gaussiana dei valori dei pixel all'interno di una classe. La classificazione avverrà in tre passaggi: 1) partendo dalle aree di training il classificatore stima la media e la varianza di ogni classe.  Nel caso di dati multidimensionali si avrà un vettore di medie 1xN (con N = numero di bande) e una matrice di covarainza (NxN) per ogni classe.; ii) una funzione di tipo gaussiano viene definita per ogni classe partendo dalle medie e dalle varianze stimate al passaggio precedente; e iii) per ogni pixel dell'immagine da classificare si ottiene un valore della funzione gaussiana di ogni classe e si sceglie la classe che fornisce il valore più alto.

Gli input al classificatore sono un file vettoriale contente una colonna con l'indicazione della classe in formato numerico (1,2,...,N), e (opzionale) l'indicazione delle feature (attributi del vettore) da usare nella classificazione. Se le feature non sono già contenute nel file vettoriale dovrà essere data in input un'immagine raster da cui estrarre i valori delle feature.
L'utente potrà anche inserire un vettoraile da usare nella fase di validazione.

.. warning::

  Ogni classe deve avere un numero di pixel superiore al numero totale di feature. Se questo vincolo non è soddisfatto il classificatore si blocca a acusa della non invertibilità della matrice di covarianza della classe il cui numero di campioni è limitato. Questo problema si può evitare riducendo il numero di feature o aumentando il numero di campioni.

.. only:: latex

  .. image:: ../_static/tool_images/massima_verosimiglianza.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione delle classi.

**Seleziona la colonna con indicazione della classe**: selezionare tra le colonne del file vettoriale quella che indica le classi.

**Dati di input raster** (opzionale): immagine da cui estrarre le feature e da classificare (opzionale).

**Seleziona le bande da utilizzare cliccandoci sopra** (opzionale): selezionare le bande da utilizzare. Se non si seleziona nulla vengono usate tutte le bande.

Parametri
------------

**Effettuare la cross validation**: se scelto viene effettuata la cross validation sul file di training.

**Selezionare il numero di fold della cross validation maggiore di 2**: inserire il numero di subset in cui verrà diviso il training set nella cross validation. Deve essere maggiore o uguale a 2. Dato N il numero di fold, il classificatore a rotazione verrà allenato con N-1 subsets e validato sul subset rimanente. L'accuratezza finale sarà la media delle N accuratezze.

**Selezione feature**:

	* *no*: nessuna selezione delle feature.
	* *manuale*: le feature vengono selezionate manualemnte.
	* *file*: le feature sono scelte in base al file di output del modulo "Selezione feature per la classificazione".

**File di selezione** (opzionale): inserire il file ottenuto in output dal modulo "Selezione feature per la classificazione". Attivato solo se l'opzione "file" viene scelta nel menu "selezione feature".

**Vettoriale di validazione** (opzionale): file vettoriale contenente le aree di validazione e l'indicazione delle classi.

**Seleziona la colonna per la validazione** (opzionale): selezionare tra le colonne del file vettoriale quella che indica le classi.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output in formato ".tif". Se viene effettuata una validazione (tramite cross-validation o file vettoriale) verrà creato anche uno (o due) file ".csv" contente/i le statistiche di accuratezza.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
