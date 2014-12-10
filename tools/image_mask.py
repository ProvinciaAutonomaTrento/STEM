# -*- coding: utf-8 -*-

"""
***************************************************************************
    image_mask.py
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

from stem_base_dialogs import BaseDialog

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name)
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        self.addLayerToComboBox(self.BaseInput, 0)

        self.LabelOut.setText(self.tr(name, "Impostando la maschera "
                                     "tutte le successive operazioni "
                                     "verranno effettuate all'interno "
                                     "della mappa selezionata"))
        self.TextOut.hide()
        self.BrowseButton.hide()
        self.AddLayerToCanvas.setText(self.tr(name, "Rimuovi la maschera"))
        self.AddLayerToCanvas.setChecked(False)
        self.LocalCheck.hide()
        self.MultiBand.hide()
        self.QGISextent.hide()

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def _accept(self):
        s = QSettings()
        if self.AddLayerToCanvas.isChecked():
            s.setValue("stem/mask", "")
        else:
            name = str(self.BaseInput.currentText())
            source = self.getLayersSource(name)
            s.setValue("stem/mask", source)
