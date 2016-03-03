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
from stem_utils_server import STEMSettings
from pyro_stem import PYROSERVER
from pyro_stem import LASPYROOBJNAME
from pyro_stem import LAS_PORT
import sys
from las_stem import stemLAS
import traceback
from stem_utils import STEMMessageHandler, STEMUtils
import os


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.las')
        self.toolName = name
        self.iface = iface

        self._insertFileInput()

        self.QGISextent.hide()
        self.AddLayerToCanvas.hide()
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
            source = str(self.TextIn.text())
            out = str(self.TextOut.text())
            local = self.LocalCheck.isChecked()
            if local:
                las = stemLAS()
            else:
                if sys.platform == 'win32':
                    source = STEMUtils.pathClientWinToServerLinux(source)
                    out = STEMUtils.pathClientWinToServerLinux(out)
                import Pyro4
                las = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                   port=LAS_PORT,
                                                                   name=LASPYROOBJNAME))
            las.initialize()
            las.bosco(source, out)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=self.TextOut.text()))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
