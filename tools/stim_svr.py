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
        self.labelcol = "Seleziona la colonna con indicazione del parametro da stimare"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)

        self._insertSecondSingleInput(pos=2, label="Dati di input raster")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1, empty=True)
        self.llcc = "Selezionare le bande da utilizzare cliccandoci sopra"
        self._insertLayerChooseCheckBox2(self.llcc, pos=3)
        self.BaseInput2.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)
        self.label_layer2.setEnabled(False)
        self.layer_list2.setEnabled(False)

        self._insertThirdLineEdit(label="Inserire il numero di fold della "
                                  "cross validation", posnum=0)

        kernels = ['RBF', 'lineare', 'polinomiale', 'sigmoidale']

        self.lk = 'Selezionare il kernel da utilizzare'
        self._insertFirstCombobox(self.lk, 1, kernels)
        self.BaseInputCombo.currentIndexChanged.connect(self.kernelChanged)
        self._insertFirstLineEdit(label="Inserire il parametro C", posnum=2)
        self._insertSecondLineEdit(label="Inserire il valore di gamma",
                                   posnum=3)

        trasf = ['nessuna', 'logaritmo', 'radice quadrata']

        self.lk = 'Selezionare la trasformazione'
        self._insertFirstCombobox(self.lk, 4, trasf)

        mets = ['no', 'manuale', 'file']
        self.lm = "Selezione variabili"
        self._insertMethod(mets, self.lm, 5)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self.lio = "File di selezione"
        self._insertFileInputOption(self.lio, 6)
        self.labelFO.setEnabled(False)
        self.TextInOpt.setEnabled(False)
        self.BrowseButtonInOpt.setEnabled(False)

        self._insertSingleInputOption(7, label="Vettoriale di validazione")
        STEMUtils.addLayerToComboBox(self.BaseInputOpt, 0, empty=True)
        #self.BaseInputOpt.setEnabled(False)
        #self.labelOpt.setEnabled(False)

        label = "Seleziona la colonna per la validazione"
        self._insertSecondCombobox(label, 8)

        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2)
        self.BaseInputOpt.currentIndexChanged.connect(self.columnsChange2)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        if self.BaseInput2.currentText() != "":
            STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)
            self.label_layer2.setText(self.tr("", self.llcc))
        else:
            STEMUtils.addColumnsName(self.BaseInput, self.layer_list2, True)
            self.label_layer2.setText(self.tr("", "Colonne delle feature da "
                                              "utilizzare"))

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)

    def columnsChange2(self):
        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2)

    def methodChanged(self):
        if self.MethodInput.currentText() == 'file':
            self.labelFO.setEnabled(True)
            self.TextInOpt.setEnabled(True)
            self.BrowseButtonInOpt.setEnabled(True)
            self.label_layer2.setEnabled(False)
            self.layer_list2.setEnabled(False)
        elif self.MethodInput.currentText() == 'manuale':
            self.label_layer2.setEnabled(True)
            self.layer_list2.setEnabled(True)
            self.labelFO.setEnabled(False)
            self.TextInOpt.setEnabled(False)
            self.BrowseButtonInOpt.setEnabled(False)
            self.indexChanged()
        else:
            self.labelFO.setEnabled(False)
            self.TextInOpt.setEnabled(False)
            self.BrowseButtonInOpt.setEnabled(False)
            self.label_layer2.setEnabled(False)
            self.layer_list2.setEnabled(False)

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
            invectcol = str(self.layer_list.currentText())
            cut, cutsource, mask = self.cutInput(invect, invectsource,
                                                 'vector')
            if cut:
                invect = cut
                invectsource = cutsource
            inrast = str(self.BaseInput2.currentText())

            if inrast != "":
                inrastsource = STEMUtils.getLayersSource(inrast)
                nlayerchoose = STEMUtils.checkLayers(inrastsource,
                                                     self.layer_list2)
                rasttyp = STEMUtils.checkMultiRaster(inrastsource,
                                                     self.layer_list2)
                cut, cutsource, mask = self.cutInput(inrast, inrastsource,
                                                     rasttyp)
                if cut:
                    inrast = cut
                    inrastsource = cutsource
            else:
                nlayerchoose = STEMUtils.checkLayers(invectsource,
                                                     self.layer_list2, False)
                try:
                    nlayerchoose.remove(invectcol)
                except:
                    pass

            feat = str(self.MethodInput.currentText())

            infile = self.TextInOpt.text()

            optvect = str(self.BaseInputOpt.currentText())
            if optvect:
                optvectsource = STEMUtils.getLayersSource(optvect)
                optvectcols = str(self.BaseInputCombo2.currentText())
                cut, cutsource, mask = self.cutInput(optvect, optvectsource,
                                                     'vector')
                if cut:
                    optvect = cut
                    optvectsource = cutsource

            from PyQt4.QtCore import *
            import pdb
            pyqtRemoveInputHook()
            pdb.set_trace()
            # TODO finish
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
