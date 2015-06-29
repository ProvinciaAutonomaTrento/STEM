# -*- coding: utf-8 -*-

"""
Tool to perform linear regression

It use the STEM library **machine_learning** and external *numpy*, *sklearn*
libraries

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
import traceback
from machine_learning import MLToolBox, SEP, NODATA
from sklearn.svm import SVC
import numpy as np
import pickle as pkl
import os


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput(label='Dati di input vettoriale')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.labelcol = "Seleziona la colonna con indicazione del parametro da stimare"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)

        self._insertSecondSingleInput(pos=2, label="Dati di input raster")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1, empty=True)
        self.llcc = "Selezionare le bande da utilizzare cliccandoci sopra"
        self._insertLayerChooseCheckBox2(self.llcc, pos=3)
        self.BaseInput2.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)
        self.label_layer2.setEnabled(False)
        self.layer_list2.setEnabled(False)

        self._insertThirdLineEdit(label="Inserire il numero di fold della "
                                  "cross validation", posnum=0)

        kernels = ['nessuna', 'logaritmo', 'radice quadrata']

        self.lk = 'Selezionare la trasformazione'
        self._insertFirstCombobox(self.lk, 1, kernels)


        mets = ['no', 'manuale', 'file']
        self.lm = "Selezione variabili"
        self._insertMethod(mets, self.lm, 2)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self.lio = "File di selezione"
        self._insertFileInputOption(self.lio, 3)
        self.labelFO.setEnabled(False)
        self.TextInOpt.setEnabled(False)
        self.BrowseButtonInOpt.setEnabled(False)

        self._insertSingleInputOption(4, label="Vettoriale di validazione")
        STEMUtils.addLayerToComboBox(self.BaseInputOpt, 0, empty=True)
        #self.BaseInputOpt.setEnabled(False)
        #self.labelOpt.setEnabled(False)

        label = "Seleziona la colonna per la validazione"
        self._insertSecondCombobox(label, 5)

        ls = "Indice di accuratezza per la selezione del modello"
        self._insertThirdCombobox(ls, 6, ['R²', 'MSE'])

        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2)
        self.BaseInputOpt.currentIndexChanged.connect(self.columnsChange2)

        label = "Creare output"
        self._insertCheckbox(label, 8)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        if self.BaseInput2.currentText() != "":
            STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)
            self.label_layer2.setText(self.tr("", self.llcc))
        else:
            STEMUtils.addColumnsName(self.BaseInput, self.layer_list2, True)
            self.label_layer2.setText(self.tr("", "Colonne delle feature da "
                                              "utilizzare"))

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list2)

    def columnsChange2(self):
        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2)

    def methodChanged(self):
        if self.MethodInput.currentText() == 'file':
            self.labelFO.setEnabled(True)
            self.TextInOpt.setEnabled(True)
            self.BrowseButtonInOpt.setEnabled(True)
            self.label_layer2.setEnabled(False)
            self.layer_list2.setEnabled(False)
        elif self.MethodInput.currentText() == 'manuale':
            self.label_layer2.setEnabled(True)
            self.layer_list2.setEnabled(True)
            self.labelFO.setEnabled(False)
            self.TextInOpt.setEnabled(False)
            self.BrowseButtonInOpt.setEnabled(False)
            self.indexChanged()
        else:
            self.labelFO.setEnabled(False)
            self.TextInOpt.setEnabled(False)
            self.BrowseButtonInOpt.setEnabled(False)
            self.label_layer2.setEnabled(False)
            self.layer_list2.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def getTransform(self):
        if self.BaseInputCombo.currentText() == 'logaritmo':
            return np.log, np.exp
        elif self.BaseInputCombo.currentText() == 'radice quadrata':
            return np.sqrt, np.exp2
        else:
            return None, None

    def getScoring(self):
        if self.BaseInputCombo3.currentText() == 'MSE':
            return 'mean_squared_error'
        else:
            return 'r2'

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        com = ['python', 'mlcmd.py']
        try:
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            invectcol = str(self.layer_list.currentText())
            cut, cutsource, mask = self.cutInput(invect, invectsource,
                                                 'vector')
            prefcsv = "lin_{vect}_{col}".format(vect=invect, col=invectcol)
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
                prefcsv += "_{rast}_{n}".format(rast=inrast,
                                                n=len(nlayerchoose))
                if cut:
                    inrast = cut
                    inrastsource = cutsource
                ncolumnschoose = None
                com.extend(['--raster', inrastsource])
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
            feat = str(self.MethodInput.currentText())

            optvect = str(self.BaseInputOpt.currentText())
            if optvect:
                optvectsource = STEMUtils.getLayersSource(optvect)
                optvectcols = str(self.BaseInputCombo2.currentText())
                cut, cutsource, mask = self.cutInput(optvect, optvectsource,
                                                     'vector')
                if cut:
                    optvect = cut
                    optvectsource = cutsource
                com.extend(['--test-vector', optvectsource, '--test-column',
                            optvectcols])
            else:
                optvectsource = None
                optvectcols = None

            from regressors import LINEAR
            model = LINEAR

            fscolumns = None
            if feat == 'manuale':
                infile = self.TextInOpt.text()
                if os.path.exists(infile):
                    com.extend(['--feature-selection-file', infile])
                    fscolumns = np.loadtxt(infile)

            trasf, utrasf = self.getTransform()
            scor = self.getScoring()

            home = STEMSettings.value("stempath")
            trnpath = os.path.join(home,
                                   "{p}_csvtraining.csv".format(p=prefcsv))
            crosspath = os.path.join(home,
                                     "{p}_csvcross.csv".format(p=prefcsv))

            com.extend(['--n-folds', str(nfold), '--n-jobs', '1', '--n-best',
                        '1', '--scoring', 'accuracy', '--models', str(model),
                        '--csv-cross', crosspath, '--csv-training', trnpath,
                        '--best-strategy', 'mean', invectsource, invectcol])
            if ncolumnschoose:
                com.extend(['-u', ncolumnschoose])
            if self.checkbox.isChecked():
                com.extend(['-e', '--output-raster-name', self.TextOut.text()])
            if self.LocalCheck.isChecked():
                mltb = MLToolBox()
            else:
                import Pyro4
                mltb = Pyro4.Proxy("PYRONAME:stem.machinelearning")
            mltb.set_params(vector_file=invectsource, column=invectcol,
                            use_columns=ncolumnschoose,
                            raster_file=inrastsource, models=model,
                            scoring=scor, n_folds=nfold, n_jobs=1,
                            tvector=optvectsource, tcolumn=optvectcols,
                            traster=None, n_best=1,
                            best_strategy=getattr(np, 'mean'),
                            scaler=None, fselector=None, decomposer=None,
                            transform=trasf, untransform=utrasf)

            nodata = -9999
            overwrite = False
            delimiter = ';'

            # ------------------------------------------------------------
            # Extract training samples

            if (not os.path.exists(trnpath) or overwrite):
                print('    From:')
                print('      - vector: %s' % mltb.vector)
                print('      - training column: %s' % mltb.column)
                if mltb.use_columns:
                    print('      - use columns: %s' % mltb.use_columns)
                if mltb.raster:
                    print('      - raster: %s' % mltb.raster)
                X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                             dtype=np.uint32, nodata=nodata)
            else:
                print('    Load from:')
                print('      - %s' % trnpath)
                dt = np.loadtxt(trnpath, delimiter=SEP, skiprows=1)
                X, y = dt[:, :-1], dt[:, -1]
            X = X.astype(float)
            print('\nTraining sample shape:', X.shape)

            # ------------------------------------------------------------
            # Transform the input data
            if fscolumns:
                X = mltb.data_transform(X=X, y=y, scaler=None,
                                        fscolumns=fscolumns,
                                        fsfile=infile, fsfit=True)

            # ----------------------------------------------------------------
            # Extract test samples
            print('\nExtract test samples')
            if mltb.tvector and mltb.tcolumn:
                # extract_training(vector_file, column, csv_file, raster_file=None,
                #                  use_columns=None, delimiter=SEP, nodata=None,
                #                  dtype=np.uint32)
                # testpath = os.path.join(args.odir, args.csvtest)
                testpath = os.path.join(home,
                                        "{pref}_csvtestsample.csv".format(pref=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    print('    From:')
                    print('      - vector: %s' % mltb.tvector)
                    print('      - training column: %s' % mltb.tcolumn)
                    if mltb.use_columns:
                        print('      - use columns: %s' % mltb.use_columns)
                    if mltb.raster:
                        print('      - raster: %s' % mltb.traster)
                    Xtest, ytest = mltb.extract_test(csv_file=testpath,
                                                     nodata=nodata)
                    dt = np.concatenate((Xtest.T, ytest[None, :]), axis=0).T
                    np.savetxt(testpath, dt, delimiter=SEP,
                               header="# last column is the training.")
                else:
                    print('    Load from:')
                    print('      - %s' % trnpath)
                    dt = np.loadtxt(testpath, delimiter=SEP, skiprows=1)
                    Xtest, ytest = dt[:, :-1], dt[:, -1]
                Xtest = Xtest.astype(float)
                print('Training sample shape:', Xtest.shape)

            # ---------------------------------------------------------------
            # Cross Models
            print('\nCross-validation of the models')

            bpkpath = os.path.join(home,
                                   "{pref}_best_pickle.csv".format(pref=prefcsv))
            if (not os.path.exists(crosspath) or overwrite):
                cross = mltb.cross_validation(X=X, y=y, transform=transform)
                np.savetxt(crosspath, cross, delimiter=delimiter, fmt='%s',
                           header=delimiter.join(['id', 'name', 'mean', 'max',
                                                  'min', 'std', 'time']))
                mltb.find_best(models)
                best = mltb.select_best()
                with open(bpkpath, 'w') as bpkl:
                    pkl.dump(best, bpkl)
            else:
                print('    Read cross-validation results from file:')
                print('      -  %s' % crosspath)
                try:
                    with open(bpkpath, 'r') as bpkl:
                        best = pkl.load(bpkl)
                except:
                    STEMMessageHandler.error("Problem reading file {name} "
                                             "please remove all files with"
                                             "prefix {pre} in {path}".format(
                                             name=bpkpath, pre=prefcsv,
                                             path=home))
                order, models = mltb.find_best(models=best)
                best = mltb.select_best(best=models)
            print('\nBest models:')
            print(best)

            # ---------------------------------------------------------------
            # test Models
            if Xtest is not None and ytest is not None:
                print('\nTest models with an indipendent dataset')
                testpath = os.path.join(home,
                                        "{pref}_csvtestmodel.csv".format(pref=prefcsv))
                bpkpath = os.path.join(home,
                                       "{pref}_test_pickle.csv".format(pref=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    test = mltb.test(Xtest=Xtest, ytest=ytest, X=X, y=y,
                                     transform=transform)
                    np.savetxt(testpath, test, delimiter=delimiter, fmt='%s',
                               header=delimiter.join(test[0].__dict__.keys()))
                    mltb.find_best(models, strategy=lambda x: x,
                                   key='score_test')
                    best = mltb.select_best()
                    with open(bpkpath, 'w') as bpkl:
                        pkl.dump(best, bpkl)
                else:
                    with open(bpkpath, 'r') as bpkl:
                        best = pkl.load(bpkl)
                    order, models = mltb.find_best(models=best,
                                                   strategy=lambda x: x,
                                                   key='score_test')
                    best = mltb.select_best(best=models)
                print('Best models:')
                print(best)

            # ----------------------------------------------------------------
            # execute Models and save the output raster map
            if self.checkbox.isChecked():
                print('\Execute the model to the whole raster map.')
                mltb.execute(best=best, transform=transform,
                             untransform=untransform,
                             output_file=self.TextOut.text())

                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'raster')

        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
