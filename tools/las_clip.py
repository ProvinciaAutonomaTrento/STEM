# -*- coding: utf-8 -*-

"""
Tool to clip LAS file

It use the **las_stem** library

Date: August 2014

Copyright: (C) 2014 Luca Delucchi

Authors: Luca Delucchi

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMMessageHandler, STEMUtils
from stem_utils_server import STEMSettings
from las_stem import stemLAS
import traceback
from gdal_stem import infoOGR
import os
from pyro_stem import PYROSERVER
from pyro_stem import LASPYROOBJNAME
from pyro_stem import LAS_PORT


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.las')
        self.toolName = name
        self.iface = iface

        self._insertFileInput()
        self.AddLayerToCanvas.setText(self.tr(name, "Utilizzare la maschera"))

        label_inv = "Maschera inversa"
        self._insertSecondCheckbox(label_inv, 0)

        label_lib = "Scegliere la libreria da utilizzare"
        libs = [None, 'pdal', 'liblas']
        self._insertMethod(libs, label_lib, 1)

        label_compr = "Comprimere il file di output"
        self._insertCheckbox(label_compr, 1, output=True)
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)

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
            area = " ".join(self.rect_str)
        elif self.AddLayerToCanvas.isChecked():
            mask = STEMSettings.value("mask", "")
            ogrinfo = infoOGR()
            ogrinfo.initialize(mask)
            area = ogrinfo.getWkt()
        try:
            source = str(self.TextIn.text())
            out = str(self.TextOut.text())
            if self.LocalCheck.isChecked():
                las = stemLAS()
                temp_out = out
            else:
                import Pyro4
                las = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                   port=LAS_PORT,
                                                                   name=LASPYROOBJNAME))
                source = STEMUtils.pathClientWinToServerLinux(source)
                temp_out = STEMUtils.pathClientWinToServerLinux(out)
            las.initialize()
            if self.checkbox.isChecked():
                compres = True
            else:
                compres = False
            if self.checkbox2.isChecked():
                inv = True
            else:
                inv = False
            com = las.clip(source, temp_out, area, inverted=inv, compressed=compres,
                           forced=self.MethodInput.currentText())
            STEMUtils.saveCommand(com)
            if os.path.exists(out):
                STEMMessageHandler.success("{ou} LAS file created".format(ou=out))
            else:
                STEMMessageHandler.error("{ou} LAS file not created".format(ou=out))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
