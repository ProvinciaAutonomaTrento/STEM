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
from qgis.utils import iface

import os
from STEMToolbox import Ui_STEMToolBox

##      {"groupItem"                    :[{"toolName":"module"}]}
TOOLS = {"Pre-elaborazione immagini"
                                        :[{"Filtro riduzione del rumore":"image_filter",
                                        "Correzione atmosferica":"image_corratmo",
                                        "Segmentazione":"image_segm",
                                        "Pansharpening":"image_pansh",
                                        "Maschera":"image_mask",
                                        "Accatastamento":"image_multi"}],
        "Pre-elaborazioni LIDAR"
                                        :[{"Filtraggio file LAS":"las_filter",
                                        "Unione file LAS":"las_union",
                                        "Ritaglio file LAS":"las_clip",
                                        "Rasterizzazione file LAS":"las_extract",
                                        "Estrazione CHM":"las_removedtm" }],
        "Estrazione/selezione feature"
        " per la classificazione"
                                        :[{"Feature di tessitura":"feat_texture",
                                        "Feature geometriche":"feat_geometry",
                                        "Indici di vegetazione":"feat_vege",
                                        "Selezione feature":"feat_select"}],
        "Classificazione supervisionata"
                                        :[{"Support Vector Machines":"class_svm",
                                        "Minima distanza":"class_mindist",
                                        "Massima Verosimiglianza":"class_maxvero",
                                        "Spectral Angle Mapper":"class_sap"}],
        "Post-classificazione"
                                        :[{"Attribuzione/modifica classi tematiche":"clas_mod",
                                        "Riduzione degli errori":"error_reduction",
                                        "Statistiche":"vali_stats",
                                        "Metriche di accuratezza":"vali_accu",
                                        "K-fold cross validation":"vali_kfold"}],
        "Estrazione feature dalle chiome"
                                        :[{"Delineazione chiome":"feat_delin",
                                        "Estrazione feature":"" }],
        "Stima di parametri"
                                        :[{"Selezione variabili":"stim_selvar",
                                        "Stimatore lineare":"stim_linear",
                                        "Support Vector Regression":"stim_svr"}],
        "Post-elaborazione stima"
                                        :[{"Aggregazione ad aree":"post_aggraree",
                                        "Metriche di accuratezza":"post_accu",
                                        "K-fold cross validation":"post_kfold"}],
        "Struttura bosco"
                                        :[{"Struttura bosco":"bosco"}]
}

class STEMToolbox(QDockWidget, Ui_STEMToolBox):
    def __init__(self):
        QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.populateTree()
        self.toolTree.doubleClicked.connect(self.executeTool)

    def executeTool(self):
        item = self.toolTree.currentItem()
        if isinstance(item, TreeToolItem):
            toolName = item.text(0)
            module = TOOLS[item.parent().text(0)][0][toolName]
            
            globals()["toolModule"] = __import__(module)
            dlg = toolModule.STEMToolsDialog(iface, toolName)
            dlg.exec_()

    def populateTree(self):
        self.toolTree.clear()
        for gr, modToolList in TOOLS.iteritems():
            groupItem = QTreeWidgetItem()
            groupItem.setText(0, gr)
            groupItem.setToolTip(0, gr)
            iconGroupItem = QIcon(os.path.dirname(__file__) + '/images/rootItemTool.svg')
            groupItem.setIcon(0, iconGroupItem)
            for tool, module in modToolList[0].iteritems():
                toolItem = TreeToolItem(tool)
                if not module:
                    toolItem.setDisabled(True)
                groupItem.addChild(toolItem)

            self.toolTree.addTopLevelItem(groupItem)
            self.toolTree.sortItems(0, Qt.AscendingOrder)

class TreeToolItem(QTreeWidgetItem):
    def __init__(self, toolName):
        QTreeWidgetItem.__init__(self)
        iconToolItem = QIcon(os.path.dirname(__file__) + '/images/itemTool.svg')
        self.setIcon(0, iconToolItem)
        self.setToolTip(0, toolName)
        self.setText(0, toolName)
