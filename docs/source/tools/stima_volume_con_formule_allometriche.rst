Stima volume con formule allometriche
=========================================

Il modulo effettua la stima del volume delle singole piante utilizzando le formule allometriche pubblicate in Scrinzi et al. (2010).

.. only:: latex

  .. image:: ../_static/tool_images/stima_volume_con_formule_allometriche.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente la posizione degli alberi. Tra gli attributi deve essere presente il diametro, la specie e l'altezza.

**Seleziona la colonna con indicazione della specie**: selezionare tra le colonne del file vettoriale quella che indica la specie. La specie deve essere fornita con i seguenti codici:

		* *ar*: abete rosso;
		* *ab*: abete bianco;
		* *la*: larice;
		* *pn*: pino nero;
		* *ps*: pino silvestre;
		* *pc*: pino cembro;
		* *fa*: faggio;
		* *al*: altre latifoglie.

**Seleziona la colonna con indicazione del diametro**: selezionare tra le colonne del file vettoriale quella che indica il diametro.

**Seleziona la colonna con indicazione dell'altezza**: selezionare tra le colonne del file vettoriale quella che indica l'altezza.


Parametri
------------

Output
------------

**Nome della nuova colonna con il volume**: inserire il nome della nuova colonna con il volume. Massimo 10 caratteri. Niente spazi.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
