# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'STEMToolbox.ui'
#
# Created: Thu Dec 11 12:40:25 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_STEMToolBox(object):
    def setupUi(self, STEMToolBox):
        STEMToolBox.setObjectName(_fromUtf8("STEMToolBox"))
        STEMToolBox.resize(289, 438)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.toolTree = QtGui.QTreeWidget(self.dockWidgetContents)
        self.toolTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.toolTree.setHeaderHidden(True)
        self.toolTree.setObjectName(_fromUtf8("toolTree"))
        self.toolTree.headerItem().setText(0, _fromUtf8("1"))
        self.verticalLayout.addWidget(self.toolTree)
        STEMToolBox.setWidget(self.dockWidgetContents)

        self.retranslateUi(STEMToolBox)
        QtCore.QMetaObject.connectSlotsByName(STEMToolBox)

    def retranslateUi(self, STEMToolBox):
        STEMToolBox.setWindowTitle(QtGui.QApplication.translate("STEMToolBox", "STEM Toolbox", None, QtGui.QApplication.UnicodeUTF8))

