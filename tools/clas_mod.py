# -*- coding: utf-8 -*-

"""
***************************************************************************
    clas_mod.py
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
from qgis.core import *
from qgis.gui import *

from stem_base_dialogs import BaseDialog
from grass_stem import helpUrl


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        items = ['automatico', 'area', 'manuale']
        label = "Seleziona il metodo da utilizzare"
        self._insertFirstCombobox(items, label, 1)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)
        label2 = "Inserire la dimensione minima da tenere in considerazione"
        self._insertFirstLineEdit(label2, 2)
        labelText = "Inserire le regole per la riclassificazione secondo lo " \
                    "stile richiesto dal comando di GRASS GIS r.reclass." \
                    "Per maggiori informazioni consultare l'help"
        self._insertTextArea(labelText, 3)
        self.LabelTextarea.setEnabled(False)
        self.TextArea.setEnabled(False)
        self.LabelLinedit.setEnabled(False)
        self.Linedit.setEnabled(False)
        self.helpui.fillfromUrl(helpUrl('r.clump'))

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == 'automatico':
            self.LabelTextarea.setEnabled(False)
            self.TextArea.setEnabled(False)
            self.LabelLinedit.setEnabled(False)
            self.Linedit.setEnabled(True)
            self.helpui.fillfromUrl(helpUrl('r.clump'))
        elif self.BaseInputCombo.currentText() == 'manuale':
            self.LabelTextarea.setEnabled(True)
            self.TextArea.setEnabled(True)
            self.LabelLinedit.setEnabled(False)
            self.Linedit.setEnabled(False)
            self.helpui.fillfromUrl(helpUrl('r.reclass'))
        else:
            self.LabelTextarea.setEnabled(False)
            self.TextArea.setEnabled(False)
            self.LabelLinedit.setEnabled(True)
            self.Linedit.setEnabled(True)
            self.helpui.fillfromUrl(helpUrl('r.reclass.area'))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)
