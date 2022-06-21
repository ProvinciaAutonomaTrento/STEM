# -*- coding: utf-8 -*-

"""
Date: December 2020

Authors: Trilogis

Copyright: (C) 2020 Trilogis

This create the menu in the toolbar and the toolbox
"""
from __future__ import print_function
from __future__ import absolute_import

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from future import standard_library
standard_library.install_aliases()
from builtins import object

__author__ = 'Trilogis'
__date__ = 'december 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys

from qgis.core import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "tools"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "libs"))


from .stem_base_dialogs import SettingsDialog, helpDialog 
from .stem_toolbox import STEMToolbox
from .stem_utils import STEMMessageHandler, STEMUtils, PathMapping
from stem_utils_server import STEMSettings
import codecs

#BASE_CONFIG_KEYS = "grasspath grassdata grasslocation grasspathserver grassdataserver grasslocationserver".split()
BASE_CONFIG_KEYS = "grasspath grassdata grasslocation".split()

class STEMPlugin(object):
    """This is the main function of the plugin. The class it is used into
    __init_.py file"""
    def __init__(self, iface):
        
#         os.environ['PYRO_SERIALIZERS_ACCEPTED'] += ',pickle'
#         os.environ['PYRO_SERIALIZER'] = 'pickle'
#
        
        self.iface = iface
        self.stemMenu = None
        STEMUtils.stemMkdir()
        
 

    def copyRScriptFiles(self):
        from qgis.core import QgsApplication
        import shutil
        
        
        source_folder = QgsApplication.qgisSettingsDirPath() + "python/plugins/STEM/builtin_scripts/"
        destination_folder = QgsApplication.qgisSettingsDirPath() + "processing/rscripts/"
        
         # projDB = QgsApplication.qgisSettingsDirPath() + "processing/rscripts/Accatastamento.rsx"
        
        
        #shutil.copyfile(QgsApplication.qgisSettingsDirPath() + "python/plugins/STEM/builtin_scripts/Accatastamento.rsx", projDB)

        for file_name in os.listdir(source_folder):
            # construct full file path
            source = source_folder + file_name
            destination = destination_folder + file_name
            # copy only files
            if os.path.isfile(source):
                shutil.copy(source, destination)
                print('copied', file_name)





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
        # Azzera la maschera all'avvio del plugin
        STEMSettings.setValue("mask", "")
        STEMSettings.setValue("mask_inverse", "")
        # TODO: azzera il check "Maschera inversa nella GUI"
        
        if not any([STEMSettings.value(key, "") for key in BASE_CONFIG_KEYS]):
            
            
            
            
            # Nessuna delle variabili e` impostata
            print("Inizializzazione variabili di default")
            #STEMSettings.setValue("grasspath", r"C:\OSGeo4W64\bin\grass70.bat")
            #STEMSettings.setValue("grassdata", r"C:\Users\test\Desktop\grassdata")
            #STEMSettings.setValue("grasslocation", r"STEM")
            #STEMSettings.setValue("grasspathserver", r"/usr/local/bin/grass70")
            #STEMSettings.setValue("grassdataserver", r"/mnt/temp_dir/grassdata")
            #STEMSettings.setValue("grasslocationserver", r"STEM")
            #STEMUtils.set_mapping_table([PathMapping('/mnt/temp_dir/grassoutput/', 'Y:\\'),
            #                             PathMapping('/mnt/alfresco_root_dir', 'Z:\\')])
            #STEMSettings.setValue("epsgcode", r"25832")
            #STEMSettings.setValue("memory", "1")
            
            
            
        #from qgis.utils import plugins
        #if 'processing_r' not in plugins:
        #    QMessageBox.critical(None, "ERRORE", str("Per poter eseguire il plugin STEM è necessario aver installato il plugin Processing R Provider.")) 
        #    self.toolbox.setVisible(False)
        #    return
        #self.toolbox.setVisible(True)
        self.copyRScriptFiles()
        
        try:
            from qgis.utils import plugins
            plugin2_instance = plugins['processing_r']
            plugin2_instance.provider.load()
  # Or: plugin2_instance.get_another_object_from_plugin2()
        except Exception as e:
            logging.exception(e)
       
        
        
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
        #myfile, __, __ = QFileDialog.getSaveFileName(None, "Selezionare il file in cui"
        #                                     " salvare la configurazione", "",  "File di configurazione (*.ini *.txt)")
        
        myfile = QFileDialog().getSaveFileName(None,"Selezionare il file in cui salvare la configurazione",
                                                      "","File di configurazione (*.ini *.txt)")
         
        if myfile and myfile[0] != "":
            import shutil
            import tempfile
            f = tempfile.NamedTemporaryFile(delete=False)
            if sys.platform != 'win32':
                shutil.copy(STEMSettings.s.fileName(), myfile)
            else:
                #with codecs.open(myfile,'w',encoding='utf8') as f:
                #with open(myfile, 'w') as f:
                f = open(myfile[0], 'w')
                STEMSettings.saveToFile(f)
                f.close()
                    
            STEMMessageHandler.success("Configurazione salvata in {n}, si prega "
                                       "di rimuovere i tools non utili".format(n=myfile[0]))
        
        import platform,socket,re,uuid,logging
        try:
            info={}
            info['Qgis Version']=Qgis.QGIS_VERSION
            info['platform']=platform.system()
            info['platform-release']=platform.release()
            info['platform-version']=platform.version()
            info['architecture']=platform.machine()
            info['hostname']=socket.gethostname()
            info['ip-address']=socket.gethostbyname(socket.gethostname())
            info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
            info['processor']=platform.processor()
            print(info)
            
        except Exception as e:
            logging.exception(e)
        
   
            
        

    def load(self):
        """Load parameters from a file"""
        myfile = QFileDialog.getOpenFileName(None, "Selezionare il file con la"
                                             " configurazione da caricare", "", "File di configurazione (*.ini *.txt)")
        if myfile:
            import configparser
            newconfig = configparser.ConfigParser()
            #newconfig.read(myfile)
            newconfig.readfp(codecs.open(myfile[0], "r", "utf8"))
            newsections = newconfig.sections()

            STEMSettings.s.clear()
            
            for news in newsections:
                items = newconfig.items(news)
                for i in items:
                    #STEMSettings.s.setValue(i[0], i[1])
                    if news == "General":                       
                        STEMSettings.setValue(i[0], i[1])
                    else:
                        STEMSettings.setValue(news + "/" + i[0], i[1])
                    
                    
                    
            STEMMessageHandler.success("Opzioni caricate correttamente")


    def help(self):
        """Show the help dialog"""
        dialog = helpDialog()
        dialog.home()
        dialog.exec_()
