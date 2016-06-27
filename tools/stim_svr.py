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

from PyQt4.QtGui import QHBoxLayout, QLabel, QLineEdit, QComboBox

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMLogging
from stem_utils_server import STEMSettings
import traceback
from machine_learning import MLToolBox, SEP, BEST_STRATEGY_MEAN
from exported_objects import return_argument
from sklearn.svm import SVR
import numpy as np
import pickle as pkl
import os
from PyQt4.QtCore import SIGNAL
from functools import partial
from pyro_stem import PYROSERVER
from pyro_stem import MLPYROOBJNAME
from pyro_stem import ML_PORT
from osgeo import ogr

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

        labelc = "Effettuare la cross validation"
        self._insertSecondCheckbox(labelc, 0)
        self.checkbox2.stateChanged.connect(self.crossVali)

        self._insertThirdLineEdit(label="Inserire il numero di fold della "
                                  "cross validation", posnum=1)
        self.Linedit3.setEnabled(False)
        kernels = ['RBF', 'lineare', 'polinomiale', 'sigmoidale']

        self.lk = 'Selezionare il kernel da utilizzare'
        self._insertFirstCombobox(self.lk, 2, kernels)
        
        self._insertFirstLineEdit(label="Inserire il parametro C", posnum=3)
        self._insertSecondLineEdit(label="Inserire il valore di epsilon",
                                   posnum=4)
        self._insertFourthLineEdit(label="Inserire il valore di gamma",
                                   posnum=5)
        self._insertFifthLineEdit(label="Inserire il valore di r", posnum=6)
        self._insertSixthLineEdit(label="Inserire il valore del grado del polinomio", posnum=7)

        trasf = ['nessuna', 'logaritmo', 'radice quadrata']

        self.lk = 'Selezionare la trasformazione'
        self._insertFourthCombobox(self.lk, 8, trasf)

        mets = ['no', 'manuale', 'file']
        self.lm = "Selezione variabili"
        self._insertMethod(mets, self.lm, 9)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self.llcc = "Colonne delle feature da utilizzare"
        self._insertLayerChooseCheckBox2Options(self.llcc, pos=10)
        self.label_layer2.setEnabled(False)
        self.layer_list2.setEnabled(False)

        self.lio = "File di selezione"
        self._insertFileInputOption(self.lio, 11, "Text file (*.txt)")
        self.labelFO.setEnabled(False)
        self.TextInOpt.setEnabled(False)
        self.BrowseButtonInOpt.setEnabled(False)

        self._insertSingleInputOption(12, label="Vettoriale di validazione")
        STEMUtils.addLayerToComboBox(self.BaseInputOpt, 0, empty=True)
        #self.BaseInputOpt.setEnabled(False)
        #self.labelOpt.setEnabled(False)

        label = "Seleziona la colonna per la validazione"
        self._insertSecondCombobox(label, 13)

        ls = "Indice di accuratezza per la selezione del modello"
        self._insertThirdCombobox(ls, 14, [u'R²', u'MSE'])

        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2,
                                 empty=True)
        self.BaseInputOpt.currentIndexChanged.connect(self.columnsChange2)

        label = "Creare output"
        self._insertCheckbox(label, 15)

        # colonna per i valori della stima
        self.horizontalLayout_field = QHBoxLayout()
        self.labelfield = QLabel()
        self.labelfield.setObjectName("labelfield")
        self.labelfield.setText(self.tr(name, "Colonna per i valori della stima"))
        self.horizontalLayout_field.addWidget(self.labelfield)
        self.TextOutField = QLineEdit()
        self.TextOutField.setObjectName("TextOutField")
        self.TextOutField.setMaxLength(9)
        self.horizontalLayout_field.addWidget(self.TextOutField)
        self.verticalLayout_output.insertLayout(4, self.horizontalLayout_field)
        
        # vettoriale di mappa
        self.horizontalLayout_combo4 = QHBoxLayout()
        self.horizontalLayout_combo4.setObjectName("horizontalLayout_combo4")
        self.LabelCombo4 = QLabel()
        self.LabelCombo4.setObjectName("LabelCombo4")
        self.LabelCombo4.setWordWrap(True)
        self.horizontalLayout_combo4.addWidget(self.LabelCombo4)
        self.BaseInputCombo4 = QComboBox()
        self.BaseInputCombo4.setEditable(True)
        self.BaseInputCombo4.setObjectName("BaseInputCombo4")
        self.horizontalLayout_combo4.addWidget(self.BaseInputCombo4)
        
        self.verticalLayout_output.insertLayout(5, self.horizontalLayout_combo4)
        self.LabelCombo4.setText(self.tr("", "Vettoriale di mappa"))
        STEMUtils.addLayerToComboBox(self.BaseInputCombo4, 0, empty=True)
        
        # inserimento output mappa
        self._insertSecondOutput("Risultato mappa", 6)
        self.BrowseButton2.setText(self.tr(name, "Sfoglia"))
        self.connect(self.BrowseButton2, SIGNAL("clicked()"),
                     partial(self.browseDir, self.TextOut2))

        STEMSettings.restoreWidgetsValue(self, self.toolName)
        
        self.outputStateChanged()
        self.checkbox.stateChanged.connect(self.outputStateChanged)
        
        self.BaseInputCombo.currentIndexChanged.connect(self.kernelChanged)
        self.kernelChanged()
        
        self.BaseInputCombo4.currentIndexChanged.connect(self.map_vector_status_changed)
        self.map_vector_status_changed() # we don't want to have output enabled the first time
        
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())
        
    def check_number_of_folds(self):
        if self.checkbox2.isChecked():
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            vect = ogr.Open(invectsource)
            layer = vect.GetLayer()
            nfeatures = layer.GetFeatureCount()
            if nfeatures < int(self.Linedit3.text()):
                return u"Il numero di features ({}) non può essere inferiore al numero di fold ({}).".format(nfeatures, int(self.Linedit3.text()))
        return ""        

    def check_vettoriale_validazione(self):
        if self.BaseInputOpt.currentText() != "" and self.BaseInputCombo2.currentText() == "":
            return "Devi specificare una colonna per la validazione"
        else:
            return ""    
        
    def map_vector_status_changed(self):
        if self.BaseInputCombo4.currentText() == '':
            self.LabelOut2.setEnabled(False)
            self.TextOut2.setEnabled(False)
            self.BrowseButton2.setEnabled(False)
