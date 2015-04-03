# -*- coding: utf-8 -*-

"""
Create a raster map starting from LAS file using univariate statistics

It use the **grass_stem** library and it run several times *r.in.lidar* GRASS
command.

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
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
from grass_stem import stats, helpUrl
import os, traceback


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertFileInput()
        methods = ['all', 'first', 'last', 'mid']
        label = "Selezionare il ritorno desiderato"
        self._insertFirstCombobox(label, 0, methods)
        label = "Selezionare il metodo statistico da utilizzare"
        self._insertMethod(stats, label, 1)
        label = "Risoluzione finale del raster"
        self._insertFirstLineEdit(label, 2)
        self.labelMethod = "Percentile"
        self._insertSecondLineEdit(self.labelMethod, 3)
        self.MethodInput.currentIndexChanged.connect(self.checkPercentile)
        self.LabelLinedit2.setEnabled(False)
        self.Linedit2.setEnabled(False)
        self.helpui.fillfromUrl(self.SphinxUrl())

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def checkPercentile(self):
        if self.MethodInput.currentText() == 'percentile':
            self.LabelLinedit2.setText(self.tr("", self.labelMethod))
            self.LabelLinedit2.setEnabled(True)
            self.Linedit2.setEnabled(True)
            self.Linedit2.setText('0.95')
        elif self.MethodInput.currentText() == 'trimmean':
            self.LabelLinedit2.setText(self.tr("", "Valore del trim"))
            self.LabelLinedit2.setEnabled(True)
            self.Linedit2.setEnabled(True)
            self.Linedit2.clear()
        else:
            self.LabelLinedit2.setEnabled(False)
            self.Linedit2.setEnabled(False)
            self.Linedit2.clear()

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            name = os.path.basename(source).replace('.las', '')
            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name, self.LocalCheck.isChecked())
            method = str(self.MethodInput.currentText())
            returnfilter = self.BaseInputCombo.currentText()
            reso = self.Linedit.text()
            perc = self.Linedit2.text()

            if returnfilter == 'all':
                returnfilter = None

            # TODO save parameter of import
            if method == 'percentile':
                gs.las_import(source, tempout, method, returnpulse=returnfilter,
                              resolution=reso, percentile=perc)
            elif method == 'trimmean':
                gs.las_import(source, tempout, method, returnpulse=returnfilter,
                              resolution=reso, trim=perc)
            else:
                gs.las_import(source, tempout, method, returnpulse=returnfilter,
                              resolution=reso)

            STEMUtils.exportGRASS(gs, self.overwrite, self.TextOut.text(),
                                  tempout, 'raster')

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'raster')
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
