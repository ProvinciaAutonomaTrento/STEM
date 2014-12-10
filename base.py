# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base.ui'
#
# Created: Thu Dec 11 00:32:32 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(702, 563)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_input = QtGui.QVBoxLayout()
        self.verticalLayout_input.setObjectName(_fromUtf8("verticalLayout_input"))
        self.verticalLayout.addLayout(self.verticalLayout_input)
        self.verticalLayout_output = QtGui.QVBoxLayout()
        self.verticalLayout_output.setObjectName(_fromUtf8("verticalLayout_output"))
        self.horizontalLayout_output = QtGui.QHBoxLayout()
        self.horizontalLayout_output.setObjectName(_fromUtf8("horizontalLayout_output"))
        self.LabelOut = QtGui.QLabel(Dialog)
        self.LabelOut.setWordWrap(True)
        self.LabelOut.setObjectName(_fromUtf8("LabelOut"))
        self.horizontalLayout_output.addWidget(self.LabelOut)
        self.TextOut = QtGui.QLineEdit(Dialog)
        self.TextOut.setObjectName(_fromUtf8("TextOut"))
        self.horizontalLayout_output.addWidget(self.TextOut)
        self.BrowseButton = QtGui.QPushButton(Dialog)
        self.BrowseButton.setObjectName(_fromUtf8("BrowseButton"))
        self.horizontalLayout_output.addWidget(self.BrowseButton)
        self.verticalLayout_output.addLayout(self.horizontalLayout_output)
        self.verticalLayout.addLayout(self.verticalLayout_output)
        self.verticalLayout_options = QtGui.QVBoxLayout()
        self.verticalLayout_options.setObjectName(_fromUtf8("verticalLayout_options"))
        self.verticalLayout.addLayout(self.verticalLayout_options)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.groupBox = QgsCollapsibleGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.LocalCheck = QtGui.QCheckBox(self.groupBox)
        self.LocalCheck.setMaximumSize(QtCore.QSize(16777215, 30))
        self.LocalCheck.setChecked(True)
        self.LocalCheck.setObjectName(_fromUtf8("LocalCheck"))
        self.gridLayout_3.addWidget(self.LocalCheck, 0, 0, 1, 1)
        self.AddLayerToCanvas = QtGui.QCheckBox(self.groupBox)
        self.AddLayerToCanvas.setMaximumSize(QtCore.QSize(16777215, 30))
        self.AddLayerToCanvas.setChecked(True)
        self.AddLayerToCanvas.setObjectName(_fromUtf8("AddLayerToCanvas"))
        self.gridLayout_3.addWidget(self.AddLayerToCanvas, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.MultiBand = QtGui.QCheckBox(self.groupBox)
        self.MultiBand.setObjectName(_fromUtf8("MultiBand"))
        self.horizontalLayout_2.addWidget(self.MultiBand)
        self.QGISextent = QtGui.QCheckBox(self.groupBox)
        self.QGISextent.setObjectName(_fromUtf8("QGISextent"))
        self.horizontalLayout_2.addWidget(self.QGISextent)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "STEM", None, QtGui.QApplication.UnicodeUTF8))
        self.LabelOut.setText(QtGui.QApplication.translate("Dialog", "Risultato", None, QtGui.QApplication.UnicodeUTF8))
        self.BrowseButton.setText(QtGui.QApplication.translate("Dialog", "Sfoglia", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Opzioni", None, QtGui.QApplication.UnicodeUTF8))
        self.LocalCheck.setText(QtGui.QApplication.translate("Dialog", "Esegui localmente", None, QtGui.QApplication.UnicodeUTF8))
        self.AddLayerToCanvas.setText(QtGui.QApplication.translate("Dialog", "Aggiungi risultato sulla mappa", None, QtGui.QApplication.UnicodeUTF8))
        self.MultiBand.setText(QtGui.QApplication.translate("Dialog", " Raster multibanda", None, QtGui.QApplication.UnicodeUTF8))
        self.QGISextent.setText(QtGui.QApplication.translate("Dialog", "Utilizza estensione QGIS", None, QtGui.QApplication.UnicodeUTF8))

from qgis.gui import QgsCollapsibleGroupBox
