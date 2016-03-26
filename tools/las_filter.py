# -*- coding: utf-8 -*-

"""
Tool to filter LAS file

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
import traceback
from las_stem import stemLAS
import time
import os
from pyro_stem import PYROSERVER
from pyro_stem import LASPYROOBJNAME
from pyro_stem import LAS_PORT


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.las')
        self.toolName = name
        self.iface = iface

        self.QGISextent.hide()
        self.AddLayerToCanvas.hide()
        self._insertFileInput()

        returns = ['', 'primo', 'ultimo', 'altri']
        label = "Seleziona il ritorno da mantenere"
        self._insertFirstCombobox(label, 1, returns)

        label1 = "Inserire i valori minimo e massimo per le X"
        self._insertFirstLineEdit(label1, 2)
        label2 = "Inserire i valori minimo e massimo per le Y"
        self._insertSecondLineEdit(label2, 3)
        label3 = "Inserire i valori minimo e massimo per le Z"
        self._insertThirdLineEdit(label3, 4)
        label4 = "Inserire i valori minimo e massimo per l'intensità"
        self._insertFourthLineEdit(label4, 5)
        label5 = "Inserire i valori minimo e massimo per l'angolo di scansione"
        self._insertFifthLineEdit(label5, 6)
        label6 = "Inserire il valore della classe da tenere"
        self._insertSixthLineEdit(label6, 7)
        label_lib = "Scegliere la libreria da utilizzare"
        libs = [None, 'pdal', 'liblas']
        self._insertMethod(libs, label_lib, 8)

        label_compr = "Comprimere il file di output"
        self._insertCheckbox(label_compr, 1, output=True)
        self.checkbox.stateChanged.connect(self.compressStateChanged)
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
        if self.BaseInputCombo.currentText() == '':
            return None
        elif self.BaseInputCombo.currentText() == 'primo':
            return 'first'
        elif self.BaseInputCombo.currentText() == 'ultimo':
            return 'last'
        elif self.BaseInputCombo.currentText() == 'altri':
            return 'others'

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            out = str(self.TextOut.text())
            if self.checkbox.isChecked():
                compres = True
            else:
                compres = False
            out = STEMUtils.check_las_compress(out, compres)
            out_orig = out
            if self.LocalCheck.isChecked():
                las = stemLAS()
            else:
                import Pyro4
                las = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                   port=LAS_PORT,
                                                                   name=LASPYROOBJNAME))
                source = STEMUtils.pathClientWinToServerLinux(source)
                out = STEMUtils.pathClientWinToServerLinux(out)
            las.initialize()
            xs = STEMUtils.splitIntoList(self.Linedit.text())
            ys = STEMUtils.splitIntoList(self.Linedit2.text())
            zs = STEMUtils.splitIntoList(self.Linedit3.text())
            ints = STEMUtils.splitIntoList(self.Linedit4.text())
            angs = STEMUtils.splitIntoList(self.Linedit5.text())
            clas = self.Linedit6.text()
            ret = self.check_return()

            com = las.filterr(source, out, xs, ys, zs, ints, angs, clas,
                              retur=ret, forced=self.MethodInput.currentText(),
                              compressed=compres,
                              local=self.LocalCheck.isChecked())
            STEMUtils.saveCommand(com)
            t = time.time()
            while not os.path.isfile(out_orig):
                if time.time()-t > 5:
                    STEMMessageHandler.error("{ou} LAS file not created".format(ou=out_orig))
                    return
                time.sleep(.1)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=out_orig))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
