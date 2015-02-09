# -*- coding: utf-8 -*-

"""
***************************************************************************
    class_svm.py
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
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput(label='Dati di input vettoriale')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.labelcol = "Seleziona la colonna con indicazione della classe"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))

        self._insertSecondSingleInput(pos=2, label="Dati di input raster")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        self._insertLayerChooseCheckBox(pos=3)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list)
        self.label_layer.setEnabled(False)
        self.layer_list.setEnabled(False)

        kernels = ['lineare', 'polinomiale', 'RBF']

        self.lk = 'Selezionare il kernel da utilizzare'
        self._insertFirstCombobox(self.lk, 0, kernels)
        self.BaseInputCombo.currentIndexChanged.connect(self.kernelChanged)
        self._insertFirstLineEdit(label="Inserire il parametro C", posnum=1)
        self._insertSecondLineEdit(label="Inserire il valore del grado del polinomio",
                                   posnum=2)
        self.LabelLinedit2.setEnabled(False)
        self.Linedit2.setEnabled(False)

        mets = ['no', 'manuale', 'file']
        self.lm = "Selezione feature"
        self._insertMethod(mets, self.lm, 3)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self.lio = "File di selezione"
        self._insertFileInputOption(self.lio, 4)
        self.labelFO.setEnabled(False)
        self.TextInOpt.setEnabled(False)
        self.BrowseButtonInOpt.setEnabled(False)

        self._insertSingleInputOption(5, label="Vettoriale di validazione")
        STEMUtils.addLayerToComboBox(self.BaseInputOpt, 0)
        #self.BaseInputOpt.setEnabled(False)
        #self.labelOpt.setEnabled(False)

        label = "Seleziona la colonna per la validazione"
        self._insertSecondCombobox(label, 6)

        STEMUtils.addColumnsName(self.BaseInput, self.BaseInputCombo)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def kernelChanged(self):
        if self.BaseInputCombo.currentText() == 'lineare':
            self.LabelLinedit2.setEnabled(False)
            self.Linedit2.setEnabled(False)
        else:
            self.LabelLinedit2.setEnabled(True)
            self.Linedit2.setEnabled(True)
        if self.BaseInputCombo.currentText() == 'polinomiale':
            self.LabelLinedit2.setText(self.tr("", "Inserire il valore del "
                                               "grado del polinomio"))
        elif self.BaseInputCombo.currentText() == 'RBF':
            self.LabelLinedit2.setText(self.tr("", "Inserire il valore di gamma"))

    def methodChanged(self):
        if self.MethodInput.currentText() == 'file':
            self.labelFO.setEnabled(True)
            self.TextInOpt.setEnabled(True)
            self.BrowseButtonInOpt.setEnabled(True)
            self.label_layer.setEnabled(False)
            self.layer_list.setEnabled(False)
        elif self.MethodInput.currentText() == 'manuale':
            self.label_layer.setEnabled(True)
            self.layer_list.setEnabled(True)
            self.labelFO.setEnabled(False)
            self.TextInOpt.setEnabled(False)
            self.BrowseButtonInOpt.setEnabled(False)
        else:
            self.labelFO.setEnabled(False)
            self.TextInOpt.setEnabled(False)
            self.BrowseButtonInOpt.setEnabled(False)
            self.label_layer.setEnabled(False)
            self.layer_list.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        if not self.overwrite:
            self.overwrite = STEMUtils.fileExists(self.TextOut.text())
        try:
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            invectcols = str(self.layer_list.currentText())
            inrast = str(self.BaseInput2.currentText())
            inrastsource = STEMUtils.getLayersSource(inrast)
            nlayerchoose = STEMUtils.checkLayers(inrastsource, self.layer_list)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            feat = str(self.MethodInput.currentText())
            kernel = str(self.BaseInputCombo.currentText())
            cpar = self.Linedit.text()
            otherpar = self.Linedit2.text()
            infile = self.TextInOpt.text()
            optvect = str(self.BaseInputOpt.currentText())
            optvectcols = str(self.BaseInputCombo2.currentText())
            outnames = []
            cut, cutsource, mask = self.cutInput(name, source, typ)
            if cut:
                name = cut
                source = cutsource
            # TODO finish
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
