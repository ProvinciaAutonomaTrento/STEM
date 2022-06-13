Support Vector regression
==========================

IIl modulo effettua la classificazione di immagini o vettori usando l'algoritmo di supervisionato non-parametrico Support Vector Regression (SVR). L'algoritmo SVM si basa sul principio che lo spazio delle variabili di partenza può essere trasformato in uno spazio a più alta dimensionalità in cui la stima lineare è possibile. La trasformazione è effettuata utilizzando una funzione kernel.
Gli input allo stimatore sono un file vettoriale contente una colonna con l'indicazione del target da stimare (es: volume) in formato numerico, e (opzionale) l'indicazione delle variabili (attributi del vettore) da usare nella stima (es: percentili LIDAR, altezza LIDAR media, dimensione della chioma, ecc.). Va inserito il vettoriale di mappa e cioè l'intera area da stimare (es. griglia) avente come attributi le stesse variabili indicate nel vettoriale di training. L'utente potrà anche inserire un vettoriale da usare nella fase di validazione. Se si inserisce un vettoriale di validazione le metriche calcolate saranno: R2, RMSE e MAE.

.. only:: latex

  .. image:: ../_static/tool_images/support_vector_regression.png


Input
------------

**Dati di input vettoriale di training**: file vettoriale contente le aree di training e l'indicazione del parametro da stimare.

**Seleziona la colonna con indicazione del parametro da stimare**: selezionare tra le colonne del file vettoriale quella che indica il target da stimare.

**Vettoriale di mappa**: file vettoriale dell'area da stimare. Gli attributi devono chiamarsi nella stessa maniera e essere dello stesso tipo del vettoriale di training.

**Vettoriale di validazione** (opzionale): file vettoriale contenente le aree di validazione o di mappatura. I nomi delle colonne del vettoriale devono essere le stesse delle varaibili utilizzate nella creazione del modello.

**Seleziona la colonna per la validazione** (opzionale): selezionare tra le colonne del file vettoriale quella che indica il target. Se si effettua la mappatura non ve scelto nulla.

**File di selezione** (opzionale): inserire il file ottenuto in output dal modulo "Selezione variabili per la stima". Attivato solo se l'opzione "file" viene scelta nel menu "selezione variabili".

Parametri
------------

**Inserire il numero di fold della cross-validation** (opzionale): inserire il numero di fold della cross-validation.

**Selezionare il kernel da utilizzare**:

	* *radiale*: kernel di tipo gaussiano Radial Basis Function (scelta consigliata).
	* *lineare*: kernel di tipo lineare.
	* *polinomiale*: kernel polinomiale.

.. warning::

  Si suggerisce di evitare il kernel lineare poichè fa aumentare a dismisura i tempi di elaborazione.

**Inserire il parametro C** (opzionale): parametro di regolarizzazione. Valori suggeriti: numero intero tra 1 e 100.

**Inserire il valore di gamma** (opzionale): parametro del kernel radiale.

**Inserire il valore del grado del polinomio** (opzionale): parametro del kernel polinomiale.

**Inserire il valore di epsilon**: parametro dello stimatore SVR.

**Seleziona la trasformazione**: tipologia di trasformazione dei dati. Può essere nessuna, radice quadra e logaritmica.

**Selezione variabili**:

	* *no*: nessuna selezione delle variabili. Tutte le variabili verranno utilizzate.
	* *manuale*: le variabili vengono selezionate manualmente.
	* *file*: le variabili sono scelte in base al file di output del modulo "Selezione variabili per la stima".

**Colonne delle features da utilizzare** (opzionale): selezionare le varaibili da utilizzare separate da uno spazio. Attivo solo se la selezione varaibili *manuale* è selezionata.

**Nome colonna per i valori della stima**: inserire il nome della colonna del risultato ottenuto con stimatore lineare.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

**Accuratezza**: inserire il percorso e il nome del file di output .txt, contenente le metriche di accuratezza nel caso si sia inserito il vettoriale di validazione.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
