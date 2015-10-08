# -*- coding: utf-8 -*-

"""
Tool to extract texture feature

It use the **grass_stem** library and it run *r.texture* GRASS command.

Date: August 2014

Copyright: (C) 2014 Luca Delucchi

Authors: Luca Delucchi

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
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
from gdal_stem import file_info
from grass_stem import temporaryFilesGRASS
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox()
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        methods = ['asm', 'contrast', 'corr', 'var', 'idm', 'sa', 'se', 'sv',
                   'entr', 'dv', 'de', 'moc1', 'moc2']
        label = "Metodo per calcolare la tessitura"
        self._insertMethod(methods, label, 0)
        label = "Dimensione della finestra mobile"
        self._insertFirstLineEdit(label, 1)
        self.helpui.fillfromUrl(self.SphinxUrl())

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            coms = []
            outnames = []
            cut, cutsource, mask = self.cutInput(name, source, typ)
            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = temporaryFilesGRASS(name, self.LocalCheck.isChecked())
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                gs.check_mask(mask)

            if len(nlayerchoose) > 1:
                raster = file_info()
                raster.init_from_name(source)
                for n in nlayerchoose:
                    layer = raster.getColorInterpretation(n)
                    out = '{name}_{lay}'.format(name=tempout, lay=layer)
                    outnames.append(out)
                    com = ['r.texture', 'input={name}.{l}'.format(name=tempin,
                                                                  l=layer),
                           'output={name}'.format(name=out),
                           'size={val}'.format(val=self.Linedit.text()),
                           'method={met}'.format(met=self.MethodInput.currentText())]
                    coms.append(com)
                    STEMUtils.saveCommand(com)
            else:
                outnames.append(tempout)
                com = ['r.texture', 'input={name}'.format(name=tempin),
                       'output={name}'.format(name=tempout),
                       'size={val}'.format(val=self.Linedit.text()),
                       'method={met}'.format(met=self.MethodInput.currentText())]
                coms.append(com)
                STEMUtils.saveCommand(com)

            gs.run_grass(coms)
            gs.create_group(tempout, tempout, True)

            STEMUtils.exportGRASS(gs, self.overwrite, self.TextOut.text(),
                                  tempout, typ)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
