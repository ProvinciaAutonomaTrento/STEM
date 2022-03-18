STEM - Sistema di TElerilevamento e di Monitoraggio del territorio e dell'ambiente trentino
===========

Il progetto STEM, finanziato dalla Provincia Autonoma di Trento, ha previsto lo sviluppo di un sistema informativo finalizzato all’archiviazione, elaborazione e diffusione delle informazioni telerilevate utili ai processi di pianificazione, gestione e monitoraggio territoriale. Una componente fondamentale del progetto è costituita da plugin, per ambiente open-source QGIS, utili alla classificazione dell'uso del suolo e stima di parametri forestali quali: altezza, densità, struttura e volume legnoso.

Requisiti
-------------------------

* QGIS >= 3.22
* GRASS >= 7.8
* R >= 4.0

Passi installazione
-------------------------
1.	Installare QGIS. Il plugin è stato creato per la versione QGIS 3.X, ma se ne consiglia l'utilizzo dalla versione LTR 3.22 (o successive).
2.	Installare il motore di calcolo R, scaricandolo direttamente dal sito https://cran.r-project.org/. Il plugin supporta la versione 4.0 o successive.
3.	Da QGIS, tramite l’apposito modulo, installare il plugin "Processing R Provider" e configurarlo alla voce "Impostazioni -> Opzioni -> Processing -> Programmi -> R". 
4.	Copiare il contenuto della Repository Git (cartelle "processing" e "python") nella cartella del profilo utente di QGIS ("Impostazioni -> Profili Utente -> Apri la Cartella del Profilo Attivo"). 
5.	Verificare la presenza della voce "STEM" nelle voci di menu di QGIS, nel caso ricaricare i Plugin o riavviare QGIS.
7.	Verificare che nella tool box "Strumenti di Processing" (attivabile dalla voce "Processing -> Strumenti") sia presente il gruppo "R" e le cartelle "Pre Elaborazione", "Classificazione Supervisionata", "Stima dei Parametri", ...).
8.	 Da QGIS, verificare che i parametri presenti nella form "STEM impostazioni" (attivabile dalla voce "STEM -> Impostazioni") siano corretti; nel caso di prima installazione premere il pulsante "Init/Reload Configuration" per impostarli in automatico.

