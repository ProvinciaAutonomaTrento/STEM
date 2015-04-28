Support Vector Machines
================================

Il modulo effettua la classificazione di immagini o vettori usando l'algoritmo di classificazione supervisionata non-parametrico Support Vector Machine (SVM). La'lgoritmo SVM si basa sul principio che lo spazio delle feature di partenza puo' essere trasformato in uno spazio a più alta dimensionalità in cui le classi sono linearmente separabili. La trasformazione é effettuata utilizzando una funzione kernel.
Gli input al classificatore sono un file vettoriale contente una colonna con l'indicazione della classe in formato numerico(1,2,...,N), e (opzionale) l'indicazione delle feature (attributi del vettore) da usare nella classificazione. Se le feature non sono già contenute nel file vettoriale dovrà essere data in input un'immagine raster da cui estrarle.
L'utente potrà anche inserire un vettoriale da usare nella fase di validazione.

.. only:: latex

  .. image:: ../_static/tool_images/support_vector_machines.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione delle classi.

**Seleziona la colonna con indicazione della classe**: selezionare tra le colonne del file vettoriale quella che indica le classi.

**Dati di input raster** (opzionale): immagine da cui estrarre le feature e da classificare (opzionale).

**Seleziona le bande da utilizzare cliccandoci sopra** (opzionale): selezionare le bande da utilizzare. Se non si seleziona nulla vengono usate tutte le bande.

Parametri
------------

**Selezionare il kernel da utilizzare**:

	* *RBF*: kernel di tipo gaussiano Radial Basis Function.
	* *lineare*: kernel di tipo lineare.
	* *polinomiale*: kernel polinomiale.

**Inserire il parametro C**: parametro di regolarizzazione. Valori suggeriti: numero intero tra 1 e 100.

**Inserire il valore di gamma** (opzionale): parametro del kernel RBF.

**Inserire il valore del grado del polinomio** (opzionale): parametro del kernel polinomiale.

**Selezione feature**:

	* *no*: nessuna selezione delle feature.
	* *manuale*: le feature vengono selezionate manualemnte.
	* *file*: le feature sono scelte in base al file di output del modulo "Selezione feature per la classificazione".

**File di selezione** (opzionale): inserire il file ottenuto in output dal modulo "Selezione feature per la classificazione". Attivato solo se l'opzione "file" viene scelta nel menu "selezione feature".

**Vettoriale di validazione** (opzionale): file vettoriale contenente le aree di validazione e l'indicazione delle classi.

**Seleziona la colonna per la validazione** (opzionale): selezionare tra le colonne del file vettoriale quella che indica le classi.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
