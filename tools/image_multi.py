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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from stem_utils import STEMUtils
from stem_base_dialogs import BaseDialog
from gdal_functions import convertGDAL

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertMultipleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        formats = ['GTIFF', 'ENVI']
        self._insertFirstCombobox(formats, 'Formato di output', 0)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        items = []
        for index in xrange(self.BaseInput.count()):
            items.append(self.BaseInput.item(index))
        labels = [STEMUtils.getLayersSource(i.text()) for i in items]
        outformat = str(self.BaseInputCombo.currentText())
        pyqtRemoveInputHook()
        import pdb; pdb.set_trace()
        cgdal = convertGDAL(labels, self.TextOut.text(), outformat)
        cgdal.write()
        if self.AddLayerToCanvas.isChecked():
            STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'raster')
