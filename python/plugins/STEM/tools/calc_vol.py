# -*- coding: utf-8 -*-

"""
Tool to calculate volume using allometric equations

It use the **gdal_stem** library

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
import traceback
#from gdal_stem import infoOGR
import os
#from pyro_stem import PYROSERVER
#from pyro_stem import GDAL_PORT
#from pyro_stem import OGRINFOPYROOBJNAME
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


def task_finished(context, params, self, addToCanvas, successful, results):

    self.runButton.setEnabled(True)
    
    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY)
    else:
        print("Elaboration completed.")
        
        out = params['Output'];
        
        if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'vector')

        STEMMessageHandler.success("{ou} file created".format(ou=out))
       


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.shp')
        self.toolName = name
        self.iface = iface
        self.LocalCheck.hide()        
        self.groupBox_2.hide()
        self.QGISextent.hide()
                
        self._insertSingleInput(label='Dati di input')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.BaseInput.setCurrentIndex(-1)
        self.labelcol = "Seleziona la colonna indicazione specie"
        self._insertLayerChoose(pos=2)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        
        self.labelcol = "Seleziona la colonna indicazione diametro"
        self._insertSecondLayerChoose(pos=3)
        self.label_layer2.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list2)
        
        self.labelcol = "Seleziona la colonna indicazione altezza"
        self._insertThirdLayerChoose(pos=4)
        self.label_layer3.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list3)
        
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def columnsChange(self):
        """Change columns in the combobox according with the layer choosen"""
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list2)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list3)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
        
            name = str(self.BaseInput.currentText())
            source = str(STEMUtils.getLayersSource(name))
            print('source ' + str(source))
            

            colindiceclasse =  str(self.layer_list.currentText())
            print('colindiceclasse ' + str(colindiceclasse))            
            
            specie =  str(self.layer_list.currentText())
            print('specie ' + str(specie))
            dia =  str(self.layer_list2.currentText())
            print('dia ' + str(dia))
            hei =  str(self.layer_list3.currentText())
            print('hei ' + str(hei))
            
            out = str(self.TextOut.text())
            print('out ' + str(out))
            
            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)
       
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Stima_volume_formule_allometriche')
            
            params = { 
                    'Dati_di_input' : source, 
                    'Seleziona_colonna_indicazione_specie' : specie, 
                    'Seleziona_colonna_indicazione_diametro' : dia, 
                    'Seleziona_colonna_indicazione_altezza' : hei,
                    'Output' : out
                    }

            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
            
                               #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)


            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked()))
            QgsApplication.taskManager().addTask(task)

      
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
        
        """
        com = ['python', 'gdal_stem.py']
        try:
            name = str(self.BaseInput.currentText())
            original_name = name
            source = str(STEMUtils.getLayersSource(name))
            original_source = source
            specie = STEMUtils.checkLayers(source, self.layer_list, False)
            dia = STEMUtils.checkLayers(source, self.layer_list2, False)
            hei = STEMUtils.checkLayers(source, self.layer_list3, False)
            cut, cutsource, mask = self.cutInput(name, source, 'vector', local=self.LocalCheck.isChecked())
            if cut:
                name = cut
                source = cutsource

            out = str(self.TextOut.text())
            if self.overwrite and os.path.exists(out):
                out_pref = os.path.basename(out).replace('.shp', '')
                out_path = os.path.dirname(out)
                STEMUtils.removeFiles(out_path, pref=out_pref)

            com.extend(['--volume', out, '--height', hei, '--diameter', dia,
                        '--specie', specie])
            STEMUtils.saveCommand(com)
            if self.LocalCheck.isChecked():
                ogrinfo = infoOGR()
            else:
                source = STEMUtils.pathClientWinToServerLinux(source)
            ogrinfo.initialize(source, 1)
            ogrinfo.calc_vol(out, hei, dia, specie)

            if self.AddLayerToCanvas.isChecked():
                if original_name == name:
                    STEMUtils.reloadVectorLayer(original_name)
                else:
                    STEMUtils.addLayerIntoCanvas(cutsource, 'vector')
                
            if not self.LocalCheck.isChecked():
                ogrinfo._pyroRelease()
        except:
            if not self.LocalCheck.isChecked():
                ogrinfo._pyroRelease()
            
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
         """
