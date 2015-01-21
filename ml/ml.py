# -*- coding: utf-8 -*-
from __future__ import print_function

# from python standard library
import gc
import os
import time
import tempfile
import random
import pickle as pkl


# to check the amount of free memory available for the analisys
import psutil

# import scientific libraires
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import RFECV
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import cross_val_score, LeaveOneOut

# import greographical libraries
from osgeo import gdal
from osgeo import ogr

gdal.UseExceptions()

# import local libraries
from fs import SSF

NONE = -9999

MODELS = {# UC_26 Support Vector Machine (SVM)
          'SVM': [],
          # UC_27 Classificazione minima distanza: KNeighborsClassifier
          # UC_28 Classificazione massima verosimiglianza: EmpiricalCovariance
          # UC_29 Spectral Angle Mapper (SAM) i.spec.sam (G6)
          # UC_30 Stimatore lineare: LinearRegression
          # UC_32 Attribuzione/modifica delle classi tematiche: SVR
          'SVR': []}


class WriteError(Exception):
    pass


def read_raster(rast_file, nbands=1):
    """Read raster map file check if have the required number of bands"""
    rast = gdal.Open(rast_file)
    if rast is None:
        TypeError('Unable to open %s' % rast_file)

    if rast.RasterCount > nbands:
        TypeError('The file: %s contains only one band' % rast_file)
    return rast


def empty_rast(newrast_file, rast, format=None,
               datatype=gdal.GDT_Int32, nodata=-9999):
    trns = rast.GetGeoTransform()
    driver = (rast.GetDriver() if format is None
              else gdal.GetDriverByName(format))
    # get the new raster instance
    nrast = driver.Create(newrast_file, rast.RasterXSize, rast.RasterYSize,
                          1, datatype)
    nrast.SetGeoTransform(trns)
    band = nrast.GetRasterBand(1)
    band.SetNoDataValue(nodata)
    band.Fill(nodata)
    return nrast


def vect2rast(vect_file, rast_file, asrast, column, format='GTiff',
              datatype=gdal.GDT_Int32, nodata=-9999):
    """Transform a vector file to a raster map"""
    vect = ogr.Open(vect_file)
    rast = empty_rast(rast_file, asrast, format=format,
                      datatype=datatype, nodata=-nodata)
    gdal.RasterizeLayer(rast, [1], vect.GetLayer(), burn_values=[1],
                        options=["ATTRIBUTE=%s" % column, ])
    return rast


def estimate_best_row_buffer(rast, dtype, factor=1):
    """Estimates the best number of rows to use the system.
    Return the number of rows.

    :param rast: an opened gdal raster instance.
    :type rast: gdal raster instance
    :param dtype: raster type of the output raster map
    :type dtyype: dtype
    :param factor: factor that reduce the memory consumption: $memory//factor$
    :type dtyype: numeric
    """
    intfactor = 4   # internal factor => further reduction for safety reasons
    nbands = rast.RasterCount
    rows, cols = rast.RasterYSize, rast.RasterXSize
    ctype = dtype()
    mem = psutil.virtual_memory()
    onerow = cols * ctype.nbytes * nbands
    if onerow * intfactor > mem.free:
        raise MemoryError("Not possible to allocate enough memory")
    brows = mem.free // onerow // intfactor // factor
    return rows if brows > rows else brows


def get_index_pixels(trst, nodata):
    """Return a dictionary with the row as key and a list with the
    pixel values."""
    # FIXME: do it in chunk and not in memory
    indx = (trst.ReadAsArray() != nodata).nonzero()
    # organize all the pixel by row to optimize the extraction
    pixels = {}
    for row, col in zip(*indx):
        lcols = pixels.get(row, list())
        lcols.append(col)
        pixels[row] = lcols
    return pixels


