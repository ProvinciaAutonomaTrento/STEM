# -*- coding: utf-8 -*-

"""

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
from gdal_stem import TreesTools
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback
import Pyro4
from pyro_stem import PYROSERVER
from pyro_stem import TREESTOOLSNAME
from pyro_stem import GDAL_PORT

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.shp')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput(label="CHM utilizzato per calcolare le cime"
                                      " degli alberi")
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)
        self._insertSecondSingleInput(label="Vettoriale contenente le cime"
                                      " degli alberi")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)
        min_label = "Valore minimo del raggio massimo della chioma"
        self._insertFirstLineEdit(min_label, 0)

        max_label = "Valore massimo del raggio massimo della chioma"
        self._insertSecondLineEdit(max_label, 1)

        min_height = "Valore minimo dell'altezza della chioma"
        self._insertThirdLineEdit(min_height, 2)

        min_cre = "Soglia crescita chioma basata su altezza media chioma"
        self._insertFourthLineEdit(min_cre, 3)
        self.Linedit4.setText('0.65')

        min_alb = "Soglia crescita chioma basata su altezza albero"
        self._insertFifthLineEdit(min_alb, 4)
        self.Linedit5.setText('0.65')

        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

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
            
#             rasttyp = STEMUtils.checkMultiRaster(source)
#             cut, cutsource, mask = self.cutInput(name, source, rasttyp, local=self.LocalCheck.isChecked())
#             
#             if cut:
#                 name = cut
#                 source = cutsource
            
            name2 = str(self.BaseInput2.currentText())
            source2 = STEMUtils.getLayersSource(name2)
            
            cut, cutsource, mask = self.cutInput(name2, source2,
                                     'vector', local=self.LocalCheck.isChecked())
            
            if cut:
                name2 = cut
                source2 = cutsource
            
            out = str(self.TextOut.text())
            if self.LocalCheck.isChecked():
                trees_tools = TreesTools()
                trees_tools.definizione_chiome(source, source2, out,
                                               int(self.Linedit.text()),
                                               int(self.Linedit2.text()),
                                               int(self.Linedit3.text()),
                                               float(self.Linedit4.text()),
                                               float(self.Linedit5.text()),
                                               overwrite=self.overwrite)
            else:
                trees_tools = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                           port=GDAL_PORT,
                                                                           name=TREESTOOLSNAME))
                remote_source = STEMUtils.pathClientWinToServerLinux(source)
                remote_source2 = STEMUtils.pathClientWinToServerLinux(source2)
                remote_out = STEMUtils.pathClientWinToServerLinux(out)
                trees_tools.definizione_chiome(remote_source, remote_source2, remote_out,
                                               int(self.Linedit.text()),
                                               int(self.Linedit2.text()),
                                               int(self.Linedit3.text()),
                                               float(self.Linedit4.text()),
                                               float(self.Linedit5.text()),
                                               overwrite=self.overwrite)
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'vector')
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
