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
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
from grass_stem import temporaryFilesGRASS, stats
import os
import traceback
import sys


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
        self.labelMethod = "Percentile (valori supportati 1-100)"
        self._insertSecondLineEdit(self.labelMethod, 3)
        self.labelClass = "Classe o classi (separate da virgola senza spazi) su cui filtrare il file LAS"
        self._insertThirdLineEdit(self.labelClass, 4)
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
            self.Linedit2.setText('95')
        elif self.MethodInput.currentText() == 'trimmean':
            self.LabelLinedit2.setText(self.tr("", "Valore del trim (valori "
                                                   "supportati 0-50)"))
            self.LabelLinedit2.setEnabled(True)
            self.Linedit2.setEnabled(True)
            self.Linedit2.clear()
        else:
            self.LabelLinedit2.setEnabled(False)
            self.Linedit2.setEnabled(False)
            self.Linedit2.clear()

    def get_input_path_fields(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal().
        """
        return [str(self.TextIn.text())]


    def get_output_path_fields(self):
        """Fornisce al padre una lista di path di output da verificare
        prima di invocare onRunLocal().
        """
        return []

    def check_form_fields(self):
        try:
            reso = float(self.Linedit.text())
        except ValueError as e:
            # Errore
            reso = -1
        return [] if reso > 0 else ['Il parametro Risoluzione finale deve essere un numero maggiore di zero']

    def onRunLocal(self):
        # Rasterizzazione file LAS
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            gs = None
            source = str(self.TextIn.text())
            name = os.path.basename(source).replace('.las', '')
            local = self.LocalCheck.isChecked()
            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            method = str(self.MethodInput.currentText())
            returnfilter = self.BaseInputCombo.currentText()
            reso = self.Linedit.text()
            perc = self.Linedit2.text()
            classes = self.Linedit3.text()

            if not os.path.isfile(source):
                STEMMessageHandler.error("File di input non valido")
                return

            if returnfilter == 'all':
                returnfilter = None

            bbox = None
            if self.QGISextent.isChecked():
                self.mapDisplay()
                bbox = self.rect_str

            output = self.TextOut.text()
            if not local and sys.platform == 'win32':
                source = STEMUtils.pathClientWinToServerLinux(source)
                output = STEMUtils.pathClientWinToServerLinux(output)
            if method == 'percentile':
                gs.las_import(source, tempout, method, returnpulse=returnfilter,
                              resolution=reso, percentile=perc, region=bbox,
                              classes=classes)
            elif method == 'trimmean':
                gs.las_import(source, tempout, method, returnpulse=returnfilter,
                              resolution=reso, trim=perc, region=bbox,
                              classes=classes)
            else:
                gs.las_import(source, tempout, method, returnpulse=returnfilter,
                              resolution=reso, region=bbox, classes=classes)

            STEMUtils.exportGRASS(gs, self.overwrite, output, tempout,
                                  'raster')

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'raster')
            
            if not local:
                gs._pyroRelease()
        except:
            if not local and gs is not None:
                gs._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
