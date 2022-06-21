# -*- coding: utf-8 -*-

"""
Tool to filter LAS file

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
import traceback
from las_stem import stemLAS
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
        
        self.toolName = name
        self.iface = iface
        self.QGISextent.hide()
        self.AddLayerToCanvas.hide()
        self.LocalCheck.hide()
        
        self.groupBox.hide()
        
        self._insertFileInput()
        self._insertLoadParametersButton()
      
       
       # returns = ['', 'primo', 'ultimo', 'altri']
        returns = ['']
        label = "Seleziona il ritorno da mantenere"
        self._insertFirstCombobox(label, 1, returns)
        
        label1 = "Inserire il valore minimo per le X"
        self._insertFirstLineEdit(label1, 2)
        label2 = "Inserire il valore massimo per le X"
        self._insertSecondLineEdit(label2, 3)

        label3 = "Inserire il valore minimo per le Y"
        self._insertThirdLineEdit(label3, 4)
        label4 = "Inserire il valore massimo per le Y"
        self._insertFourthLineEdit(label4, 5)

        label5 = "Inserire il valore minimo per le Z"
        self._insertFifthLineEdit(label5, 6)
        label6 = "Inserire il valore massimo per le Z"
        self._insertSixthLineEdit(label6, 7)
        
        label7 = "Inserire il valore minimo per l'intensità"
        self._insertSeventhLineEdit(label7, 8)
        label8 = "Inserire il valore massimo per l'intensità"
        self._insertEighthLineEdit(label8, 9)        
        label9 = "Inserire il valore minimo per l'angolo di scansione"
        self._insertNinthLineEdit(label9, 10)
        label10 = "Inserire il valore massimo per l'angolo di scansione"
        self._insertTenthLineEdit(label10, 11)        
        
        label11 = "Inserire il valore della classe da tenere"
        #self._insertEleventhLineEdit(label11, 12)
#         label_lib = "Scegliere la libreria da utilizzare"
#         libs = [None, 'pdal', 'liblas']
#         self._insertMethod(libs, label_lib, 8)

#        label_compr = "Comprimere il file di output"
#        self._insertCheckbox(label_compr, 1, output=True)
#        self.checkbox.stateChanged.connect(self.compressStateChanged)
        classi = ['']
        self._insertSecondCombobox(label11,13,classi)
      
        
        
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

    def check_return(self):
        #if self.BaseInputCombo.currentText() == '':
        #    return None
#            return None
        #elif self.BaseInputCombo.currentText() == 'primo':
        #    return 1
#            return 'first'
        #elif self.BaseInputCombo.currentText() == 'ultimo':
        #    return 4
#            return 'last'
        #elif self.BaseInputCombo.currentText() == 'altri':
        #    return  
        
            
            #ritorno_list = ['all','first','last','mid']
        ritorno_val = self.BaseInputCombo.currentText()
            
        if ritorno_val == "":
            ritorno = 0
        elif ritorno_val == str(self.BaseInputCombo.count() - 1) :
            ritorno = 99
        else:
            ritorno = int(ritorno_val)            
                
        return ritorno
#            return 'others'

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            print('source ' + str(source))
            out = str(self.TextOut.text())
            if os.path.exists(out): 
                os.remove(out)
            print('out ' + str(out))
#            if self.checkbox.isChecked():
#                compres = True
#            else:
#                compres = False
#            out = STEMUtils.check_las_compress(out, compres)
#            out_orig = out
#            if self.LocalCheck.isChecked():
#                las = stemLAS()
#            else:
#                source = STEMUtils.pathClientWinToServerLinux(source)
#                out = STEMUtils.pathClientWinToServerLinux(out)
#            las = stemLAS() # aggiunto
#            las.initialize()
            xs_min = self.Linedit.text()
            if xs_min == str(""):
                xs_min = None
            print('xs_min ' + str(xs_min))
            
            xs_max = self.Linedit2.text()
            if xs_max == str(""):
                xs_max = None
            print('xs_max ' + str(xs_max))
            
            ys_min = self.Linedit3.text()
            if ys_min == str(""):
                ys_min = None            
            print('ys_min ' + str(ys_min))            
            
            ys_max = self.Linedit4.text()
            if ys_max == str(""):
                ys_max = None
            print('ys_max ' + str(ys_max))
            
            zs_min = self.Linedit5.text()
            if zs_min == str(""):
                zs_min = None
            print('zs_min ' + str(zs_min))
            
            zs_max = self.Linedit6.text()
            if zs_max == str(""):
                zs_max = None
            print('zs_max ' + str(zs_max))
            
            ints_min = self.Linedit7.text()
            if ints_min == str(""):
                ints_min = None
            print('ints_min ' + str(ints_min))
            
            ints_max = self.Linedit8.text()
            if ints_max == str(""):
                ints_max = None
            print('ints_max ' + str(ints_max))
            
            angs_min = self.Linedit9.text()
            if angs_min == str(""):
                angs_min = None
            print('angs_min ' + str(angs_min))
            
            angs_max = self.Linedit10.text()
            if angs_max == str(""):
                angs_max = None
            print('angs_max ' + str(angs_max))
            
            clas = self.BaseInputCombo2.currentText()
            if clas == str(""):
                clas = None
            print('clas ' + str(clas))

            ret = self.check_return()
            print('ret ' + str(ret))
            
            
     #            com = las.filterr(source, out, xs, ys, zs, ints, angs, clas,
#                              retur=ret, forced='pdal',
#                              compressed=compres,
#                              local=True)#self.LocalCheck.isChecked())
#            STEMUtils.saveCommand(com)

            
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Filtro_las')
            
            
            params = {
                     'FileLas' : source,
                     'Output' : out, 
                     'Seleziona_ritorno' : ret,
                     'Inserire_valore_massimo__X' : xs_max, 'Inserire_valore_minimo__X' : xs_min,
                     'Inserire_valore_massimo__Y' : ys_max, 'Inserire_valore_minimo__Y' : ys_min,
                     'Inserire_valore_massimo__Z' : zs_max, 'Inserire_valore_minimo__Z' : zs_min,
                     'Inserire_valore_massimo_intensita' : ints_max, 'Inserire_valore_minimo_intensita' : ints_min,
                     'Inserire_valore_massimo_angolo_scansion' : angs_max, 'Inserire_valore_minimo_angolo_scansion' : angs_min,
                     'Inserire_valore_di_classificazione' : clas}
                    
            ###################################################################


            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
            task.executed.connect(partial(task_finished, context))
            QgsApplication.taskManager().addTask(task)


        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return




