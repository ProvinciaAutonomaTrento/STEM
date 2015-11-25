# -*- coding: utf-8 -*-

"""
Tool to calculate several vegetation indices

It use the **grass_stem** library and it run several times *i.vi* GRASS
command.

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
import traceback
from gdal_stem import file_info
from grass_stem import temporaryFilesGRASS
import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)

        self._insertLayerChooseCheckBox(label="Selezionare la banda per il "
                                        "canale rosso", combo=False)

        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        self._insertLayerChooseCheckBox2(label="Selezionare la banda per il "
                                         "canale infrarosso", combo=False)

        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2)

        self._insertLayerChooseCheckBox3(label="Selezionare la banda per il "
                                         "canale verde", combo=False)

        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list3, True)

        self._insertLayerChooseCheckBox4(label="Selezionare la banda per il "
                                         "canale blue", combo=False)

        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list4, True)

        methods = ['arvi', 'dvi', 'evi', 'evi2', 'gari', 'gemi', 'ipvi',
                   'ndvi', 'savi', 'sr', 'vari']

        lm = "Selezionare l'indice di vegetazione"
        self._insertMethod(methods, lm, 0)

        self.helpui.fillfromUrl(self.SphinxUrl())

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list3, True)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list4, True)

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
            method = self.MethodInput.currentText()
            red = str(STEMUtils.checkLayers(source, self.layer_list))
            nir = str(STEMUtils.checkLayers(source, self.layer_list2))
            green = STEMUtils.checkLayers(source, self.layer_list3)
            blue = STEMUtils.checkLayers(source, self.layer_list4)
            nlayers = [red, nir]
            if green:
                nlayers.append(str(green))
            if blue:
                nlayers.append(str(blue))
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)

            output = self.TextOut.text()
            local = self.LocalCheck.isChecked()
            cut, cutsource, mask = self.cutInput(name, source, typ,
                                                 local=local)

            if cut:
                name = cut
                source = cutsource
            if not local and sys.platform == 'win32':
                old_source = source
                source = STEMUtils.pathClientWinToServerLinux(source)
                output = STEMUtils.pathClientWinToServerLinux(output, False)
            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            if mask:
                gs.check_mask(mask)

            gs.import_grass(source, tempin, typ, nlayers)
            raster = file_info()
            raster.init_from_name(old_source)
            red = raster.getColorInterpretation(red)
            nir = raster.getColorInterpretation(nir)
            com = ['i.vi', 'red={name}.{l}'.format(name=tempin, l=red),
                   'nir={name}.{l}'.format(name=tempin, l=nir),
                   'output={name}'.format(name=tempout),
                   'viname={m}'.format(m=method)]
            if method in ['arvi', 'evi', 'gari', 'vari']:
                if not blue:
                    STEMMessageHandler.error("Selezionare la banda blu")
                    return
                else:
                    blue = raster.getColorInterpretation(blue)
                    com.append("blue={name}.{b}".format(name=tempin, b=blue))
            if method in ['gari', 'vari']:
                if not green:
                    STEMMessageHandler.error("Selezionare la banda verde")
                    return
                else:
                    green = raster.getColorInterpretation(green)
                    com.append("green={name}.{g}".format(name=tempin, g=green))
            STEMUtils.saveCommand(com)

            gs.run_grass([com])

            STEMUtils.exportGRASS(gs, self.overwrite, output, tempout, typ)
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
