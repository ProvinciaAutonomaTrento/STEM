# -*- coding: utf-8 -*-

"""
Tool to patch plus LAS file in one

It use the **las_stem** library

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import range
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from las_stem import stemLAS
from stem_utils import STEMMessageHandler, STEMUtils
from stem_utils_server import STEMSettings
import traceback
import time
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


def task_finished(context, successful, results):
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

        self.groupBox.hide()
        self.groupBox_2.hide()

        self.QGISextent.hide()
        self.AddLayerToCanvas.hide()
        self.LocalCheck.hide()
        
        self._insertFileInput()
        self._insertSecondFileInput(pos=2)
#        self._insertMultipleInput(multi=True)

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
        try:
#            items = []
#            if len(self.BaseInput.selectedItems()) != 0:
#                items = self.BaseInput.selectedItems()
#            else:
#                for index in range(self.BaseInput.count()):
#                    items.append(self.BaseInput.item(index).text())
#            out = self.TextOut.text()
#            if self.checkbox.isChecked():
#                compres = True
#            else:
#                compres = False
#            out = STEMUtils.check_las_compress(out, compres)
#            out_locale = out
#            if self.LocalCheck.isChecked():
#                las = stemLAS()
#            else:
#                for i in range(len(items)):
#                    items[i] = STEMUtils.pathClientWinToServerLinux(items[i])
#                out = STEMUtils.pathClientWinToServerLinux(out)
#            las = stemLAS() # aggiunto

#            las.initialize()
            
#            com = las.union(items, out, compres, local= True) #self.LocalCheck.isChecked())
 #           STEMUtils.saveCommand(com)
 
            source1 = str(self.TextIn.text())
            print('source1 ' + str(source1))
            source2 = str(self.TextIn2.text())
            print('source2 ' + str(source2))
            out = str(self.TextOut.text())
            print('out ' + str(out))


            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Unione_las')
            
            
            params = {
                     'FileLas' : source1, 
                     'FileLas_2' :  source2, 
                     'Output' : out
                     }
            
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
            task.executed.connect(partial(task_finished, context))
            QgsApplication.taskManager().addTask(task)


        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
