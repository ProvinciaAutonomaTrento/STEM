# -*- coding: utf-8 -*-
"""
Command line tool to do classification and valuation using different methods

Authors: Pietro Zambelli

Date: October 2014
"""
from __future__ import print_function

# from python standard library
import imp
import sys
import os
import argparse
from datetime import datetime
import pickle as pkl
from pprint import pprint

# import scientific libraires
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import RFECV
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC

# import local libraries
from feature_selection import SSF
from machine_learning import MLToolBox, SEP, NODATA, get_cv


MODELS = {# UC_26 Support Vector Machine (SVM)
          'SVM': [],
          # UC_27 Classificazione minima distanza: KNeighborsClassifier
          # UC_28 Classificazione massima verosimiglianza: EmpiricalCovariance
          # UC_29 Spectral Angle Mapper (SAM) i.spec.sam (G6)
          # UC_30 Stimatore lineare: LinearRegression
          # UC_32 Attribuzione/modifica delle classi tematiche: SVR
          'SVR': []}

TRANS = {'sqrt': np.sqrt, 'log': np.log}
UNTRANS = {'sqrt': np.exp2, 'log': np.exp}


# =======================================================================
# Parser functions
def pca_components(string):
    try:
        return int(string)
    except ValueError:
        return None if string == '' else string


def importable(path):
    return imp.load_source("classifiers", path)


def index(string, sep=',', rangesep='-'):
    """
    >>> indx = '1-5,34-36,40'
    >>> [i for i in get_indexes(indx)]
    [1, 2, 3, 4, 5, 34, 35, 36, 40]
    """
    if string == '':
        return
    for ind in string.split(sep):
        if rangesep in ind:
            start, stop = ind.split(rangesep)
            for i in range(int(start), int(stop) + 1):
                yield i
        else:
            yield int(ind)


def indexstr(string):
    return [i for i in index(string)]


