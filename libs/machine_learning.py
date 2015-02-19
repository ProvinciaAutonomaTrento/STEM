# -*- coding: utf-8 -*-
from __future__ import print_function

# from python standard library
import gc
import os
import time
import tempfile
import random
import itertools
from collections import namedtuple


# to check the amount of free memory available for the analisys
import psutil

# import scientific libraires
import numpy as np

from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import cross_val_score, LeaveOneOut

try:
    from sklearn.cross_validation import check_scoring
except ImportError:
    from scorer import check_scoring

# import greographical libraries
from osgeo import gdal
from osgeo import ogr

gdal.UseExceptions()

SEP = ';'
NODATA = -9999


CVResult = namedtuple('CVResult',
                      ['index', 'name', 'mean', 'max', 'min', 'std', 'time'])
TestResult = namedtuple('TestResult', ['index', 'name', 'score', ])


class WriteError(Exception):
    pass


def cvbar(total, fill='#', empty='-', barsize=30,
          fmt=("{index:03d}/{total:03d} {mean:.3f} {max:.3f} {min:.3f} "
               "{std:.3f}, {time:.1f}s"),
          _best=[CVResult(0, '', 0, 0, 0, 0, 0), ]):
    total -= 1
    ftotal = 1. if total == 0 else float(total)

    def printinfo(i, cross):
        rest = i / ftotal
        ifill = int(rest * barsize)
        bar = '[%s%s] %3d%%"' % (fill * ifill,
                                 empty * (barsize - ifill),
                                 int(rest * 100.))
        best = _best[0]
        if best.mean < cross.mean:
            _best[0] = cross
            best = cross
        bst = '%s is the best so far (%03d): %.4f' % (best.name, best.index,
                                                      best.mean)
        info = fmt.format(total=total, **cross.__dict__)
        print('\r\x1b[3A\n{bar}\n{best}\n{info}'.format(bar=bar, best=bst,
                                                        info=info), end='')
    return printinfo


def split_in_chunk(iterable, lenght=10000):
    """Split a list in chunk.

    >>> for chunk in split_in_chunk(range(25)): print chunk
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
    (20, 21, 22, 23, 24)
    >>> for chunk in split_in_chunk(range(25), 3): print chunk
    (0, 1, 2)
    (3, 4, 5)
    (6, 7, 8)
    (9, 10, 11)
    (12, 13, 14)
    (15, 16, 17)
    (18, 19, 20)
    (21, 22, 23)
    (24,)
    """
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, lenght))
        if not chunk:
            return
        yield chunk


def read_raster(rast_file, nbands=1):
    """Read raster map file check if have the required number of bands"""
    rast = gdal.Open(rast_file)
    if rast is None:
        TypeError('Unable to open %s' % rast_file)

    if rast.RasterCount > nbands:
        TypeError('The file: %s contains only one band' % rast_file)
    return rast


def empty_rast(newrast_file, rast, format=None,
               datatype=gdal.GDT_Int32, nodata=NODATA):
    trns = rast.GetGeoTransform()
    driver = (rast.GetDriver() if format is None
              else gdal.GetDriverByName(format))
    # get the new raster instance
    nrast = driver.Create(newrast_file, rast.RasterXSize, rast.RasterYSize,
                          1, datatype)
    nrast.SetGeoTransform(trns)
    band = nrast.GetRasterBand(1)
    #import ipdb; ipdb.set_trace()
    band.SetNoDataValue(float(nodata))
    band.Fill(nodata)
    return nrast


def vect2rast(vector_file, rast_file, asrast, column, format='GTiff',
              datatype=gdal.GDT_Int32, nodata=NODATA):
    """Transform a vector file to a raster map"""
    vect = ogr.Open(vector_file)
    rast = empty_rast(rast_file, asrast, format=format,
                      datatype=datatype, nodata=nodata)
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


