# -*- coding: utf-8 -*-

"""
Tool to select feature using Sequential Forward Floating Feature Selection
(SSF).

It use the STEM library **machine_learning** and **feature_selection** and
the external *numpy*

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
from cgi import logfile

__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMLogging
from stem_utils_server import STEMSettings
from qgis.PyQt.QtWidgets import QMessageBox

import traceback
import os
import processing

##Dati_di_input_vettoriale_di_training=vector polygon
##Colonna_indicazione_classe=Field Dati_di_input_vettoriale_di_training
##Strategia_selezione_feature=selection mean;minimum
##Seleziona_numero_variabili=number
##Dati_di_input_raster=raster
##Output_JM=output file
##Output_features=output file


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



from qgis.PyQt.QtWidgets import QMessageBox



def task_finished(context, params, self, addToCanvas, successful, results):

    self.runButton.setEnabled(True)
    
    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY)
    else:
        print("Elaboration completed.")
        
        out1 = params['Output_JM'];
        out2 = params['Output_features'];
      
        #processing.run("gdal:translate",{
        #                                'INPUT' : out, 
        #                                'TARGET_CRS' : "EPSG:"+ params['Definisci_EPSG'],  
         #                               'NODATA' : params['Definisci_EPSG'], 
        #                                'OUTPUT' : out})
   
        #print(results)
        
        STEMMessageHandler.success("{ou},{ou1} files created".format(ou=out1,ou1=out2))
       
        

   






class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.txt')
        self.toolName = name
        self.iface = iface
        
        self.LocalCheck.hide()
        self.groupBox.hide()
        self.QGISextent.hide()
        
        self._insertSingleInput(label='Dati di input vettoriale di training')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.BaseInput.setCurrentIndex(-1)
        #self.BaseInput.setFilters(QgsMapLayerProxyModel.VectorLayer)
        
        self.labelcol = "Seleziona la colonna con indicazione della classe"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)

        self._insertSecondSingleInput(pos=2, label="Dati di input raster")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1, empty=True)
        self.BaseInput2.setCurrentIndex(-1)

        mets = ['mean', 'minimum']
        self.lm = "Selezione la strategia da utilizzare"
        self._insertMethod(mets, self.lm, 0)
        label1 = "Seleziona numero variabili"
        self._insertThresholdInteger(label=label1, minn=2, maxx=99, step=1, posnum =1)
        
        self._insertSecondFileOutput(label = "Lista feature selezionate", posnum=2, filt= "TXT files (*.txt)")
        
        self.helpui.fillfromUrl(self.SphinxUrl())

        self.AddLayerToCanvas.hide()
        
        self.LabelOut.setText("Report Selezione")
        
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)

    def onClosing(self):
        self.onClosing(self)
        
    def on_field_changed(fieldName):
        print(fieldName)
        print("Layer field changed")        


    def checkInvalidCharsInFields(self, layerName):
        cols = []
        carattere_non_valido = False
        
        layer = STEMUtils.getLayer(layerName.currentText())
        data = layer.dataProvider()
        fields = data.fields()
    
        for i in fields:
            cols.append(i.name())
                
            if (i.name()[:1] == "_"): 
                carattere_non_valido = True
                    
        if (carattere_non_valido ==True):
            QMessageBox.warning(None, "STEM Plugin", 
                                                    "Uno dei campi del dataset inizia con un carattere non valido ['_'], si prega di rimuoverlo prima di procedere.", 
                                                    QMessageBox.Ok, QMessageBox.Ok)
            return -1
        
        return 0


    def onRunLocal(self):
        # Selezione feature per classificazione
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            print('invectsource ' + str(invectsource))
            invectcol = str(self.layer_list.currentText())
            print('invectcol ' + str(invectcol))

            inrast = str(self.BaseInput2.currentText())
            inrastsource = STEMUtils.getLayersSource(inrast)
            print('inrastsource ' + str(inrastsource))


            meth = str(self.MethodInput.currentText())
            if meth == 'mean':
                meth = 0
            elif  meth ==  'minimum':
                meth = 1
            else:
                meth = 2
            print('meth ' + str(meth))

            nfeat = int(self.thresholdi.value())
            print('nfeat ' + str(nfeat))
            out = self.TextOut.text()
            print('out ' + str(out))
            outJM = self.TextOut2.text()
            print('outJM ' + str(outJM))
            
            if (self.checkInvalidCharsInFields(self.BaseInput) == -1):
                return  
                
            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)
                
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Selezione_feature_classificazione')
            
            params = { 
                'Dati_di_input_vettoriale_di_training' : invectsource, 
                'Colonna_indicazione_classe' : invectcol, 
                'Strategia_selezione_feature' : meth, 
                'Seleziona_numero_variabili' : nfeat,
                'Dati_di_input_raster' : inrastsource, 
                'Output_JM' : out, 
                'Output_features' : outJM}
            ###################################################################
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
                                #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)
 
 
            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked()))
            QgsApplication.taskManager().addTask(task)
  
        except:
            #STEMMessageHandler.warning("Aumentare il valore di: numero di variabili")
            QMessageBox.warning(self, "Probabile errore nei parametri",
                                u"Possibile soluzione:\n - Aumentare il valore di: numero di variabili\n - Aumentare il numero di poligoni nel vettoriale di training")
            # TODO: rilanciare il dialog
            dialog = STEMToolsDialog(self.iface, self.toolName)
            dialog.exec_()
            return
            
            STEMMessageHandler.warning("Aumentare il numero di variabili nei parametri della maschera")
            return
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
