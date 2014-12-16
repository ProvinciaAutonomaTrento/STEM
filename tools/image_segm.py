# -*- coding: utf-8 -*-

"""
***************************************************************************
    image_segm.py
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
from stem_utils import STEMUtils
from stem_functions import temporaryFilesGRASS


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox()
        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        self._insertSecondOutput("Goodness of fit", 1)
        self.connect(self.BrowseButton2, SIGNAL("clicked()"), self.BrowseDir)
        self.BrowseButton2.setText(self.tr(name, "Sfoglia"))

        self._insertThresholdDouble(0.001, 1.000, 0.001, 1, 3)

        methods = ['euclidean', 'manhattan']
        label = "Seleziona il metodo di calcolo della similarità"
        self._insertMethod(methods, label, 2)

        li = "Numero massimo di iterazioni"
        self._insertThresholdInteger(1, 100000, 1, 3, li)
        self.thresholdi.setValue(20)

        ln = "Selezionare il numero minimo di celle in un segmento"
        self._insertFirstLineEdit(ln, 3)
        self.Linedit.setText('1')

        lm = "Inserire il valore di memoria da utilizzare in MB"
        self._insertSecondLineEdit(lm, 4)
        self.Linedit2.setText('500')
        #self.BaseInputPan.currentIndexChanged.connect(self.operatorChanged)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        name = str(self.BaseInput.currentText())
        source = STEMUtils.getLayersSource(name)
        nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
        typ = STEMUtils.checkMultiRaster(source, self.layer_list)
        thre = str(self.thresholdd.value())
        itera = str(self.thresholdi.value())
        size = str(self.Linedit.text())
        memory = str(self.Linedit2.text())
        coms = []

        cut, cutsource, mask = self.cutInput(name, source, typ)

        if cut:
            name = cut
            source = cutsource
        tempin, tempout, gs = temporaryFilesGRASS(name)
        gs.import_grass(source, tempin, typ, nlayerchoose)
        if mask:
            gs.check_mask(mask)

        com = ['i.segment', 'group={name}'.format(name=tempin),
               'output={outname}'.format(outname=tempout),
               'thres={val}'.format(val=thre),
               'similarity={met}'.format(met=self.MethodInput.currentText()),
               'minsize={val}'.format(val=size),
               'memory={val}'.format(val=memory),
               'iter={val}'.format(val=itera)]
        if self.TextOut2.text():
            good = 'goodness_{name}'.format(name=tempout)
            com.append('goodness={val}'.format(val=good))
        coms.append(com)
        self.saveCommand(com)

        gs.run_grass(coms)

        gs.export_grass(tempout, self.TextOut.text(), typ, False)
        if self.TextOut2.text():
            gs.export_grass('goodness_{name}'.format(name=tempout),
                            self.TextOut2.text(), typ)
        else:
            gs.removeMapset()
        if self.AddLayerToCanvas.isChecked():
            STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
            if self.TextOut2.text():
                STEMUtils.addLayerIntoCanvas(self.TextOut2.text(), typ)
