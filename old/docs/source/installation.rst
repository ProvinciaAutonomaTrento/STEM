Come installare il plugin
==============================

Il plugin richiede `GRASS GIS 7`_, `GDAL`_, `PDAL`_, `libLAS`_ e le
librerie di Python `numpy`_, `scikit-learn`_ (versione uguale alla 0.15.2),
`psutil`_ (versione maggiore alla 2.1.1), `Pyro4`_ (dev'essere la
stessa versione nei client e nel server) e `smop`_

Installazione su Linux
------------------------------

In base alla distribuzione installare i pacchetti sopra indicati
con il software manager preferito.

Se le librerie Python non sono disponibili per la distribuzione in uso
si possono installare tramite `pip`_

Installazione su Windows
----------------------------------------

**STEP1**: installazione qgis e dipendenze:

	1.	download eseguibile OSGeo4W dal sito: http://trac.osgeo.org/osgeo4w/. Scaricare la versione a 32bit!
	2.	lanciare l’eseguibile di OSGeo4W come amministartore;
	3.	scegliere “Advanced Install” e cliccare su “Next”;
	4.	scegliere “Install from Internet” e cliccare su “Next”;
	5.	mantenere le opzioni di default e cliccare su “Next”;
	6.	mantenere le opzioni di default e cliccare su “Next”;
	7.	mantenere le opzioni di default e cliccare su “Next”;
	8.	selezionare il sito da cui fare il download (dovrebe gia’ essere selezionato) e cliccare su “Next”;
	9.	selezionare i pacchetti da installare:
		a.	Qgis;
		b.	grass 7.0;
		c.	scipy;
		d.	numpy;
		e.	scikit-learn;
	10.	una volta scelti cliccare su “Next”;
	11.	a questo punto OSGeo4W installera’ i pacchetti necessari. Al termine uscire.


**STEP2**: installazione di pip:

	1.	dal sito https://pip.pypa.io/en/latest/installing.html scaricare “get-pip.py”;
	2.	aprire la Shell OSGeo4W in modalità amministratore;
	3.	dalla shell andare nella cartella in cui si e’ salvato “get-pip.py”;
	4.	digitare il comando: “python get-pip.py”;
	5.	se va a buon fine, digitare poi il comando: “pip install -U setuptools”.


**STEP3**: installazione delle librerie:

	1.	aprire la Shell OSGeo4W in modalità amministratore.
	2.	installare “psutil” digitando il comando: “pip install psutil --upgrade”;
	3.	installare “numpy” digitando il comando: “pip install numpy --upgrade”;
	4.	installare “scipy” digitando il comando: “pip install scipy --upgrade”;
	5.	installare “scikit-learn” digitando il comando: “pip install scikit-learn --upgrade”.


**STEP4**: copiare la cartella del plug-in STEM nella cartella dei plugin di Qgis. Esempio: “C:\\Users\\Angelo\\.qgis2\\python\\plugins”.

Risoluzione dei problemi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Potrebbe mancare Visual Studio 2010 c++: in mancanza di questo non
possibile installare il pacchetto di `numpy`_ corretto. Tipico errore:
"Unable to find vcvarsall.bat".

 * soluzione: installare Visual Studio 2010 c++ 2010 Express dal sito
   https://www.visualstudio.com/downloads/download-visual-studio-vs#DownloadFamilies_4;

 * installare "Microsoft Visual C++ Compiler for Python 2.7" tramite il sito
   http://www.microsoft.com/en-us/download/details.aspx?id=44266.

Errata versione `numpy`_: versioni precedenti alla 1.9.2 di `numpy`_ non sono
compatibili con `scikit-learn`_ versione maggiore della 0.15.0.

 * soluzione: aggiornare `numpy`_ tramite il comando
   `easy_install.exe --upgrade numpy`
   oppure disinstallarlo con `pip uninstall numpy` e poi reinstallarlo
   con `pip install numpy` per evitare residui di versioni.

Errore "ImportError: cannot import name inplace_column_scale": possibili
residui di precedenti installazioni di `scikit-learn`_.

 * Soluzione: cancellare il file
   $Home_OSGeo4W\python27\Lib\site-packages\sklearn\utils\sparsefuncs.py.


Installazione pacchetti aggiuntivi GRASS GIS
--------------------------------------------------
Il modulo per calcolare lo Spectral Angle Mapper richiede un modulo aggiuntivo
per GRASS GIS (denominati `Addons <https://grass.osgeo.org/grass70/manuals/addons/>`_).
In special modo bisogna installare l'addons `i.spec.sam <https://grass.osgeo.org/grass70/manuals/addons/i.spec.sam.html>`_,
per fare ciò bisogna:

* lanciare GRASS GIS
* andare in ``Impostazioni -> Estensioni (addons) aggiuntive -> Installa estensione dagli addons``
* cliccare su ``imagery -> i.spec.sam`` all'interno della ``Lista delle estensioni``
* cliccare sul bottone ``Installa``

A questo punto l'estensione è installata. Per controllare la corretta installazione
si può digitare ``i.spec.sam`` nel ``Layer Manager`` all'interno della
``Console dei programmi``; se tutto è andato a buon fine si aprirà la finestra
del comando.

.. _`GRASS GIS 7`: http://grass.osgeo.org
.. _`GDAL`: http://gdal.osgeo.org
.. _`numpy`: http://www.numpy.org/
.. _`scikit-learn`: http://scikit-learn.org/
.. _`pip`: http://www.pip-installer.org/
.. _`OSGeo4W`: http://trac.osgeo.ogr/osgeo4w
.. _`psutil`: https://github.com/giampaolo/psutil
.. _`Pyro4`: https://pythonhosted.org/Pyro4/index.html
.. _`PDAL`: http://www.pdal.io/
.. _`libLAS`: http://liblas.org/
.. _`smop`: http://chiselapp.com/user/victorlei/repository/smop-dev/index
