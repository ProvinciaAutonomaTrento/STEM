Stimatore lineare
=================

Il modulo esegue la stima di parametri utilizzando uno stimatore lineare.
Gli input allo stimatore sono un file vettoriale contente una colonna con l'indicazione del target da stimare (es: volume) in formato numerico, e (opzionale) l'indicazione delle variabili (attributi del vettore) da usare nella stima (es: percentili LIDAR, altezza LIDAR media, dimensione della chioma, ecc.). Se le variabili non sono già contenute nel file vettoriale dovrà essere data in input un'immagine raster da cui estrarle.
L'utente potrà anche inserire un vettoriale da usare nella fase di validazione.

.. only:: latex

  .. image:: ../_static/tool_images/stimatore_lineare.png

*Esempio*: stima diametro singoli alberi
Lo shapefile di input ("Dati di input vettoriale") avra' per esempio una tabella degli attributidi questo tipo:

  .. image:: ../_static/tool_images/stimatore_lineare_esempio_input.png

 Nel caso della stima del diametro di un albero useremo come target la colonna "DBH_cm" e come variabili per esempio l'altezza dell'albero (colonna "Height_m") e l'area della chioma (colonna "Area"). Le due varaibili andranno selezionate dal menu' "Colonne delle feature da utilizzare".


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione del parametro da stimare.

**Seleziona la colonna con indicazione del parametro da stimare**: selezionare tra le colonne del file vettoriale quella che indica il target da stimare.

**Colonne delle feature da utilizzare** (opzionale): selezionare le varaibili da utilizzare. Se non si seleziona nulla vengono usate tutte le variabili. Attivo solo se la selezione varaibili *manuale* è selezionata.

Parametri
------------

**Effettuare la cross-validation**: se scelto viene effettuata la cross validation.

**Inserire il numero di fold della cross-validation**: inserire il numero di fold della cross-validation.

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

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
