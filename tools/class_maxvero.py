# -*- coding: utf-8 -*-

"""
Tool to classify maps through Maximum likelihood.

It use the STEM library machine_learning and numpy, sklearn library

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
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings, STEMLogging
import traceback
from sklearn.naive_bayes import GaussianNB
from machine_learning import MLToolBox, SEP
import os
import pickle as pkl
import numpy as np


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
        self.llcc = "Selezionare le bande da utilizzare cliccandoci sopra"
        self._insertLayerChooseCheckBox2(self.llcc, pos=3)
        self.BaseInput2.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)

        self.label_layer2.setEnabled(False)
        self.layer_list2.setEnabled(False)

        self._insertThirdLineEdit(label="Inserire il numero di fold della "
                                  "cross validation", posnum=0)

        mets = ['no', 'manuale', 'file']
        self.lm = "Selezione feature"
        self._insertMethod(mets, self.lm, 3)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self.lio = "File di selezione"
        self._insertFileInputOption(self.lio, 4)
        self.labelFO.setEnabled(False)
        self.TextInOpt.setEnabled(False)
        self.BrowseButtonInOpt.setEnabled(False)

        self._insertSingleInputOption(5, label="Vettoriale di validazione")
        STEMUtils.addLayerToComboBox(self.BaseInputOpt, 0, empty=True)

        label = "Seleziona la colonna per la validazione"
        self._insertSecondCombobox(label, 6)

        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2)
        self.BaseInputOpt.currentIndexChanged.connect(self.columnsChange2)

        label = "Creare output"
        self._insertCheckbox(label, 7)

        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

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

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        com = ['python', 'mlcmd.py']
        log = STEMLogging()
        try:
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            invectcol = str(self.layer_list.currentText())
            cut, cutsource, mask = self.cutInput(invect, invectsource,
                                                 'vector')
            prefcsv = "maxvero_{vect}_{col}".format(vect=invect, col=invectcol)
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
            prefcsv += "_{n}".format(n=nfold)
            models = [{'name': 'gaussianNB', 'model': GaussianNB,
                       'kwargs': {}}]
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

            home = STEMSettings.value("stempath")
            trnpath = os.path.join(home,
                                   "{p}_csvtraining.csv".format(p=prefcsv))
            crosspath = os.path.join(home,
                                     "{p}_csvcross.csv".format(p=prefcsv))

            com.extend(['--n-folds', str(nfold), '--n-jobs', '1', '--n-best',
                        '1', '--scoring', 'accuracy', '--models', str(models),
                        '--csv-cross', crosspath, '--csv-training', trnpath,
                        '--best-strategy', 'mean', invectsource, invectcol])
            fscolumns = None
            if feat == 'manuale':
                infile = self.TextInOpt.text()
                if os.path.exists(infile):
                    com.extend(['--feature-selection-file', infile])
                    fscolumns = np.loadtxt(infile)
            if ncolumnschoose:
                com.extend(['-u', ncolumnschoose])
            if self.checkbox.isChecked():
                com.extend(['-e', '--output-raster-name', self.TextOut.text()])
            STEMUtils.saveCommand(com)
            if self.LocalCheck.isChecked():
                mltb = MLToolBox()
            else:
                import Pyro4
                mltb = Pyro4.Proxy("PYRONAME:stem.machinelearning")
            mltb.set_params(vector_file=invectsource, column=invectcol,
                            use_columns=ncolumnschoose,
                            raster_file=inrastsource, traster=None,
                            models=models, scoring='accuracy',
                            n_folds=nfold, n_jobs=1, n_best=1,
                            tvector=optvectsource, tcolumn=optvectcols,
                            best_strategy=getattr(np, 'mean'),
                            scaler=None, fselector=None, decomposer=None,
                            transform=None, untransform=None)

            nodata = -9999
            overwrite = False
            delimiter = ';'
            # ---------------------------------------------------------------
            # Extract training samples
            log.debug('Extract training samples')

            if (not os.path.exists(trnpath) or overwrite):
                log.debug('    From:')
                log.debug('      - vector: %s' % mltb.vector)
                log.debug('      - training column: %s' % mltb.column)
                if mltb.use_columns:
                    log.debug('      - use columns: %s' % mltb.use_columns)
                if mltb.raster:
                    log.debug('      - raster: %s' % mltb.raster)
                X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                             dtype=np.uint32, nodata=nodata)
            else:
                log.debug('    Load from:')
                log.debug('      - %s' % trnpath)
                dt = np.loadtxt(trnpath, delimiter=SEP, skiprows=1)
                X, y = dt[:, :-1], dt[:, -1]
            X = X.astype(float)
            log.debug('Training sample shape: {val}'.format(val=X.shape))

            if fscolumns:
                X = mltb.data_transform(X=X, y=y, scaler=None,
                                        fscolumns=fscolumns,
                                        fsfile=infile, fsfit=True)
            # -----------------------------------------------------------------------
            # Extract test samples
            log.debug('Extract test samples')
            Xtest, ytest = None, None
            if mltb.tvector and mltb.tcolumn:
                # extract_training(vector_file, column, csv_file, raster_file=None,
                #                  use_columns=None, delimiter=SEP, nodata=None,
                #                  dtype=np.uint32)
                # testpath = os.path.join(args.odir, args.csvtest)
                testpath = os.path.join(home,
                                        "{p}_csvtest.csv".format(p=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    log.debug('    From:')
                    log.debug('      - vector: %s' % mltb.tvector)
                    log.debug('      - training column: %s' % mltb.tcolumn)
                    if mltb.use_columns:
                        log.debug('      - use columns: %s' % mltb.use_columns)
                    if mltb.raster:
                        log.debug('      - raster: %s' % mltb.traster)
                    Xtest, ytest = mltb.extract_test(csv_file=testpath,
                                                     nodata=nodata)
                    dt = np.concatenate((Xtest.T, ytest[None, :]), axis=0).T
                    np.savetxt(testpath, dt, delimiter=SEP,
                               header="# last column is the training.")
                else:
                    log.debug('    Load from:')
                    log.debug('      - %s' % trnpath)
                    dt = np.loadtxt(testpath, delimiter=SEP, skiprows=1)
                    Xtest, ytest = dt[:, :-1], dt[:, -1]
                Xtest = Xtest.astype(float)
                log.debug('Training sample shape: {val}'.format(val=Xtest.shape))

            # ---------------------------------------------------------------
            # Cross Models
            log.debug('Cross-validation of the models')

            bpkpath = os.path.join(home,
                                   "{p}_best_pickle.pkl".format(p=prefcsv))
            if (not os.path.exists(crosspath) or overwrite):
                cross = mltb.cross_validation(X=X, y=y, transform=None)
                np.savetxt(crosspath, cross, delimiter=delimiter, fmt='%s',
                           header=delimiter.join(['id', 'name', 'mean', 'max',
                                                  'min', 'std', 'time']))
                mltb.find_best(models)
                best = mltb.select_best()
                with open(bpkpath, 'w') as bpkl:
                    pkl.dump(best, bpkl)
            else:
                log.debug('    Read cross-validation results from file:')
                log.debug('      -  %s' % crosspath)
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
            log.debug('Best models:')
            log.debug(best)

            # ---------------------------------------------------------------
            # test Models
            if Xtest is not None and ytest is not None:
                log.debug('Test models with an indipendent dataset')
                testpath = os.path.join(home,
                                        "{p}_csvtest.csv".format(p=prefcsv))
                bpkpath = os.path.join(home,
                                       "{p}_test_pickle.pkl".format(p=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    test = mltb.test(Xtest=Xtest, ytest=ytest, X=X, y=y,
                                     transform=None)
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
                log.debug('Best models:')
                log.debug(best)

            # ----------------------------------------------------------------
            # execute Models and save the output raster map

            if self.checkbox.isChecked():
                out = self.TextOut.text()
                log.debug('Execute the model to the whole raster map.')
                mltb.execute(X=X, y=y, output_file=out,
                             best=best, transform=None, untransform=None)

                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(out, 'raster')
                STEMMessageHandler.success("Il file {name} è stato scritto "
                                           "correttamente".format(name=out))
            else:
                STEMMessageHandler.success("Esecuzione completata")
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
