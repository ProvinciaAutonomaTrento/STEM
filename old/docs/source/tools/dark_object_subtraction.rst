Dark object subtraction
================================

Il modulo esegue la correzione atmosferica sulla mappa raster di input utilizzando l'algoritmo "Dark Object Subtraction"". Il modulo funziona solo con dati satellitari Landsat. Non utilizzare per dati da aereo.

Questo modulo viene utilizzato per trasformare i digital number calibrati di immagini Landsat in radianza "top-of-atmosphere" o riflettanza "top-of-atmosphere" e in temperatura (banda 6 dei sensori TM e ETM +). Facoltativamente, può essere usato per calcolare la radianza in superficie o riflettanza con correzione atmosferica (metodo DOS).
Di solito, per farlo sono necessari la data di produzione, la data di acquisizione, e l'elevazione solare. Inoltre, per Landsat-7 ETM + è necessario anche il "gain" (alto o basso) delle bande Landsat. Questi dati vengono letti dal file di metadati (.met o MTL.txt) per tutti i Landsat MSS, TM, ETM + e OLI / TIRS.

Attenzione: Qualsiasi valore del raster nullo o inferiore rispetto QCALmin viene impostato a null nel raster di uscita e non è incluso nelle equazioni.

**Valori "uncorrected at-sensor" (Metodo di correzione atmosferica = uncorrected, default)**

Le correzioni geometriche e radiometriche standard generano delle immagini con digital number calibrati (QCAL = DN). Per poter standardizzare ulteriormente l'impatto dell'illuminazione sulla geometria, le immagini QCAL sono convertite prima di tutto in radianza "at-sensor" e poi in riflettanza "at-sensor". La banda termica è prima convertita da QCAL in radianza "at-sensor", e poi in temperatura effettiva "at-sensor" in gradi Kelvin. La correzione radiometrica converte i valori QCAL in radianza "at-sensor" (misurata in W/(m² * sr * µm)) usando le equazioni:
	* gain = (Lmax - Lmin) / (QCALmax - QCALmin)
	* bias = Lmin - gain * QCALmin
	* radianza = gain * QCAL + bias
dove, *Lmax* e *Lmin* sono costanti di calibrazione, e *QCALmax* e *QCALmin* sono i valori massimo e minimo del range della radianza riscalata in QCAL.
Successivamente per calcolare la riflettanza "at-sensor" le equazioni sono:
	* sun_radiance = [Esun * sin(e)] / (PI * d^2)
	* reflectance = radiance / sun_radiance
dove, *d* è la distanza Terra-Sole in unità astronomiche, *e* è l'angolo di elevazione del sole, e *Esun* è il valore medio di irradianza esoatmosferica in W/(m² * µm).

**Valori semplificati "at-surface" (Metodo di correzione atmosferica = dos[1-4])**

La correzione atmosferica e la calibrazione della riflettanza rimuovono la "path radiance", ovvero la luce sporadica dall'atmosfera, e l'effetto spettrale dell'illuminazione solare. Le equazioni per ottenere la radianza "at-surface" e la riflettanza "at-surface" (non valide per le bande termiche) sono le seguenti:

	* sun_radiance = TAUv * [Esun * sin(e) * TAUz + Esky] / (PI * d^2)
	* radiance_path = radiance_dark - percent * sun_radiance
	* radiance = (at-sensor_radiance - radiance_path)
	* reflectance = radiance / sun_radiance

dove *percent* è un valore tra 0.0 e 1.0 (di solito 0.01), *Esky* è l'irradianza diffusa, *TAUz* è la trasmittanza dell'atmosfera lungo il percorso tra il sole e la superficie del suolo, e *TAUv* è la trasmittanza dell'atmosfera lungo il percorso tra la superficie del suolo e il sensore. *radiance_dark* è la radianza "at-sensor" calcolata dall'oggetto più scuro, ad esempio il valore di digital number con almeno 'dark_parameter' (solitamente 1000) pixels per l'intera immagine. I valori sono,

	* DOS1: TAUv = 1.0, TAUz = 1.0 and Esky = 0.0
	* DOS2: TAUv = 1.0, Esky = 0.0, and TAUz = sin(e) per tutte le bande con lunghezza d'onda massima minore di 1 (i.e. bands 4-6 MSS, 1-4 TM, and 1-4 ETM+). Per le altre bande TAUz = 1.0
	* DOS3: TAUv = exp[-t/cos(sat_zenith)], TAUz = exp[-t/sin(e)], Esky = rayleigh
	* DOS4: TAUv = exp[-t/cos(sat_zenith)], TAUz = exp[-t/sin(e)], Esky = PI * radiance_dark

Attenzione: la radinaza in uscita non viene modificata (es.: i valori negativi non vengono settati a 0) quindi è possibile vi siano valori negativi. In ogni caso i valori di riflettanza vengono settati a 0 quando negativi.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `i.landsat.toar <http://grass.osgeo.org/grass70/manuals/i.landsat.toar.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/dark_object_subtraction.png

Input
------------

**Selezionare la cartella contenente i file Landsat**: selezionare la acrtella contenet i file Landsat. I file devono avere i nomi nel segunte formato: "basename.1" per la banda 1, "basename.2" per la banda 2, ecc. "basename" viene inserito tra i parametri.

**Selezionare il file dei metadata dei dati Landsat da analizzare**: Selezionare il file dei metadati dei dati Landsat da analizzare che dovrà essere o ".met" o chiamarsi "MTL.txt".

Parametri
------------

**Selezionare il prefisso dei dati Landsat**: inserire il prefisso per i nomi dei file di input ("basename").

**Metodo di correzione atmosferica**:

	* *uncorrected*
	* *dos1*
	* *dos2*
	* *dos2b*
	* *dos3*
	* *dos4*

**Percentuale della radianza solare**: percentuale della radianza solare nella path radiance. E' richiesto solo se il methodo è un "dos". Valore di default: 0.01.

**Numero minimo di pixel da considerare numero digitale dark object**: numero minimo di pixel da considerare digital number come dark object. E' richiesto solo se il methodo è un "dos". Valore di default: 1000.

**Valore dello scattering di Rayleigh, si utilizza solo con il metodo "dos3"**: valore di irradianza diffusa di Rayleigh. Richiesto solo per il metodo "dos3". Valore di default: 0.

Output
------------

**Selezionare il prefisso per salvare i risultati**: prefisso dei nomi dei file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
