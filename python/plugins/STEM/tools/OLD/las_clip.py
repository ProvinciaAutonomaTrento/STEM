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
import os
#from pyro_stem import PYROSERVER
#from pyro_stem import LASPYROOBJNAME
#from pyro_stem import LAS_PORT
import processing # aggiunto


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
            
            ###################### R script here ##############################
            processing.run("r:Ritaglio_las", { 'FileLas' : source, 'Maschera' : invecsource, 'Output' : out})
            ###################################################################
            
#            if not self.LocalCheck.isChecked():
#                las._pyroRelease()
            
            t = time.time()
            while not os.path.isfile(out):
                if time.time()-t > 5:
                    STEMMessageHandler.error("{ou} LAS file not created".format(ou=out))
                    return
                time.sleep(.1)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=out))
        except:
#            if not self.LocalCheck.isChecked():
#                las._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