def cross_val_model(model, X, y,
                    cv=None, n_folds=5, n_jobs=5,
                    scoring=None, score_func=None,
                    verbose=0, ):
    cv = get_cv(y, n_folds) if cv is None else cv

    start = time.time()
    model['mod'] = model['model'](**model.get('kwargs', {}))
    scores = cross_val_score(model['mod'], X, y, cv=cv, n_jobs=n_jobs,
                             scoring=scoring, verbose=verbose)
    scoretime = time.time() - start
    model['scores'] = scores
    model['score_time'] = scoretime
    vals = CVResult(model.get('index', 1), model['name'], scores.mean(),
                    scores.max(), scores.min(), scores.std(), scoretime)
    return vals


def test_model(model, Xtraining, ytraining, Xtest, ytest,
               scoring=None, score_func=None):
    model['mod'] = model['model'](**model.get('kwargs', {}))
    model['mod'].fit(Xtraining, ytraining)
    scorer = check_scoring(model['mod'], score_func=score_func, scoring=scoring)
    model['score_test'] = scorer(model['mod'], Xtest, ytest)
    return TestResult(model.get('index', 1), model['name'], model['score_test'])


def find_best(models, strategy=np.mean, key='scores'):
    """Return a tuple with the order of the best model and a dictionary with
    the models parameters.

    Return
    -------

    ([(score0, key0), (score1, key1), ...], {key0: Model0, key1: Model1})
    """
    mods = {m.__name__: 0. for m in set(model['model'] for model in models)}
    best = {}
    for m in models:
        val = strategy(m[key])
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


def columns2indexes(fields, columns):
    """Return an array with column indexes

    >>> class Field()
    ...     def __init__(self, name):
    ...         self.name = name
    ...
    >>> fields = [Field(name) for name in ['cat', 'c1', 'c2', 'c3', 'tr']]
    >>> column_indexes(fields, ['cat', ])
    array([0, ])
    >>> column_indexes(fields, ['c1', 'c2', 'c3' ])
    array([1, 2, 3])
    """
    return np.array([i for i in range(len(fields))
                     if fields[i].name in columns])


def extract_vector_fields(layer, icols):
    """Return an array from a vector layer with the data corresponding to
    the index of the columns given.
    """
    # TODO: can we avoid to cycle over the row and column of the
    # vector properties, avoid to do this in python should make it
    # significantly faster
    layer.ResetReading()
    for f in layer:
        yield [f.GetField(i) for i in icols]


