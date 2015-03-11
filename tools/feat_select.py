# -*- coding: utf-8 -*-

"""
***************************************************************************
    feat_select.py
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

from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
from stem_base_dialogs import BaseDialog
from feature_selection import SSF
import traceback


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
        #self.BaseInput.currentIndexChanged.connect(self.columnsChange)

        self._insertSecondSingleInput(pos=2, label="Dati di input raster")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1, empty=True)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        if not self.overwrite:
            self.overwrite = STEMUtils.fileExists(self.TextOut.text())
        try:
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            invectcol = str(self.layer_list.currentText())
            cut, cutsource, mask = self.cutInput(invect, invectsource,
                                                 'vector')
            prefcsv = "svm_{vect}_{col}".format(vect=invect, col=invectcol)
            if cut:
                invect = cut
                invectsource = cutsource
            inrast = str(self.BaseInput2.currentText())

            if inrast != "":
                inrastsource = STEMUtils.getLayersSource(inrast)
                nlayerchoose = STEMUtils.checkLayers(inrastsource,
                                                     self.layer_list2)
                rasttyp = STEMUtils.checkMultiRaster(inrastsource,
                                                     self.layer_list2)
                cut, cutsource, mask = self.cutInput(inrast, inrastsource,
                                                     rasttyp)
                prefcsv += "_{rast}_{n}".format(rast=inrast, n=len(nlayerchoose))
                if cut:
                    inrast = cut
                    inrastsource = cutsource
                ncolumnschoose = None
            else:
                ncolumnschoose = STEMUtils.checkLayers(invectsource,
                                                       self.layer_list2, False)
                nlayerchoose = None
                inrast = None
                inrastsource = None
                try:
                    ncolumnschoose.remove(invectcol)
                except:
                    pass
                prefcsv += "_{n}".format(n=len(ncolumnschoose))

            nfold = int(self.Linedit3.text())
            models = self.getModel()
            feat = str(self.MethodInput.currentText())
            infile = self.TextInOpt.text()

            mltb = MLToolBox(vector_file=invectsource, column=invectcol,
                             use_columns=ncolumnschoose,
                             raster_file=inrastsource,
                             models=models, scoring='accuracy',
                             n_folds=nfold, n_jobs=1,
                             n_best=1,
                             tvector=None, tcolumn=None,
                             traster=None,
                             best_strategy=getattr(np, 'mean'),
                             scaler=None, fselector=None, decomposer=None,
                             transform=None, untransform=None)

            home = STEMSettings.value("stempath")
            nodata = -9999
            overwrite = False
            delimiter = ';'

            # ------------------------------------------------------------
            # Extract training samples

            print('    From:')
            print('      - vector: %s' % mltb.vector)
            print('      - training column: %s' % mltb.column)
            if mltb.use_columns:
                print('      - use columns: %s' % mltb.use_columns)
            if mltb.raster:
                print('      - raster: %s' % mltb.raster)
            X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                         nodata=args.nodata, dtype=np.uint32)

            X = X.astype(float)
            print('\nTraining sample shape:', X.shape)

            # --------------------------------------------------------------
            # Feature selector
            fselector = SSF(strategy=getattr(np, args.SSF_strategy))

            # ------------------------------------------------------------
            # Transform the input data
            X = mltb.data_transform(X=X, y=y, scaler=None, fselector=fselector,
                                    decomposer=None, fscolumns=None,
                                    fsfile=self.TextOut.text(), fsfit=True)
            return
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
