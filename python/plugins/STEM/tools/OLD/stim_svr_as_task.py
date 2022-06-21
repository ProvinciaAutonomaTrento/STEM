# -*- coding: utf-8 -*-

"""
Tool to perform Support Vector Regression

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
from __future__ import print_function

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
#from sklearn.svm import SVR
#import numpy as np
#import pickle as pkl
import os

#from functools import partial
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



def task_finished(context, params, addToCanvas, successful, results):
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
                
        """
        self._insertSingleInput(label='Dati di input vettoriale di training')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.labelcol = "Seleziona la colonna con indicazione del parametro da stimare"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)

        labelc = "Effettuare la cross validation"
        self._insertSecondCheckbox(labelc, 0)
        self.checkbox2.stateChanged.connect(self.crossVali)

        self._insertThirdLineEdit(label="Inserire il numero di fold della "
                                  "cross validation", posnum=1)
        self.Linedit3.setEnabled(False)
        kernels = ['RBF', 'lineare', 'polinomiale', 'sigmoidale']

        self.lk = 'Selezionare il kernel da utilizzare'
        self._insertFirstCombobox(self.lk, 2, kernels)
        
        self._insertFirstLineEdit(label="Inserire il parametro C (opzionale)", posnum=3)
        self._insertSecondLineEdit(label="Inserire il valore di epsilon (opzionale)",
                                   posnum=4)
        self._insertFourthLineEdit(label="Inserire il valore di gamma (opzionale)",
                                   posnum=5)
        self._insertFifthLineEdit(label="Inserire il valore di r (opzionale)", posnum=6)
        self._insertSixthLineEdit(label="Inserire il valore del grado del polinomio (opzionale)", posnum=7)

        trasf = ['nessuna', 'logaritmo', 'radice quadrata']

        self.lk = 'Selezionare la trasformazione'
        self._insertFourthCombobox(self.lk, 8, trasf)

        mets = ['no', 'manuale', 'file']
        self.lm = "Selezione variabili"
        self._insertMethod(mets, self.lm, 9)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self.llcc = "Colonne delle feature da utilizzare"
        self._insertLayerChooseCheckBox2Options(self.llcc, pos=10)
        self.label_layer2.setEnabled(False)
        self.layer_list2.setEnabled(False)

        self.lio = "File di selezione"
        self._insertFileInputOption(self.lio, 11, "Text file (*.txt)")
        self.labelFO.setEnabled(False)
        self.TextInOpt.setEnabled(False)
        self.BrowseButtonInOpt.setEnabled(False)

        self._insertSingleInputOption(12, label="Vettoriale di validazione")
        STEMUtils.addLayerToComboBox(self.BaseInputOpt, 0, empty=True)
        #self.BaseInputOpt.setEnabled(False)
        #self.labelOpt.setEnabled(False)

        label = "Seleziona la colonna per la validazione"
        self._insertSecondCombobox(label, 13)

        ls = "Indice di accuratezza per la selezione del modello"
        self._insertThirdCombobox(ls, 14, [u'R²', u'MSE'])

        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2,
                                 empty=True)
        self.BaseInputOpt.currentIndexChanged.connect(self.columnsChange2)

        label = "Creare output"
        self._insertCheckbox(label, 15)

        # colonna per i valori della stima
        self.horizontalLayout_field = QHBoxLayout()
        self.labelfield = QLabel()
        self.labelfield.setObjectName("labelfield")
        self.labelfield.setText(self.tr(name, "Colonna per i valori della stima"))
        self.horizontalLayout_field.addWidget(self.labelfield)
        self.TextOutField = QLineEdit()
        self.TextOutField.setObjectName("TextOutField")
        self.TextOutField.setMaxLength(9)
        self.horizontalLayout_field.addWidget(self.TextOutField)
        self.verticalLayout_output.insertLayout(4, self.horizontalLayout_field)
        
        # vettoriale di mappa
        self.horizontalLayout_combo5 = QHBoxLayout()
        self.horizontalLayout_combo5.setObjectName("horizontalLayout_combo5")
        self.LabelCombo5 = QLabel()
        self.LabelCombo5.setObjectName("LabelCombo5")
        self.LabelCombo5.setWordWrap(True)
        self.horizontalLayout_combo5.addWidget(self.LabelCombo5)
        self.BaseInputCombo5 = QComboBox()
        self.BaseInputCombo5.setEditable(True)
        self.BaseInputCombo5.setObjectName("BaseInputCombo5")
        self.horizontalLayout_combo5.addWidget(self.BaseInputCombo5)
        
        self.verticalLayout_input.insertLayout(2, self.horizontalLayout_combo5)
        self.LabelCombo5.setText(self.tr("", "Vettoriale di mappa"))
        STEMUtils.addLayerToComboBox(self.BaseInputCombo5, 0, empty=True)
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        
        self.outputStateChanged()
        self.checkbox.stateChanged.connect(self.outputStateChanged)
        
        self.BaseInputCombo.currentIndexChanged.connect(self.kernelChanged)
        self.kernelChanged()
        """
        
        """
        self.labelcol = "Seleziona la colonna del parametro da stimare"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        #self.BaseInput.currentIndexChanged.connect(self.columnsChange)
        
        self._insertSecondSingleInput(label='Vettoriale di mappa', pos=2)
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)
        
        self._insertThresholdInteger(label="Inserire numero fold della cross validation (opzionale)", minn=0, maxx=99, step=1, posnum =3)
        
        kernel_list = ['lineare', 'polinomiale', 'radiale']
        self._insertFirstCombobox("Seleziona il kernel da utilizzare", 4, kernel_list)
        
        self._insertThresholdInteger(label="Inserire il parametro C (opzionale)", minn=0, maxx=99, step=1, posnum =5)
        
        self._insertSecondThresholdInteger(label="Inserire il valore di epsilon (opzionale)", minn=0, maxx=99, step=1, posnum =6)
        
        self._insertThirdThresholdInteger(label="Inserire il valore di gamma(opzionale)", minn=0, maxx=99, step=1, posnum =7)

        self._insertFourthThresholdInteger(label="Inserire il valore del polinomio", , minn=0, maxx=99, step=1, posnum =8)        
        
        trasformazioni_list = ['nessuna', 'radice quadrata', 'logaritmica']
        self._insertSecondCombobox("Selezionare la trasformazione", 9, trasformazioni_list)
        
        variabili_list = ['no', 'manuale', 'file']
        self._insertThirdCombobox("Selezionare la trasformazione", 10, variabili_list)
        
        label = "Colonne delle feature da utilizzare (opzionale)"
        self._insertFirstLineEdit(label, 11)
        
        self._insertThirdSingleInput(label="Vettoriale di validazione (opzionale)", pos=12)
        STEMUtils.addLayerToComboBox(self.BaseInput3, 0, empty=True)
        
        self.labelcol = "Seleziona colonna per la validazione (opzionale)"
        self._insertSecondLayerChoose(pos=13)
        self.label_layer2.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput3, self.layer_list2)
        
        label = "Nome colonna per i valori della stima"
        self._insertSecondLineEdit(label, 14)
        
        self._insertSecondFileOutput(label = "Accuratezza", posnum = 15)        
        
        """
        
        self._insertSingleInput(label='Dati di input vettoriale di training')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.BaseInput.setCurrentIndex(-1)
        self.labelcol = "Seleziona la colonna del parametro da stimare"
        self._insertLayerChoose(pos=2)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)
        
        self._insertSecondSingleInput(label='Vettoriale di mappa',pos=3)
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)
        self.BaseInput2.setCurrentIndex(-1)
        
        self._insertThresholdInteger(label="Inserire numero fold della cross validation (opzionale - 0.00 per NULL)", minn=0, maxx=99, step=1, posnum =3)
        
        kernel_list = ['lineare', 'polinominiale', 'radiale']
        self._insertFirstCombobox("Selezionare il kernel da utilizzare", 4, kernel_list)
        
        label1 = "Inserire il parametro C (opzionale - 0.00 per NULL)"
        self._insertThresholdInteger(label=label1, minn=0, maxx=99, step=1, posnum =5)

        label2 = "Inserire il parametro epsilon (opzionale - 0.00 per NULL)"
        self._insertSecondThresholdInteger(label=label2, minn=0, maxx=99, step=1, posnum =6)
        
        label3 = "Inserire il valore di gamma (opzionale - 0.00 per NULL)"
        self._insertThirdThresholdInteger(label=label3, minn=0, maxx=99, step=1, posnum =7)

        label4 = "Inserire il valore del polinomio (opzionale - 0.00 per NULL)"
        self._insertFourthThresholdInteger(label=label4, minn=0, maxx=99, step=1, posnum =8)        
        
        trasf_list = ['nessuna', 'radice quadrata', 'logaritmica']
        self._insertSecondCombobox("Selezionala la trasformazione", 9, trasf_list)
        
        selezvariabili_list = ['no', 'manuale', 'file']
        self._insertThirdCombobox("Seleziona variabili", 10, selezvariabili_list)
        self.BaseInputCombo3.currentIndexChanged.connect(self.methodChanged)
      
        
        
        
        label = "Colonne delle features da utilizzare"
        self._insertFirstLineEdit(label, 11)
        self.LabelLinedit.hide()
        self.Linedit.hide()
       
        
        self._insertFileInputOption(pos=12, label = "File di selezione (opzionale)", filt="TXT file (*.txt)")
        #self._insertSecondFileInput(filterr="TXT file (*.txt)", label="File di selezione (opzionale)", pos = 7)
        #self._insertSecondFileInput(filterr="TXT file (*.txt)", label="File di selezione (opzionale)", pos = 12)        

        self.labelFO.hide()
        self.TextInOpt.hide()
        self.BrowseButtonInOpt.hide()
      
        
        
        
        
        self._insertThirdSingleInput(label='Vettoriale di validazione (opzionale)',pos=13)
        STEMUtils.addLayerToComboBox(self.BaseInput3, 0)
        self.BaseInput3.setCurrentIndex(-1)        
        self.labelcol = "Seleziona colonna per la validazione (opzionale)"
        self._insertSecondLayerChoose(pos=14)
        self.label_layer2.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput3, self.layer_list2)
        self.BaseInput3.currentIndexChanged.connect(self.columnsChange3)
        
        label = "Nome colonna risultato stima (max 10 caratteri)"
        self._insertSecondLineEdit(label, 15)        
        
        self._insertSecondFileOutput(label = "Accuratezza", posnum = 16, filt= ".txt")
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()

        
#    def check_number_of_folds(self):
#        if self.checkbox2.isChecked():
#            invect = str(self.BaseInput.currentText())
#            invectsource = STEMUtils.getLayersSource(invect)
#            vect = ogr.Open(invectsource)
#            layer = vect.GetLayer()
#            nfeatures = layer.GetFeatureCount()
#            if nfeatures < int(self.Linedit3.text()):
#                return u"Il numero di features ({}) non può essere inferiore al numero di fold ({}).".format(nfeatures, int(self.Linedit3.text()))
#        return ""        
#
#    def check_vettoriale_validazione(self):
#        if self.BaseInputOpt.currentText() != "" and self.BaseInputCombo2.currentText() == "":
#            return "Devi specificare una colonna per la validazione"
#        else:
#            return ""
#
#    def outputStateChanged(self):
#        if self.checkbox.isChecked():
#            self.LabelOut.setEnabled(True)
#            self.TextOut.setEnabled(True)
#            self.BrowseButton.setEnabled(True)
#            self.AddLayerToCanvas.setEnabled(True)
#            self.labelfield.setEnabled(True)
#            self.TextOutField.setEnabled(True)
#        else:
#            self.LabelOut.setEnabled(False)
#            self.TextOut.setEnabled(False)
#            self.BrowseButton.setEnabled(False)
#            self.AddLayerToCanvas.setEnabled(False)
#            self.labelfield.setEnabled(False)
#            self.TextOutField.setEnabled(False)

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)

    def columnsChange2(self):
        STEMUtils.addColumnsName(self.BaseInput2, self.layer_list2)
                                 
    def columnsChange3(self):
        STEMUtils.addColumnsName(self.BaseInput3, self.layer_list2)

#   def kernelChanged(self):
#       kernel = self.BaseInputCombo.currentText()
#       if kernel == 'lineare':
#           self.LabelLinedit4.setEnabled(False)
#           self.Linedit4.setEnabled(False)
#           self.LabelLinedit5.setEnabled(False)
#           self.Linedit5.setEnabled(False)
#           self.LabelLinedit6.setEnabled(False)
#           self.Linedit6.setEnabled(False)
#       elif kernel == 'polinomiale':
#           self.LabelLinedit4.setEnabled(True)
#           self.Linedit4.setEnabled(True)
#           self.LabelLinedit5.setEnabled(True)
#           self.Linedit5.setEnabled(True)
#           self.LabelLinedit6.setEnabled(True)
#           self.Linedit6.setEnabled(True)
#       elif kernel == 'sigmoidale':
#           self.LabelLinedit4.setEnabled(True)
#           self.Linedit4.setEnabled(True)
#           self.LabelLinedit5.setEnabled(True)
#           self.Linedit5.setEnabled(True)
#           self.LabelLinedit6.setEnabled(False)
#           self.Linedit6.setEnabled(False)
#       elif kernel == 'RBF':
#           self.LabelLinedit4.setEnabled(True)
#           self.Linedit4.setEnabled(True)
#           self.LabelLinedit5.setEnabled(False)
#           self.Linedit5.setEnabled(False)
#           self.LabelLinedit6.setEnabled(False)
#           self.Linedit6.setEnabled(False)
#
    def methodChanged(self):
        if self.BaseInputCombo3.currentText() == 'file':
            self.labelFO.show()
            self.TextInOpt.show()
            self.BrowseButtonInOpt.show()
            self.LabelLinedit.hide()
            self.Linedit.hide()
            self.Linedit.clear()
            
            
            #self.layer_list2.clear()
            #self.labelFO.setEnabled(True)
            #self.TextInOpt.setEnabled(True)
            #self.BrowseButtonInOpt.setEnabled(True)
            #self.label_layer2.setEnabled(False)
            #self.layer_list2.setEnabled(False)
        elif self.BaseInputCombo3.currentText() == 'manuale':
            
            self.labelFO.hide()
            self.TextInOpt.hide()
            self.TextInOpt.clear()
            self.BrowseButtonInOpt.hide()
            self.LabelLinedit.show()
            self.Linedit.show()    
        else:
            self.labelFO.hide()
            self.TextInOpt.hide()
            self.TextInOpt.clear()
            self.BrowseButtonInOpt.hide()
            self.LabelLinedit.hide()
            self.Linedit.hide()
            self.Linedit.clear()
        
        
        
#       if self.MethodInput.currentText() == 'file':
#           self.layer_list2.clear()
#           self.labelFO.setEnabled(True)
#           self.TextInOpt.setEnabled(True)
#           self.BrowseButtonInOpt.setEnabled(True)
#           self.label_layer2.setEnabled(False)
#           self.layer_list2.setEnabled(False)
#       elif self.MethodInput.currentText() == 'manuale':
#           self.label_layer2.setEnabled(True)
#           self.layer_list2.setEnabled(True)
#           self.labelFO.setEnabled(False)
#           self.TextInOpt.setEnabled(False)
#           self.BrowseButtonInOpt.setEnabled(False)
#           STEMUtils.addColumnsName(self.BaseInput, self.layer_list2,
#                                    multi=True)
#       else:
#           self.layer_list2.clear()
#           self.labelFO.setEnabled(False)
#           self.TextInOpt.setEnabled(False)
#           self.BrowseButtonInOpt.setEnabled(False)
#           self.label_layer2.setEnabled(False)
#           self.layer_list2.setEnabled(False)
#
#   def getModel(self, csv):
#       kernel_name = {
#           'RBF': 'rbf',
#           'sigmoidale': 'sigmoid',
#           'polinomiale': 'poly',
#           'lineare': 'linear'
#       }
#       
#       kernel = str(self.BaseInputCombo.currentText())
#       params = {}
#       params['kernel'] = kernel_name[kernel]
#       name = 'SVR_k{}'.format(params['kernel'])
#       
#       if self.Linedit.text():
#           params['C'] = float(self.Linedit.text())
#           name += '_C{}'.format(params['C'])
#           
#       if self.Linedit2.text():
#           params['epsilon'] = float(self.Linedit2.text())
#           
#       if kernel in ['RBF', 'sigmoidale', 'polinomiale']:
#           if self.Linedit4.text():
#               params['gamma'] = float(self.Linedit4.text())
#               name += '_g{}'.format(params['gamma'])
#               
#           if kernel in ['sigmoidale', 'polinomiale']:
#               if self.Linedit5.text():
#                   params['coef0'] = float(self.Linedit5.text())
#                   name += '_r{}'.format(params['coef0'])
#                   
#               if kernel == 'polinomiale':
#                   if self.Linedit6.text():
#                       params['degree'] = int(self.Linedit6.text())
#                       name += '_d{}'.format(params['degree'])
#                       
#       return [{'name': name, 'model': SVR, 'kwargs': params}], csv + name
#
#   def crossVali(self):
#       if self.checkbox2.isChecked():
#           self.Linedit3.setEnabled(True)
#       else:
#           self.Linedit3.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

#    def getTransform(self):
#        if self.BaseInputCombo4.currentText() == 'logaritmo':
#            return np.log, np.exp
#        elif self.BaseInputCombo4.currentText() == 'radice quadrata':
#            return np.sqrt, np.exp2
#        else:
#            return None, None
#
#    def getScoring(self):
#        if self.BaseInputCombo3.currentText() == 'MSE':
#            return 'mean_squared_error'
#        else:
#            return 'r2'
 
    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
#        com = ['python', 'mlcmd.py']
#        log = STEMLogging()
#        invect = str(self.BaseInput.currentText())
#        invectsource = STEMUtils.getLayersSource(invect)
#        invectcol = str(self.layer_list.currentText())
#        cut, cutsource, mask = self.cutInput(invect, invectsource,
#                                             'vector', local=self.LocalCheck.isChecked())
#        prefcsv = "stimsvr_{vect}_{col}".format(vect=invect,
#                                                col=invectcol)
                                                

        try:
            vetditraining = str(self.BaseInput.currentText())
            vetditraining = STEMUtils.getLayersSource(vetditraining);
            print('vetditraining ' + str(vetditraining))
            
            colparamdastimare = str(self.layer_list.currentText())
            print('colparamdastimare ' + str(colparamdastimare))
            
            vetdimappa = str(self.BaseInput2.currentText())
            vetdimappa = STEMUtils.getLayersSource(vetdimappa);
            print('vetdimappa ' + str(vetdimappa))
            
            nrfoldcrossvalid = int(self.thresholdi.value())
            if nrfoldcrossvalid == 0:
                nrfoldcrossvalid = None
            print('nrfoldcrossvalid ' + str(nrfoldcrossvalid))
            
            kerneldautilizzare = self.BaseInputCombo.currentText()
            if kerneldautilizzare == 'lineare':
                kerneldautilizzare = 0
            elif kerneldautilizzare == 'polinominiale':
                kerneldautilizzare = 1
            else:
                kerneldautilizzare = 2
            print('kerneldautilizzare ' + str(kerneldautilizzare))
            
            parametroC = int(self.thresholdi.value())
            if parametroC == 0:
                parametroC = None
            print('parametroC ' + str(parametroC))
            
            valoreepsilon = int(self.thresholdi2.value())
            if valoreepsilon == 0:
                valoreepsilon = None
            print('valoreepsilon ' + str(valoreepsilon))

            valoregamma = int(self.thresholdi3.value())
            if valoregamma == 0:
                valoregamma = None
            print('valoregamma ' + str(valoregamma))

            valpolinomio = int(self.thresholdi4.value())
            if valpolinomio == 0:
                valpolinomio = None
            print('valpolinomio ' + str(valpolinomio))
            
            trasformazione = self.BaseInputCombo2.currentText()
            if trasformazione == 'nessuna':
                trasformazione = 0
            elif trasformazione == 'radice quadrata':
                trasformazione = 1
            else:
                trasformazione = 2
            print('trasformazione ' + str(trasformazione))
            
            selezionavariabili = self.BaseInputCombo3.currentText()
            if selezionavariabili == 'no':
                selezionavariabili = 0
            elif selezionavariabili == 'manuale':
                selezionavariabili = 1
            else:
                selezionavariabili = 2
            print('selezionavariabili ' + str(selezionavariabili))
            
            colonnedautilizzare = self.Linedit.text()
            if colonnedautilizzare == '':
                colonnedautilizzare = None
            print('colonnedautilizzare ' + str(colonnedautilizzare))
            
            filediselezione = str(self.TextInOpt.text())
            print('filediselezione ' + str(filediselezione))
            
            vetdivalidazione = str(self.BaseInput3.currentText())
            vetdivalidazione = STEMUtils.getLayersSource(vetdivalidazione);
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
            if len(nomecolonnavaloristima) > 10:
                nomecolonnavaloristima = nomecolonnavaloristima[:10]
                
                
            print('nomecolonnavaloristima ' + str(nomecolonnavaloristima))
            
            out = str(self.TextOut.text())
            print('out ' + str(out))
            
            accuratezza = str(self.TextOut2.text())
            print('accuratezza ' + str(accuratezza))
            
            
            
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Support_Vector_Regression')
            
            params = { 
                'Dati_di_input_vettoriale_di_training' : vetditraining, 
                'Seleziona_la_colonna_del_parametro_da_stimare' : colparamdastimare, 
                'Vettoriale_di_mappa' : vetdimappa, 
                'Inserire_numero_di_fold_della_cross_validation' : nrfoldcrossvalid, 
                'Seleziona_il_kernel_da_utilizzare' : kerneldautilizzare,
                'Inserire_il_parametro_C' : parametroC, 
                'Inserire_il_valore_di_epsilon' : valoreepsilon, 
                'Inserire_il_valore_di_gamma' : valoregamma, 
                'Inserire_il_valore_del_polinomio' : valpolinomio,
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
            
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
            task.executed.connect(partial(task_finished, context, params, self.AddLayerToCanvas.isChecked()))
            QgsApplication.taskManager().addTask(task)

      
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return

        """
        if not self.LocalCheck.isChecked():
            home = STEMUtils.get_temp_dir()
        else:
            home = STEMSettings.value("stempath")
        try:
            if cut:
                invect = cut
                invectsource = cutsource

            ncolumnschoose = [self.layer_list.itemText(i) for i in range(self.layer_list.count())]
            inrastsource = None
            try:
                ncolumnschoose.remove(invectcol)
            except:
                pass
            prefcsv += "_{n}".format(n=len(ncolumnschoose))

            feat = str(self.MethodInput.currentText())
            fscolumns = None
            if feat == 'file':
                infile = self.TextInOpt.text()
                if os.path.exists(infile):
                    com.extend(['--feature-selection-file', infile])
                    fscolumns = np.loadtxt(infile)
                    ncolumnschoose_new = []
                    i = 0
                    for n in fscolumns:
                        if n == 1:
                            ncolumnschoose_new.append(ncolumnschoose[i])
                        i += 1
                    ncolumnschoose = ncolumnschoose_new
            elif feat == 'manuale':
                ncolumnschoose = STEMUtils.checkLayers(invectsource,
                                                       self.layer_list2, False)

            if self.checkbox2.isChecked():
                nfold = int(self.Linedit3.text())
                prefcsv += "_{n}".format(n=nfold)
            else:
                nfold = None

            models, prefcsv = self.getModel(prefcsv)
            feat = str(self.MethodInput.currentText())

            optvect = str(self.BaseInputOpt.currentText())
            if optvect:
                optvectsource = STEMUtils.getLayersSource(optvect)
                com.extend(['--test-vector', optvectsource])
                if str(self.BaseInputCombo2.currentText()) == '':
                    optvectcols = None
                else:
                    optvectcols = str(self.BaseInputCombo2.currentText())
                    com.extend(['--test-column', optvectcols])
                cut, cutsource, mask = self.cutInput(optvect, optvectsource,
                                                     'vector', local=self.LocalCheck.isChecked())
                if cut:
                    optvect = cut
                    optvectsource = cutsource

            else:
                optvectsource = None
                optvectcols = None

            trasf, utrasf = self.getTransform()
            scor = self.getScoring()

            trnpath = os.path.join(home,
                                   "{p}_csvtraining.csv".format(p=prefcsv))
            crosspath = os.path.join(home,
                                     "{p}_csvcross.csv".format(p=prefcsv))
            out = str(self.TextOut.text())

            com.extend(['--n-folds', str(nfold), '--n-jobs', '1', '--n-best',
                        '1', '--scoring', 'accuracy', '--models', str(models),
                        '--csv-cross', crosspath, '--csv-training', trnpath,
                        '--best-strategy', 'mean', invectsource, invectcol])

            if ncolumnschoose:
                com.extend(['-u', ' '.join(ncolumnschoose)])
            if self.checkbox.isChecked():
                com.extend(['-e', '--output-file', self.TextOut.text()])

            log.debug(' '.join(str(c) for c in com))
            STEMUtils.saveCommand(com)
            if self.LocalCheck.isChecked():
                mltb = MLToolBox()
            else:
                invectsource = STEMUtils.pathClientWinToServerLinux(invectsource)
                inrastsource = STEMUtils.pathClientWinToServerLinux(inrastsource)
                optvectsource = STEMUtils.pathClientWinToServerLinux(optvectsource)
            mltb.set_params(vector=invectsource, column=invectcol,
                            use_columns=ncolumnschoose,
                            raster=inrastsource, models=models,
                            scoring=scor, n_folds=nfold, n_jobs=1,
                            tvector=optvectsource, tcolumn=optvectcols,
                            traster=None, n_best=1,
                            best_strategy=BEST_STRATEGY_MEAN,
                            scaler=None, fselector=None, decomposer=None,
                            transform=trasf, untransform=utrasf)

            nodata = -9999
            overwrite = True
            # ------------------------------------------------------------
            # Extract training samples

            if (not os.path.exists(trnpath) or overwrite):
