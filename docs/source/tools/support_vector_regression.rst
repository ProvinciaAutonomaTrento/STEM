Support Vector regression
==========================

IIl modulo effettua la classificazione di immagini o vettori usando l'algoritmo di supervisionato non-parametrico Support Vector Regression (SVR). L'algoritmo SVM si basa sul principio che lo spazio delle variabili di partenza può essere trasformato in uno spazio a più alta dimensionalità in cui la stima lineare è possibile. La trasformazione è effettuata utilizzando una funzione kernel.
Gli input allo stimatore sono un file vettoriale contente una colonna con l'indicazione del target da stimare in formato numerico, e (opzionale) l'indicazione delle variabili (attributi del vettore) da usare nella stima. Se le variabili non sono già contenute nel file vettoriale dovrà essere data in input un'immagine raster da cui estrarle.
L'utente potrà anche inserire un vettoriale da usare nella fase di validazione.

.. only:: latex

  .. image:: ../_static/tool_images/support_vector_regression.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione dei target.

**Seleziona la colonna con indicazione del target**: selezionare tra le colonne del file vettoriale quella che indica il target da stimare.

**Dati di input raster** (opzionale): immagine da cui estrarre le variabili e da stimare (opzionale).

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

**Inserire il valore di epsilon**: parametro dello stimatore SVR.

**Selezione variabili**:

	* *no*: nessuna selezione delle variabili.
	* *manuale*: le variabili vengono selezionate manualmente.
	* *file*: le variabili sono scelte in base al file di output del modulo "Selezione variabili per la stima".

**File di selezione** (opzionale): inserire il file ottenuto in output dal modulo "Selezione variabili per la stima". Attivato solo se l'opzione "file" viene scelta nel menu "selezione variabili".

**Vettoriale di validazione** (opzionale): file vettoriale contenente le aree di validazione e l'indicazione del target.

**Seleziona la colonna per la validazione** (opzionale): selezionare tra le colonne del file vettoriale quella che indica il target.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
