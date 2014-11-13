# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base.ui'
#
# Created: Mon Oct 20 10:51:17 2014
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
        self.verticalLayout_std_opt = QtGui.QVBoxLayout()
        self.verticalLayout_std_opt.setObjectName(_fromUtf8("verticalLayout_std_opt"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.LocalCheck = QtGui.QCheckBox(Dialog)
        self.LocalCheck.setMaximumSize(QtCore.QSize(16777215, 30))
        self.LocalCheck.setChecked(True)
        self.LocalCheck.setObjectName(_fromUtf8("LocalCheck"))
        self.horizontalLayout.addWidget(self.LocalCheck)
        self.AddLayerToCanvas = QtGui.QCheckBox(Dialog)
        self.AddLayerToCanvas.setMaximumSize(QtCore.QSize(16777215, 30))
        self.AddLayerToCanvas.setChecked(True)
        self.AddLayerToCanvas.setObjectName(_fromUtf8("AddLayerToCanvas"))
        self.horizontalLayout.addWidget(self.AddLayerToCanvas)
        self.verticalLayout_std_opt.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.MultiBand = QtGui.QCheckBox(Dialog)
        self.MultiBand.setObjectName(_fromUtf8("MultiBand"))
        self.horizontalLayout_2.addWidget(self.MultiBand)
        self.QGISextent = QtGui.QCheckBox(Dialog)
        self.QGISextent.setObjectName(_fromUtf8("QGISextent"))
        self.horizontalLayout_2.addWidget(self.QGISextent)
        self.verticalLayout_std_opt.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.verticalLayout_std_opt)
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
        Dialog.setWindowTitle(_translate("Dialog", "STEM", None))
        self.LabelOut.setText(_translate("Dialog", "Risultato", None))
        self.BrowseButton.setText(_translate("Dialog", "Sfoglia", None))
        self.LocalCheck.setText(_translate("Dialog", "Esegui localmente", None))
        self.AddLayerToCanvas.setText(_translate("Dialog", "Aggiungi risultato sulla mappa", None))
        self.MultiBand.setText(_translate("Dialog", " Raster multibanda", None))
        self.QGISextent.setText(_translate("Dialog", "Utilizza estensione QGIS", None))

