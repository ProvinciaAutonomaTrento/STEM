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
from stem_utils import STEMMessageHandler, STEMSettings, STEMUtils
import traceback
from las_stem import stemLAS


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
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
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            out = str(self.TextOut.text())
            if self.LocalCheck.isChecked():
                las = stemLAS()
            else:
                import Pyro4
                las = Pyro4.Proxy("PYRONAME:stem.las")
            las.initialize()
            if self.checkbox.isChecked():
                compres = True
            else:
                compres = False
            xs = STEMUtils.splitIntoList(self.Linedit.text())
            ys = STEMUtils.splitIntoList(self.Linedit2.text())
            zs = STEMUtils.splitIntoList(self.Linedit3.text())
            ints = STEMUtils.splitIntoList(self.Linedit4.text())
            angs = STEMUtils.splitIntoList(self.Linedit5.text())
            clas = STEMUtils.splitIntoList(self.Linedit6.text())

            las.filterr(source, out, xs, ys, zs, ints, angs, clas,
                        compressed=compres,
                        forced=self.MethodInput.currentText())
            STEMMessageHandler.success("{ou} LAS file created".format(ou=out))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
