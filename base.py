# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/base.ui'
#
# Created: Mon Feb  2 11:31:15 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(702, 563)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(Dialog)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 694, 526))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_8 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_8.setMargin(3)
        self.gridLayout_8.setHorizontalSpacing(6)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_3 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.verticalLayout_input = QtGui.QVBoxLayout()
        self.verticalLayout_input.setObjectName(_fromUtf8("verticalLayout_input"))
        self.gridLayout_6.addLayout(self.verticalLayout_input, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.verticalLayout_options = QtGui.QVBoxLayout()
        self.verticalLayout_options.setObjectName(_fromUtf8("verticalLayout_options"))
        self.gridLayout_5.addLayout(self.verticalLayout_options, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_4 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.verticalLayout_output = QtGui.QVBoxLayout()
        self.verticalLayout_output.setObjectName(_fromUtf8("verticalLayout_output"))
        self.horizontalLayout_output = QtGui.QHBoxLayout()
        self.horizontalLayout_output.setObjectName(_fromUtf8("horizontalLayout_output"))
        self.LabelOut = QtGui.QLabel(self.groupBox_4)
        self.LabelOut.setWordWrap(True)
        self.LabelOut.setObjectName(_fromUtf8("LabelOut"))
        self.horizontalLayout_output.addWidget(self.LabelOut)
        self.TextOut = QtGui.QLineEdit(self.groupBox_4)
        self.TextOut.setObjectName(_fromUtf8("TextOut"))
        self.horizontalLayout_output.addWidget(self.TextOut)
        self.BrowseButton = QtGui.QPushButton(self.groupBox_4)
        self.BrowseButton.setObjectName(_fromUtf8("BrowseButton"))
        self.horizontalLayout_output.addWidget(self.BrowseButton)
        self.verticalLayout_output.addLayout(self.horizontalLayout_output)
        self.gridLayout_7.addLayout(self.verticalLayout_output, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_4)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.groupBox = QgsCollapsibleGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.AddLayerToCanvas = QtGui.QCheckBox(self.groupBox)
        self.AddLayerToCanvas.setMaximumSize(QtCore.QSize(16777215, 30))
        self.AddLayerToCanvas.setChecked(True)
        self.AddLayerToCanvas.setObjectName(_fromUtf8("AddLayerToCanvas"))
        self.gridLayout_3.addWidget(self.AddLayerToCanvas, 1, 3, 1, 1)
        self.QGISextent = QtGui.QCheckBox(self.groupBox)
        self.QGISextent.setObjectName(_fromUtf8("QGISextent"))
        self.gridLayout_3.addWidget(self.QGISextent, 1, 1, 1, 1)
        self.LocalCheck = QtGui.QCheckBox(self.groupBox)
        self.LocalCheck.setMaximumSize(QtCore.QSize(16777215, 30))
        self.LocalCheck.setChecked(True)
        self.LocalCheck.setObjectName(_fromUtf8("LocalCheck"))
        self.gridLayout_3.addWidget(self.LocalCheck, 1, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.gridLayout_8.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "STEM", None))
        self.groupBox_3.setTitle(_translate("Dialog", "Input", None))
        self.groupBox_2.setTitle(_translate("Dialog", "Parametri", None))
        self.groupBox_4.setTitle(_translate("Dialog", "Output", None))
        self.LabelOut.setText(_translate("Dialog", "Risultato", None))
        self.BrowseButton.setText(_translate("Dialog", "Sfoglia", None))
        self.groupBox.setTitle(_translate("Dialog", "Opzioni", None))
        self.AddLayerToCanvas.setText(_translate("Dialog", "Aggiungi risultato sulla mappa", None))
        self.QGISextent.setText(_translate("Dialog", "Utilizza estensione QGIS", None))
        self.LocalCheck.setText(_translate("Dialog", "Esegui localmente", None))

from qgis.gui import QgsCollapsibleGroupBox
