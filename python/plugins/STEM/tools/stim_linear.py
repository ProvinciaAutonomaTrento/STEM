# -*- coding: utf-8 -*-

"""
Tool to perform linear regression

It use the STEM library **machine_learning** and external *numpy*, *sklearn*
libraries

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
from builtins import range
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QComboBox

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMLogging
from stem_utils_server import STEMSettings
import traceback
#from machine_learning import MLToolBox, SEP, BEST_STRATEGY_MEAN
#from exported_objects import return_argument
#import numpy as np
#import pickle as pkl
import os
#from pyro_stem import PYROSERVER
#from pyro_stem import MLPYROOBJNAME
#from pyro_stem import ML_PORT
#from osgeo import ogr
#from functools import partial
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



from qgis.PyQt.QtWidgets import QMessageBox



def task_finished(context, params, self, addToCanvas, successful, results):
    
    self.runButton.setEnabled(True)
 
    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY)
    else:
        print("Elaboration completed.")
        
        
        out = params['Risultato'];
      
        if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'vector')

        STEMMessageHandler.success("{ou} file created".format(ou=out))
        


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.shp')
        self.toolName = name
        self.iface = iface
        
        self.LocalCheck.hide()
        self.QGISextent.hide()        
        
        self._insertSingleInput(label='Dati di input vettoriale di training                                 ')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.BaseInput.setCurrentIndex(-1)
        
        self.labelcol = "Seleziona la colonna del parametro da stimare"
        self._insertLayerChoose(pos=2)
        
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        
        
        selezvariabili_list = ['no', 'manuale', 'file']
        self._insertSecondCombobox("Seleziona variabili", 3, selezvariabili_list)
        self.BaseInputCombo2.currentIndexChanged.connect(self.methodChanged)
      
        
         
        
        self._insertFileInputOption(pos=4, label = "File di selezione (opzionale)", filt="TXT file (*.txt)")
        #self._insertSecondFileInput(filterr="TXT file (*.txt)", label="File di selezione (opzionale)", pos = 7)
    
        
        self._insertLocalLayerChooseCheckBox69("Colonne delle features da utilizzare \n(sono mostrate solo le colonne con egual Nome e Type nei dataset training e mappa)", pos=6)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list69)
      
        
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)
        
        self._insertSecondSingleInput(label='Vettoriale di mappa',pos=3)
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)
        self.BaseInput2.setCurrentIndex(-1)
        
        
        self.BaseInput2.currentIndexChanged.connect(self.columnsChangeWithCheck)
      
        

        
       
        self.labelFO.hide()
        self.TextInOpt.hide()
        self.BrowseButtonInOpt.hide()
      
        label = "Colonne delle features da utilizzare"
        self._insertFirstLineEdit(label, 5)
        self.LabelLinedit.hide()
        self.Linedit.hide()
        
                
        self._insertThresholdInteger(label="Inserire numero fold della cross validation (opzionale)", minn=0, maxx=99, step=1, posnum =6)
        
        trasf_list = ['nessuna', 'radice quadrata', 'logaritmica']
        self._insertFirstCombobox("Selezionala la trasformazione", 7, trasf_list)
        

        
        
        
        self._insertThirdSingleInput(label='Vettoriale di validazione (opzionale)',pos=8)
        STEMUtils.addLayerToComboBox(self.BaseInput3, 0, empty=True)
        self.BaseInput3.setCurrentIndex(-1)   
        
        self.labelcol = "Seleziona colonna per la validazione (opzionale)"
        self._insertSecondLayerChoose(pos=9)
        self.label_layer2.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput3, self.layer_list2)
        self.BaseInput3.currentIndexChanged.connect(self.columnsChange3)
        
        
        self.label_layer2.hide()
        self.layer_list2.hide()
                                 
        
        #-------------------------------
        #COSA BRUTTA BRUTTA DA CAMBIARE

        self.horizontalLayout_layer = QHBoxLayout()
        self.horizontalLayout_layer.setObjectName("horizontalLayout_layer")
        self.label_layer99 = QLabel()
        self.label_layer99.setObjectName("label_layer_99")
        self.label_layer99.setText("")
        self.horizontalLayout_layer.addWidget(self.label_layer99)
        self.verticalLayout_input.insertLayout(100, self.horizontalLayout_layer)

        #-------------------------------
        #FINE COSA BRUTTA BRUTTA DA CAMBIARE

        
        
        
        
        
        
        
        label = "Nome colonna risultato stima (max 10 caratteri)"
        self._insertSecondLineEdit(label, 10)
        
        self._insertSecondFileOutput(label = "Accuratezza", posnum = 11, filt= "TXT files (*.txt)")
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()

        self.LabelOut2.hide()
        self.TextOut2.hide()
        self.BrowseButton2.hide()
        
        self.label_layer69.hide()
        self.layer_list69.hide() 









#   def check_vettoriale_validazione(self):
#       if self.BaseInputOpt.currentText() != "" and self.BaseInputCombo2.currentText() == "":
#           return "Devi specificare una colonna per la validazione"
#       else:
#           return ""   
#   
#   def check_number_of_folds(self):
#       if self.checkbox2.isChecked():
#           invect = str(self.BaseInput.currentText())
#           invectsource = STEMUtils.getLayersSource(invect)
#           vect = ogr.Open(invectsource)
#           layer = vect.GetLayer()
#           nfeatures = layer.GetFeatureCount()
#           if nfeatures < int(self.Linedit3.text()):
#               return u"Il numero di features ({}) non può essere inferiore al numero di fold ({}).".format(nfeatures, int(self.Linedit3.text()))
#       return ""
#
#   def outputStateChanged(self):
#       if self.checkbox.isChecked():
#           self.LabelOut.setEnabled(True)
#           self.TextOut.setEnabled(True)
#           self.BrowseButton.setEnabled(True)
#           self.AddLayerToCanvas.setEnabled(True)
#           self.labelfield.setEnabled(True)
#           self.TextOutField.setEnabled(True)
#       else:
#           self.LabelOut.setEnabled(False)
#           self.TextOut.setEnabled(False)
#           self.BrowseButton.setEnabled(False)
#           self.AddLayerToCanvas.setEnabled(False)
#           self.labelfield.setEnabled(False)
#           self.TextOutField.setEnabled(False)


    


    def columnsChangeWithCheck(self):
        
        STEMUtils.addColumnsNameWithCheck(self.BaseInput, self.BaseInput2, self.layer_list69)
       
        #STEMUtils.addColumnsName(self.BaseInput, self.layer_list69)
  

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        
        
        STEMUtils.addColumnsNameWithCheck(self.BaseInput, self.BaseInput2, self.layer_list69)
       
        #STEMUtils.addColumnsName(self.BaseInput, self.layer_list69)
       

    def columnsChange2(self):
        STEMUtils.addColumnsName(self.BaseInput2, self.layer_list2)
                                 
    def columnsChange3(self):
        STEMUtils.addColumnsName(self.BaseInput3, self.layer_list2)

        if self.BaseInput3.currentText() == "":
            self.LabelOut2.hide()
            self.TextOut2.hide()
            self.BrowseButton2.hide()
            self.label_layer2.hide()
            self.layer_list2.hide() 
            
        else:
            self.LabelOut2.show()
            self.TextOut2.show()
            self.BrowseButton2.show()
            self.label_layer2.show()
            self.layer_list2.show() 


    def methodChanged(self):
        if self.BaseInputCombo2.currentText() == 'file':
            self.labelFO.show()
            self.TextInOpt.show()
            self.BrowseButtonInOpt.show()
            self.LabelLinedit.hide()
            self.Linedit.hide()
            self.Linedit.clear()
            self.label_layer69.hide()
            self.layer_list69.hide() 
            
            #self.layer_list2.clear()
            #self.labelFO.setEnabled(True)
            #self.TextInOpt.setEnabled(True)
            #self.BrowseButtonInOpt.setEnabled(True)
            #self.label_layer2.setEnabled(False)
            #self.layer_list2.setEnabled(False)
        elif self.BaseInputCombo2.currentText() == 'manuale':
            
            self.labelFO.hide()
            self.TextInOpt.hide()
            self.TextInOpt.clear()
            self.BrowseButtonInOpt.hide()
            #self.LabelLinedit.show()
            #self.Linedit.show()   
            self.label_layer69.show()
            self.layer_list69.show()  
        else:
            self.labelFO.hide()
            self.TextInOpt.hide()
            self.TextInOpt.clear()
            self.BrowseButtonInOpt.hide()
            self.LabelLinedit.hide()
            self.Linedit.hide()
            self.Linedit.clear()
            self.label_layer69.hide()
            self.layer_list69.hide() 
            
            
#            self.label_layer2.setEnabled(True)
#            self.layer_list2.setEnabled(True)
#            self.labelFO.setEnabled(False)
#            self.TextInOpt.setEnabled(False)
#            self.BrowseButtonInOpt.setEnabled(False)
#            STEMUtils.addColumnsName(self.BaseInput, self.layer_list2,
#                                     multi=True)
#        else:
#            self.layer_list2.clear()
#            self.labelFO.setEnabled(False)
#            self.TextInOpt.setEnabled(False)
#            self.BrowseButtonInOpt.setEnabled(False)
#            self.label_layer2.setEnabled(False)
#            self.layer_list2.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

#    def getTransform(self):
#        if self.BaseInputCombo.currentText() == 'logaritmo':
#            return np.log, np.exp
#        elif self.BaseInputCombo.currentText() == 'radice quadrata':
#            return np.sqrt, np.exp2
#        else:
#            return None, None
#
#    def getScoring(self):
#        if self.BaseInputCombo3.currentText() == 'MSE':
#            return 'mean_squared_error'
#        else:
#            return 'r2'
#
#    def crossVali(self):
#        if self.checkbox2.isChecked():
#            self.Linedit3.setEnabled(True)
#        else:
#            self.Linedit3.setEnabled(False)
            

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            vetditraining = str(self.BaseInput.currentText())
            vetditraining = STEMUtils.getLayersSource(vetditraining)
            print('vetditraining ' + str(vetditraining))
            
            colparamdastimare = str(self.layer_list.currentText())
            print('colparamdastimare ' + str(colparamdastimare))
            
            vetdimappa = str(self.BaseInput2.currentText())
            vetdimappa = STEMUtils.getLayersSource(vetdimappa)
            print('vetdimappa ' + str(vetdimappa))
            
            nrfoldcrossvalid = int(self.thresholdi.value())
            if nrfoldcrossvalid == 0:
                nrfoldcrossvalid = None
            print('nrfoldcrossvalid ' + str(nrfoldcrossvalid))
            
            trasformazione = self.BaseInputCombo.currentText()
            if trasformazione == 'nessuna':
                trasformazione = 0
            elif trasformazione == 'radice quadrata':
                trasformazione = 1
            else:
                trasformazione = 2
            print('trasformazione ' + str(trasformazione))            
            
            selezionavariabili = self.BaseInputCombo2.currentText()
            if selezionavariabili == 'no':
                selezionavariabili = 0
            elif selezionavariabili == 'manuale':
                selezionavariabili = 1
            else:
                selezionavariabili = 2            
            print('selezionavariabili ' + str(selezionavariabili))
            
            
            nocolumnschoose = str(self.layer_list69.currentData())
            nocolumnschoose = nocolumnschoose.replace("'", "")
            nocolumnschoose = nocolumnschoose.replace("[", "")
            nocolumnschoose = nocolumnschoose.replace("]", "")
            nocolumnschoose = nocolumnschoose.replace(",", "")
            
            print('nocolumnschoose ' + str(nocolumnschoose))
             
            #colonnedautilizzare = self.Linedit.text()
            
            colonnedautilizzare =  nocolumnschoose
            if colonnedautilizzare == '':
                colonnedautilizzare = None
            print('colonnedautilizzare ' + str(colonnedautilizzare))
            
            #filediselezione = str(self.TextIn2.text())
            #print('filediselezione ' + str(filediselezione))
            
            filediselezione = str(self.TextInOpt.text())
    
            print('filediselezione ' + str(filediselezione))
         
            vetdivalidazione = str(self.BaseInput3.currentText())
            vetdivalidazione = STEMUtils.getLayersSource(vetdivalidazione)
 
            if vetdivalidazione == "":
                vetdivalidazione = None
            print('vetdivalidazione ' + str(vetdivalidazione))        
            
            colonnavalidazione = str(self.layer_list2.currentText())
            if colonnavalidazione == "":
                colonnavalidazione = None            
            print('colonnavalidazione ' + str(colonnavalidazione))
            
            nomecolonnavaloristima = self.Linedit2.text()
            if nomecolonnavaloristima == '':
                nomecolonnavaloristima = None            
                QMessageBox.warning(self, "Nome colonna risultato Errato",
                                 "Il nome della colonna del risultato stima inserito è nullo o errato.")
                return 
     
            if len(nomecolonnavaloristima) > 10:
                nomecolonnavaloristima = nomecolonnavaloristima[:10]
       
     
            print('nomecolonnavaloristima ' + str(nomecolonnavaloristima))
            
            out = str(self.TextOut.text())
            print('out ' + str(out))
            
            accuratezza = str(self.TextOut2.text())
            print('accuratezza ' + str(accuratezza))


            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)
     

            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Stimatore_lineare')
            
            params = { 
                   'Dati_di_input_vettoriale_di_training' : vetditraining, 
                   'Seleziona_la_colonna_del_parametro_da_stimare' : colparamdastimare, 
                   'Vettoriale_di_mappa' : vetdimappa, 
                   'Inserire_numero_di_fold_della_cross_validation' : nrfoldcrossvalid, 
                   'Selezionare_la_trasformazione' : trasformazione,
                   'Seleziona_variabili' : selezionavariabili, 
                   'Colonne_delle_feature_da_utilizzare' : colonnedautilizzare, 
                   'File_di_selezione' : filediselezione, 
                   'Vettoriale_di_validazione' : vetdivalidazione,
                   'Seleziona_colonna_per_la_validazione' : colonnavalidazione, 
                   'Risultato' : out, 
                   'Nome_colonna_per_i_valori_della_stima' : nomecolonnavaloristima,
                   'Accuratezza' : accuratezza
                   }
            ###################################################################
            
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback= feedback)
           
                    #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)
           
            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked(), self.textBrowser))
            QgsApplication.taskManager().addTask(task)
            
        
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
#===                              