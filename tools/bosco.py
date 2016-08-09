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
import time
from stem_utils import STEMMessageHandler, STEMUtils
import os


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.las')
        self.toolName = name
        self.iface = iface

        self._insertFileInput()
        
        self._insertFirstLineEdit('Altezza arbusti', 0)
        self._insertSecondLineEdit('Dimensione celle', 1)
        self._insertThirdLineEdit('Min thickness', 2)
        self._insertFourthLineEdit('R2 min perc', 3)
        self._insertFifthLineEdit('Delta R', 4)
        
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
            
            altezza_arbusti = self.Linedit.text().strip() if self.Linedit.text().strip() else None
            dimensione_celle = self.Linedit2.text().strip() if self.Linedit2.text().strip() else None
            min_thickness = self.Linedit3.text().strip() if self.Linedit3.text().strip() else None
            R2_min_perch = self.Linedit4.text().strip() if self.Linedit4.text().strip() else None
            delta_R = self.Linedit5.text().strip() if self.Linedit5.text().strip() else None
            
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
            las.bosco(source, 
                      out, 
                      altezza_arbusti,
                      dimensione_celle,
                      min_thickness,
                      R2_min_perch,
                      delta_R)
            
            if not local:
                las._pyroRelease()
            
            t = time.time()
            while not os.path.isfile(self.TextOut.text()):
                if time.time()-t > 5:
                    STEMMessageHandler.error("{ou} LAS file not created".format(ou=self.TextOut.text()))
                    return
                time.sleep(.1)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=self.TextOut.text()))
        except:
            if not local:
                las._pyroRelease()
            
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
