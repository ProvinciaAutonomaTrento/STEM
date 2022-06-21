# -*- coding: utf-8 -*-

"""
Create a raster map starting from LAS file using univariate statistics

It use the **grass_stem** library and it run several times *r.in.lidar* GRASS
command.

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
from grass_stem import temporaryFilesGRASS, stats
import os
import traceback
import sys
from qgis.PyQt.QtWidgets import QMessageBox

import processing
from functools import partial
import traceback
from qgis.core import (QgsTaskManager, QgsMessageLog,
                       QgsProcessingAlgRunnerTask, QgsApplication,
                       QgsProcessingContext, QgsProcessingFeedback,
                       QgsProject, QgsSettings)
from qgis.core import (QgsApplication, QgsTask, QgsMessageLog)


MESSAGE_CATEGORY = 'AlgRunnerTask'
context = QgsProcessingContext()
feedback = QgsProcessingFeedback()


def task_finished(context,params, addToCanvas, successful, results):
    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY, Qgis.Warning)
    else:
        print("Elaboration completed.")
   
    
    out = params['Risultato'];
     
   
    if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'raster')

    STEMMessageHandler.success("{ou} file created".format(ou=out))
      



class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface
        self.LocalCheck.hide()
        #self.groupBox.hide()
        self.QGISextent.hide()
                
        self._insertFileInput(pos=0)
        self._insertLoadParametersButton()
   
        #ritorno_list = ['all','first','last','mid']
        ritorno_list = ['']
        self._insertFirstCombobox("Seleziona il ritorno deiderato", 1, ritorno_list)
        
        metodostat_list = ['n','min','max','range','sum','mean','stddev','variance','coeff_var','median','percentile','skewness','trimmean']
        self._insertSecondCombobox("Seleziona il metodo statistico da utilizzare", 2, metodostat_list)
        
        label1 = "Risoluzione finale del raster"
        self._insertThresholdInteger(label=label1, minn=0, maxx=99, step=0.05, posnum =3)

        label2 = "Percentile valori supportati [1 100] (opzionale - 0.00 per NULL)"
        self._insertSecondThresholdInteger(label=label2, minn=0, maxx=100, step=0.05, posnum =4)
        
        label3 = "Soglia trim (opzionale - 0.00 per NULL)"
        self._insertThirdThresholdInteger(label=label3, minn=0, maxx=99, step=0.05, posnum =5)
        
        label4 = "Classe o classi da mantenere (opzionale)"
        #self._insertFirstLineEdit(label4, 6)        
        
        self._insertLayerChooseCheckBox2Options(label4,True,6)
        
        
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)        


    def onRunLocal(self):
        # Rasterizzazione file LAS
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            #gs = None
            source = str(self.TextIn.text())
            print('source ' + str(source))
            
            #ritorno_list = ['all','first','last','mid']
            ritorno_val = self.BaseInputCombo.currentText()
            
            if ritorno_val == "":
                ritorno = 0
            elif ritorno_val == str(self.BaseInputCombo.count() - 1) :
                ritorno = 99
            else:
                ritorno = int(ritorno_val)            
            
            print('ritorno ' + str(ritorno))
            
            metodostat_list = ['n','min','max','range','sum','mean','stddev','variance','coeff_var','median','percentile','skewness','trimmean']
            metodostat_val = self.BaseInputCombo2.currentText()
            metodostat = metodostat_list.index(metodostat_val)
            print('metodostat ' + str(metodostat))
            
            ris = (self.thresholdi.value())
            
            if ris == 0:
                QMessageBox.warning(self, "Errore nei parametri","La risoluzione dell'immagine in uscita deve essere maggiore di 0")
                dialog = STEMToolsDialog(self.iface, self.toolName)
                dialog.exec_()
                return
            
            
            print('ris ' + str(ris))
            
            percentile = (self.thresholdi2.value())
            if percentile == 0:
                percentile = None
            print('percentile ' + str(percentile))
            
            sogliatrim = (self.thresholdi3.value())
            if sogliatrim == 0:
                sogliatrim = None
            print('sogliatrim ' + str(sogliatrim))
            
            output = self.TextOut.text()
            print('output ' + str(output))
            
            #classfiltlas = self.Linedit.text()
            
            classfiltlas = self.layer_list2.lineEdit().text()
            
            print('classfiltlas ' + str(classfiltlas))

#           bbox = None
#           if self.QGISextent.isChecked():
#               self.mapDisplay()
#               bbox = self.rect_str

            nodata = 0
            if self.NODATAlineEdit.text():
                nodata = float(self.NODATAlineEdit.text())
        
            EPSG = "25832"
            if self.EPSGlineEdit.text():
                EPSG = self.EPSGlineEdit.text()



    
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Rasterizzazione_file_Las')
            
            
            params = {
                    'File_LAS_di_input' : source, 
                    'Seleziona_il_ritorno_desiderato' : ritorno, 
                    'Seleziona_il_metodo_statistico_da_utilizzare' : metodostat,
                    'Risoluzione_finale_del_raster' : ris, 
                    'Percentile_valori_supportati_1_100' : percentile, 
                    'Classe_o_classi_separate_da_uno_spazio_su_cui_filtrare_il_file_Las' :  classfiltlas, 
                    'Soglia_trim' : sogliatrim,
                    'Definisci_valori_NA' : nodata, 
                    'Definisci_EPSG' : EPSG, 
                    'Risultato' : output
                    }

            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
            task.executed.connect(partial(task_finished, context,params,self.AddLayerToCanvas.isChecked()))
            QgsApplication.taskManager().addTask(task)


        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return


