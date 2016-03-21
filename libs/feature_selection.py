# -*- coding: utf-8 -*-
"""
Sequential forward floating feature selection with Jeffries-Matusita Distance

Reference: Pudil, P.; Novovicová, J. & Kittler, J.
           Floating search methods in feature selection Pattern recognition letters,
           Elsevier, 1994, 15, 1119-1125

Authors: Michele Dalponte & Hans Ole Ørka & Pietro Zambelli

Date: October 2014
"""
from __future__ import print_function
from itertools import combinations
from math import log, exp, sqrt
import numpy as np
from numpy.linalg import inv, det
from stem_utils_server import STEMLoggingServer

VERBOSE = True


def read(finput, delimiter=None, skip_header=1):
    """Read a file of input and return classes and data"""
    sdata = np.genfromtxt(finput, dtype=str, delimiter=delimiter,
                          skip_header=skip_header)
    return sdata.T[-1].astype(float).astype(int), sdata[:, :-1].astype(float)


def fgroup(classes, data, func, labels=None):
    labels = labels if labels else sorted(set(classes))
    res = {}
    for label in labels:
        res[label] = func(data[classes == label])
    return res


def mean(data):
    return np.mean(data, axis=0)


def cov(data):
    return np.cov(data.T)


def v2m(arr, id0, id1):
    """Extract values from a covariance matrix.

    >>> arr = np.arange(1, 10).reshape((3, 3))
    >>> arr
    array([[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]])

    >>> v2m(arr, (0, 1), (0, 1))
    array([[1, 2],
           [4, 5]])

    >>> v2m(arr, (0, 2), (0, 2))
    array([[1, 3],
           [7, 9]])

    """
    x, y = np.array([(i0, i1) for i0 in id0 for i1 in id1]).T
    return arr[x, y].reshape((len(id0), len(id1)))


def communicate(msg, verbose=False, logging=None):
    if verbose:
        print(msg)
    if logging:
        logging.info(msg)


def info(numb_of_features, dist, fs, verbose=False, logging=None):
    communicate("SSF(%d) Feature to select: %d" % (numb_of_features, numb_of_features),
                verbose, logging)
    communicate("SSF(%d) Maximum minimum distance: %.4f" % (numb_of_features, dist),
                verbose, logging)
    communicate("SSF(%d) Features selected: %r" % (numb_of_features, fs),
                verbose, logging)
    communicate("", verbose, logging)


def bhat1(f_id, mua, cva, mub, cvb):
    mu_a, cv_a = mua[f_id], cva[f_id, f_id]
    mu_b, cv_b = mub[f_id], cvb[f_id, f_id]
    mu_diff = mu_a - mu_b
    cv_sum = cv_a + cv_b
    return (1. / 8. * mu_diff * 1./(cv_sum * 0.5) * mu_diff +
            0.5 * log((cv_sum * 0.5)/sqrt(cv_a * cv_b)))


def bhatN(f_id, mua, cva, mub, cvb):
    mu_a, cv_a = mua[f_id], v2m(cva, f_id, f_id)
    mu_b, cv_b = mub[f_id], v2m(cvb, f_id, f_id)
    mu_diff = mu_a - mu_b
    cv_sum = cv_a + cv_b
    return (np.dot(np.dot(mu_diff, inv(cv_sum * 0.5)), mu_diff)/8. +
            0.5 * np.log(det(cv_sum * 0.5) / np.sqrt(det(cv_a) * det(cv_b))))


def jm(f_id, mu, cv, strategy, comb=None, bhat=bhatN):
    comb = comb if comb else combinations(sorted(mu.keys()), 2)
    return strategy([sqrt(2.*(1-exp(-bhat(f_id, mu[a], cv[a], mu[b], cv[b]))))
                     for a, b in comb])