def extract_training(vector_file, column, csv_file, raster_file=None,
                     use_columns=None, delimiter=SEP, nodata=None,
                     dtype=np.uint32):
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
    :param delimiter: the csv delimiter, default is ;
    :type csv_file: str
    :param nodata: value of nodata category, default: None
    :type nodata: numeric

    Returns
    -------

    A tuple with two array: X and y
    """
    if raster_file:
        rast = read_raster(raster_file)
        band = rast.GetRasterBand(1)
        nodata = band.GetNoDataValue() if nodata is None else nodata
        tmp_file = os.path.join(tempfile.gettempdir(),
                                'tmprast%d' % random.randint(1000, 9999))
        # vect_file, rast_file, asrast, column, format='GTiff',
        #              datatype=gdal.GDT_Int32, nodata=-9999
        trst = vect2rast(vector_file=vector_file, rast_file=tmp_file,
                         asrast=rast, column=column, nodata=nodata)
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
        os.remove(tmp_file)
        gc.collect()  # force to free memory of unreferenced objects
    else:
        vect = ogr.Open(vector_file)
        layer = vect.GetLayer()
        fields = layer.schema
        itraining = columns2indexes(fields, column)
        icols = columns2indexes(fields, use_columns)
        training = np.array(extract_vector_fields(layer, (itraining, ))).T[0]
        dt = np.array(extract_vector_fields(layer, icols))
        data = np.concatenate((dt.T, training[None, :]), axis=0).T
        header = delimiter.join([fields[i].name for i in icols] + [column, ])
    np.savetxt(csv_file, data, header=header, delimiter=delimiter)
    return data[:, :-1].astype(float), data[:, -1]  # X, y


def run_model(model, data):
    """Execute the model and return the predicted data"""
    start = time.time()
    model['predict'] = model['mod'].predict(data)
    model['execution_time'] += time.time() - start
    return model['predict']


def apply_models(input_file, output_file, models, X, y, transformations,
                 transform=None, untransform=None, use_columns=None):
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

    if transform is not None:
        y = transform(y)

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

    if use_columns is None:
        # the input file is a raster
        rast = read_raster(input_file)
        rxsize, rysize = rast.RasterXSize, rast.RasterYSize
        brows = estimate_best_row_buffer(rast, np.float32, 1)  # len(models))
        # compute the number of chunks
        nchunks = rysize // brows + (1 if rysize % brows else 0)
        print('number of chunks: %d' % nchunks)
        # TODO: fix read_chunks to read and use only the selected
        # features and not all bands
        for chunk, data in enumerate(read_chunks(rast, nchunks, brows)):
            # trasform input data following the users options
            for trans in transformations:
                data = trans.transform(data)

            # run the model to the data
            for model in models:
                yoff = chunk * brows
                ysize = brows if chunk < (nchunks - 1) else rysize - yoff
                # predict
                predict = run_model(model, data).astype(dtype=np.uint32)
                if untransform is not None:
                    predict = untransform(predict)
                # write_chunk(band, data, yoff, rxsize, ysize)
                write_chunk(model['band'], predict, yoff, rxsize, ysize)
                gc.collect()  # force to free memory of unreferenced objects
    else:
        # input is a vector
        ivect = ogr.Open(input_file)
        ilayer = ivect.GetLayer()
        ifields = ilayer.schema
        icols = columns2indexes(ifields, use_columns)

        # Create the output Layer
        odriver = ogr.GetDriverByName("ESRI Shapefile")
        # Remove output shapefile if it already exists
        if os.path.exists(output_file):
            odriver.DeleteDataSource(output_file)
        # Create the output shapefile
        osrc = odriver.CreateDataSource(output_file)
        olayer = osrc.CreateLayer("states_centroids", geom_type=ogr.wkbPoint)

        # Add a new field for each model to the output layer
        ofieldtype = ogr.OFTInteger if y.dtype == np.int else ogr.OFTReal
        for model in models:
            olayer.CreateField(ogr.FieldDefn(model['name'], ofieldtype))

        # read the vector input data and features splitted in chunksS
        dchunk = split_in_chunk(extract_vector_fields(ilayer, icols))
        fchunk = split_in_chunk(ilayer)

        for features, data in zip(fchunk, dchunk):
            # transform the data consistently before to apply the model
            for trans in transformations:
                data = trans.transform(data)

            for model in models:
                # apply the model to the data chunk
                predict = run_model(model, data).astype(dtype=np.uint32)
                # if the data were transformed, then traform them back
                # to original values
                if untransform is not None:
                    predict = untransform(predict)

                col = model['name']
                for ofeature, value in zip(features, predict):
                    # update feature field
                    ofeature.SetField(col, value)
            # save feature to the new vector map
            for ofeature in features:
                olayer.CreateFeature(ofeature)

        # Close DataSources
        osrc.Destroy()



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
                   use_columns=None,
                   output_file='{0}', models=None, training_csv=None,
                   scoring=None, score_func=None, nodata=NODATA,
                   n_folds=5, n_jobs=1, n_best=1, best_strategy=np.mean,
                   tvector=None, tcolumn=None, traster=None, test_csv=None,
                   scaler=None, fselector=None, decomposer=None,
                   transform=None, untransform=None):
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
        scoring : str
            Scoring function name to use during the cross-validation and test.
            valid string are:
            ``accuracy``, ``f1``, ``precision``, ``recall``, ``roc_auc``,
            ``adjusted_rand_score``, ``mean_absolute_error``,
            ``mean_squared_error``, ``r2``
        score_func : function
            Scoring function to use during the cross-validation and test.
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
        decomposer : Instance with fit and transform methods
            Instance for the decomposition of the data-set before apply the
            model.
        transform : Set a function to transform the target before apply
            the model.
        untrasform : Set a function to remove the transformation before write
            the model result.
        """
        self.X = None
        self.y = None
        self.raster = raster_file
        self.vector = vector_file
        self.output = output_file
        self.column = column
        self.use_columns = use_columns
        self.training_csv = training_csv
        self.models = models
        self.scoring = scoring
        self.score_func = score_func
        self.nodata = nodata
        self.n_folds = n_folds
        self.n_jobs = n_jobs
        self.n_best = n_best
        self.best_strategy = best_strategy
        self.tvector = tvector,
        self.tcolumn = tcolumn,
        self.traster = traster,
        self.test_csv = test_csv,
        self.scaler = scaler
        self.fselector = fselector
        self.decomposer = decomposer
        self.transform = transform
        self.untransform = untransform

    def get_params(self):
        keys = ('raster_file', 'vector_file', 'output_file', 'column',
                'training_csv', 'models', 'scoring', 'score_func', 'nodata',
                'n_folds', 'n_jobs', 'n_best', 'tvector', 'tcolumn', 'traster',
                'test_csv', 'scaler', 'fselector', 'decomposer',
                'transform', 'untransform')
        return {key: getattr(self, key) for key in keys}

    def extract_training(self, vector_file=None, column=None, use_columns=None,
                         csv_file=None, raster_file=None, delimiter=SEP,
                         nodata=None, dtype=np.uint32):
        """Return the data and classes array for the training, and save them on
        self.X and self.y, see: ``extract_training`` function for more detail
        on the parameters.

        Parameters
        ----------

        raster_file: path
            Raster file name/path used to extract the training values.
        vector_file: path
            Vector file name/path used to assign a valeu/class for the rainign.
        column: str
            Column name containing the values/classes.
        csv_file: path,
            CSV file name containing the data and the training values.
        delimiter: str, default=SEP
            Delimiter that will be used when savint to CSV.
        nodata: numeric
            Value to use for nodata
        dtype: numpy dtype
            Type of the raster map
        """
        self.raster = self.raster if raster_file is None else raster_file
        self.vector = self.vector if vector_file is None else vector_file
        self.column = self.column if column is None else column
        self.use_columns = (self.use_columns if use_columns is None
                            else use_columns)
        self.training_csv = self.training_csv if csv_file is None else csv_file
        self.nodata = nodata
        self.X, self.y = extract_training(vector_file=self.vector,
                                          column=self.column,
                                          use_columns=self.use_columns,
                                          csv_file=self.training_csv,
                                          raster_file=self.raster,
                                          delimiter=delimiter, nodata=nodata,
                                          dtype=dtype)
        return self.X, self.y

    def extract_test(self, vector_file=None, column=None, use_columns=None,
                     csv_file=None, raster_file=None, delimiter=SEP,
                     nodata=None, dtype=np.uint32):
        self.traster = ((self.traster if self.traster is None else self.raster)
                        if raster_file is None else raster_file)
        self.tvector = self.tvector if vector_file is None else vector_file
        self.tcolumn = self.tcolumn if column is None else column
        self.use_columns = (self.use_columns if use_columns is None
                            else use_columns)
        self.test_csv = self.test_csv if csv_file is None else csv_file
        self.nodata = nodata
        self.Xtest, self.ytest = extract_training(vector_file=self.vector,
                                                  column=self.column,
                                                  use_columns=self.use_columns,
                                                  csv_file=self.test_csv,
                                                  raster_file=self.raster,
                                                  delimiter=delimiter,
                                                  nodata=nodata,
                                                  dtype=dtype)
        return self.Xtest, self.ytest

    def data_transform(self, X=None, y=None, scaler=None, fselector=None,
                       decomposer=None, trans=None, fscolumns=None,
                       fsfile=None):
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
        X = self.X if X is None else X
        y = self.y if y is None else y
        Xt = X
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
        else:
            self._trans = trans

        for trans in self._trans:
            trans.fit(Xt, y)
            Xt = trans.transform(Xt)
            if fsfile is not None:
                try:
                    np.savetxt(fsfile, trans.support_)
                except AttributeError:
                    pass
        return Xt

    def cross_validation(self, models=None, X=None, y=None,
                         scoring=None, score_func=None,
                         n_folds=None, n_jobs=None, cv=None,
                         transform=None, verbose=True,
                         fmt=None):
        """Return a numpy array with the scoring results for each model.

        Parameters
        ----------

        models: list of dictionaries
            List of dictionaries, see classifiers.py and regressors.py file
            for examples.
        X: 2D array
            It is a 2D array with the data.
        y: 1D array
            It is a 1D array with the values/classes used to assess the
            performance of the model.
        scoring : str
            Scoring function name to use during the cross-validation and test.
            valid string are:
            ``accuracy``, ``f1``, ``precision``, ``recall``, ``roc_auc``,
            ``adjusted_rand_score``, ``mean_absolute_error``,
            ``mean_squared_error``, ``r2``
        score_func : function
            Scoring function to use during the cross-validation and test.
        n_folds: int
            Number of folds that will be used during the cross-validation. If
            n_folds < 0 Leave One Out method is used.
        n_jobs: int
            Number of processors used for the cross-validation
        cv:
            Cross-Validation instance.
        """
        y = self.y if y is None else y
        self.transform = transform if transform is not None else self.transform
        y = y if self.transform is None else self.transform(y)
        X = self.data_transform(X=self.X if X is None else X, y=y)
        self.scoring = self.scoring if scoring is None else scoring
        self.score_func = self.score_func if score_func is None else score_func
        self.models = self.models if models is None else models
        self.n_folds = n_folds if n_folds else self.n_folds
        self.n_jobs = n_jobs if n_jobs else self.n_jobs
        self.cv = cv if cv else get_cv(y, n_folds=self.n_folds)
        res = []
        info = (cvbar(len(self.models), fill='#', empty='-', barsize=30)
                if verbose else lambda x, y: '')
        print('\n' * 3)
        for i, mod in enumerate(self.models):
            cross = cross_val_model(mod, X, y, self.cv, n_jobs=self.n_jobs,
                                    scoring=self.scoring)
            res.append(cross)
            info(i, cross)
        return np.array(res)

    def test(self, Xtest, ytest, models=None, X=None, y=None,
             scoring=None, score_func=None, transform=None):
        """Return a list with the score for each model."""
        X = self.X if X is None else X
        y = self.y if y is None else y
        self.transform = transform if transform is not None else self.transform
        y = y if self.transform is None else self.transform(y)
        ytest = ytest if self.transform is None else self.transform(ytest)
        self.scoring = self.scoring if scoring is None else scoring
        self.score_func = self.score_func if score_func is None else score_func
        self.models = self.models if models is None else models
        return [test_model(model, X, y, Xtest, ytest,
                           scoring=self.scoring, score_func=self.score_func)
                for model in self.models]

    def select_best(self, n_best=None, best=None, order=None):
        """Return a dictionary with ``{key: model}``, for only the best
        N models.
        """
        n_best = self.n_best if n_best is None else n_best
        best = self.best if best is None else best
        order = self.order if order is None else order
        best_mods = [k[1] for k in (order[:n_best]
                     if n_best > 0 or n_best < len(order) else order)]
        return [self.best[b] for b in best_mods]

    def find_best(self, models=None, strategy=None, key='scores'):
        """Return a list of tuple ``(score, key)`` and a dictionary
        with ``{key: model}``.
        """
        self.models = self.models if models is None else models
        self.best_strategy = (self.best_strategy if strategy is None
                              else strategy)
        self.order, self.best = find_best(models, strategy=self.best_strategy,
                                          key=key)
        return self.order, self.best

    def execute(self, raster_file=None, output_file=None,
                best=None, X=None, y=None, trans=None,
                transform=None, untransform=None):
        """Apply the best method or the list of model selected to the input
        raster map."""
        self.raster = self.raster if raster_file is None else raster_file
        self.output = self.output if output_file is None else output_file
        best = self.select_best() if best is None else best
        self._trans = self._trans if trans is None else trans
        self.transform = transform if transform is not None else self.transform
        self.untransform = untransform if untransform is not None else self.untransform
        X = self.X if X is None else X
        y = self.y if y is None else y
        apply_models(self.raster, self.output, best, X, y, self._trans,
                     transform=self.transform, untransform=self.untransform)
