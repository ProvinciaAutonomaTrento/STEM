# -*- coding: utf-8 -*-

"""
stem_plugin.py
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "tools"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "libs"))


from stem_base_dialogs import SettingsDialog, helpDialog
from stem_toolbox import STEMToolbox
from stem_utils import STEMSettings, STEMUtils


class STEMPlugin:
    """This is the main function of the plugin. The class it is used into
    __init_.py file"""
    def __init__(self, iface):
        self.iface = iface
        self.stemMenu = None

    def initGui(self):
        """Function used to initialize the gui. ???"""
        # insert into top-level menu
        menuBar = self.iface.mainWindow().menuBar()
        self.stemMenu = QMenu(menuBar)
        self.stemMenu.setTitle(QCoreApplication.translate("STEM", "S&TEM"))

        # Toolbox
        self.toolbox = STEMToolbox()
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.toolbox)

        self.toolboxAction = self.toolbox.toggleViewAction()
        self.toolboxAction.setIcon(QIcon(os.path.join(os.path.dirname(__file__),
                                                      'images', 'icon.svg')))
        self.toolboxAction.setText(QCoreApplication.translate('STEM',
                                                              '&STEM Toolbox'))
        self.stemMenu.addAction(self.toolboxAction)

        self.stemMenu.addAction(QIcon(os.path.join(os.path.dirname(__file__),
                                                   'images', 'settings.svg')),
                                "&Impostazioni", self.settings)
        self.stemMenu.addAction(QIcon.fromTheme('document-save'),
                                "&Salvare tutti i parametri delle impostazioni"
                                " di STEM in un file", self.save)
        self.stemMenu.addAction(QIcon.fromTheme('help-contents'),
                                "&Help", self.help)

        self.mkdir()

        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(),
                           self.stemMenu)

    def mkdir(self):
        """Create the directory to store some files of STEM project.
        It's create in ~/.qgis2
        """
        home = os.path.join(QgsApplication.qgisSettingsDirPath(), "stem")
        if not os.path.exists(home):
            os.mkdir(home)
            STEMSettings.setValue('stempath', home)

    def unload(self):
        """Unload the plugin"""
        self.toolbox.setVisible(False)
        self.stemMenu.deleteLater()

    def settings(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self.iface.mainWindow(), self.iface)
        dialog.exec_()

    def save(self):
        """Save parameters to a file"""
        STEMUtils.saveParameters()

    def help(self):
        """Show the help dialog"""
        dialog = helpDialog()
        dialog.home()
        dialog.exec_()
