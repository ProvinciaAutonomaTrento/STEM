# -*- coding: utf-8 -*-

"""
Tool to create a new raster map with all the bands of input data

It use the **gdal_stem** library.

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

import sys

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
from gdal_stem import convertGDAL
from pyro_stem import PYROSERVER
from pyro_stem import GDALCONVERTPYROOBJNAME
from pyro_stem import GDAL_PORT


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='')
        self.toolName = name
        self.iface = iface

        self._insertMultipleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1, source=True)

        formats = ['GTIFF', 'ENVI']
        self._insertFirstCombobox('Formato di output', 0, formats)

        mets = ['Selezionare il formato di output', 'numeri interi',
                'numeri decimali']
        self.digit = None
        self.lm = "Selezionare la tipologia del formato di output"
        self._insertMethod(mets, self.lm, 1)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)
        #label = "Risoluzione per tutte le bande del file di output"
        #self._insertFirstLineEdit(label, 2)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

        self.helpui.fillfromUrl(self.SphinxUrl())

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def methodChanged(self):
        if self.MethodInput.currentText() == 'numeri interi':
            # int32
            self.digit = 5
        elif self.MethodInput.currentText() == 'numeri decimali':
            # float32
            self.digit = 6
        else:
            self.digit = None

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        if not self.digit:
            STEMMessageHandler.error("Selezionare il formato di output")
            return
        STEMSettings.saveWidgetsValue(self, self.toolName)
        items = []

        if len(self.BaseInput.selectedItems()) != 0:
            items = self.BaseInput.selectedItems()
        else:
            for index in xrange(self.BaseInput.count()):
                items.append(self.BaseInput.item(index))
        sources = [i.text() for i in items]
        names = [STEMUtils.getNameFromSource(i) for i in sources]
        outformat = str(self.BaseInputCombo.currentText())
        cut, cutsource = self.cutInputMulti(names, sources)
        if cut:
                items = cut
                sources = cutsource
        if self.overwrite:
            out = self.TextOut.text() + '.tmp'
        else:
            out = self.TextOut.text()
        if self.LocalCheck.isChecked():
            cgdal = convertGDAL()
        else:
            import Pyro4
            cgdal = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                 port=GDAL_PORT,
                                                                 name=GDALCONVERTPYROOBJNAME))
        if not self.LocalCheck.isChecked() and sys.platform == 'win32':
            # with open(r'Z:\idt\tempout\temp.log','a') as f:
            #     f.write('Converto i path '+ \
            #             ' '.join([STEMUtils.pathClientWinToServerLinux(x) for x in sources])+ \
            #             ' '+STEMUtils.pathClientWinToServerLinux(out))

            cgdal.initialize([STEMUtils.pathClientWinToServerLinux(x) for x in sources],
                             output=STEMUtils.pathClientWinToServerLinux(out),
                             outformat=outformat,
                             bandtype=self.digit)
        else:
            # with open(r'Z:\idt\tempout\temp.log','a') as f:
            #     f.write('Non converto i path')
            cgdal.initialize(sources, output=out, outformat=outformat,
                             bandtype=self.digit)

        #if self.Linedit.text():
        #    resolution = float(self.Linedit.text())
        #else:
        #    resolution = None
        cgdal.write()

        if self.overwrite:
            STEMUtils.renameRast(out, self.TextOut.text())
        if self.AddLayerToCanvas.isChecked():
            STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'raster')
        else:
            STEMMessageHandler.success("{ou} file created".format(ou=self.TextOut.text()))
