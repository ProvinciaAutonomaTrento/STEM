# -*- coding: utf-8 -*-

"""
Date: August 2014

Authors: Luca Delucchi, Salvatore La Rosa

Copyright: (C) 2014 Luca Delucchi

Manage the toolbox
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from qgis.utils import iface
import os

toolboxDockWidget = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                'ui', 'toolbox.ui'))[0]

##      {("order","groupItem")          :[{("order","toolName"):"module"}]}
TOOLS = {("0", "Pre-elaborazione immagini"): [{
                                              ("0", "Maschera"): "image_mask",
                                              ("1", "Accatastamento"): "image_multi",
                                              ("2", "Raster:Georeferenziatore:Georeferenziatore"): "&Georef",
                                              ("3", "Raster:Proiezioni:Riproiezione"): "&Ripro",
                                              ("4", "Raster:Miscellanea:Unione"): "&Union",
                                              ("5", "Raster:Raster Calculator"): "&Calc",
                                              ("6", "Correzione atmosferica"): "image_atmo",
                                              ("7", "Filtro riduzione del rumore"): "image_filter",
                                              ("8", "Segmentazione"): "image_segm",
                                              ("9", "Pansharpening"): "image_pansh",
                                              ("9", "Dark object subtraction"): "image_dos"
                                              }],
         ("1", "Pre-elaborazioni LIDAR"): [{
                                           ("0", "Filtraggio file LAS"): "las_filter",
                                           ("1", "Unione file LAS"): "las_union",
                                           ("2", "Ritaglio file LAS"): "las_clip",
                                           ("3", "Estrazione CHM"): "las_removedtm"
                                           }],
         ("2", "Estrazione feature"): [{
                                       ("0", "Delimitazione chiome"): "feat_delin",
                                       ("1", "Feature di tessitura"): "feat_texture",
                                       ("2", "Feature geometriche"): "feat_geometry",
                                       ("3", "Indici di vegetazione"): "feat_vege",
                                       ("4", "Rasterizzazione file LAS"): "las_extract",
                                       ("5", "Estrazione feature LiDAR da poligoni"): "las_feat"
                                       }],
         ("3", "Selezione feature/variabili"): [{
                                                ("0", "Selezione feature per classificazione"): "feat_select",
                                                ("1", "Selezione variabili per la stima"): "stim_selvar",
                                                }],
         ("4", "Classificazione supervisionata"): [{
                                                   ("0", "Support Vector Machines"): "class_svm",
                                                   ("1", "Minima distanza"): "class_mindist",
                                                   ("2", "Massima Verosimiglianza"): "class_maxvero",
                                                   ("3", "Spectral Angle Mapper"): "class_sap"
                                                   }],
         ("5", "Post-classificazione"): [{
                                         ("0", "Attribuzione/modifica classi tematiche"): "clas_mod",
                                         ("1", "Filtro maggioranza"): "error_reduction",
                                         ("2", "Metriche di accuratezza"): "post_accu",
                                         }],
         ("6", "Stima di parametri"): [{
                                       ("1", "Stima volume con formule allometriche"): "calc_vol",
                                       ("2", "Stimatore lineare"): "stim_linear",
                                       ("3", "Support Vector Regression"): "stim_svr"
                                       }],
         ("7", "Post-elaborazione"): [{
                                            ("0", "Aggregazione ad aree"): "post_aggraree",
                                            ##("1", "Metriche di accuratezza"): "post_accu",
                                            ##("2", "K-fold cross validation"): "post_kfold",
                                            ("1", "Statistiche singolo raster"): "post_stats",
                                            ("2", "Statistiche su due raster"): "post_stats2"
                                            }],
         ("8", "Struttura bosco"): [{("0", "Struttura bosco"): "bosco"}]
         }


class STEMToolbox(QDockWidget, toolboxDockWidget):
    """Class for the STEM toolbox"""
    def __init__(self):
        QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.toolTree.setColumnCount(4)
        self.toolTree.setColumnHidden(1, True)
        self.toolTree.setColumnHidden(2, True)
        self.toolTree.setColumnHidden(3, True)
        self.toolTree.setAlternatingRowColors(True)

        self.populateTree()
        self.toolTree.doubleClicked.connect(self.executeTool)

    def executeTool(self):
        """Function to execute the tool"""
        item = self.toolTree.currentItem()
        if isinstance(item, QGISTreeToolItem):
            menuTitle = []
            toolName = ':'.join([item.text(2), item.text(3), item.text(0)])
            try:
                module = TOOLS[(item.parent().text(1),
                                item.parent().text(0))][0][(item.text(1),
                                                           toolName)]
            except:
                newToolName = ':'.join([item.text(2), item.text(3)])
                module = TOOLS[(item.parent().text(1),
                                item.parent().text(0))][0][(item.text(1),
                                                           newToolName)]
                toolName = newToolName
            if toolName.split(":")[0] == "Raster":
                items = iface.rasterMenu()
            elif toolName.split(":")[0] in ["Vector", "Vettore"]:
                items = iface.vectorMenu()
            for firstact in items.actions():
                menuTitle.append(firstact.text())
                if firstact.text().find(toolName.split(":")[1][:6]) != -1 or \
                   firstact.text().find(toolName.split(":")[1][:6].lower()) != -1:
                    secondact = firstact
                    try:
                        for act in secondact.menu().actions():
                            if act.text().find(module[1:]) != -1:
                                act.trigger()
                    except:
                        firstact.trigger()

            # check if plugin is active otherwise popup plugin manager dialog
            match = [s for s in menuTitle if toolName.split(":")[1][:6] in s]
            if not match:
                match = [s for s in menuTitle if toolName.split(":")[1][:6].lower() in s]
            if not match:
                plIface = iface.pluginManagerInterface()
                plIface.pushMessage("E' necessario attivare il plugin prima!", 1, 10)
                iface.actionManagePlugins().trigger()

        if isinstance(item, TreeToolItem):
            toolName = item.text(0)
            module = TOOLS[(item.parent().text(1),
                            item.parent().text(0))][0][(item.text(1),
                                                       toolName)]
            globals()["toolModule"] = __import__(module)
            dlg = toolModule.STEMToolsDialog(iface, toolName)
            dlg.exec_()

    def populateTree(self):
        """Function to populate the toolbox tree"""
        self.toolTree.clear()
        for gr, modToolList in TOOLS.iteritems():
            groupItem = QTreeWidgetItem()
            groupItem.setText(0, gr[1])
            groupItem.setText(1, gr[0])
            groupItem.setToolTip(0, gr[1])
            iconGroupItem = QIcon(os.path.join(os.path.dirname(__file__),
                                               'images', 'rootItemTool.svg'))
            groupItem.setIcon(0, iconGroupItem)
            for tool, module in modToolList[0].iteritems():
                if module.startswith("&"):
                    toolItem = QGISTreeToolItem(tool)
                else:
                    toolItem = TreeToolItem(tool)
                if not module:
                    toolItem.setDisabled(True)
                groupItem.addChild(toolItem)

            self.toolTree.addTopLevelItem(groupItem)
            self.toolTree.sortItems(1, Qt.AscendingOrder)


class TreeToolItem(QTreeWidgetItem):
    """Class for STEM tool, it set itemtool image

    :param str toolName: the name of tool
    """
    def __init__(self, toolName):
        QTreeWidgetItem.__init__(self)
        iconToolItem = QIcon(os.path.join(os.path.dirname(__file__),
                                          'images', 'itemTool.svg'))
        self.setIcon(0, iconToolItem)
        self.setToolTip(0, toolName[1])
        self.setText(0, toolName[1])
        self.setText(1, toolName[0])


class QGISTreeToolItem(QTreeWidgetItem):
    """Class for QGIS standard tool it set the QGIS icon

    :param str toolName: the name of tool
    """
    def __init__(self, toolName):
        QTreeWidgetItem.__init__(self)
        iconToolItem = QIcon(os.path.join(os.path.dirname(__file__),
                                          'images', 'qgis.png'))
        self.setIcon(0, iconToolItem)
        try:
            self.setToolTip(0, toolName[1].split(":")[2])
            self.setText(0, toolName[1].split(":")[2])
        except:
            try:
                self.setToolTip(0, toolName[1].split(":")[1])
                self.setText(0, toolName[1].split(":")[1])
            except:
                pass
        self.setText(1, toolName[0])
        self.setText(2, toolName[1].split(":")[0])
        self.setText(3, toolName[1].split(":")[1])
