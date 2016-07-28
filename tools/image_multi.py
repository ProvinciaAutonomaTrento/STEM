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
import os

from PyQt4.QtGui import QMessageBox

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='')
        self.iface = iface
        self.toolName = name

        self._insertMultipleInputTable()
        STEMUtils.addLayerToTable(self.BaseInput)

        formats = ['GTIFF', 'ENVI']
        self._insertFirstCombobox('Formato di output', 0, formats)
        self.BaseInputCombo.currentIndexChanged.connect(self.output_file_type_changed)
        
        mets = ['Selezionare il formato di output', 'numeri interi',
                'numeri decimali']
        self.digit = None
        self.lm = "Selezionare la tipologia del formato di output"
        self._insertMethod(mets, self.lm, 1)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)
#         label = "Risoluzione per tutte le bande del file di output"
#         self._insertFirstLineEdit(label, 2)

        label = "Valore di NODATA (default -9999)"
        self._insertFirstLineEdit(label, 2)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

        self.helpui.fillfromUrl(self.SphinxUrl())

    def output_file_type_changed(self):
        output = os.path.splitext(self.TextOut.text())[0]
        if self.BaseInputCombo.currentText() == 'GTIFF':
            self.TextOut.setText(output + ".tif")
        elif self.BaseInputCombo.currentText() == 'ENVI':
            self.TextOut.setText(output)
        
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

    def get_input_path_fields(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal().
        """
        return self.get_input_sources()


    def get_output_path_fields(self):
        """Fornisce al padre una lista di path di output da verificare
        prima di invocare onRunLocal().
        """
        return []

    def get_input_sources(self):
        return [str(self.BaseInput.item(row, 0).text()) for row in xrange(self.BaseInput.rowCount())]

    def onRunLocal(self):
        # Accatastamento
        local = self.LocalCheck.isChecked()
        if not self.digit:
            # STEMMessageHandler.error("Selezionare il formato di output")
            QMessageBox.critical(self, "Parametro mancante",
                                 "Selezionare il formato di output")
            return
        STEMSettings.saveWidgetsValue(self, self.toolName)
        sources = self.get_input_sources()
        if not sources:
            QMessageBox.warning(self, "Errore nei parametri",
                                u"Non è stato selezionato nessun input")
            # TODO: rilanciare il dialog
            dialog = STEMToolsDialog(self.iface, self.toolName)
            dialog.exec_()
            return
        names = [STEMUtils.getNameFromSource(i) for i in sources]
        outformat = str(self.BaseInputCombo.currentText())
        cut, cutsource = self.cutInputMulti(names, sources, local=local)

        if cut:
             items = cut
             sources = cutsource

        out = self.TextOut.text()
        if outformat == 'GTIFF' and not (out.endswith('.tif') or
           out.endswith('.TIF') or out.endswith('.tiff') or out.endswith('.TIFF')):
            out = out + '.tif'
        out_orig = out

        if local:
            cgdal = convertGDAL()
        else:
            import Pyro4
            cgdal = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                 port=GDAL_PORT,
                                                                 name=GDALCONVERTPYROOBJNAME))
        if not self.LocalCheck.isChecked() and sys.platform == 'win32':
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
        
        nodata = -9999.0
        if self.Linedit.text():
            nodata = float(self.Linedit.text())
        
        cgdal.write(nodata = nodata)

        if self.AddLayerToCanvas.isChecked():
            STEMUtils.addLayerIntoCanvas(out_orig, 'raster')

        STEMMessageHandler.success("{ou} file created".format(ou=out_orig))
        
        if not local:
            cgdal._pyroRelease()
