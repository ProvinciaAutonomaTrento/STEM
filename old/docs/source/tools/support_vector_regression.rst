Support Vector regression
==========================

IIl modulo effettua la classificazione di immagini o vettori usando l'algoritmo di supervisionato non-parametrico Support Vector Regression (SVR). L'algoritmo SVM si basa sul principio che lo spazio delle variabili di partenza può essere trasformato in uno spazio a più alta dimensionalità in cui la stima lineare è possibile. La trasformazione è effettuata utilizzando una funzione kernel.
Gli input allo stimatore sono un file vettoriale contente una colonna con l'indicazione del target da stimare in formato numerico, e (opzionale) l'indicazione delle variabili (attributi del vettore) da usare nella stima. L'utente potrà anche inserire un vettoriale da usare nella fase di validazione o di mappatura di un'area più ampia (es. vettoriale di una griglia).

.. only:: latex

  .. image:: ../_static/tool_images/support_vector_regression.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione dei target.

**Seleziona la colonna con indicazione del parametro da stimare**: selezionare tra le colonne del file vettoriale quella che indica il parametro da stimare.

**Seleziona le variabili da utilizzare cliccandoci sopra** (opzionale): selezionare le variabili da utilizzare. Se non si seleziona nulla vengono usate tutte le variabili.

Parametri
------------

**Effettuare la cross-validation**: se scelto viene effettuata la cross validation.

**Inserire il numero di fold della cross-validation**: inserire il numero di fold della cross-validation.

**Selezionare il kernel da utilizzare**:

	* *RBF*: kernel di tipo gaussiano Radial Basis Function (scelta consigliata).
	* *lineare*: kernel di tipo lineare.
	* *polinomiale*: kernel polinomiale.

.. warning::

  Si suggerisce di evitare il kernel lineare poichè fa aumentare a dismisura i tempi di elaborazione.

**Inserire il parametro C**: parametro di regolarizzazione. Valori suggeriti: numero intero tra 1 e 100.

**Inserire il valore di gamma** (opzionale): parametro del kernel RBF.

**Inserire il valore del grado del polinomio** (opzionale): parametro del kernel polinomiale.

**Inserire il valore di epsilon**: parametro dello stimatore SVR.

**Selezione variabili**:

	* *no*: nessuna selezione delle variabili.
	* *manuale*: le variabili vengono selezionate manualmente.
	* *file*: le variabili sono scelte in base al file di output del modulo "Selezione variabili per la stima".

**File di selezione** (opzionale): inserire il file ottenuto in output dal modulo "Selezione variabili per la stima". Attivato solo se l'opzione "file" viene scelta nel menu "selezione variabili".

**Vettoriale di validazione** (opzionale): file vettoriale contenente le aree di validazione o di mappatura. I nomi delle colonne del vettoriale devono essere le stesse delle varaibili utilizzate nella creazione del modello.

**Seleziona la colonna per la validazione** (opzionale): selezionare tra le colonne del file vettoriale quella che indica il target. Se si effettua la mappatura non ve scelto nulla.

**Indice di accuratezza per la selezione del modello** (opzionale):

	* *MSE*: Mean Square Error.
	* *R2*: R2.

**Creare output**: se scelto viene creato l'output, ovvero un vettoriale uguiale a quello di validazione/mappatura con un campo aggiuntivo col parametro stimato. Se non viene dato nessun input alla voce *Vettoriale di validazione* l'output verrà creato partendo dal vettoriale di training.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

**Colonna per i valori della stima**: nome della colonna dove verranno salvati i valori stimati. Al nome indicato viene aggiunta in fondo una *S* per indicare ceh la stima è stata effettuata mediante stimatore SVR.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
