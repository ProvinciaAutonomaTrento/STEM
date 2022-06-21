# -*- coding: utf-8 -*-

"""
Tool to perform CHM from LAS file

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
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback
from las_stem import stemLAS
import time
import os
#from pyro_stem import PYROSERVER
#from pyro_stem import LASPYROOBJNAME
#from pyro_stem import LAS_PORT
import processing


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
        self._insertSecondSingleInput(label="File DTM di input")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        self.BaseInput2.setCurrentIndex(-1)
        #STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        #label_compr = "Comprimere il file di output"
        #self._insertCheckbox(label_compr, 1, output=True)
        #self.checkbox.stateChanged.connect(self.compressStateChanged)
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

    def get_output_path_fields(self):
        """Fornisce al padre una lista di path di output da verificare
        prima di invocare onRunLocal().
        """
        return []

    def get_input_sources(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal()"""
        return []

    def check_form_fields(self):
        """Fornisce al padre una lista di errori che riguardano i campi della form.
        Non include gli errori che possono esser verificati con le funzioni precedenti"""

        #dtm_name = str(self.BaseInput2.currentText())
        #dtm_source = STEMUtils.getLayersSource(dtm_name)

        #if not dtm_source:
        #    return [u'Input DTM non è un layer di QGIS valido']

        return []

    def onRunLocal(self):
        # Estrazione CHM
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source_las = str(self.TextIn.text())
            print('source_las ' + str(source_las))
            inrast = str(self.BaseInput2.currentText())
            inrastsource = STEMUtils.getLayersSource(inrast)
            print('inrastsource ' + str(inrastsource))
            #dtm_name = str(self.BaseInput2.currentText())
            #dtm_source = STEMUtils.getLayersSource(dtm_name)
            outLas = str(self.TextOut.text())
            print('outLas ' + str(outLas))
#            if self.checkbox.isChecked():
#                compres = True
#            else:
#                compres = False
#            out = STEMUtils.check_las_compress(out, compres)
#            out_orig = out
#            if self.LocalCheck.isChecked():
#                las = stemLAS()
#                source_task = source
#                out_task = out
#                dtm_source_task = dtm_source
#            else:
#                source_task = STEMUtils.pathClientWinToServerLinux(source)
#                out_task = STEMUtils.pathClientWinToServerLinux(out)
#                dtm_source_task = STEMUtils.pathClientWinToServerLinux(dtm_source)
#            las = stemLAS() # aggiunto
#            las.initialize()
#            if os.path.exists(out_task): 
#                os.remove(out_task)
#            if os.path.exists(outRaster): #aggiunto
#                os.remove(outRaster) #aggiunto
            if os.path.exists(outLas): #aggiunto
                os.remove(outLas) #aggiunto                
#            com = las.chm(source_task, out_task, dtm_source_task,
#                          compressed=compres,
#                          local=True)#self.LocalCheck.isChecked())
#            STEMUtils.saveCommand(com)
            
            

            ###################### R script here ##############################
            processing.run("r:Estrazione_CHM", { 'FileLas' : source_las, 'DTM' : inrastsource, 'Output_las' : outLas})
            ###################################################################

#            if not self.LocalCheck.isChecked():
#                las._pyroRelease()

            t = time.time()
            while not os.path.isfile(outLas):
                if time.time()-t > 5:
                    STEMMessageHandler.error("{ou} file not created".format(ou=outLas))
                    return
                time.sleep(.1)
            STEMMessageHandler.success("{ou} file created".format(ou=outLas))
        except:
#            if not self.LocalCheck.isChecked():
#                las._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
