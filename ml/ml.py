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


def vect2rast(vector_file, rast_file, asrast, column, format='GTiff',
              datatype=gdal.GDT_Int32, nodata=-9999):
    """Transform a vector file to a raster map"""
    vect = ogr.Open(vector_file)
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


def find_best(models, strategy=np.mean):
    """Return a tuple with the order of the best model and a dictionary with
    the models parameters.

    Return
    -------

    ([(score0, key0), (score1, key1), ...], {key0: Model0, key1: Model1})
    """
    mods = {m.__name__: 0. for m in set(model['model'] for model in models)}
    best = {}
    for m in models:
        val = strategy(m['scores'])
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
    if band.WriteArray(data.reshape((ysize, xsize)), 0,   yoff):
        raise WriteError("Not able to write the chunk!")
    band.FlushCache()


#def write_chunk(band, chunk, nchunks, chunkrows, data):
#    """Write data chunk to a raster map."""
#    #                   xoff yoff               xsize       ysize
#    if band.WriteRaster(0,   chunk * chunkrows, band.XSize, chunkrows,
#                        data.reshape((chunkrows, band.XSize)).tostring(),
#                        band.XSize, chunkrows):
#        msg = "Not able to write the chunk: %d, with shape: %r"
#        raise WriteError(msg % (chunk, (chunkrows, band.XSize)))