def backword(fs, mu, cv, strategy, comb=None):
    comb = comb if comb else combinations(sorted(mu.keys()), 2)
    change = list(combinations(fs, len(fs) - 1))[::-1]
    distance = np.array([jm(np.array(f_id), mu, cv, strategy, comb, bhatN)
                         for f_id in change])
    idistmax = distance.argmax()
    return -1 if (idistmax == len(fs) - 1) else idistmax


def seq_forward_floating_fs(data, classes, strategy=np.mean, precision=6,
                            n_features=None, logging=None, verbose=False):
    """Sequential Forward Floating Feature Selection with
    Jeffries-Matusita Distance.
    """
    #labels = sorted(set(classes))
    message = None
    nrows, ncols = data.shape
    mu = fgroup(classes, data, mean)
    cv = fgroup(classes, data, cov)
    ##########################################################################
    # STRART
    ##########################################################################
    # computing JM for single features
    classes_comb = list(combinations(sorted(mu.keys()), 2))
    if verbose:
        print('Compute single features distances')
    dist = np.array([jm(f_id, mu, cv, strategy, classes_comb, bhat1)
                     for f_id in range(ncols)])
    idistmax = dist.argmax()
    res = {1: dict(features=idistmax, distance=dist[idistmax])}
    info(1, dist[idistmax], [idistmax, ], verbose, logging)

    # computing JM for two features
    features_comb = np.array(list(combinations(range(ncols), 2)))

    if verbose:
        print('Compute couple features distances')
    dist = np.array([jm(f_id, mu, cv, strategy, classes_comb, bhatN)
                     for f_id in features_comb])

    idistmax = dist.argmax()
    fs = features_comb[idistmax]
    res[2] = dict(features=fs, distance=dist[idistmax])

    info(2, dist[idistmax], fs, verbose, logging)

    # computing JM for N features
    i = 3
    nfeat = ncols - i if n_features is None else n_features + 1
    check = round(sqrt(2), precision)
    while (i < nfeat):
        fslist = list(fs)
        features_comb = np.array([fslist + [j, ]
                                  for j in range(ncols) if j not in fs])
        try:
            dist = np.array([jm(f_id, mu, cv, strategy, classes_comb, bhatN)
                             for f_id in features_comb])
        except:
            raise RuntimeError("WARNING: Distace is NaN, this could happen"
                               " when the number of training for a class is"
                               "  too low and the covariance matrix is not "
                               "invertible or in some bands there are two "
                               "equal values")

        if np.isnan(dist.max()):
            message = "Attenzione, distanza NaN. la matrice di covarianza non e` invertibile: i campioni di training potrebbero" + \
                    " essere troppo pochi, oppure ci potrebbero essere bande tutte con valori uguali. "
            communicate(("WARNING: Distace is NaN, this could happen when"
                         " the number of training for a class is too low"
                         " and the covariance matrix is not invertible."),
                        verbose=verbose, logging=logging)
            info(i, np.nan, fs, verbose, logging)
            return res, message

        idistmax = dist.argmax()
        fs = features_comb[idistmax]
        info(i, dist[idistmax], fs, verbose, logging)
        bw = backword(fs, mu, cv, strategy, classes_comb)
        if bw != -1:
            fs = np.array([f for e, f in enumerate(fs) if e != bw])
            res[i-1] = dict(features=fs,
                            distance=jm(fs, mu, cv, strategy, classes_comb))
        else:
            i += 1
            res[i] = dict(features=fs, distance=dist[idistmax])

        if check == round(dist[idistmax], precision):
            message = "La distanza ha raggiunto il punto di saturazione."
            return res, message
    return res, message


