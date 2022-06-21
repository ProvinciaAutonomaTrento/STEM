# -*- coding: utf-8 -*-

"""
Tool to perform variable selection

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

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMLogging
from stem_utils_server import STEMSettings
#from sklearn.feature_selection import SelectKBest, f_regression
import traceback
#from machine_learning import MLToolBox, SEP, NODATA, BEST_STRATEGY_MEAN
import os
#import numpy as np
from gdal_stem import infoOGR
#from pyro_stem import PYROSERVER
#from pyro_stem import MLPYROOBJNAME
#from pyro_stem import ML_PORT
from qgis.PyQt.QtCore import Qt
import processing

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.txt')
        self.toolName = name
        self.iface = iface
        self.LocalCheck.hide()
        self.QGISextent.hide()

        self.groupBox.hide()
        self.groupBox_2.hide()

        self.AddLayerToCanvas.hide()

        self._insertSingleInput(label='Dati di input vettoriale di training')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.BaseInput.setCurrentIndex(-1)
        self.labelcol = "Seleziona la colonna con indicazione del parametro da stimare"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)
        
        self._insertLayerChooseCheckBox2(label = "Colonna da non considerare nella selezione", pos=2)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list2)
        
        self._insertSecondFileOutput(label = "Variabili significative", posnum=3, filt= ".txt")        

        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        
        self.layer_list.currentIndexChanged.connect(self.column_to_estimate_changed)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)
        self.column_to_estimate_changed()
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()
        
        

    def column_to_estimate_changed(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list2)
        column_to_estimate = self.layer_list.currentText()
        self.layer_list2.removeItem(self.layer_list2.findText(column_to_estimate))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.column_to_estimate_changed()

    def onClosing(self):
        self.onClosing(self)

    
    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            vetditraining = str(self.BaseInput.currentText())
            print('vetditraining ' + str(vetditraining))
            
            colparamdastimare = str(self.layer_list.currentText())
            print('colparamdastimare ' + str(colparamdastimare))
                    
            nocolumnschoose = str(self.layer_list2.currentText())
            print('nocolumnschoose ' + str(nocolumnschoose))
             
            out = self.TextOut.text()
            print('out ' + str(out))
            
            outvariabilisignificative = self.TextOut2.text()
            print('outvariabilisignificative ' + str(outvariabilisignificative))
                                       
            ###################### R script here ##############################
            processing.run("r:Selezione_variabili_di_stima", { 'Dati_di_input_vettoriale_di_training' : vetditraining, 'Seleziona_colonna_con_indicazione_del_parametro_da_stimare' : colparamdastimare, 
            'Colonna_da_non_considerare_nella_selezione' : nocolumnschoose, 'Risultato' : out,
            'Variabili_significative' : outvariabilisignificative})
            ###################################################################

            return
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return