def extract_training(raster_file, vector_file, column, csv_file,
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
    # vect_file, rast_file, asrast, column, format='GTiff',
    #              datatype=gdal.GDT_Int32, nodata=-9999
    trst = vect2rast(vector_file=vector_file, rast_file=tmp_file, asrast=rast,
                     column=column, nodata=nodata)
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
    return data[:, :-1].astype(float), data[:, -1]  # X, y


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
        model['out'] = empty_rast(output_file.format(model['name']), rast)
        model['band'] = model['out'].GetRasterBand(1)
        model['execution_time'] = 0.

    # compute the number of chunks
    nchunks = rysize // brows + (1 if rysize % brows else 0)
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


class MLToolBox(object):
    def __init__(self, *args, **kwargs):
        """The MLToolBox class can be instantiate without any argument,
        however if the argument are given then they are set using the
        ``set_params`` method.
        """
        self._trans = []

        # set values
        self.set_params(*args, **kwargs)

    def set_params(self, raster_file=None, vector_file=None, column=None,
                   output_file='{0}', models=None, scoring=None,
                   n_folds=5, n_jobs=1, n_best=1, best_strategy=np.mean,
                   scaler=None, fselector=None, decomposer=None):
        """Method to set class attributes, the attributes are:

        Parameters
        ----------

        raster_file : str, raster input file/path
            Raster file with the pixel bands to be classified.
        vector_file : str, vector input file/path
            Vector input file with the training areas to train the model.
        column: str, column name
            Column name with the data that will be used to train the models.
        output_file : output file/path
            Output file where the model results are stored.
        models : list of dictionaries
            List of dictionaries containing the models that will be tested.
        scoring : str or callable
            Scoring function that we want to use during the cross-validation.
        n_folds : int, default=5
            Number of folds that will be used during the cross-validation.
        n_jobs : int or None, default=1
            Number of processors that will be used during the cross-validation.
        best_strategy: function, default: mean
            Function to select the best model mased on the cross-validated
            scores, models wiht higher values is selected.
        scaler : Instance with fit and transform methods
            Instance that scale the data-set before apply the model.
        fselector : Instance with fit and transform methods
            Instance that select the most relevant features in the data-set
            before apply the model.
        decompoer : Instance with fit and transform methods
            Instance for the decomposition of the data-set before apply the
            model.
        """
        self.raster = raster_file
        self.vector = vector_file
        self.output = '{0}'
        self.column = column
        self.models = models
        self.scoring = scoring
        self.n_folds = n_folds
        self.n_jobs = n_jobs
        self.n_best = n_best
        self.scaler = scaler
        self.fselector = fselector
        self.decomposer = decomposer

    def get_params(self):
        pass

    def extract_training(self, raster_file=None, vector_file=None, column=None,
                         csv_file=None, delimiter=' ', nodata=None,
                         dtype=np.uint32):
        """Return the data and classes array for the training, and save them on
        self.X and self.y, see: ``extract_training`` function for more detail
        on the parameters.

        raster_file, shape_file, column, csv_file,
                     delimiter=' ', nodata=None, dtype=np.uint32
        """
        self.raster = self.raster if raster_file is None else raster_file
        self.vector = self.vector if vector_file is None else vector_file
        self.column = self.column if column is None else column
        self.training_csv = self.training_csv if csv_file is None else csv_file
        self.X, self.y = extract_training(raster_file=self.raster,
                                          vector_file=self.vector,
                                          column=self.column,
                                          csv_file=self.training_csv,
                                          delimiter=delimiter, nodata=nodata,
                                          dtype=dtype)
        return self.X, self.y

    def transform(self, X=None, y=None,
                  scaler=None, fselector=None,  decomposer=None, trans=None,
                  fscolumns=None, fsfile=None):
        """Transform a data-set scaling values, reducing the number of
        features and appling decomposition.

        Parameters
        -----------

        X : array
            Float 2D array with the data to be transformed
        y : array
            Array with the target values or classes
        scaler : instance
            Object with methods: ``fit`` and ``transform``.
        fselector : instance
            Object with methods: ``fit`` and ``transform``.
        decomposer : instance
            Object with methods: ``fit`` and ``transform``.
        trans : list of instances
            List of transformer instances that will be applied in
            sequence.
        fscolumns : boolean array
            Boolean array with the data column that will be selected.
        fsfile : path
            Path where to save the boolean array selected by the feature
            selection process.

        Example
        --------

        >>> mltb = MLToolBox()
        >>> scaler = StandardScaler(with_mean=True, with_std=True)
        >>> # instantiate some feature selector:
        >>> ssf = SSF(strategy=getattr(np, args.SSF_strategy))
        >>> rfecv = RFECV(estimator=SVC(), cv=cv)
        >>> lsvc = LinearSVC(C=0.01, penalty="l1", dual=False)
        >>> etree = ExtraTreesClassifier(n_estimators=250, random_state=0)
        >>> # instantiate some decomposition
        >>> pca = PCA(n_components=10)
        >>> # now transform
        >>> Xtrans = mltb.transform(X, scaler=scaler, fselector=ssf, pca=pca)
        """
        self.X = self.X if X is None else X
        self.y = self.y if y is None else y
        Xt = self.X
        if trans is None:
            self.scaler = scaler if scaler else self.scaler
            if self.scaler is not None:
                self._trans.append(self.scaler)
            self.fselector = fselector if fselector else self.fselector
            if self.fselector is not None:
                if fscolumns is None:
                    self._trans.append(self.fselector)
                else:
                    Xt = Xt[:, fscolumns]
            self.decomposer = decomposer if decomposer else self.decomposer
            if decomposer is not None:
                self._trans.append(self.decomposer)

        for trans in self._trans:
            trans.fit(Xt, self.y)
            Xt = trans.transform(Xt)
            if fsfile is not None:
                try:
                    np.savetxt(fsfile, trans.support_)
                except AttributeError:
                    pass
        #if fselector is not None and fsfile is not None and done is False:
        #    raise
        self.Xt = Xt
        return Xt

    def test(self, models=None, X=None, y=None, scoring=None,
             n_folds=None, n_jobs=None, cv=None):
        """Return a numpy array with the scoring results for each model."""
        X = (self.Xt if self.Xt is not None else self.X) if X is None else X
        self.y = self.y if y is None else y
        self.scoring = self.scoring if scoring is None else scoring
        self.models = self.models if models is None else models
        self.cv = get_cv(self.y, n_folds=self.n_folds)
        res = np.array([test_model(mod, X, self.y, self.cv, n_jobs=self.n_jobs,
                                   scoring=self.scoring)
                        for mod in self.models])
        return res

    def select_best(self, n_best=1, best=None, order=None):
        """Return a dictionary with ``{key: model}``, for only the best
        N models.
        """
        n_best = self.n_best if n_best is None else n_best
        best = self.best if best is None else best
        order = self.order if order is None else order
        best_mods = [k[1] for k in (order[:n_best]
                     if n_best > 0 or n_best < len(order) else order)]
        return [self.best[b] for b in best_mods]

    def find_best(self, models=None, strategy=np.mean):
        """Return a list of tuple ``(score, key)`` and a dictionary
        with ``{key: model}``.
        """
        self.models = self.models if models is None else models
        self.order, self.best = find_best(models, strategy=strategy)
        return self.order, self.best

    def execute(self, raster_file=None, output_file=None,
                best=None, X=None, y=None, trans=None):
        """Apply the best method or the list of model selected to the input
        raster map."""
        self.raster = self.raster if raster_file is None else raster_file
        self.output = self.output if output_file is None else output_file
        best = self.select_best() if best is None else best
        self._trans = self._trans if trans is None else trans
        X = (self.Xt if self.Xt is not None else self.X) if X is None else X
        self.y = self.y if y is None else y
        apply_models(self.raster, self.output, best,
                     X, self.y, self._trans)


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
                        metavar='n_components', default=NONE, nargs='?',
                        help='See PCA n_componets documentation')
    parser.add_argument('-f', '--feature-selection', default='RFECV',
                        dest='fs', help='Feature selection',
                        choices=['SSF', 'RFECV', 'LinearSVC',
                                 'ExtraTreesClassifier'], )
    parser.add_argument('-ff', '--feature-selection', default=None,
                        dest='ff', help='File with the Feature selected.')
    parser.add_argument('-fs', '--SSF-strategy', default='min',
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
    # Get Models
    models = getattr(args.models, args.listname)
    # write indexes
    for index, mod in enumerate(models):
        mod['index'] = index

    # filter models by index
    if args.imod:
        models = [models[i] for i in args.imod]

    # =======================================================================
    # Instantiate the class
    mltb = MLToolBox(raster_file=args.raster, vector_file=args.vector,
                     column=args.column, models=models, scoring=args.scoring,
                     n_folds=args.n_folds, n_jobs=args.n_jobs,
                     n_best=args.n_best,
                     best_strategy=getattr(np, args.best_strategy),
                     scaler=None, fselector=None, decomposer=None)

    # -----------------------------------------------------------------------
    # Extract training samples
    trnpath = os.path.join(args.odir, args.csvtraining)
    if (not os.path.exists(trnpath) or args.overwrite):
        X, y = mltb.extract_training(csv_file=trnpath, delimiter=';',
                                     nodata=0, dtype=np.uint32)
    else:
        dt = np.loadtxt(trnpath, delimiter=';', skiprows=1)
        X, y = dt[:, :-1], dt[:, -1]
    X = X.astype(float)

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
    if args.fs:
        if args.ff:
            fspath = os.path.join(args.odir, args.ff)
            if (os.path.exists(fspath) and not args.overwrite):
                fscolumns = np.loadtxt(fspath)
        fselector = fselect[args.fs]

    # -----------------------------------------------------------------------
    # Decomposer
    decomposer = PCA(n_components=args.pca) if args.pca != NONE else None

    # -----------------------------------------------------------------------
    # Transform the input data
    mltb.transform(X=X, y=y,
                   scaler=scaler, fselector=fselector, decomposer=decomposer,
                   fscolumns=fscolumns, fsfile=args.ff)

    # -----------------------------------------------------------------------
    # test Models
    respath = os.path.join(args.odir, args.csvresults)
    bpkpath = os.path.join(args.odir, args.best_pickle)
    if (not os.path.exists(respath) or args.overwrite):
        res = mltb.test()
        sep=';'
        np.savetxt(respath, res, delimiter=sep, fmt='%s',
                   header=sep.join(['id', 'name', 'mean', 'max', 'min',
                                    'std', 'time']))
        mltb.find_best(models, strategy=args.best_strategy)
        best = mltb.select_best()
        with open(bpkpath, 'w') as bpkl:
            pkl.dump(best, bpkl)
    else:
        with open(bpkpath, 'r') as bpkl:
            best = pkl.load(bpkl)
        #models = [best[k] for k in best]
        order, models = mltb.find_best(models=best)
        best = mltb.select_best(best=models)

    # -----------------------------------------------------------------------
    # execute Models and save the output raster map
    if args.execute:
        mltb.execute(best=best)
