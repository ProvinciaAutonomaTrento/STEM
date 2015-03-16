# -*- coding: utf-8 -*-

"""
image_atmo.py
---------------------
Date                 : August 2014
Copyright            : (C) 2014 Luca Delucchi
Email                : luca.delucchi@fmach.it

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
from grass_stem import helpUrl
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertFileInput(pos=1)
        self.lf = "Selezionare file con i parametri 6s"
        self.labelF.setText(self.tr("", self.lf))

        self._insertLayerChoose()
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        items = ['6s']
        label = "Seleziona l'algortimo da utilizzare"
        self._insertFirstCombobox(label, 2, items)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)

        self.helpui.fillfromUrl(helpUrl('i.atcorr'))

        self._insertCheckbox('Convertire la mappa di input in riflettanza '
                             '(default è radianza)', 3)
        self._insertSecondCheckbox('ETM+ precedente al 1 Luglio 2000', 4)
        self._insertThirdCheckbox('ETM+ successivo al 1 Luglio 2000', 4)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == '6s':
            self.LabelLinedit.setText(self.tr(self.toolName, self.lf))
            self.BrowseButtonIn.setEnabled(True)
            self.helpui.fillfromUrl(helpUrl('i.atcorr'))

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        if not self.overwrite:
            self.overwrite = STEMUtils.fileExists(self.TextOut.text())
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            coms = []
            outnames = []
            cut, cutsource, mask = self.cutInput(name, source, typ)
            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name)
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                gs.check_mask(mask)

            outnames.append(tempout)
            com = ['i.atcorr', 'input={name}'.format(name=tempin),
                   'output={outname}'.format(outname=tempout),
                   'parameters={para}'.format(self.TextIn.text())]
            if self.checkbox.isChecked():
                com.append('-r')
            if self.checkbox2.isChecked():
                com.append('-r')
            if self.checkbox3.isChecked():
                com.append('-a')
            coms.append(com)
            self.saveCommand(com)
            gs.run_grass(coms)

            STEMUtils.exportGRASS(gs, self.overwrite, self.TextOut.text(),
                                  tempout, typ)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