# =======================================================================
# Define the parser options
def get_parser():
    """Create the parser for running as script"""
    parser = argparse.ArgumentParser(description='Test several machine-'
                                                 'learning models.')
    parser.add_argument('vector', type=str, metavar='VECTOR',
                        help='Training vector format supported by OGR')
    parser.add_argument('column', type=str, metavar='COLUMN',
                        help='Column name with the values/classes'
                             ' used as training')
    parser.add_argument('-u', '--use-columns', type=str, metavar='COLUMNS',
                        default=None, nargs='+', dest='use_columns',
                        help='Name of the columns containing the data that '
                             'will be used instad of the raster input map.')
    parser.add_argument('-r', '--raster', type=str, default=None, dest='raster',
                        help='Multi/Hyper spectral raster file supported by GDAL')
    parser.add_argument('-t', '--csv-training', type=str, dest='csvtraining',
                        default='training.csv',
                        help='Name of the CSV file with the training values'
                             ' extracted by the raster and vector map.')
    parser.add_argument('-cr', '--csv-cross', type=str, dest='csvcross',
                        default='cross_validation.csv',
                        help='Name of the CSV file with the models results.')
    parser.add_argument('-cd', '--csv-delimiter', type=str, default=SEP,
                        dest='csvdelimiter', help='CSV delimiter.')
    parser.add_argument('-m', '--models', type=importable,
                        dest='models', default='classifiers.py',
                        help='A python file containing a list of dictionary'
                             ' with the models that will be tested.')
    parser.add_argument('-n', '--list-name', type=str,
                        dest='listname', default='ALL',
                        help='The python name variable with the model list')
    parser.add_argument('-k', '--scoring', default='accuracy', dest='scoring',
                        choices=['accuracy', 'f1', 'precision',
                                 'recall', 'roc_auc', 'adjusted_rand_score',
                                 'mean_absolute_error', 'mean_squared_error',
                                 'r2'],
                        help='Set the method that will be used for the model'
                             ' evaluation. See:\nhttp://scikit-learn.org/'
                             'stable/modules/model_evaluation.html')
    parser.add_argument('-i', '--mod-indexes', type=indexstr,
                        dest='imod', default='',
                        help='Define which model will be tested'
                             ' by index, for example with the following string'
                             ' "1-5,34-36,40", only model with index:'
                             '[1, 2, 3, 4, 5, 34, 35, 36, 40] will be used.')
    parser.add_argument('-x', '--cols-indexes', type=str,
                        dest='icols', default='',
                        help='Npy input file with the columns index to use'
                              'could be use to select a subset of the dataset')
    parser.add_argument('-o', '--output-dir', type=str,
                        dest='odir', default='',
                        help='Specify the directory that will contain all the'
                             'outputs')
    parser.add_argument('-of', '--output-file', type=str,
                        dest='ofile', default=None,
                        help='Specify the output filename')
    parser.add_argument('-w', '--output-raster-name', type=str,
                        dest='rname', default='%s',
                        help='Specify the name of the output raster map that'
                             ' will be written.')
    parser.add_argument('-c', '--cross-validation', action='store_true',
                        dest='cross', default=False,
                        help='Apply the models to the input data and '
                             'write the output raster maps.')
    parser.add_argument('-e', '--execute', action='store_true',
                        dest='execute', default=False,
                        help='Apply the models to the input data and '
                             'write the output raster maps.')
    parser.add_argument('--o', '--overwrite', action='store_true',
                        dest='overwrite', default=False,
                        help='overwrite')
    parser.add_argument('-b', '--n-best', type=int,
                        dest='n_best', default=1,
                        help='Number of best model to apply on the raster.')
    parser.add_argument('-bs', '--best-strategy', default='mean',
                        dest='best_strategy', choices=['min', 'mean', 'median'],
                        help='Strategy to use to select the best classifier.')
    parser.add_argument('-bp', '--best-pickle',
                        default='best_model.pickle',
                        dest='best_pickle', type=str,
                        help='All the best models are saved and serialized '
                             'using python pickle.')
    parser.add_argument('-nf', '--n-folds', type=int, dest='n_folds',
                        default=5, help='Number of folds that we want to use'
                                        ' to cross validate the dataset.')
    parser.add_argument('-nj', '--n-jobs', type=int, dest='n_jobs',
                        default=1, help='Number of jobs that we want to use'
                                        ' during the cross validations.')
    parser.add_argument('-s', '--scale', type=bool, nargs=2, dest='scale',
                        metavar='S', help='StandardScaler options: '
                                          'with_mean, with_std')
    parser.add_argument('-p', '--pca', type=pca_components, dest='pca',
                        metavar='n_components', default=NODATA, nargs='?',
                        help='See PCA n_componets documentation')
    parser.add_argument('-f', '--feature-selection', default='None',
                        dest='fs', help='Feature selection',
                        choices=['None', 'SSF', 'RFECV', 'LinearSVC',
                                 'ExtraTreesClassifier'], )
    parser.add_argument('-ff', '--feature-selection-file', default=None,
                        dest='ff', help='File with the Feature selected.')
    parser.add_argument('-fs', '--SSF-strategy', default='min',
                        dest='SSF_strategy', choices=['min', 'mean', 'median'],
                        help='Sequential Forward Floating Feature Selection'
                             ' (SSF) strategy to select the best.')
    parser.add_argument('-tr', '--test-raster', type=str, default=None,
                        dest='traster',
                        help='Multi/Hyper spectral raster file supported by'
                             ' GDAL')
    parser.add_argument('-tv', '--test-vector', type=str, default=None,
                        dest='tvector',
                        help='Training vector format supported by OGR')
    parser.add_argument('-tc', '--test-column', type=str, default=None,
                        dest='tcolumn',
                        help='Column name with the values/classes'
                             ' used as training')
    parser.add_argument('-tp', '--test-pickle',
                        default='test_model.pickle',
                        dest='test_pickle', type=str,
                        help='All the test models results saved and serialized '
                             'using python pickle.')
    parser.add_argument('-tf', '--csv-test', type=str, dest='csvtest',
                        default='test.csv',
                        help='Name of the CSV file with the test values'
                             ' extracted by the raster and vector map.')
    parser.add_argument('--transform', choices=['sqrt', 'log', ],
                        dest='transform', default=None,
                        help='Transform regression target before to apply the'
                             'regression.')
    parser.add_argument('-l', '--labels', type=pca_components, dest='labels',
                        metavar='LABEL', default=None, nargs='+',
                        help='Label tag')
    parser.add_argument('-v', '--verbosity', type=int, choices=(0, 1, 2),
                        default=0, dest='verbosity', help='Output verbosity.')
    parser.add_argument('-nd', '--no-data', type=float, default=NODATA,
                        dest='nodata',
                        help='Name of the columns containing the data that '
                             'will be used instad of the raster input map.')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.odir and not os.path.isdir(args.odir):
        os.mkdir(args.odir)

    with open(os.path.join(args.odir, 'history.txt'), 'a') as cmd:
        cmd.write('# %s\n' % str(datetime.now()))
        cmd.write(' '.join(sys.argv) + '\n')

    # -----------------------------------------------------------------------
    # Get Models
    models = getattr(args.models, args.listname)
    # write indexes
    for i, mod in enumerate(models):
        mod['index'] = i

    # filter models by index
    if args.imod:
        models = [models[i] for i in args.imod]

    # =======================================================================
    # Instantiate the class
    mltb = MLToolBox(vector_file=args.vector, column=args.column,
                     use_columns=args.use_columns, raster_file=args.raster,
                     models=models, scoring=args.scoring,
                     n_folds=args.n_folds, n_jobs=args.n_jobs,
                     n_best=args.n_best, nodata=args.nodata,
                     tvector=args.tvector, tcolumn=args.tcolumn,
                     traster=args.traster,
                     best_strategy=getattr(np, args.best_strategy),
                     scaler=None, fselector=None, decomposer=None,
                     transform=None, untransform=None)

    # -----------------------------------------------------------------------
    # Extract training samples
    print('\nExtract training samples')
    trnpath = os.path.join(args.odir, args.csvtraining)
    if (not os.path.exists(trnpath) or args.overwrite):
        print('    From:')
        print('      - vector: %s' % mltb.vector)
        print('      - training column: %s' % mltb.column)
        if mltb.use_columns:
            print('      - use columns: %s' % mltb.use_columns)
        if mltb.raster:
            print('      - raster: %s' % mltb.raster)
        X, y = mltb.extract_training(csv_file=trnpath, delimiter=SEP,
                                     nodata=args.nodata, dtype=np.uint32)
    else:
        print('    Load from:')
        print('      - %s' % trnpath)
        dt = np.loadtxt(trnpath, delimiter=SEP, skiprows=1)
        X, y = dt[:, :-1], dt[:, -1]
    X = X.astype(float)
    print('\nTraining sample shape:', X.shape)

    fselect = {
           # Sequential Forward Floating Feature Selection
           # with Jeffries-Matusita Distance
           'SSF': SSF(strategy=getattr(np, args.SSF_strategy)),
           # Recursive Feature Elimination and Cross-Validated (RFECV)
           'RFECV': RFECV(estimator=SVC(), cv=get_cv(y, args.n_folds)),
           # Linear Support Vector Classification
           'LinearSVC': LinearSVC(C=0.01, penalty="l1", dual=False),
           # Tree-based feature selection
           'ExtraTreesClassifier': ExtraTreesClassifier(n_estimators=250,
                                                        random_state=0)
           }

    # -----------------------------------------------------------------------
    # Scale
    scaler = None
    if args.scale:
        wm, ws = args.scale
        scaler = StandardScaler(with_mean=wm, with_std=ws)

    # -----------------------------------------------------------------------
    # Feature selector
    fselector = None
    fscolumns = None
    fspath = None
    if args.ff:
        fspath = os.path.join(args.odir, args.ff)
        if (os.path.exists(fspath) and not args.overwrite):
            fscolumns = np.loadtxt(fspath)
    if args.fs != 'None':
        fselector = fselect[args.fs]

    # -----------------------------------------------------------------------
    # Decomposer
    decomposer = PCA(n_components=args.pca) if args.pca != NODATA else None

    # -----------------------------------------------------------------------
    # Transform the input data
    X = mltb.data_transform(X=X, y=y, scaler=scaler, fselector=fselector,
                            decomposer=decomposer, fscolumns=fscolumns,
                            fsfile=fspath, fsfit=True)

    # -----------------------------------------------------------------------
    # Transform the training/target
    if args.transform:
        transform = TRANS[args.transform]
        untransform = UNTRANS[args.transform]
    else:
        transform, untransform = None, None

    # -----------------------------------------------------------------------
    # Extract test samples
    Xtest, ytest = None, None
    if args.tvector and args.tcolumn:
        # extract_training(vector_file, column, csv_file, raster_file=None,
        #                  use_columns=None, delimiter=SEP, nodata=None,
        #                  dtype=np.uint32)
        print('\nExtract test samples')
        testpath = os.path.join(args.odir, args.csvtest)
        if (not os.path.exists(testpath) or args.overwrite):
            print('    From:')
            print('      - vector: %s' % mltb.tvector)
            print('      - training column: %s' % mltb.tcolumn)
            if mltb.use_columns:
                print('      - use columns: %s' % mltb.use_columns)
            if mltb.raster:
                print('      - raster: %s' % mltb.traster)
            Xtest, ytest = mltb.extract_test(csv_file=testpath,
                                             nodata=args.nodata)
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

    # -----------------------------------------------------------------------
    # Cross Models
    if args.cross:
        print('\nCross-validation of the models')
        crosspath = os.path.join(args.odir, args.csvcross)
        bpkpath = os.path.join(args.odir, args.best_pickle)
        if (not os.path.exists(crosspath) or args.overwrite):
            cross = mltb.cross_validation(X=X, y=y, transform=transform)
            np.savetxt(crosspath, cross, delimiter=args.csvdelimiter, fmt='%s',
                       header=args.csvdelimiter.join(['id', 'name', 'mean', 'max',
                                                      'min', 'std', 'time']))
            mltb.find_best(models)
            best = mltb.select_best()
            with open(bpkpath, 'w') as bpkl:
                pkl.dump(best, bpkl)
        else:
            print('    Read cross-validation results from file:')
            print('      -  %s' % crosspath)
            with open(bpkpath, 'r') as bpkl:
                best = pkl.load(bpkl)
            order, models = mltb.find_best(models=best)
            best = mltb.select_best(best=models)
        print('\nBest models:')
        pprint(best)

    # -----------------------------------------------------------------------
    # test Models
    if Xtest is not None and ytest is not None:
        print('\nTest models with an indipendent dataset')
        testpath = os.path.join(args.odir, args.csvtest)
        bpkpath = os.path.join(args.odir, args.test_pickle)
        if (not os.path.exists(testpath) or args.overwrite):
            Xtest = mltb.data_transform(X=Xtest, y=ytest)
            test = mltb.test(Xtest=Xtest, ytest=ytest, X=X, y=y,
                             transform=transform)
            np.savetxt(testpath, test, delimiter=args.csvdelimiter, fmt='%s',
                       header=args.csvdelimiter.join(test[0].__dict__.keys()))
            mltb.find_best(models, strategy=lambda x: x, key='score_test')
            best = mltb.select_best()
            with open(bpkpath, 'w') as bpkl:
                pkl.dump(best, bpkl)
        else:
            with open(bpkpath, 'r') as bpkl:
                best = pkl.load(bpkl)
            order, models = mltb.find_best(models=best, strategy=lambda x: x, key='score_test')
            best = mltb.select_best(best=models)
        print('Best models:')
        pprint(best)

    # -----------------------------------------------------------------------
    # execute Models and save the output raster/vector map
    if args.execute:
        print('\Execute the model to the whole raster map.')
        mltb.execute(X=X, y=y, best=best, output_file=args.ofile,
                     transform=transform, untransform=untransform)

    print('Finished!')
