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

##      {("order","groupItem")          :[{("order","toolName"):"module"}]}
TOOLS = {("0","Pre-elaborazione immagini")
                                        :[{("0","Filtro riduzione del rumore"):"image_filter",
                                        ("1","Correzione atmosferica"):"image_corratmo",
                                        ("2","Segmentazione"):"image_segm",
                                        ("3","Pansharpening"):"image_pansh",
                                        ("4","Maschera"):"image_mask",
                                        ("5","Accatastamento"):"image_multi"}],
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
                                        ("3","Selezione feature"):"feat_select"}],
        ("3","Classificazione supervisionata")
                                        :[{("0","Support Vector Machines"):"class_svm",
                                        ("1","Minima distanza"):"class_mindist",
                                        ("2","Massima Verosimiglianza"):"class_maxvero",
                                        ("3","Spectral Angle Mapper"):"class_sap"}],
        ("4","Post-classificazione")
                                        :[{("0","Attribuzione/modifica classi tematiche"):"clas_mod",
                                        ("1","Riduzione degli errori"):"error_reduction",
                                        ("2","Statistiche"):"vali_stats",
                                        ("3","Metriche di accuratezza"):"vali_accu",
                                        ("4","K-fold cross validation"):"vali_kfold"}],
        ("5","Estrazione feature dalle chiome")
                                        :[{("0","Delineazione chiome"):"feat_delin",
                                        ("1","Estrazione feature"):"" }],
        ("6","Stima di parametri")
                                        :[{("0","Selezione variabili"):"stim_selvar",
                                        ("0","Stimatore lineare"):"stim_linear",
                                        ("0","Support Vector Regression"):"stim_svr"}],
        ("7","Post-elaborazione stima")
                                        :[{("0","Aggregazione ad aree"):"post_aggraree",
                                        ("1","Metriche di accuratezza"):"post_accu",
                                        ("2","K-fold cross validation"):"post_kfold"}],
        ("8","Struttura bosco")
                                        :[{("0","Struttura bosco"):"bosco"}]
}

class STEMToolbox(QDockWidget, Ui_STEMToolBox):
    def __init__(self):
        QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        #self.fill_widget(self.toolTree, TOOLS)
        self.toolTree.setColumnCount(2)
        self.toolTree.setColumnHidden(1, True)
        self.toolTree.setAlternatingRowColors(True)
        
        self.populateTree()
        self.toolTree.doubleClicked.connect(self.executeTool)

    def executeTool(self):
        item = self.toolTree.currentItem()
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
                toolItem = TreeToolItem(tool)
                if not module:
                    toolItem.setDisabled(True)
                groupItem.addChild(toolItem)

            self.toolTree.addTopLevelItem(groupItem)
            self.toolTree.sortItems(1, Qt.AscendingOrder)
            self.toolTree.resizeColumnToContents(0)
            
    def fillItem(self, item, value):
        ''' Will be removed'''
        #item.setExpanded(True)
        if type(value) is dict:
          for key, val in sorted(value.iteritems()):
            child = QTreeWidgetItem()
            child.setText(0, unicode(key))
            item.addChild(child)
            self.fill_item(child, val)
        elif type(value) is list:
          for val in value:
            child = QTreeWidgetItem()
            item.addChild(child)
            if type(val) is dict:      
              child.setText(0, '[dict]')
              self.fill_item(child, val)
            elif type(val) is list:
              child.setText(0, '[list]')
              self.fill_item(child, val)
            else:
              child.setText(0, unicode(val))              
            child.setExpanded(True)
        else:
          child = QTreeWidgetItem()
          child.setText(0, unicode(value))
          item.addChild(child)

    def fillWidget(self, widget, value):
        ''' Will be removed'''
        widget.clear()
        self.fill_item(widget.invisibleRootItem(), value)

class TreeToolItem(QTreeWidgetItem):
    def __init__(self, toolName):
        QTreeWidgetItem.__init__(self)        
        iconToolItem = QIcon(os.path.dirname(__file__) + '/images/itemTool.svg')
        self.setIcon(0, iconToolItem)
        self.setToolTip(0, toolName[1])
        self.setText(0, toolName[1])
        self.setText(1, toolName[0])
