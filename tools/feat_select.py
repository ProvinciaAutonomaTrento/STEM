# -*- coding: utf-8 -*-

"""
Tool to select feature using Sequential Forward Floating Feature Selection
(SSF).

It use the STEM library **machine_learning** and **feature_selection** and
the external *numpy*

Date: August 2014

Copyright: (C) 2014 Luca Delucchi

Authors: Luca Delucchi

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings, STEMLogging
from feature_selection import SSF
import traceback
from machine_learning import MLToolBox, SEP, NODATA
import numpy as np
import os
from functools import partial
from PyQt4.QtCore import SIGNAL


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput(label='Dati di input vettoriale')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.labelcol = "Seleziona la colonna con indicazione della classe"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)

        self._insertSecondSingleInput(pos=2, label="Dati di input raster")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1, empty=True)

        mets = ['mean', 'min', 'median']
        self.lm = "Selezione la strategia da utilizzare"
        self._insertMethod(mets, self.lm, 0)
        labeln = "Numero massimo di feature da selezionare"
        self. _insertFirstLineEdit(labeln, 1)
        self.connect(self.BrowseButton, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.TextOut, '.txt'))

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        log = STEMLogging()
        com = ['python', 'mlcmd.py']
        try:
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            invectcol = str(self.layer_list.currentText())
            cut, cutsource, mask = self.cutInput(invect, invectsource,
                                                 'vector')
            prefcsv = "featsel_{vect}_{col}".format(vect=invect,
                                                    col=invectcol)
            if cut:
                invect = cut
                invectsource = cutsource
            inrast = str(self.BaseInput2.currentText())

            inrastsource = STEMUtils.getLayersSource(inrast)

            com.extend(['--raster', inrastsource])

            meth = str(self.MethodInput.currentText())

            if self.LocalCheck.isChecked():
                mltb = MLToolBox()
            else:
                import Pyro4
                mltb = Pyro4.Proxy("PYRONAME:stem.machinelearning")
            com.extend(['--n-jobs', '1', '--n-best', '1', '--scoring',
                        'accuracy', '--best-strategy', 'mean',
                        '--feature-selection', 'SSF', invectsource, invectcol])
            mltb.set_params(vector_file=invectsource, column=invectcol,
                            use_columns=None,
                            raster_file=inrastsource,
                            models=None, scoring='accuracy',
                            n_folds=None, n_jobs=1, n_best=1,
                            tvector=None, tcolumn=None, traster=None,
                            best_strategy=getattr(np, 'mean'),
                            scaler=None, fselector=None, decomposer=None,
                            transform=None, untransform=None)

            home = STEMSettings.value("stempath")

            # ------------------------------------------------------------
            # Extract training samples
            trnpath = os.path.join(home,
                                   "{pr}_csvtraining.csv".format(pr=prefcsv))
            log.debug('    From:')
            log.debug('      - vector: %s' % mltb.vector)
            log.debug('      - training column: %s' % mltb.column)
            if mltb.use_columns:
                log.debug('      - use columns: %s' % mltb.use_columns)
            if mltb.raster:
                log.debug('      - raster: %s' % mltb.raster)
            X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                         nodata=NODATA, dtype=np.uint32)

            X = X.astype(float)
            log.debug('\nTraining sample shape: {val}'.format(val=X.shape))

            # --------------------------------------------------------------
            # Feature selector
            fselector = SSF(strategy=getattr(np, meth),
                            n_features=int(self.Linedit.text()))

            # ------------------------------------------------------------
            # Transform the input data
            out = self.TextOut.text()
            X = mltb.data_transform(X=X, y=y, scaler=None, fselector=fselector,
                                    decomposer=None, fscolumns=None,
                                    fsfile=out, fsfit=True)
            STEMMessageHandler.success("Il file {name} è stato scritto "
                                       "correttamente".format(name=out))
            return
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
