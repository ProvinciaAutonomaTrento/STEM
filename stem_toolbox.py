# -*- coding: utf-8 -*-

"""
***************************************************************************
    stem_toolbox.py
    ---------------------
    Date                 : June 2014
    Copyright            : (C) 2014 Luca Delucchi
    Email                : 
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
__date__ = 'June 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.utils import iface

import os
from STEMToolbox import Ui_STEMToolBox

class STEMToolbox(QDockWidget, Ui_STEMToolBox):
    def __init__(self):
        QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        ##           {"rootItem"                    :[{"toolName"                    :"module"}]}
        self.tools = {"Pre-elaborazione immagini"   :[{"Filtro riduzione del rumore":"image_filter",
                                                    "Correzione atmosferica":"image_corratmo",
                                                    "Segmentazione":"image_segm",
                                                    "Pansharpening":"image_pansh",
                                                    "Maschera":"image_mask",
                                                    "Accatastamento":"image_multi"}],
                      "Pre-elaborazioni LIDAR"      :[{"Filtraggio file LAS":"las_filter",
                                                     "Unione file LAS":"las_union",
                                                     "Ritaglio file LAS":"las_clip",
                                                     "Rasterizzazione file LAS":"las_extract",
                                                     "Estrazione CHM":"las_removedtm" }]
                      }
        
        self.populateTree()
        self.toolTree.doubleClicked.connect(self.executeTool)

    def executeTool(self):
        item = self.toolTree.currentItem()
        if isinstance(item, TreeToolItem):
            toolName = item.text(0)
            module = self.tools[item.parent().text(0)][0][toolName]
        
            globals()["toolModule"] = __import__(module)
            dlg = toolModule.STEMToolsDialog
            dlg(iface, toolName).exec_()

    def populateTree(self):
        self.toolTree.clear()
        for gr, modToolList in self.tools.iteritems():
            groupItem = QTreeWidgetItem()
            groupItem.setText(0, gr)
            groupItem.setToolTip(0, gr)
            iconGroupItem = QIcon(os.path.dirname(__file__) + '/icons/rootItemTool_.svg')
            groupItem.setIcon(0, iconGroupItem)
            for tool, module in modToolList[0].iteritems():
                toolItem = TreeToolItem(tool)
                groupItem.addChild(toolItem)
            
            self.toolTree.addTopLevelItem(groupItem)
            self.toolTree.sortItems(0, Qt.AscendingOrder)

class TreeToolItem(QTreeWidgetItem):
    def __init__(self, toolName):
        QTreeWidgetItem.__init__(self)
        iconToolItem = QIcon(os.path.dirname(__file__) + '/icons/itemTool.svg')
        self.setIcon(0, iconToolItem)
        self.setToolTip(0, toolName)
        self.setText(0, toolName)
