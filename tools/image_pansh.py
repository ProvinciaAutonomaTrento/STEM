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
from stem_utils import STEMUtils

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)
        self._insertLayerChoose()
        methods = ['brovey', 'ihs', 'pca']
        self._insertMethod(methods, "Seleziona tipo di Pansharpening", 0)
        tooltip = self.tr(name, "Inserire i numeri dei "
                        "layer da utilizzare, divisi da \n"
                        "una virgola, il primo "
                        "dev'essere il canale per il rosso,\n"
                        " il secondo per verde, il terzo "
                        "per il blu, mentre il quarto deve\n"
                        " essere la banda con risoluzione"
                        " più alta")
        self.layer_list.setToolTip(tooltip)
        self.label_layer.setToolTip(tooltip)
        self.LabelOut.setText(self.tr(name, "Prefisso del risultato"))

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
