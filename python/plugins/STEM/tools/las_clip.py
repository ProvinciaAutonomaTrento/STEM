# -*- coding: utf-8 -*-

"""
Tool to clip LAS file

It use the **las_stem** library

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
from stem_utils import STEMMessageHandler, STEMUtils
from stem_utils_server import STEMSettings
from las_stem import stemLAS
import traceback
from gdal_stem import infoOGR
import time
from qgis.PyQt.QtWidgets import QMessageBox

import os
#from pyro_stem import PYROSERVER
#from pyro_stem import LASPYROOBJNAME
#from pyro_stem import LAS_PORT
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


def task_finished(context, self, successful, results):
    
    self.runButton.setEnabled(True)
    
    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY, Qgis.Warning)
    else:
        print("Elaboration completed.")
   
        print(results)
        outLas = results['Output']        
        
        t = time.time()
        while not os.path.isfile(outLas):
            if time.time()-t > 5:
                STEMMessageHandler.error("{ou} file not created".format(ou=outLas))
                return
            time.sleep(.1)
            STEMMessageHandler.success("{ou} file created".format(ou=outLas))
        
        print("Task completed.")
        
        STEMMessageHandler.success("{ou} file created".format(ou=outLas))
   


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        
        filters = "LAS files (*.las);;LAZ files (*.laz)"
        BaseDialog.__init__(self, name, iface.mainWindow(), filters)
  
        #BaseDialog.__init__(self, name, iface.mainWindow(), suffix='')
        self.toolName = name
        self.iface = iface
        
        self.QGISextent.hide()
        self.AddLayerToCanvas.hide()
        self.LocalCheck.hide()
        
        self.groupBox.hide()
        self.groupBox_2.hide()

        self._insertFileInput()
        
        self._insertSecondSingleInput(label="Maschera")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)
        self.BaseInput2.setCurrentIndex(-1)
#        self.AddLayerToCanvas.setText(self.tr(name, "Utilizzare la maschera"))

#        label_inv = "Maschera inversa"
#        self._insertSecondCheckbox(label_inv, 0)

#         label_lib = "Scegliere la libreria da utilizzare"
#         libs = [None, 'pdal', 'liblas']
#         self._insertMethod(libs, label_lib, 1)

#        label_compr = "Comprimere il file di output"
#        self._insertCheckbox(label_compr, 1, output=True)
#        self.checkbox.stateChanged.connect(self.compressStateChanged)
        
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        
    def compressStateChanged(self):
        checked = self.checkbox.isChecked()
        self.TextOut.setText(STEMUtils.check_las_compress(self.TextOut.text(), checked))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        """
        if not self.QGISextent.isChecked() and not self.AddLayerToCanvas.isChecked():
            STEMMessageHandler.error("Selezionare se utilizzare l'estensione "
                                     "di QGIS o la maschera, questa è da "
                                     "impostare con l'apposito modulo")
            return
        elif self.QGISextent.isChecked() and self.AddLayerToCanvas.isChecked():
            STEMMessageHandler.error("Selezionare solo uno tra la maschera e "
                                     "l'estensione di QGIS")
            return
        elif self.QGISextent.isChecked():
            self.mapDisplay()
            area = " ".join(self.rect_str)##
        elif self.AddLayerToCanvas.isChecked():
            mask = STEMSettings.value("mask", "")
            ogrinfo = infoOGR()
            ogrinfo.initialize(mask)
            area = ogrinfo.getWkt()
        """
        try:

            source = str(self.TextIn.text())
            print('source ' + str(source))
            out = str(self.TextOut.text())
            print('out ' + str(out))
            
            extension = (os.path.splitext(out)[1]).lower()
            
            if (extension != ".las" and extension != ".laz"):
                QMessageBox.warning(self, "Errore nei parametri",
                                u"Estensione file di output non corretta")
            # TODO: rilanciare il dialog
                #dialog = STEMToolsDialog(self.iface, self.toolName)
                #dialog.exec_()
                return 2
            
            
            invec = str(self.BaseInput2.currentText())
            invecsource = STEMUtils.getLayersSource(invec)
            print('invecsource ' + str(invecsource))            
        
#            if self.checkbox.isChecked():
#                compres = True
#            else:
#                compres = False
#            out = STEMUtils.check_las_compress(out, compres)
#            if self.LocalCheck.isChecked():
#                las = stemLAS()
#                temp_out = out
#            else:
#                source = STEMUtils.pathClientWinToServerLinux(source)
#                temp_out = STEMUtils.pathClientWinToServerLinux(out)
#            las = stemLAS() # aggiunto
#            temp_out = out # aggiunto
#            las.initialize()
#            if self.checkbox2.isChecked():
#                inv = True
#            else:
#                inv = False
#            com = las.clip(source, temp_out, area, inverted=inv, compressed=compres,
#                           forced='pdal', local=self.LocalCheck.isChecked())
#            STEMUtils.saveCommand(com)
            
            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)
            
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Ritaglio_las')
            
            
            params = {
                'FileLas' : source, 
                'Maschera' : invecsource, 
                'Output' : out
                }

            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)

                              #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)
            
            task.executed.connect(partial(task_finished, context, self))
            QgsApplication.taskManager().addTask(task)


        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return


  
            
            
