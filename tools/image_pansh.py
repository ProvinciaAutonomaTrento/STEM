# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 12:16:58 2014

@author: lucadelu
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from stem_functions import temporaryFilesGRASS
from stem_base_dialogs import BaseDialog
from base import _translate


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface
        self.name = "Pansharpening"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()
        self.addLayerToComboBox(self.BaseInput, 1)
        self._insertLayerChoose()
        methods = ['brovey', 'ihs', 'pca']
        self._insertMethod(methods, "Seleziona tipo di Pansharpening", 0)
        self.label_layer.setText(_translate("Dialog", "Inserire i numeri dei "
                                            "layer da utilizzare, divisi da "
                                            "una virgola, il primo "
                                            "dev'essere il canale per il rosso"
                                            ", il secondo per verde, il terzo "
                                            "per il blu, mentre il quarto deve"
                                            " essere la banda con risoluzione"
                                            " più alta", None))
        self.LabelOut.setText(_translate("Dialog", "Prefisso del risultato",
                                         None))

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onClosing(self):
        BaseDialog.onClosing(self)

    def onRun(self):
        uLs = self.layer_list.currentText().split(',')
        if len(uLs) != 4:
            self.onError("Il numero di layer dev'essere uguale a quattro")
        name = str(self.BaseInput.currentText())
        tempin, tempout, gs = temporaryFilesGRASS(name)
        method = str(self.methodInput.currentText())
        source = self.getLayersSource(name)
        com = ['i.pansharpen', 'red={name}.{l}'.format(name=tempin, l=uLs[0]),
               'green={name}.{l}'.format(name=tempin, l=uLs[1]),
               'blue={name}.{l}'.format(name=tempin, l=uLs[2]),
               'base={name}'.format(name=tempout),
               'pan={name}.{l}'.format(val=self.size.text(), l=uLs[3]),
               'method={met}'.format(met=method)]
        gs.run_grass(source, tempin, tempout, self.TextOut.text(),
                     'raster', com)
