# -*- coding: utf-8 -*-

"""
***************************************************************************
    stem_plugin.py
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

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "tools"))

from stem_base_dialogs import SettingsDialog
from stem_toolbox import STEMToolbox


class STEMPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.stemMenu = None

    def initGui(self):
        #insert into top-level menu
        self.stemMenu = QMenu(QCoreApplication.translate("STEM", "S&TEM"))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(),
                                                     self.stemMenu)
        ## Toolbox
        self.toolbox = STEMToolbox()
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.toolbox)

        self.toolboxAction = self.toolbox.toggleViewAction()
        self.toolboxAction.setIcon(QIcon(os.path.dirname(__file__) + '/images/icon.svg'))
        self.toolboxAction.setText(QCoreApplication.translate('STEM', '&STEM Toolbox'))
        self.stemMenu.addAction(self.toolboxAction)

        self.stemMenu.addAction("&Impostazioni", self.settings)

    def unload(self):
        self.iface.mainWindow().menuBar().removeAction(self.stemMenu.menuAction())

    def settings(self):
        dialog = SettingsDialog(self.iface.mainWindow(), self.iface)
        dialog.exec_()
