# -*- coding: utf-8 -*-

"""
Tool to classify maps through Support vector machine

It use the STEM library **machine_learning** and *numpy*, *sklearn* libraries

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
#from machine_learning import MLToolBox, SEP, BEST_STRATEGY_MEAN
#from exported_objects import return_argument
import os
#import pickle as pkl
#from sklearn.svm import SVC
#import numpy as np
#from pyro_stem import PYROSERVER
#from pyro_stem import MLPYROOBJNAME
#from pyro_stem import ML_PORT
#from osgeo import ogr
import processing


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
        
        label = "Elenco features (opzionale)"
        self._insertFirstLineEdit(label, 4)
        
        self._insertFileInputOption(pos=5, label = "File features (opzionale)", filt="TXT file (*.txt)")
        
        labelc = "Creazione mappa"
        self._insertCheckbox(labelc, 6)
        
        self._insertThresholdInteger(label="Valore C (opzionale - 0.00 per NULL)", minn=0, maxx=99, step=0.05, posnum =7)
        self._insertSecondThresholdInteger(label="Valore sigma (opzionale - 0.00 per NULL)", minn=0, maxx=99, step=0.05, posnum =8)
        
        self._insertThirdSingleInput(label='Aree validazione (opzionale)',pos=7)
        STEMUtils.addLayerToComboBox(self.BaseInput3, 0)
        self.BaseInput3.setCurrentIndex(-1)
        
        self._insertSecondThresholdInteger(label="Numero fold cross validation (opzionale - 0.00 per NULL)", minn=0, maxx=99, step=1, posnum =8)
        
        self._insertSecondFileOutput(label = "Output Info modello", posnum = 9, filt= ".txt")
        self._insertThirdFileOutput(label = "Output Metriche accuratezza", posnum = 10, filt= ".txt")
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()

        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())        
        
        
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

#   def columnsChange2(self):
#       STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2)
#
#   def crossVali(self):
#       if self.checkbox2.isChecked():
#           self.Linedit3.setEnabled(True)
#       else:
#           self.Linedit3.setEnabled(False)
#
#   def kernelChanged(self):
#       kernel = self.BaseInputCombo.currentText()
#       if kernel == 'lineare':
#           self.LabelLinedit2.setEnabled(False)
#           self.Linedit2.setEnabled(False)
#           self.LabelLinedit4.setEnabled(False)
#           self.Linedit4.setEnabled(False)
#           self.LabelLinedit5.setEnabled(False)
#           self.Linedit5.setEnabled(False)
#       elif kernel == 'polinomiale':
#           self.LabelLinedit2.setEnabled(True)
#           self.Linedit2.setEnabled(True)
#           self.LabelLinedit4.setEnabled(True)
#           self.Linedit4.setEnabled(True)
#           self.LabelLinedit5.setEnabled(True)
#           self.Linedit5.setEnabled(True)
#       elif kernel == 'sigmoidale':
#           self.LabelLinedit2.setEnabled(True)
#           self.Linedit2.setEnabled(True)
#           self.LabelLinedit4.setEnabled(True)
#           self.Linedit4.setEnabled(True)
#           self.LabelLinedit5.setEnabled(False)
#           self.Linedit5.setEnabled(False)
#       elif kernel == 'RBF':
#           self.LabelLinedit2.setEnabled(True)
#           self.Linedit2.setEnabled(True)
#           self.LabelLinedit4.setEnabled(False)
#           self.Linedit4.setEnabled(False)
#           self.LabelLinedit5.setEnabled(False)
#           self.Linedit5.setEnabled(False)
#
#   def methodChanged(self):
#       if self.MethodInput.currentText() == 'file':
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
#           self.indexChanged()
#       else:
#           self.labelFO.setEnabled(False)
#           self.TextInOpt.setEnabled(False)
#           self.BrowseButtonInOpt.setEnabled(False)
#           self.label_layer2.setEnabled(False)
#           self.layer_list2.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

#    def getModel(self, csv):
#        kernel_name = {
#            'RBF': 'rbf',
#            'sigmoidale': 'sigmoid',
#            'polinomiale': 'poly',
#            'lineare': 'linear'
#        }
#        
#        kernel = str(self.BaseInputCombo.currentText())
#        params = {'probability': True}       
#        params['kernel'] = kernel_name[kernel]
#        name = 'SVC_k{}'.format(params['kernel'])
#        
#        if self.Linedit.text():
#            params['C'] = float(self.Linedit.text())
#            name += '_C{}'.format(params['C'])
#            
#        if kernel in ['RBF', 'sigmoidale', 'polinomiale']:
#            if self.Linedit2.text():
#                params['gamma'] = float(self.Linedit2.text())
#                name += '_g{}'.format(params['gamma'])
#                
#            if kernel in ['sigmoidale', 'polinomiale']:
#                if self.Linedit4.text():
#                    params['coef0'] = float(self.Linedit4.text())
#                    name += '_r{}'.format(params['coef0'])
#                    
#                if kernel == 'polinomiale':
#                    if self.Linedit5.text():
#                        params['degree'] = int(self.Linedit5.text())
#                        name += '_d{}'.format(params['degree'])
#                        
#        return [{'name': name, 'model': SVC, 'kwargs': params}], csv + name
#
#    def get_input_path_fields(self):
#        """Fornisce al padre una lista di path di input da verificare
#        prima di invocare onRunLocal().
#        """
#        invect = str(self.BaseInput.currentText())
#        inrast = str(self.BaseInput2.currentText())
#        return [STEMUtils.getLayersSource(invect), STEMUtils.getLayersSource(inrast)]
#
#    
#    def get_output_path_fields(self):
#        #Fornisce al padre una lista di path di output da verificare
#        #prima di invocare onRunLocal().
#        
#        optvect = str(self.BaseInputOpt.currentText())
#        if optvect:
#            return [STEMUtils.getLayersSource(optvect)]
#        else:
#            return []
#     
#
#    def check_form_fields(self):
#        """
#        """
#        return []

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        
        try:
            fileraster = str(self.BaseInput.currentText())
            print('fileraster ' + str(fileraster))
            
            trainingaree = str(self.BaseInput2.currentText())
            trainingareesource = STEMUtils.getLayersSource(trainingaree)
            print('trainingareesource ' + str(trainingareesource))
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
            
            valoreC = (self.thresholdi.value())
            if valoreC == 0:
                valoreC = None
            print('valoreC ' + str(valoreC))
            
            valoresigma = (self.thresholdi.value())
            if valoresigma == 0:
                valoresigma = None            
            print('valoresigma ' + str(valoresigma))
            
            areevalidazione = str(self.BaseInput3.currentText())
            if areevalidazione == "":
                areevalidazione = None            
            print('areevalidazione ' + str(areevalidazione))
            
            numerofoldcrossval = int(self.thresholdi2.value())
            if(numerofoldcrossval == 0):
                numerofoldcrossval=None            
            print('numerofoldcrossval ' + str(numerofoldcrossval))
            
            outmappa = str(self.TextOut.text())
            print('outmappa ' + str(outmappa))
            
            outinfomodello = str(self.TextOut2.text())
            print('outinfomodello ' + str(outinfomodello))
            
            outmetricheaccuratezza = str(self.TextOut3.text())
            print('outmetricheaccuratezza ' + str(outmetricheaccuratezza))        
                    
            ###################### R script here ##############################
            processing.run("r:Support_Vector_Machine", { 'File_raster' : fileraster, 'Training_aree' : trainingaree, 
            'Seleziona_colonna_codice_classe' : colindiceclasse, 'Elenco_features' : elencofeaturs, 'File_features' : filefeatures,
            'Creazione_mappa' : creazionemappa, 'Valore_C' : valoreC, 'Valore_Sigma' : valoresigma, 'Aree_validazione' : areevalidazione,
            'Numero_fold_cross_validation' : numerofoldcrossval, 'Output_mappa' : outmappa, 'Output_Info_modello' : outinfomodello,
            'Output_Metriche_accuratezza' : outmetricheaccuratezza})
            ###################################################################
            
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'raster')

        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return        