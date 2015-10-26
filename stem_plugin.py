# -*- coding: utf-8 -*-

"""
Date: August 2014

Authors: Luca Delucchi, Salvatore La Rosa

Copyright: (C) 2014 Luca Delucchi


This create the menu in the toolbar and the toolbox
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
from stem_utils import STEMMessageHandler, STEMUtils
from stem_utils_server import STEMSettings


class STEMPlugin:
    """This is the main function of the plugin. The class it is used into
    __init_.py file"""
    def __init__(self, iface):
        self.iface = iface
        self.stemMenu = None
        STEMUtils.stemMkdir()

    def initGui(self):
        """Function used to initialize the gui."""
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
        self.stemMenu.addAction(QIcon.fromTheme('document-open'),
                                "&Importa i parametri delle impostazioni di "
                                "STEM da un file precedentemente salvato",
                                self.load)
        self.stemMenu.addAction(QIcon.fromTheme('help-contents'),
                                "&Help", self.help)

        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(),
                           self.stemMenu)

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
        # save in different way
        # STEMUtils.saveParameters()
        import shutil
        import tempfile
        f = tempfile.NamedTemporaryFile(delete=False)
        name = f.name
        if sys.platform != 'win32':
            name = f.name
            shutil.copy(STEMSettings.s.fileName(), name)
        else:
            STEMSettings.saveToFile(f)
            f.close()
        STEMMessageHandler.success("Configurazione salvata in {n}, si prega"
                                   "di rimuovere i tools non utili".format(n=name))

    def load(self):
        """Load parameters from a file"""
        myfile = QFileDialog.getOpenFileName(None, "Selezionare il file con la"
                                             "configurazione da caricare", "")
        import ConfigParser
        newconfig = ConfigParser.ConfigParser()
        newconfig.read(myfile)
        newsections = newconfig.sections()

        for news in newsections:
            items = newconfig.items(news)
            for i in items:
                STEMSettings.s.setValue(i[0], i[1])
        STEMMessageHandler.success("Opzioni caricate correttamente")


    def help(self):
        """Show the help dialog"""
        dialog = helpDialog()
        dialog.home()
        dialog.exec_()
