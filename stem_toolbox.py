# -*- coding: utf-8 -*-

"""
***************************************************************************
    stem_toolbox.py
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
from PyQt4 import uic
from qgis.utils import iface
import os

toolboxDockWidget = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'STEMToolbox.ui'))[0]

##      {("order","groupItem")          :[{("order","toolName"):"module"}]}
TOOLS = {("0", "Pre-elaborazione immagini")
                                        :[{("0","Filtro riduzione del rumore"):"image_filter",
#                                        ("1","Correzione atmosferica"):"image_corratmo",
                                        ("1","Segmentazione"):"image_segm",
                                        ("2","Pansharpening"):"image_pansh",
                                        ("3","Maschera"):"image_mask",
                                        ("4","Accatastamento"):"image_multi",
                                        ("5","Correzione atmosferica"):"image_atmo"}],
        ("1","Pre-elaborazioni LIDAR")
                                        :[{("0","Filtraggio file LAS"):"las_filter",
                                        ("1","Unione file LAS"):"las_union",
                                        ("2","Ritaglio file LAS"):"las_clip",
                                        ("3","Rasterizzazione file LAS"):"las_extract",
                                        ("4","Estrazione CHM"):"las_removedtm" }],
        ("2","Estrazione/selezione feature"
        " per la classificazione")
                                        :[{("0","Feature di tessitura"):"feat_texture",
                                        ("1","Feature geometriche"):"feat_geometry",
                                        ("2","Indici di vegetazione"):"feat_vege",
                                        ("3","Selezione feature"):"feat_select",
                                        ("4","Delimitazione chiome"):"feat_delin"}],
        ("3","Classificazione supervisionata")
                                        :[{("0","Support Vector Machines"):"class_svm",
                                        ("1","Minima distanza"):"class_mindist",
                                        ("2","Massima Verosimiglianza"):"class_maxvero",
                                        ("3","Spectral Angle Mapper"):"class_sap"}],
        ("4","Post-classificazione")
                                        :[{("0","Attribuzione/modifica classi tematiche"):"clas_mod",
                                        ("1","Filtro maggioranza"):"error_reduction"}],
#        ("5","Estrazione feature dalle chiome")
#                                        :[{("0","Delineazione chiome"):"feat_delin",
#                                        ("1","Estrazione feature"):"" }],
        ("5","Stima di parametri")
                                        :[{("0","Selezione variabili"):"stim_selvar",
                                        ("1","Stimatore lineare"):"stim_linear",
                                        ("2","Support Vector Regression"):"stim_svr"}],
        ("6","Post-elaborazione stima")
                                        :[{("0","Aggregazione ad aree"):"post_aggraree",
                                        ("1","Metriche di accuratezza"):"post_accu",
                                        ("2","K-fold cross validation"):"post_kfold",
                                        ("3","Statistiche"):"post_stats"}],
        ("7","Struttura bosco")
                                        :[{("0","Struttura bosco"):"bosco"}],
        ("8","QGIS Tool")
                                        :[{("0","Raster:Georeferenziatore"):"&Georef"}]
}

class STEMToolbox(QDockWidget, toolboxDockWidget):
    def __init__(self):
        QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        #self.fill_widget(self.toolTree, TOOLS)
        self.toolTree.setColumnCount(3)
        self.toolTree.setColumnHidden(1, True)
        self.toolTree.setColumnHidden(2, True)
        self.toolTree.setAlternatingRowColors(True)

        self.populateTree()
        self.toolTree.doubleClicked.connect(self.executeTool)

    def executeTool(self):
        item = self.toolTree.currentItem()
        if isinstance(item, QGISTreeToolItem):
            toolName = ':'.join([item.text(2), item.text(0)])
            module = TOOLS[(item.parent().text(1),
                            item.parent().text(0))][0][(item.text(1),
                                                       toolName)]
            if toolName.split(":")[0] == "Raster":
                items = iface.rasterMenu()
            elif toolName.split(":")[0] in ["Vector", "Vettore"]:
                items = iface.vectorMenu()
            for firstact in items.actions():
                if firstact.text().find("&" + toolName.split(":")[1][:6]) != -1:
                    secondact = firstact
                    for act in secondact.menu().actions():
                        if act.text().find(module[1:]) != -1:
                            act.trigger()

        if isinstance(item, TreeToolItem):
            toolName = item.text(0)
            module = TOOLS[(item.parent().text(1),
                            item.parent().text(0))][0][(item.text(1),
                                                       toolName)]
            globals()["toolModule"] = __import__(module)
            dlg = toolModule.STEMToolsDialog(iface, toolName)
            dlg.exec_()

    def populateTree(self):
        self.toolTree.clear()
        for gr, modToolList in TOOLS.iteritems():
            groupItem = QTreeWidgetItem()
            groupItem.setText(0, gr[1])
            groupItem.setText(1, gr[0])
            groupItem.setToolTip(0, gr[1])
            iconGroupItem = QIcon(os.path.dirname(__file__) + '/images/rootItemTool.svg')
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
    def __init__(self, toolName):
        QTreeWidgetItem.__init__(self)
        iconToolItem = QIcon(os.path.dirname(__file__) + '/images/itemTool.svg')
        self.setIcon(0, iconToolItem)
        self.setToolTip(0, toolName[1])
        self.setText(0, toolName[1])
        self.setText(1, toolName[0])

class QGISTreeToolItem(QTreeWidgetItem):
    def __init__(self, toolName):
        QTreeWidgetItem.__init__(self)
        iconToolItem = QIcon(os.path.dirname(__file__) + '/images/qgis.png')
        self.setIcon(0, iconToolItem)
        self.setToolTip(0, toolName[1].split(":")[1])
        self.setText(0, toolName[1].split(":")[1])
        self.setText(1, toolName[0])
        self.setText(2, toolName[1].split(":")[0])