class SSF(object):
    """Sequential Forward Floating Feature Selection with
    Jeffries-Matusita Distance.
    """
    def __init__(self, strategy=np.mean, precision=6, n_features=None,
                 logfile=None):
        self.strategy = strategy
        self.precision = precision
        self.n_features_ = n_features
        self.support_ = None
        self.ranking_ = None
        self.logfile = logfile

    def setup_logfile(self):
        self.logfile = STEMLoggingServer(self.logfile)

    def __repr__(self):
        return "SSF(strategy=%r, precision=%r)" % (self.strategy,
                                                   self.precision)

    def fit(self, X, y, verbose=False):
        """Fit the RFE model and automatically tune the number of
        selected features."""
        self.setup_logfile()
        try:
            res, message = seq_forward_floating_fs(X, y, strategy=self.strategy,
                                          n_features=self.n_features_,
                                          logging=self.logfile,
                                          verbose=verbose)
            self.message = message
        except Exception as exc:
            if self.logfile:
                msg = 'seq_forward_floating_fs raise {}'
                self.logfile.warning(msg.format(repr(exc)))
            raise RuntimeError("Problem with the execution of the "
                               "Sequential Forward Floating Feature"
                               " Selection: Distace is NaN, this could happen "
                               "when the number of training for a class is too"
                               " low and the covariance matrix is not invertible")
        self.n_features_ = max(res.keys())
        self.selected = res[self.n_features_]['features'] - 1
        #rank = np.empty((self.n_features_, ))
        #import ipdb; ipdb.set_trace()
        #for order, i in enumerate(selected['features']):
        #    rank[i] = order
        #self.ranking_ =
        self.support_ = np.array([True if i in self.selected else False
                                  for i in range(X.shape[1])])
        
    def transform(self, X):
        """Reduce X to the selected features."""
        return X[:, self.support_]

    def fit_transform(self, X, y):
        """Fit to data, then transform it."""
        self.fit(X, y)
        return self.transform(X)

    def get_params(self):
        """Get parameters for this estimator."""
        return dict(strategy=self.strategy, precision=self.precision)

    def get_support(self):
        return self.support_

    def inverse_transform(self):
        """Reverse the transformation operation"""
        pass

    def set_params(self, **params):
        """Set the parameters of this estimator"""
        self.strategy = params.get('strategy', self.strategy)
        self.precision = params.get('precision', self.precision)


#fit(X, y)
#fit_transform(X[, y])	Fit to data, then transform it.
#get_params([deep])	Get parameters for this estimator.
#get_support([indices])	Get a mask, or integer index, of the features selected
#inverse_transform(X)	Reverse the transformation operation
#predict(X)	Reduce X to the selected features and then predict using the underlying estimator.
#predict_proba(X)
#score(X, y)	Reduce X to the selected features and then return the score of the underlying estimator.
#set_params(**params)	Set the parameters of this estimator.
#transform(X)	Reduce X to the selected features.

if __name__ == "__main__":
    import argparse

    # Define the parser options
    parser = argparse.ArgumentParser(description='Sequential Forward Floating'
                                                 'Feature Selection with '
                                                 'Jeffries-Matusita Distance')
    parser.add_argument('data', type=argparse.FileType('r'),
                        help='CSV file with features data')
    parser.add_argument('-m', '--method', choices=['mean', 'min', 'median'],
                        default='mean', dest='method',
                        help='Feature selection method')
    parser.add_argument('-d', '--delimiter', type=str, default=' ',
                        dest='delimiter', help='CSV delimiter')
    parser.add_argument('-n', '--n-features', type=int, default=None,
                        dest='n_features',
                        help='Number of features to be selected')
    parser.add_argument('-s', '--skip-header', type=int, default=1,
                        dest='skip_header', help='Skip header rows')
    parser.add_argument('-l', type=str, dest='log',
                        help='Log file with features data selection log')
    parser.add_argument('-v', '--verbose', action='store_true',
                        dest='verbose', default=False,
                        help='Verbose, print or log the process steps')
    args = parser.parse_args()

    #import ipdb; ipdb.set_trace()
    classes, data = read(args.data, args.delimiter, args.skip_header)
    if args.log:
        import logging

        logging.basicConfig(filename=args.log, filemode='w',
                            level=logging.DEBUG)
    else:
        logging = None
    seq_forward_floating_fs(data, classes, strategy=getattr(np, args.method),
                            n_features=args.n_features,
                            verbose=args.verbose, logging=logging)
