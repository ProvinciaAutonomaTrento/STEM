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

        self._insertLayerChooseCheckBox(label="Selezionare la banda per il canale rosso",
                                        combo=False)
        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        self._insertLayerChooseCheckBox2(label="Selezionare la banda per il canale verde",
                                         combo=False)
        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2)

        self._insertLayerChooseCheckBox3(label="Selezionare la banda per il canale blu",
                                         combo=False)
        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list3)

        self._insertSecondSingleInput(5)
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        self._insertLayerChooseCheckBox4(label="Selezionare la banda con risoluzione migliore",
                                         combo=False, pos=6)
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list4)


        methods = ['brovey', 'ihs', 'pca']
        self._insertMethod(methods, "Seleziona tipo di Pansharpening", 0)

#        self._insertLayerChoose()
#        tooltip = self.tr(name, "Inserire i numeri dei "
#                                "layer da utilizzare, divisi da \n"
#                                "una virgola, il primo "
#                                "dev'essere il canale per il rosso,\n"
#                                " il secondo per verde, il terzo "
#                                "per il blu, mentre il quarto deve\n"
#                                " essere la banda con risoluzione"
#                                " più alta")
#        self.layer_list.setToolTip(tooltip)
#        self.label_layer.setToolTip(tooltip)

        self.LabelOut.setText(self.tr(name, "Prefisso del risultato"))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        name = str(self.BaseInput.currentText())
        source = STEMUtils.getLayersSource(name)
        namepan = str(self.BaseInput2.currentText())

        red = str(self.layer_list.currentIndex() + 1)
        green = str(self.layer_list2.currentIndex() + 1)
        blu = str(self.layer_list3.currentIndex() + 1)
        pan = str(self.layer_list4.currentIndex() + 1)
        nlayers = [red, green, blu]

        typ = STEMUtils.checkMultiRaster(source, self.layer_list)
        method = str(self.MethodInput.currentText())
        coms = []

        cut, cutsource, mask = self.cutInput(name, source, typ)

        if cut:
            name = cut
            source = cutsource
        tempin, tempout, gs = temporaryFilesGRASS(name)

#        pyqtRemoveInputHook()
#        import pdb

        if name == namepan:
            nlayers.append(pan)
            gs.import_grass(source, tempin, typ, nlayers)
        else:
            gs.import_grass(source, tempin, typ, nlayers)
            sourcepan = STEMUtils.getLayersSource(namepan)
            gs.import_grass(sourcepan, namepan, typ, [pan])
        if mask:
            gs.check_mask(mask)
        com = ['i.pansharpen', 'red={name}.{l}'.format(name=tempin, l=red),
               'green={name}.{l}'.format(name=tempin, l=green),
               'blue={name}.{l}'.format(name=tempin, l=blu),
               'output={name}'.format(name=tempout),
               'method={met}'.format(met=method)]
        if name == namepan:
            com.append('pan={name}.{l}'.format(name=tempin, l=pan))
        else:
            com.append('pan={name}'.format(name=namepan))
#        pdb.set_trace()
        coms.append(com)
        self.saveCommand(com)
        gs.run_grass(coms)

#        pdb.set_trace()
        gs.export_grass(tempout, self.TextOut.text(), typ, False)
        if self.AddLayerToCanvas.isChecked():
            STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