def read_pixels(bands, pixels):
    """Return an array with the training values of each pixel"""
    def read_band(band, pixels):
        """Return an arrays with the value of a band"""
        res = []
        for row in sorted(pixels.keys()):
            buf = band.ReadAsArray(0, row, band.XSize, 1, band.XSize, 1)[0]
            cols = pixels[row]
            for col in cols:
                res.append(buf[col])
        return np.array(res, dtype=buf.dtype)

    return np.array([read_band(b, pixels) for b in bands]).T


def epixels(band, pixels):
    """Extract value from a raster band and return a numpy array"""
    res = []
    for row in sorted(pixels.keys()):
        buf = band.ReadAsArray(0, row, band.XSize, 1, band.XSize, 1)
        for col in pixels[row]:
            res.append(buf[col])
    return np.array(res, dtype=np.uint32).flatten()


def get_cv(y, n_folds=5):
    """Return a cross validation instance. I n_folds <= 0 the Leave One Out
    validation is used."""
    return (StratifiedKFold(y, n_folds=n_folds, shuffle=True)
            if n_folds > 0 else LeaveOneOut(len(y)))


def test_model(model, X, y,
               cv=None, n_folds=5, n_jobs=5, scoring='accuracy', verbose=0,
               fmt=("%03d %s mean: %.3f, max: %.3f, min: %.3f, "
                    "std: %.3f, required: %.1fs")):
    cv = get_cv(y, n_folds) if cv is None else cv

    start = time.time()
    model['mod'] = model['model'](**model.get('kwargs', {}))
    scores = cross_val_score(model['mod'], X, y, cv=cv, n_jobs=n_jobs,
                             scoring=scoring, verbose=verbose)
    scoretime = time.time() - start
    model['scores'] = scores
    model['score_time'] = scoretime
    vals = (model['index'], model['name'], scores.mean(), scores.max(), scores.min(),
            scores.std(), scoretime)
    print(fmt % vals)
    return vals


def find_best(models, strategy='mean'):
    """Return a tuple with the order of the best model and a dictionary with
    the models parameters.

    Return
    -------

    ([(score0, key0), (score1, key1), ...], {key0: Model0, key1: Model1})
    """
    mods = {m.__name__: 0. for m in set(model['model'] for model in models)}
    func = getattr(np, strategy)
    best = {}
    for m in models:
        val = func(m['scores'])
        mkey = m['model'].__name__
        if mods[mkey] < val:
            mods[mkey] = val
            best[mkey] = m
    order = sorted([(v, k) for k, v in mods.items()], reverse=True)
    return order, best


def read_chunks(rast, nchunks, chunkrows):
    """Return a generator with the raster data splitted in chunks"""
    def read_chunk(bands, yoff, xsize, ysize):
        """Return a list of arrays with the bands values"""
        return [band.ReadAsArray(0, yoff, xsize, ysize,
                                 xsize, ysize).flatten()
                for band in bands]
    rxsize, rysize = rast.RasterXSize, rast.RasterYSize
    bands = [rast.GetRasterBand(i) for i in range(1, rast.RasterCount + 1)]
    for chunk in range(nchunks):
        yoff = chunk * chunkrows
        ysize = chunkrows if chunk < (nchunks - 1) else rysize - yoff
        yield np.array(read_chunk(bands, yoff, rxsize, ysize)
                       ).T.astype(np.float)


def write_chunk(band, data, yoff, xsize, ysize):
    """Write data chunk to a raster map."""
    import ipdb; ipdb.set_trace()
    if band.WriteRaster(0,   yoff, xsize, ysize,
                        data.reshape((ysize, xsize)).tostring(),
                        xsize, ysize):
        raise WriteError("Not able to write the chunk!")
    band.FlushCache()


#def write_chunk(band, chunk, nchunks, chunkrows, data):
#    """Write data chunk to a raster map."""
#    import ipdb; ipdb.set_trace()
#    #                   xoff yoff               xsize       ysize
#    if band.WriteRaster(0,   chunk * chunkrows, band.XSize, chunkrows,
#                        data.reshape((chunkrows, band.XSize)).tostring(),
#                        band.XSize, chunkrows):
#        msg = "Not able to write the chunk: %d, with shape: %r"
#        raise WriteError(msg % (chunk, (chunkrows, band.XSize)))