#             self.AddLayerToCanvas.setEnabled(False)
#             self.labelfield.setEnabled(False)
#             self.TextOutField.setEnabled(False)
        else:
            self.LabelOut2.setEnabled(True)
            self.TextOut2.setEnabled(True)
            self.BrowseButton2.setEnabled(True)

    def outputStateChanged(self):
        if self.checkbox.isChecked():
            self.LabelOut.setEnabled(True)
            self.TextOut.setEnabled(True)
            self.BrowseButton.setEnabled(True)
            self.AddLayerToCanvas.setEnabled(True)
            self.labelfield.setEnabled(True)
            self.TextOutField.setEnabled(True)
        else:
            self.LabelOut.setEnabled(False)
            self.TextOut.setEnabled(False)
            self.BrowseButton.setEnabled(False)
            self.AddLayerToCanvas.setEnabled(False)
            self.labelfield.setEnabled(False)
            self.TextOutField.setEnabled(False)

    def columnsChange(self):
        STEMUtils.addColumnsName(self.BaseInput, self.layer_list)

    def columnsChange2(self):
        STEMUtils.addColumnsName(self.BaseInputOpt, self.BaseInputCombo2,
                                 empty=True)

    def kernelChanged(self):
        kernel = self.BaseInputCombo.currentText()
        if kernel == 'lineare':
            self.LabelLinedit4.setEnabled(False)
            self.Linedit4.setEnabled(False)
            self.LabelLinedit5.setEnabled(False)
            self.Linedit5.setEnabled(False)
            self.LabelLinedit6.setEnabled(False)
            self.Linedit6.setEnabled(False)
        elif kernel == 'polinomiale':
            self.LabelLinedit4.setEnabled(True)
            self.Linedit4.setEnabled(True)
            self.LabelLinedit5.setEnabled(True)
            self.Linedit5.setEnabled(True)
            self.LabelLinedit6.setEnabled(True)
            self.Linedit6.setEnabled(True)
        elif kernel == 'sigmoidale':
            self.LabelLinedit4.setEnabled(True)
            self.Linedit4.setEnabled(True)
            self.LabelLinedit5.setEnabled(True)
            self.Linedit5.setEnabled(True)
            self.LabelLinedit6.setEnabled(False)
            self.Linedit6.setEnabled(False)
        elif kernel == 'RBF':
            self.LabelLinedit4.setEnabled(True)
            self.Linedit4.setEnabled(True)
            self.LabelLinedit5.setEnabled(False)
            self.Linedit5.setEnabled(False)
            self.LabelLinedit6.setEnabled(False)
            self.Linedit6.setEnabled(False)

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
        kernel_name = {
            'RBF': 'rbf',
            'sigmoidale': 'sigmoid',
            'polinomiale': 'poly',
            'lineare': 'linear'
        }
        
        kernel = str(self.BaseInputCombo.currentText())
        params = {'probability': True}       
        params['kernel'] = kernel_name[kernel]
        name = 'SVR_k{}'.format(params['kernel'])
        
        if self.Linedit.text():
            params['C'] = float(self.Linedit.text())
            name += '_C{}'.format(params['C'])
            
        if self.Linedit2.text():
            params['epsilon'] = float(self.Linedit2.text())
            
        if kernel in ['RBF', 'sigmoidale', 'polinomiale']:
            if self.Linedit4.text():
                params['gamma'] = float(self.Linedit4.text())
                name += '_g{}'.format(params['gamma'])
                
            if kernel in ['sigmoidale', 'polinomiale']:
                if self.Linedit5.text():
                    params['coef0'] = float(self.Linedit5.text())
                    name += '_r{}'.format(params['coef0'])
                    
                if kernel == 'polinomiale':
                    if self.Linedit6.text():
                        params['degree'] = int(self.Linedit6.text())
                        name += '_d{}'.format(params['degree'])
                        
        return [{'name': name, 'model': SVR, 'kwargs': params}], csv + name

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

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        com = ['python', 'mlcmd.py']
        log = STEMLogging()
        invect = str(self.BaseInput.currentText())
        invectsource = STEMUtils.getLayersSource(invect)
        invectcol = str(self.layer_list.currentText())
        cut, cutsource, mask = self.cutInput(invect, invectsource,
                                             'vector', local=self.LocalCheck.isChecked())
        prefcsv = "stimsvr_{vect}_{col}".format(vect=invect,
                                                col=invectcol)
        if not self.LocalCheck.isChecked():
            home = STEMUtils.get_temp_dir()
        else:
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
                    ncolumnschoose_new = []
                    i = 0
                    for n in fscolumns:
                        if n == 1:
                            ncolumnschoose_new.append(ncolumnschoose[i])
                        i += 1
                    ncolumnschoose = ncolumnschoose_new
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
                                                     'vector', local=self.LocalCheck.isChecked())
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

            log.debug(' '.join(str(c) for c in com))
            STEMUtils.saveCommand(com)
            if self.LocalCheck.isChecked():
                mltb = MLToolBox()
            else:
                import Pyro4
                mltb = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                    port=ML_PORT,
                                                                    name=MLPYROOBJNAME))
                invectsource = STEMUtils.pathClientWinToServerLinux(invectsource)
                inrastsource = STEMUtils.pathClientWinToServerLinux(inrastsource)
                optvectsource = STEMUtils.pathClientWinToServerLinux(optvectsource)
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
#                 log.debug('    From:')
#                 log.debug('      - vector: %s' % mltb.vector)
#                 log.debug('      - training column: %s' % mltb.column)
#                 if mltb.use_columns:
#                     log.debug('      - use columns: %s' % mltb.use_columns)
#                 if mltb.raster:
#                     log.debug('      - raster: %s' % mltb.raster)
                if not self.LocalCheck.isChecked():
                    trnpath = STEMUtils.pathClientWinToServerLinux(trnpath)
                X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                             nodata=nodata)
            else:
                log.debug('    Load from:')
                log.debug('      - %s' % trnpath)
                dt = np.loadtxt(trnpath, delimiter=SEP, skiprows=1)
                X, y = dt[:, :-1], dt[:, -1]
            X = X.astype(float)
            log.debug('Training sample shape: {val}'.format(val=X.shape))

            if fscolumns is not None:
                if not self.LocalCheck.isChecked():
                    infile = STEMUtils.pathClientWinToServerLinux(infile)
                X = mltb.data_transform(X=X, y=y, scaler=None,
                                        fscolumns=fscolumns,
                                        fsfile=infile, fsfit=True)

            # ----------------------------------------------------------------
            # Extract test samples
            # Extract test samples
            log.debug('Extract test samples')
            Xtest, ytest = None, None
            if mltb.getTVector() and mltb.getTColumn():
                # extract_training(vector_file, column, csv_file, raster_file=None,
                #                  use_columns=None, delimiter=SEP, nodata=None)
                # testpath = os.path.join(args.odir, args.csvtest)
                testpath = os.path.join(home,
                                        "{p}_csvtest.csv".format(p=prefcsv))
                if (not os.path.exists(testpath) or overwrite):
                    f = open(testpath, "w")
                    f.close()
                    log.debug('    From:')
                    log.debug('      - vector: %s' % mltb.getTVector())
                    log.debug('      - training column: %s' % mltb.getTColumn())
                    if mltb.getUseColumns():
                        log.debug('      - use columns: %s' % mltb.getUseColumns())
                    if mltb.getRaster():
                        log.debug('      - raster: %s' % mltb.getTRaster())
                    if not self.LocalCheck.isChecked():
                        temp_testpath = STEMUtils.pathClientWinToServerLinux(testpath)
                    else:
                        temp_testpath = testpath
                    Xtest, ytest = mltb.extract_test(csv_file=temp_testpath,
                                                     nodata=nodata)
                    dt = np.concatenate((Xtest.T, ytest[None, :]), axis=0).T
                    f = open(testpath, "w")
                    np.savetxt(f, dt, delimiter=SEP, header="# last column is the training.")
                    f.close()
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
                    mltb.find_best(model, strategy=return_argument,
                                   key='score_test')
                    best = mltb.select_best()
                    with open(bpkpath, 'w') as bpkl:
                        pkl.dump(best, bpkl)
                    if self.checkbox.isChecked():
                        STEMUtils.copyFile(testpath, out)
                else:
                    with open(bpkpath, 'r') as bpkl:
                        best = pkl.load(bpkl)
                    order, models = mltb.find_best(models=best,
                                                   strategy=return_argument,
                                                   key='score_test')
                    best = mltb.select_best(best=models)
                log.debug('Best models:')
                log.debug(best)

            # ----------------------------------------------------------------
            # execute Models and save the output raster map
            if self.checkbox.isChecked():
                if best is None:
                    order, models = mltb.find_best(models, key='score',
                                                   strategy=return_argument)
                    best = mltb.select_best(best=models)
                log.debug('Execute the model to the whole raster map.')
                map_vector = str(self.BaseInput4.currentText())
                if map_vector:
                    map_vec_source = STEMUtils.getLayersSource(map_vector)
                    finalinp = map_vec_source
                else:
                    finalinp = None
                if self.TextOutField.text():
                    fname = str(self.TextOutField.text())
                else:
                    fname = None

                if not self.LocalCheck.isChecked():
                    temp_out = STEMUtils.pathClientWinToServerLinux(out)
                else:
                    temp_out = out
                mltb.execute(input_file=finalinp, best=best, transform=trasf,
                             untransform=utrasf, output_file=temp_out,
                             field=fname)
                STEMUtils.copyFile(crosspath, out)
                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(out, 'vector')
                STEMMessageHandler.success("Il file {name} è stato scritto "
                                           "correttamente".format(name=out))
            else:
                STEMMessageHandler.success("Esecuzione completata")
            STEMUtils.removeFiles(home, "{pr}*".format(pr=prefcsv))
            
            if not self.LocalCheck.isChecked():
                mltb._pyroRelease()
        except:
            if not self.LocalCheck.isChecked():
                mltb._pyroRelease()
            STEMUtils.removeFiles(home, "{pr}*".format(pr=prefcsv))
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