#                 log.debug('    From:')
#                 log.debug('      - vector: %s' % mltb.vector)
#                 log.debug('      - training column: %s' % mltb.column)
#                 if mltb.use_columns:
#                     log.debug('      - use columns: %s' % mltb.use_columns)
#                 if mltb.raster:
#                     log.debug('      - raster: %s' % mltb.raster)
                if not self.LocalCheck.isChecked():
                    trnpath = STEMUtils.pathClientWinToServerLinux(trnpath)
                X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                             nodata=nodata)
            else:
                log.debug('    Load from:')
                log.debug('      - %s' % trnpath)
                dt = np.loadtxt(trnpath, delimiter=SEP, skiprows=1)
                X, y = dt[:, :-1], dt[:, -1]
            X = X.astype(float)
            log.debug('Training sample shape: {val}'.format(val=X.shape))

            if fscolumns is not None:
                if not self.LocalCheck.isChecked():
                    infile = STEMUtils.pathClientWinToServerLinux(infile)
                X = mltb.data_transform(X=X, y=y, scaler=None,
                                        fscolumns=fscolumns,
                                        fsfile=infile, fsfit=True)

            # ----------------------------------------------------------------
            # Extract test samples
            # Extract test samples
            log.debug('Extract test samples')
            Xtest, ytest = None, None
            if mltb.getTVector() and mltb.getTColumn():
                # extract_training(vector_file, column, csv_file, raster_file=None,
                #                  use_columns=None, delimiter=SEP, nodata=None)
                # testpath = os.path.join(args.odir, args.csvtest)
                testpath = os.path.join(home,
                                        "{p}_csvtest.csv".format(p=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    f = open(testpath, "w")
                    f.close()
                    log.debug('    From:')
                    log.debug('      - vector: %s' % mltb.getTVector())
                    log.debug('      - training column: %s' % mltb.getTColumn())
                    if mltb.getUseColumns():
                        log.debug('      - use columns: %s' % mltb.getUseColumns())
                    if mltb.getRaster():
                        log.debug('      - raster: %s' % mltb.getTRaster())
                    if not self.LocalCheck.isChecked():
                        temp_testpath = STEMUtils.pathClientWinToServerLinux(testpath)
                    else:
                        temp_testpath = testpath
                    Xtest, ytest = mltb.extract_test(csv_file=temp_testpath,
                                                     nodata=nodata)
                    dt = np.concatenate((Xtest.T, ytest[None, :]), axis=0).T
                    with open(testpath, "w") as f:
                        np.savetxt(f, dt, delimiter=SEP, header="# last column is the training.")
                else:
                    log.debug('    Load from:')
                    log.debug('      - %s' % trnpath)
                    dt = np.loadtxt(testpath, delimiter=SEP, skiprows=1)
                    Xtest, ytest = dt[:, :-1], dt[:, -1]
                Xtest = Xtest.astype(float)
                log.debug('Training sample shape: {val}'.format(val=Xtest.shape))

            # ---------------------------------------------------------------
            # Cross Models
            best = None
            if self.checkbox2.isChecked():
                log.debug('Cross-validation of the models')
                bpkpath = os.path.join(home,
                                       "{pref}_best_pickle.csv".format(pref=prefcsv))
                if (not os.path.exists(crosspath) or overwrite):
                    cross = mltb.cross_validation(X=X, y=y, transform=trasf)
                    np.savetxt(crosspath, cross, delimiter=SEP, fmt='%s',
                               header=SEP.join(['id', 'name', 'mean', 'max',
                                                      'min', 'std', 'time']))
                    mltb.find_best(models)
                    best = mltb.select_best()
                    with open(bpkpath, 'w') as bpkl:
                        pkl.dump(best, bpkl)
                else:
                    log.debug('    Read cross-validation results from file:')
                    log.debug('      -  %s' % crosspath)
                    try:
                        with open(bpkpath, 'r') as bpkl:
                            best = pkl.load(bpkl)
                    except:
                        STEMMessageHandler.error("Problem reading file {name} "
                                                 "please remove all files with"
                                                 "prefix {pre} in {path}".format(
                                                 name=bpkpath, pre=prefcsv,
                                                 path=home))
                    order, models = mltb.find_best(models=best)
                    best = mltb.select_best(best=models)
                log.debug('Best models:')
                log.debug(best)

            # ---------------------------------------------------------------
            # test Models
            if Xtest is not None and ytest is not None:
                log.debug('Test models with an indipendent dataset')
                testpath = os.path.join(home, "{p}_csvtest_{vect}_{col}."
                                        "csv".format(p=prefcsv,
                                                     vect=optvect,
                                                     col=optvectcols))
                bpkpath = os.path.join(home,
                                       "{pref}_test_pickle.csv".format(pref=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    test = mltb.test(Xtest=Xtest, ytest=ytest, X=X, y=y,
                                     transform=trasf)
                    np.savetxt(testpath, test, delimiter=SEP, fmt='%s',
                               header=SEP.join(list(test[0]._asdict().keys())))
                    mltb.find_best(models, strategy=return_argument,
                                   key='score_test')
                    best = mltb.select_best()
                    with open(bpkpath, 'w') as bpkl:
                        pkl.dump(best, bpkl)
                    if self.checkbox.isChecked():
                        STEMUtils.copyFile(testpath, out)
                else:
                    with open(bpkpath, 'r') as bpkl:
                        best = pkl.load(bpkl)
                    order, models = mltb.find_best(models=best,
                                                   strategy=return_argument,
                                                   key='score_test')
                    best = mltb.select_best(best=models)
                log.debug('Best models:')
                log.debug(best)

            # ----------------------------------------------------------------
            # execute Models and save the output raster map
            if self.checkbox.isChecked():
                if best is None:
                    order, models = mltb.find_best(models, key='score',
                                                   strategy=return_argument)
                    best = mltb.select_best(best=models)
                log.debug('Execute the model to the whole raster map.')
                map_vector = str(self.BaseInputCombo5.currentText())
                if map_vector:
                    map_vec_source = STEMUtils.getLayersSource(map_vector)
                    map_cut, map_cutsource, map_mask = self.cutInput(map_vector, map_vec_source,
                                                                     'vector', local=self.LocalCheck.isChecked())
                    if map_cut:
                        map_vector = map_cut
                        map_vec_source = map_cutsource
                    finalinp = map_vec_source
                else:
                    finalinp = None
                if self.TextOutField.text():
                    fname = str(self.TextOutField.text())
                else:
                    fname = None

                if not self.LocalCheck.isChecked():
                    temp_out = STEMUtils.pathClientWinToServerLinux(out)
                    finalinp = STEMUtils.pathClientWinToServerLinux(finalinp) if finalinp is not None else None
                else:
                    temp_out = out
                print('finalinp: '.format(finalinp))
                mltb.execute(input_file=finalinp, best=best, transform=trasf,
                             untransform=utrasf, output_file=temp_out,
                             field=fname)
                STEMUtils.copyFile(crosspath, out)
                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(out, 'vector')
                STEMMessageHandler.success("Il file {name} è stato scritto "
                                           "correttamente".format(name=out))
            else:
                STEMMessageHandler.success("Esecuzione completata")
            STEMUtils.removeFiles(home, "{pr}*".format(pr=prefcsv))
            
            if not self.LocalCheck.isChecked():
                mltb._pyroRelease()
        except:
            if not self.LocalCheck.isChecked():
                mltb._pyroRelease()
            STEMUtils.removeFiles(home, "{pr}*".format(pr=prefcsv))
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
        """