def extract_training(raster_file, shape_file, column, csv_file,
                     delimiter=' ', nodata=None, dtype=np.uint32):
    """Extract the training samples given a Raster map and a shape with the
    categories. Return two numpy array with the training data and categories

    :param raster_file: multi band raster file name/path
    :type raster_file: path
    :param shape_file: shape file name/path containing the training areas
        and classes
    :type shape_file: path
    :param column: the column name with the classes/values
    :type model: str
    :param csv_file: csv file name/path
    :type csv_file: path
    :param delimiter: the csv delimiter, default is space
    :type csv_file: str
    :param nodata: value of nodata category, default: None
    :type nodata: numeric

    Returns
    -------

    A tuple with two array: X and y
    """
    rast = read_raster(raster_file)
    band = rast.GetRasterBand(1)
    nodata = band.GetNoDataValue() if nodata is None else nodata
    tmp_file = os.path.join(tempfile.gettempdir(),
                            'tmprast%d' % random.randint(1000, 9999))
    trst = vect2rast(shape_file, tmp_file, rast, column, nodata=nodata)
    arr = trst.ReadAsArray()
    if (arr == nodata).all():
        raise TypeError("No training pixels found! all pixels are null!")
    # rows, cols = rast.RasterYSize, rast.RasterXSize
    pixels = get_index_pixels(trst, nodata)
    nbands = rast.RasterCount
    # Add all the band in the input raster map
    bands = [rast.GetRasterBand(i) for i in range(1, nbands + 1)]
    # add the training category
    bands.append(trst.GetRasterBand(1))
    data = read_pixels(bands, pixels)
    header = delimiter.join([str(i) for i in range(1, nbands + 1)] +
                            ['training', ])
    np.savetxt(csv_file, data, header=header, delimiter=delimiter)
    os.remove(tmp_file)
    gc.collect()  # force to free memory of unreferenced objects
    return data[:, :-1], data[:, -1]  # X, y


def run_model(model, data):
    """Execute the model and return the predicted data"""
    start = time.time()
    model['predict'] = model['mod'].predict(data)
    model['execution_time'] += time.time() - start
    return model['predict']


def apply_models(input_file, output_file, models, X, y, transformations):
    """Apply a machine learning model using the sklearn interface to a raster
    data.

    :param input_file: raster file name/path that will be use as input
    :type input_file: path
    :param output_file: raster file name/path that will be the output
    :type output_file: path
    :param models: is a list of dictionaries containing the attributes:
        - model: with the model class definition
        - kwargs: with the parameters that will be used to instantiate the ML
        model
    :type models: dict
    :param X: training data, each column correspond to a raster band each
        row to a pixel.
    :type X: numpy arrax (2D)
    :param y: training classes/values, each row correspond to a pixel.
    :type y: numpy arrax (1D)
    """
    if not isinstance(models, list):
        raise TypeError("models parameter must be a list.")
    rast = read_raster(input_file)
    rxsize, rysize = rast.RasterXSize, rast.RasterYSize
    brows = estimate_best_row_buffer(rast, np.float32, 1)  # len(models))

    # instantiate and train the model and create the empty raster map
    for model in models:
        model['mod'] = model['model'](**model.get('kwargs', {}))
        start = time.time()
        model['mod'].fit(X, y)
        model['training_time'] = time.time() - start
        print("trained: %s [%.2fs]" % (model['name'], model['training_time']))
        model['out'] = empty_rast(output_file % model['name'], rast)
        model['band'] = model['out'].GetRasterBand(1)
        model['execution_time'] = 0.

    # compute the number of chunks
    nchunks = rysize // brows + 1
    print('number of chunks: %d' % nchunks)
    # TODO: fix read_chunks to read and use only the selected features and not
    # all bands
    for chunk, data in enumerate(read_chunks(rast, nchunks, brows)):
        # trasform input data following the users options
        for trans in transformations:
            data = trans.transform(data)

        # run the model to the data
        for model in models:
            yoff = chunk * brows
            ysize = brows if chunk < (nchunks - 1) else rysize - yoff
            # write_chunk(band, data, yoff, rxsize, ysize)
            write_chunk(model['band'],
                        run_model(model, data).astype(dtype=np.uint32),
                        yoff, rxsize, ysize)
            gc.collect()  # force to free memory of unreferenced objects


