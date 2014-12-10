# -*- coding: utf-8 -*-

"""
***************************************************************************
    image_pansh.py
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
from stem_functions import temporaryFilesGRASS
from stem_base_dialogs import BaseDialog
from base import _translate

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name)
        self.toolName = name
        self.iface = iface

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
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

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
