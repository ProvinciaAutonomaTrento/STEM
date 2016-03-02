# -*- coding: utf-8 -*-

"""
Tool to calculate volume using allometric equations

It use the **gdal_stem** library

Date: June 2015

Copyright: (C) 2014 Luca Delucchi

Authors: Luca Delucchi

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Luca Delucchi'
__date__ = 'June 2015'
__copyright__ = '(C) 2015 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback
from gdal_stem import infoOGR
import os
from pyro_stem import PYROSERVER
from pyro_stem import GDAL_PORT
from pyro_stem import OGRINFOPYROOBJNAME

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.labelcol = "Seleziona la colonna con indicazione del specie"
        self._insertLayerChooseCheckBox(self.labelcol, pos=1, combo=False)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.labeldia = "Seleziona la colonna con indicazione del diametro"
        self._insertLayerChooseCheckBox2(self.labeldia, False)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list2)
        self.labelalt = "Seleziona la colonna con indicazione dell'altezza"
        self._insertLayerChooseCheckBox3(self.labelalt, False)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list3)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.BrowseButton.hide()
        self.helpui.fillfromUrl(self.SphinxUrl())
        self.LabelOut.setText(self.tr("", "Nome della nuova colonna con il "
                                      "volume. Massimo 10 caratteri"))

    def columnsChange(self):
        """Change columns in the combobox according with the layer choosen"""
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list2)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list3)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        com = ['python', 'gdal_stem.py']
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            specie = STEMUtils.checkLayers(source, self.layer_list, False)
            dia = STEMUtils.checkLayers(source, self.layer_list2, False)
            hei = STEMUtils.checkLayers(source, self.layer_list3, False)
            cut, cutsource, mask = self.cutInput(name, source, 'vector', local=self.LocalCheck.isChecked())
            if cut:
                name = cut
                source = cutsource

            out = str(self.TextOut.text())
            if self.overwrite and os.path.exists(out):
                out_pref = os.path.basename(out).replace('.shp', '')
                out_path = os.path.dirname(out)
                STEMUtils.removeFiles(out_path, pref=out_pref)

            com.extend(['--volume', out, '--height', hei, '--diameter', dia,
                        '--specie', specie])
            STEMUtils.saveCommand(com)
            if self.LocalCheck.isChecked():
                ogrinfo = infoOGR()
            else:
                import Pyro4
                ogrinfo = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                       port=GDAL_PORT,
                                                                       name=OGRINFOPYROOBJNAME))
            ogrinfo.initialize(source, 1)
            ogrinfo.calc_vol(out, hei, dia, specie)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.reloadVectorLayer(name)

        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
