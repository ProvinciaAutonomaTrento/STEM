# -*- coding: utf-8 -*-

"""
Tool to perform Support Vector Regression

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

from PyQt4.QtGui import QHBoxLayout, QLabel, QLineEdit

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMLogging
from stem_utils_server import STEMSettings
import traceback
from machine_learning import MLToolBox, SEP, BEST_STRATEGY_MEAN
from sklearn.svm import SVR
import numpy as np
import pickle as pkl
import os
from pyro_stem import PYROSERVER
from pyro_stem import MLPYROOBJNAME
from pyro_stem import ML_PORT


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.shp')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput(label='Dati di input vettoriale')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.labelcol = "Seleziona la colonna con indicazione del parametro da stimare"
        self._insertLayerChoose(pos=1)
        self.label_layer.setText(self.tr("", self.labelcol))
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.columnsChange)

        self.llcc = "Colonne delle feature da utilizzare"
        self._insertLayerChooseCheckBox2(self.llcc, pos=3)
        self.label_layer2.setEnabled(False)
        self.layer_list2.setEnabled(False)

        labelc = "Effettuare la cross validation"
        self._insertSecondCheckbox(labelc, 0)
        self.checkbox2.stateChanged.connect(self.crossVali)

        self._insertThirdLineEdit(label="Inserire il numero di fold della "
                                  "cross validation", posnum=1)
        self.Linedit3.setEnabled(False)
        kernels = ['RBF', 'lineare', 'polinomiale', 'sigmoidale']

        self.lk = 'Selezionare il kernel da utilizzare'
        self._insertFirstCombobox(self.lk, 2, kernels)
        self.BaseInputCombo.currentIndexChanged.connect(self.kernelChanged)
        self._insertFirstLineEdit(label="Inserire il parametro C", posnum=3)
        self._insertSecondLineEdit(label="Inserire il valore di epsilon",
                                   posnum=4)
        self._insertFourthLineEdit(label="Inserire il valore di gamma",
                                   posnum=5)

        trasf = ['nessuna', 'logaritmo', 'radice quadrata']

        self.lk = 'Selezionare la trasformazione'
        self._insertFourthCombobox(self.lk, 6, trasf)

        mets = ['no', 'manuale', 'file']
        self.lm = "Selezione variabili"
        self._insertMethod(mets, self.lm, 7)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self.lio = "File di selezione"
        self._insertFileInputOption(self.lio, 8, "Text file (*.txt)")
        self.labelFO.setEnabled(False)
        self.TextInOpt.setEnabled(False)
        self.BrowseButtonInOpt.setEnabled(False)

        self._insertSingleInputOption(9, label="Vettoriale di validazione")
        STEMUtils.addLayerToComboBox(self.BaseInputOpt, 0, empty=True)
        #self.BaseInputOpt.setEnabled(False)
        #self.labelOpt.setEnabled(False)

        label = "Seleziona la colonna per la validazione"
        self._insertSecondCombobox(label, 10)

        ls = "Indice di accuratezza per la selezione del modello"
        self._insertThirdCombobox(ls, 11, ['R²', 'MSE'])

        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2,
                                 empty=True)
        self.BaseInputOpt.currentIndexChanged.connect(self.columnsChange2)

        label = "Creare output"
        self._insertCheckbox(label, 12)

        self.horizontalLayout_field = QHBoxLayout()
        self.labelfield = QLabel()
        self.labelfield.setObjectName("labelfield")
        self.labelfield.setText(self.tr(name, "Colonna per i valori della stima"))
        self.horizontalLayout_field.addWidget(self.labelfield)
        self.TextOutField = QLineEdit()
        self.TextOutField.setObjectName("TextOutField")
        self.horizontalLayout_field.addWidget(self.TextOutField)
        self.verticalLayout_output.insertLayout(4, self.horizontalLayout_field)

        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)

    def columnsChange2(self):
        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2,
                                 empty=True)

    def kernelChanged(self):
        if self.BaseInputCombo.currentText() == 'lineare':
            self.LabelLinedit3.setEnabled(False)
            self.Linedit3.setEnabled(False)
        else:
            self.LabelLinedit3.setEnabled(True)
            self.Linedit3.setEnabled(True)
        if self.BaseInputCombo.currentText() == 'polinomiale':
            self.LabelLinedit3.setText(self.tr("", "Inserire il valore del "
                                               "grado del polinomio"))
        elif self.BaseInputCombo.currentText() in ['RBF', 'sigmoidale']:
            self.LabelLinedit3.setText(self.tr("",
                                               "Inserire il valore di gamma"))

    def methodChanged(self):
        if self.MethodInput.currentText() == 'file':
            self.layer_list2.clear()
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
            STEMUtils.addColumnsName(self.BaseInput, self.layer_list2,
                                     multi=True)
        else:
            self.layer_list2.clear()
            self.labelFO.setEnabled(False)
            self.TextInOpt.setEnabled(False)
            self.BrowseButtonInOpt.setEnabled(False)
            self.label_layer2.setEnabled(False)
            self.layer_list2.setEnabled(False)

    def getModel(self, csv):
        kernel = str(self.BaseInputCombo.currentText())
        c = float(self.Linedit.text())
        y = float(self.Linedit2.text())
        if kernel in ['RBF', 'sigmoidale']:
            if kernel == 'RBF':
                k = 'rbf'
            else:
                k = 'sigmoid'
            g = float(self.Linedit4.text())
            csv += "_{ke}_{ga}_{c}".format(ke=k, ga=g, c=c)
            return [{'name': 'SVC_k%s_C%f_g%f' % (k, c, g), 'model': SVR,
                     'kwargs': {'kernel': k, 'C': c, 'gamma': g, 'epsilon': y,
                                'probability': True}}], csv
        elif kernel == 'lineare':
            k = 'linear'
            csv += "_{ke}_{c}".format(ke=k, c=c)
            return [{'name': 'SVC_k%s_C%f' % (k, c), 'model': SVR,
                     'kwargs': {'kernel': k, 'C': c,
                                'probability': True}}], csv
        else:
            k = 'poly'
            g = float(self.Linedit4.text())
            d = 3 # TODO ask pietro
            csv += "_{ke}_{ga}_{c}".format(ke=k, ga=g, c=c)
            return [{'name': 'SVC_k%s_d%02d_C%f_g%f' % (k, d, c, g),
                     'model': SVR, 'kwargs': {'kernel': k, 'C': c, 'gamma': g,
                                              'epsilon': y, 'degree': d,
                                              'probability': True}
                     }], csv

    def crossVali(self):
        if self.checkbox2.isChecked():
            self.Linedit3.setEnabled(True)
        else:
            self.Linedit3.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def getTransform(self):
        if self.BaseInputCombo4.currentText() == 'logaritmo':
            return np.log, np.exp
        elif self.BaseInputCombo4.currentText() == 'radice quadrata':
            return np.sqrt, np.exp2
        else:
            return None, None

    def getScoring(self):
        if self.BaseInputCombo3.currentText() == 'MSE':
            return 'mean_squared_error'
        else:
            return 'r2'

    def crossVali(self):
        if self.checkbox2.isChecked():
            self.Linedit3.setEnabled(True)
        else:
            self.Linedit3.setEnabled(False)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        com = ['python', 'mlcmd.py']
        log = STEMLogging()
        invect = str(self.BaseInput.currentText())
        invectsource = STEMUtils.getLayersSource(invect)
        invectcol = str(self.layer_list.currentText())
        cut, cutsource, mask = self.cutInput(invect, invectsource,
                                             'vector')
        prefcsv = "stimsvr_{vect}_{col}".format(vect=invect,
                                                col=invectcol)
        home = STEMSettings.value("stempath")
        try:
            if cut:
                invect = cut
                invectsource = cutsource

            ncolumnschoose = [self.layer_list.itemText(i) for i in range(self.layer_list.count())]
            inrastsource = None
            try:
                ncolumnschoose.remove(invectcol)
            except:
                pass
            prefcsv += "_{n}".format(n=len(ncolumnschoose))

            feat = str(self.MethodInput.currentText())
            fscolumns = None
            if feat == 'file':
                infile = self.TextInOpt.text()
                if os.path.exists(infile):
                    com.extend(['--feature-selection-file', infile])
                    fscolumns = np.loadtxt(infile)
            elif feat == 'manuale':
                ncolumnschoose = STEMUtils.checkLayers(invectsource,
                                                       self.layer_list2, False)

            if self.checkbox2.isChecked():
                nfold = int(self.Linedit3.text())
                prefcsv += "_{n}".format(n=nfold)
            else:
                nfold = None

            model, prefcsv = self.getModel(prefcsv)
            feat = str(self.MethodInput.currentText())

            optvect = str(self.BaseInputOpt.currentText())
            if optvect:
                optvectsource = STEMUtils.getLayersSource(optvect)
                com.extend(['--test-vector', optvectsource])
                if str(self.BaseInputCombo2.currentText()) == '':
                    optvectcols = None
                else:
                    optvectcols = str(self.BaseInputCombo2.currentText())
                    com.extend(['--test-column', optvectcols])
                cut, cutsource, mask = self.cutInput(optvect, optvectsource,
                                                     'vector')
                if cut:
                    optvect = cut
                    optvectsource = cutsource

            else:
                optvectsource = None
                optvectcols = None

            trasf, utrasf = self.getTransform()
            scor = self.getScoring()

            trnpath = os.path.join(home,
                                   "{p}_csvtraining.csv".format(p=prefcsv))
            crosspath = os.path.join(home,
                                     "{p}_csvcross.csv".format(p=prefcsv))
            out = str(self.TextOut.text())

            com.extend(['--n-folds', str(nfold), '--n-jobs', '1', '--n-best',
                        '1', '--scoring', 'accuracy', '--models', str(model),
                        '--csv-cross', crosspath, '--csv-training', trnpath,
                        '--best-strategy', 'mean', invectsource, invectcol])

            if ncolumnschoose:
                com.extend(['-u', ' '.join(ncolumnschoose)])
            if self.checkbox.isChecked():
                com.extend(['-e', '--output-file', self.TextOut.text()])

            log.debug(' '.join(com))
            STEMUtils.saveCommand(com)
            if self.LocalCheck.isChecked():
                mltb = MLToolBox()
            else:
                import Pyro4
                mltb = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                    port=ML_PORT,
                                                                    name=MLPYROOBJNAME))
            mltb.set_params(vector=invectsource, column=invectcol,
                            use_columns=ncolumnschoose,
                            raster=inrastsource, models=model,
                            scoring=scor, n_folds=nfold, n_jobs=1,
                            tvector=optvectsource, tcolumn=optvectcols,
                            traster=None, n_best=1,
                            best_strategy=BEST_STRATEGY_MEAN,
                            scaler=None, fselector=None, decomposer=None,
                            transform=trasf, untransform=utrasf)

            nodata = -9999
            overwrite = False
            # ------------------------------------------------------------
            # Extract training samples

            if (not os.path.exists(trnpath) or overwrite):
                log.debug('    From:')
                log.debug('      - vector: %s' % mltb.vector)
                log.debug('      - training column: %s' % mltb.column)
                if mltb.use_columns:
                    log.debug('      - use columns: %s' % mltb.use_columns)
                if mltb.raster:
                    log.debug('      - raster: %s' % mltb.raster)
                X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                             nodata=nodata)
            else:
                log.debug('    Load from:')
                log.debug('      - %s' % trnpath)
                dt = np.loadtxt(trnpath, delimiter=SEP, skiprows=1)
                X, y = dt[:, :-1], dt[:, -1]
            X = X.astype(float)
            log.debug('Training sample shape: {val}'.format(val=X.shape))

            # ------------------------------------------------------------
            # Transform the input data
            if fscolumns is not None:
                X = mltb.data_transform(X=X, y=y, scaler=None,
                                        fscolumns=fscolumns,
                                        fsfile=infile, fsfit=True)

            # ----------------------------------------------------------------
            # Extract test samples
            Xtest, ytest = None, None
            log.debug('Extract test samples')
            if mltb.tvector and mltb.tcolumn:
                # extract_training(vector_file, column, csv_file, raster_file=None,
                #                  use_columns=None, delimiter=SEP, nodata=None)
                # testpath = os.path.join(args.odir, args.csvtest)
                testpath = os.path.join(home,
                                        "{pref}_csvtestsample.csv".format(pref=prefcsv))
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
                log.debug('Training sample shape: {val}'.format(val=X.shape))

            # ---------------------------------------------------------------
            # Cross Models
            log.debug('Cross-validation of the models')
            best = None
            bpkpath = os.path.join(home,
                                   "{pref}_best_pickle.csv".format(pref=prefcsv))
            if (not os.path.exists(crosspath) or overwrite):
                cross = mltb.cross_validation(X=X, y=y, transform=trasf)
                np.savetxt(crosspath, cross, delimiter=SEP, fmt='%s',
                           header=SEP.join(['id', 'name', 'mean', 'max',
                                                  'min', 'std', 'time']))
                mltb.find_best(model)
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
                testpath = os.path.join(home, "{p}_csvtest_{vect}_{col}."
                                        "csv".format(p=prefcsv,
                                                     vect=optvect,
                                                     col=optvectcols))
                bpkpath = os.path.join(home,
                                       "{pref}_test_pickle.csv".format(pref=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    test = mltb.test(Xtest=Xtest, ytest=ytest, X=X, y=y,
                                     transform=trasf)
                    np.savetxt(testpath, test, delimiter=SEP, fmt='%s',
                               header=SEP.join(test[0].__dict__.keys()))
                    mltb.find_best(model, strategy=lambda x: x,
                                   key='score_test')
                    best = mltb.select_best()
                    with open(bpkpath, 'w') as bpkl:
                        pkl.dump(best, bpkl)
                    STEMUtils.copyFile(testpath, out)
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
                if best is None:
                    order, models = mltb.find_best(models, key='score',
                                                   strategy=lambda x: x)
                    best = mltb.select_best(best=models)
                log.debug('Execute the model to the whole raster map.')
                if optvect:
                    finalinp = optvectsource
                else:
                    finalinp = None
                if self.TextOutField.text():
                    fname = str(self.TextOutField.text())
                else:
                    fname = None
                mltb.execute(input_file=finalinp, best=best, transform=trasf,
                             untransform=utrasf, output_file=out,
                             field=fname)
                STEMUtils.copyFile(crosspath, out)
                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(out, 'vector')
                STEMMessageHandler.success("Il file {name} è stato scritto "
                                           "correttamente".format(name=out))
            else:
                STEMMessageHandler.success("Esecuzione completata")
            STEMUtils.removeFiles(home, "{pr}*".format(pr=prefcsv))
        except:
            STEMUtils.removeFiles(home, "{pr}*".format(pr=prefcsv))
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