if __name__ == "__main__":
    import sys
    import argparse
    from datetime import datetime
    from pprint import pprint

    from argparse_checker import importable, indexstr, pca_components

    # Define the parser options
    parser = argparse.ArgumentParser(description='Test several machine-'
                                                 'learning models.')
    parser.add_argument('raster', type=str, metavar='RASTER',
                        help='Multi/Hyper spectral raster file supported by GDAL')
    parser.add_argument('vector', type=str, metavar='VECTOR',
                        help='Training vector format supported by OGR')
    parser.add_argument('column', type=str, metavar='COLUMN',
                        help='Column name with the values/classes'
                             ' used as training')
    parser.add_argument('-t', '--csv-training', type=str, dest='csvtraining',
                        default='training.csv',
                        help='Name of the CSV file with the training values'
                             ' extracted by the raster and vector map.')
    parser.add_argument('-r', '--csv-results', type=str, dest='csvresults',
                        default='results.csv',
                        help='Name of the CSV file with the models results.')
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
    parser.add_argument('-w', '--output-raster-name', type=str,
                        dest='rname', default='%s',
                        help='Specify the name of the output raster map that'
                             ' will be written.')
    parser.add_argument('-e', '--execute', action='store_true',
                        dest='execute', default=False,
                        help='Apply the models to the input data and '
                             'write the output raster maps.')
    parser.add_argument('--o', '--overwrite', action='store_true',
                        dest='overwrite', default=False,
                        help='overwrite')
    parser.add_argument('-b', '--best', type=int,
                        dest='best', default=1,
                        help='Number of best model to apply on the raster.')
    parser.add_argument('-bs', '--best-strategy', default='min',
                        dest='best_strategy', choices=['min', 'mean', 'median'],
                        help='Strategy to use to select the best classifier.')
    parser.add_argument('-bp', '--best-pickle',
                        default='best_model.pickle',
                        dest='best_pickle', type=str,
                        help='All the best models are saved and serialized '
                             'using python pickle.')
    parser.add_argument('-f', '--n-folds', type=int, dest='n_folds',
                        default=5, help='Number of folds that we want to use'
                                        ' to cross validate the dataset.')
    parser.add_argument('-j', '--n-jobs', type=int, dest='n_jobs',
                        default=1, help='Number of jobs that we want to use'
                                        ' during the cross validations.')
    parser.add_argument('-s', '--scale', type=bool, nargs=2, dest='scale',
                        metavar='S', help='StandardScaler options: '
                                          'with_mean, with_std')
    parser.add_argument('-p', '--pca', type=pca_components, dest='pca',
                        metavar='n_components', default=NONE, nargs='?',
                        help='See PCA n_componets documentation')
    parser.add_argument('-u', '--feature-selection', default='RFECV',
                        dest='fs', help='Feature selection',
                        choices=['SSF', 'RFECV', 'LinearSVC',
                                 'ExtraTreesClassifier'], )
    parser.add_argument('-y', '--SSF-strategy', default='min',
                        dest='SSF_strategy', choices=['min', 'mean', 'median'],
                        help='Sequential Forward Floating Feature Selection'
                             ' (SSF) strategy to select the best.')
    parser.add_argument('-l', '--labels', type=pca_components, dest='labels',
                        metavar='LABEL', default=None, nargs='+',
                        help='Label tag')
    parser.add_argument('-v', '--verbosity', type=int, choices=(0, 1, 2),
                        default=0, dest='verbosity', help='Output verbosity.')
    args = parser.parse_args()

    if args.odir and not os.path.isdir(args.odir):
        os.mkdir(args.odir)

    with open(os.path.join(args.odir, 'history.txt'), 'a') as cmd:
        cmd.write('# %s\n' % str(datetime.now()))
        cmd.write(' '.join(sys.argv) + '\n')

    # -----------------------------------------------------------------------
    # Extract training samples
    trnpath = os.path.join(args.odir, args.csvtraining)
    if (not os.path.exists(trnpath) or args.overwrite):
        X, y = extract_training(args.raster, args.vector, args.column,
                                trnpath, delimiter=';',
                                nodata=0, dtype=np.uint32)
    else:
        dt = np.loadtxt(trnpath, delimiter=';', skiprows=1)
        X, y = dt[:, :-1], dt[:, -1]
    cv = get_cv(y, n_folds=args.n_folds)
    X = X.astype(float)

    fselect = {
               # Sequential Forward Floating Feature Selection
               # with Jeffries-Matusita Distance
               'SSF': SSF(strategy=getattr(np, args.SSF_strategy)),
               # Recursive Feature Elimination and Cross-Validated (RFECV)
               'RFECV': RFECV(estimator=SVC(), cv=cv),
               # Linear Support Vector Classification
               'LinearSVC': LinearSVC(C=0.01, penalty="l1", dual=False),
               # Tree-based feature selection
               'ExtraTreesClassifier': ExtraTreesClassifier(n_estimators=250,
                                                            random_state=0)
               }

    # -----------------------------------------------------------------------
    # Transform the input data
    TRANSFORM = []
    if args.scale:
        wm, ws = args.scale
        scaler = StandardScaler(with_mean=wm, with_std=ws)
        print('Scale using:', scaler)
        X = scaler.fit_transform(X, y)
        TRANSFORM.append(scaler)

    # -----------------------------------------------------------------------
    # Feature selection
    if args.fs:
        print('Feature selection:', fselect[args.fs])
        fselect[args.fs].fit(X, y)
        X = fselect[args.fs].transform(X)
        TRANSFORM.append(fselect[args.fs])

    # -----------------------------------------------------------------------
    # Decompose
    if args.pca != NONE:
        pca = PCA(n_components=args.pca)
        print('Decompose using:', pca)
        X = pca.fit_transform(X, y)
        TRANSFORM.append(pca)

    # -----------------------------------------------------------------------
    # Get Models
    models = getattr(args.models, args.listname)
    # write indexes
    for index, mod in enumerate(models):
        mod['index'] = index

    # filter models by index
    if args.imod:
        models = [models[i] for i in args.imod]

    # -----------------------------------------------------------------------
    # test Models
    respath = os.path.join(args.odir, args.csvresults)
    bpkpath = os.path.join(args.odir, args.best_pickle)
    if (not os.path.exists(respath) or args.overwrite):
        sep = ';'
        res = np.array([test_model(mod, X, y, cv, n_jobs=args.n_jobs,
                                   scoring=args.scoring) for mod in models])
        np.savetxt(respath, res, delimiter=sep, fmt='%s',
                   header=sep.join(['id', 'name', 'mean', 'max', 'min',
                                    'std', 'time']))
        order, best = find_best(models, strategy=args.best_strategy)
        with open(bpkpath, 'w') as bpkl:
            pkl.dump(best, bpkl)
    else:
        with open(bpkpath, 'r') as bpkl:
            best = pkl.load(bpkl)
        best = [best[k] for k in best]
        order, best = find_best(best, strategy=args.best_strategy)

    # -----------------------------------------------------------------------
    # execute Models and save the output raster map
    if args.execute:
        n = int(args.best)
        best_mods = [k[1] for k in (order[:n]
                     if n > 0 or n < len(order) else order)]
        import ipdb; ipdb.set_trace()
        apply_models(args.raster, args.rname, [best[b] for b in best_mods],
                     X, y, TRANSFORM)



