Feature di tessitura
================================

Il modulo crea mappe raster contenti feature di tessitura a partire da un layer raster specificato dall'utente. Il modulo calcola caratteristiche tessiturali basate su matrici di dipendenza spaziale a 0, 45, 90, e 135 gradi di distanza (default = 1). Il modulo assume livelli di grigio che vanno da 0 a 255 come input. L'ingresso è riscalato automaticamente a 0 a 255 se la gamma del file di input è al di fuori di questo intervallo. In generale, più variabili costituiscono feature di tessitura: differenze nei valori di livello di grigio, grossolanità come scala di differenze dei livelli di grigio, la presenza o la mancanza di direzionalità e di schemi regolari. Una feature di tessitura può essere caratterizzata da toni (proprietà di intensità dei liveli di grigio) e la struttura (relazioni spaziali). Dal momento che le feature di tessitura sono altamente dipendenti dalla scala, si possono verificare strutture gerarchiche tra le feature.

Il modulo prende in input un layer raster e calcola le caratteristiche tessiturali basandosi su matrici di dipendenza spaziale in direzione nord-sud, est-ovest, nord-ovest, sud-ovest e nelle direzioni con un fianco a fianco, in zona (ad esempio, una distanza di 1). L'uscita consiste in quattro immagini per ogni funzione strutturale, una per ogni direzione.

Un modello di struttura comunemente usato è basato sulla cosiddetta matrice di co-occorrenza dei livelli di grigio. Questa matrice è un istogramma bidimensionale di livelli di grigio per ogni coppia di pixel che sono separati da una relazione spaziale fissa. La matrice approssima la distribuzione di probabilità congiunta di una coppia di pixel. Diverse misure di texture sono direttamente calcolate sulla matrice di co-occorrenza dei livelli di grigio.

.. only:: latex

  .. image:: ../_static/tool_images/feature_di_tessitura.png

Input
------------

**Dati di input**: selezionare il raster da utilizzare tra quelli attualmente aperti in QGIS.

**Selezionare le bande da utilizzare**: selezionare le bande che si vogliono utilizzare; se non si seleziona nulla vengono utilizzate tutte le bande.

Parametri
------------

**Metodi per calcolare la tessitura**: si possono scegliere diversi metodi di calcolo delle feature di tessitura

	* *Somma media (SA)*.
	* *Entropia (ENT)*: questa misura analizza la casualità. ENT è alto quando i valori della finestra mobile hanno valori simili. Si è bassa quando i valori sono vicini a 0 o 1 (cioè quando i pixel nella finestra locale sono uniformi).
	* *Differenza di entropie (DE)*.
	* *Somma di entropie (SE)*.
	* *Varianza (VAR)*: fornisce una misura della varianza dei toni di grigio all'interno della finestra mobile.
	* *Differenza di varianze (DV)*.
	* *Somma di varianze (SV)*.
	* *Secondo momento angolare (ASM, chiamato anche uniformità)*: questa è una misura di uniformità locale e l'opposto dell'entropia. Alti valori di ASM si verificano quando i pixel nella finestra mobile sono molto simili. Nota: la radice quadrata del'ASM è talvolta usata come misura di consistenza, e si chiama energia.
	* *Inverse Moment Difference (IDM, chiamato anche omogeneità)*: tale misura è legata inversamente alla misura di contrasto. Si tratta di una misura diretta dell'omogeneità locale di un'immagine digitale. Valori bassi sono associati a bassa omogeneità e viceversa.
	* *Contrasto (CON)*: questa misura analizza il contrasto dell'immagine (localmente variazioni a livello di grigio), come la dipendenza lineare dei livelli di grigio dei pixel vicini (somiglianza). Tipicamente alto quando la scala della trama locale è maggiore della distanza.
	* *Correlazione (COR)*: questa misura analizza la dipendenza lineare dei livelli di grigio di pixel adiacenti. Tipicamente alto quando la scala della trama locale è maggiore della distanza.
	* *Misure di informazione di correlazione (MOC)*.
	* *Coefficiente di correlazione massimo (MC)*.

**Dimensione della finestra mobile**: dimensione della finestra mobile su cui sono calcolate le feature di tessitura.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
