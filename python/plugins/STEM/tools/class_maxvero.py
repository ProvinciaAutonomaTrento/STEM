# -*- coding: utf-8 -*-

"""
Tool to classify maps through Maximum likelihood.

It use the STEM library machine_learning and numpy, sklearn library

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

from qgis.PyQt import QtCore
from qgis.PyQt import QtGui

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMLogging
from stem_utils_server import STEMSettings
import traceback
#from sklearn.naive_bayes import GaussianNB
#from machine_learning import MLToolBox, SEP, BEST_STRATEGY_MEAN
#from exported_objects import return_argument
import os
from osgeo import ogr
#import pickle as pkl
#import numpy as np
#from pyro_stem import PYROSERVER
#from pyro_stem import MLPYROOBJNAME
#from pyro_stem import ML_PORT
#from osgeo import ogr
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
        
        out = results['Output_mappa']        
        out1 = results['Output_Info_modello'] 
               
        out2 = params['Output_Metriche_accuratezza']        
        
        
        if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'raster')

        STEMMessageHandler.success("{ou},{ou1},{ou2} files created".format(ou=out,ou1=out1,ou2=out2))
    
     
        


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface
        
        self.LocalCheck.hide()
        self.QGISextent.hide()
                
        self._insertSingleInput(label="File raster")
        STEMUtils.addLayerToComboBox(self.BaseInput, 1, empty=True)
        self.BaseInput.setCurrentIndex(-1)
        
        self._insertSecondSingleInput(label='Training aree',pos=2)
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)
        self.BaseInput2.setCurrentIndex(-1)
        self.labelcol = "Seleziona la colonna codice classe"
        self._insertLayerChoose(pos=3)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput2, self.layer_list)
        self.BaseInput2.currentIndexChanged.connect(self.columnsChange)
        
        
        labelc = "Creazione mappa (opzionale)"
        self._insertCheckbox(labelc, 4)
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(self.onClicked) 
        
        label = "Elenco features (opzionale)"
        self._insertFirstLineEdit(label, 5)
        
        self._insertFileInputOption(pos=6, label = "File features (opzionale)", filt="TXT file (*.txt)")
        
        
        self._insertThirdSingleInput(label='Aree validazione (opzionale)',pos=7)
        STEMUtils.addLayerToComboBox(self.BaseInput3, 0,empty=True)
        self.BaseInput3.setCurrentIndex(-1)
        self.BaseInput3.currentIndexChanged.connect(self.methodChanged)
       
        
        self._insertSecondThresholdInteger(label="Numero fold cross validation (opzionale - 0.00 per NULL)", minn=0, maxx=99, step=1, posnum =8)
        
        self._insertSecondFileOutput(label = "Output Info modello", posnum = 9, filt= "TXT files (*.txt)")
        self._insertThirdFileOutput(label = "Output Metriche accuratezza", posnum = 10, filt= "TXT files (*.txt)")
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()

        
        self.LabelOut3.hide()
        self.TextOut3.hide()
        self.BrowseButton3.hide()
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())
    
    
    def onClicked(self):
        if self.checkbox.isChecked():
            self.TextOut.setText("")
            self.LabelOut.show()
            self.TextOut.show()
            self.BrowseButton.show()
            self.AddLayerToCanvas.show()
        else:
            self.LabelOut.hide()
            self.TextOut.hide()
            self.TextOut.setText("Fakepath")
            self.BrowseButton.hide()
            self.AddLayerToCanvas.hide()
    
    
    def methodChanged(self):
        if self.BaseInput3.currentText() != "":
            self.LabelOut3.show()
            self.TextOut3.show()
            self.BrowseButton3.show()
        else:
            self.LabelOut3.hide()
            self.TextOut3.hide()
            self.BrowseButton3.hide()
         
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
#
#   def check_vettoriale_validazione(self):
#       if self.BaseInputOpt.currentText() != "" and self.BaseInputCombo2.currentText() == "":
#           return "Devi specificare una colonna per la validazione"
#       else:
#           return ""   
#
#   def outputStateChanged(self):
#       if self.checkbox.isChecked():
#           self.LabelOut.setEnabled(True)
#           self.TextOut.setEnabled(True)
#           self.BrowseButton.setEnabled(True)
#           self.AddLayerToCanvas.setEnabled(True)
#       else:
#           self.LabelOut.setEnabled(False)
#           self.TextOut.setEnabled(False)
#           self.BrowseButton.setEnabled(False)
#           self.AddLayerToCanvas.setEnabled(False)
#
#   def indexChanged(self):
#       if self.BaseInput2.currentText() != "":
#           STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)
#           self.label_layer2.setText(self.tr("", self.llcc))
#       else:
#           STEMUtils.addColumnsName(self.BaseInput, self.layer_list2, True)
#           self.label_layer2.setText(self.tr("", "Colonne delle feature da "
#                                             "utilizzare"))

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput2, self.layer_list)

#    def columnsChange2(self):
#        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2)
#
#    def crossVali(self):
#        if self.checkbox2.isChecked():
#            self.Linedit3.setEnabled(True)
#        else:
#            self.Linedit3.setEnabled(False)
#
#    def methodChanged(self):
#        if self.MethodInput.currentText() == 'file':
#            self.labelFO.setEnabled(True)
#            self.TextInOpt.setEnabled(True)
#            self.BrowseButtonInOpt.setEnabled(True)
#            self.label_layer2.setEnabled(False)
#            self.layer_list2.setEnabled(False)
#        elif self.MethodInput.currentText() == 'manuale':
#            self.label_layer2.setEnabled(True)
#            self.layer_list2.setEnabled(True)
#            self.labelFO.setEnabled(False)
#            self.TextInOpt.setEnabled(False)
#            self.BrowseButtonInOpt.setEnabled(False)
#            self.indexChanged()
#        else:
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

    def check_number_of_classes(self):
            invect = str(self.BaseInput2.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            vect = ogr.Open(invectsource)
            layer = vect.GetLayer()
            nfeatures = layer.GetFeatureCount()
            
            list_field = [self.layer_list.currentText()]
            auxiliaryList = []
            
            for feature in layer:
                values_list = [feature.GetField(j) for j in list_field]
            
                if values_list not in auxiliaryList:
                    auxiliaryList.append(values_list)
            
            if len(auxiliaryList) < 2:
                return False
            return True


    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        
        if self.TextOut2.text()=="":
            # STEMMessageHandler.error("Selezionare il formato di output")
            QMessageBox.warning(self, "Parametro errato",
                                 "File di output del modello non impostato.")
                           
            return 2
        
      #  if not self.check_number_of_classes():
      #      # STEMMessageHandler.error("Selezionare il formato di output")
      #      QMessageBox.warning(self, "Parametro errato",
      #                           "Il numero di classi per la classificazione deve essere maggiore di 1.")
      #                     
      #      return 2
        
        try:
            fileraster = str(self.BaseInput.currentText())
            fileraster = STEMUtils.getLayersSource(fileraster)
         
            print('fileraster ' + str(fileraster))
            
            trainingaree = str(self.BaseInput2.currentText())
            trainingaree = STEMUtils.getLayersSource(trainingaree)
         
            colindiceclasse =  str(self.layer_list.currentText())
            print('colindiceclasse ' + str(colindiceclasse))
            
            elencofeaturs = self.Linedit.text()
            print('elencofeaturs ' + str(elencofeaturs))
            
            filefeatures = str(self.TextInOpt.text())
            print('filefeatures ' + str(filefeatures))
            
            if self.checkbox.isChecked():
                creazionemappa = 0
            else:
                creazionemappa = 1
            print('creazionemappa ' + str(creazionemappa))
            
            areevalidazione = str(self.BaseInput3.currentText())
            areevalidazione = STEMUtils.getLayersSource(areevalidazione)
         
            if areevalidazione == "":
                areevalidazione = None            
            print('areevalidazione ' + str(areevalidazione))
            
            numerofoldcrossval = int(self.thresholdi2.value())
            if(numerofoldcrossval == 0):
                numerofoldcrossval=None            
            print('numerofoldcrossval ' + str(numerofoldcrossval))
            
            outmappa = str(self.TextOut.text())
            print('outmappa ' + str(outmappa))
            if outmappa == "Fakepath":
                outmappa = ""
                
            outinfomodello = str(self.TextOut2.text())
            print('outinfomodello ' + str(outinfomodello))
            
            outmetricheaccuratezza = str(self.TextOut3.text())
            print('outmetricheaccuratezza ' + str(outmetricheaccuratezza))        
                    
                    
            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)
              
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Massima_Verosomiglianza')
            
            params = { 
                'File_raster' : fileraster, 
                'Training_aree' : trainingaree, 
                'Seleziona_colonna_codice_classe' : colindiceclasse, 
                'Elenco_features' : elencofeaturs, 
                'File_features' : filefeatures,
                'Creazione_mappa' : creazionemappa, 
                'Aree_validazione' : areevalidazione,
                'Numero_fold_cross_validation' : numerofoldcrossval, 
                'Output_mappa' : outmappa, 
                'Output_Info_modello' : outinfomodello,
                'Output_Metriche_accuratezza' : outmetricheaccuratezza
                }
            ###################################################################
            
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
                                                #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)

            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked()))
            QgsApplication.taskManager().addTask(task)

      
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return      
