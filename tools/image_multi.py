# -*- coding: utf-8 -*-

"""
***************************************************************************
    image_multi.py
    ---------------------
    Date                 : August 2014
    Copyright            : (C) 2014 Luca Delucchi
    Email                : luca.delucchi@fmach.it
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMSettings
from gdal_stem import convertGDAL


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertMultipleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        formats = ['GTIFF', 'ENVI']
        self._insertFirstCombobox('Formato di output', 0, formats)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

        self.helpui.fillfromUrl(self.SphinxUrl())

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        if not self.overwrite:
            self.overwrite = STEMUtils.fileExists(self.TextOut.text())
        items = []

        if len(self.BaseInput.selectedItems()) != 0:
            items = self.BaseInput.selectedItems()
        else:
            for index in xrange(self.BaseInput.count()):
                items.append(self.BaseInput.item(index))
        names = [i.text() for i in items]
        sources = [STEMUtils.getLayersSource(i) for i in names]
        outformat = str(self.BaseInputCombo.currentText())
        cut, cutsource = self.cutInputMulti(names, sources, 'raster')
        if cut:
                items = cut
                labels = cutsource
        if self.overwrite:
            out = self.TextOut.text() + '.tmp'
        else:
            out = self.TextOut.text()
        cgdal = convertGDAL(labels, out, outformat)
        cgdal.write()
        if self.overwrite:
            STEMUtils.renameRast(out, self.TextOut.text())
        if self.AddLayerToCanvas.isChecked():
            STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'raster')
