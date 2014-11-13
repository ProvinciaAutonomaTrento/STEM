# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 13:29:26 2014

@author: lucadelu
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from stem_base_dialogs import BaseDialog
from base import _fromUtf8, _translate

class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface
        self.name = "Maschera"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()
        self.addLayerToComboBox(self.BaseInput, 0)

        self.LabelOut.setText(_translate("Dialog", "Impostando la maschera "
                                         "tutte le successive operazioni "
                                         "verranno effettuate all'interno "
                                         "della mappa selezionata", None))
        self.TextOut.hide()
        self.BrowseButton.hide()
        self.AddLayerToCanvas.setText(_translate("Dialog",
                                                 "Rimuovi la maschera", None))
        self.AddLayerToCanvas.setChecked(False)
        self.LocalCheck.hide()
        self.MultiBand.hide()
        self.QGISextent.hide()

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onClosing(self):
        BaseDialog.onClosing(self)

    def _accept(self):
        s = QSettings()
        if self.AddLayerToCanvas.isChecked():
            s.setValue("stem/mask", "")
        else:
            name = str(self.BaseInput.currentText())
            source = self.getLayersSource(name)
            s.setValue("stem/mask", source)
