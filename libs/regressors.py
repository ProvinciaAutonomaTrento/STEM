# -*- coding: utf-8 -*-
"""
Authors: Pietro Zambelli

This file contains some lists of scikit-learn regressors.
Similarly to what is described in the classifiers, here are define a list of
dictionaries, each dictionary must have the following keys:

* name: is a string to define the identification name
* model: definition of a class
* kwargs: is a dictionary with the parameters to use for the initialization
          of the classification.

An example could be:

::

    LINEAR = [dict(name='LinearRegression',
                   model=LinearRegression,
                   kwargs={})]

Please look the source code to know more about the regressors available.
"""
import numpy as np

from sklearn.svm import SVR

from sklearn.linear_model import (LinearRegression,
                                  Ridge, Lasso, ElasticNet, MultiTaskLasso,
                                  Lars, LassoLars, BayesianRidge,
                                  ARDRegression, LogisticRegression,
                                  SGDRegressor, PassiveAggressiveRegressor,
                                  RANSACRegressor,
                                  RidgeCV, LassoLarsCV,
                                  OrthogonalMatchingPursuitCV)
from sklearn.neighbors import (KNeighborsRegressor, RadiusNeighborsRegressor)
from sklearn.gaussian_process import GaussianProcess
from sklearn.ensemble import (ExtraTreesRegressor, AdaBoostRegressor,
                              BaggingRegressor, GradientBoostingRegressor,
                              RandomForestRegressor, )


ALPHAS = [0.00001, 0.0001, 0.001, 0.01, 0.1,
          1.0, 10.0, 100.0, 1000.0, 10000.0]
RATIO = [0., 0.10, 0.25, 0.50, 0.75, 0.90, 1.]

LINEAR = [dict(name='LinearRegression',
               model=LinearRegression, kwargs={})]

RIDGE = [dict(name='Ridge_a%f' % a, model=Ridge, kwargs={'alpha': a})
         for a in ALPHAS]

LASSO = [dict(name='Lasso_a%f' % a, model=Lasso, kwargs={'alpha': a})
         for a in ALPHAS]

ELAST = [dict(name='ElasticNet_a%f_r%f' % (a, r), model=ElasticNet,
              kwargs={'alpha': a, 'l1_ratio': r})
         for a in ALPHAS for r in RATIO]

MTLASSO = [dict(name='MultiTaskLasso_a%f' % a,
                model=MultiTaskLasso,
                kwargs={'alpha': a, 'max_iter': 10000,}) for a in ALPHAS]

LARS = [dict(name='Lars_c%s' % str(c), model=Lars,
             kwargs={'n_nonzero_coefs': c})
         for c in (1, 2, 3, 4, 5, 10, 25, 50, 100, np.inf)]

LLARS = [dict(name='LassoLars_a%f' % a, model=LassoLars,
              kwargs={'alpha': a})
         for a in ALPHAS]

BRIDGE = [{'name': 'BayesianRidge', 'classifier': BayesianRidge, }, ]

ARDR = [{'name': 'ARDRegression', 'classifier': ARDRegression, }, ]


LOGISTIC = [dict(name='LogisticRegression_p%s_C%f' % (p, c),
                 model=LogisticRegression,
                 kwargs={'penalty': p, 'C': c})
            for c in ALPHAS for p in ('l1', 'l2')]

# SGDRegressor(loss='squared_loss', penalty='l2', alpha=0.0001, l1_ratio=0.15, fit_intercept=True, n_iter=5, shuffle=False, verbose=0, epsilon=0.1, random_state=None, learning_rate='invscaling', eta0=0.01, power_t=0.25, warm_start=False)
loss = 'squared_loss', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive'
penality = 'l2', 'l1', 'elasticnet'
SGD = [dict(name='SGDRegressor_l%s_p%s_a%f_r%f' % (l, p, a, r),
            model=SGDRegressor,
            kwargs={'loss': l, 'penalty': p, 'alpha': a, 'l1_ratio': r})
       for a in ALPHAS for r in RATIO for l in loss for p in penality]

PERCEPT = [dict(name='Perceptron_p%s_a%f' % (p, a),
                model=SGDRegressor,
                kwargs={'loss': l, 'penalty': p, 'alpha': a, 'l1_ratio': r})
           for a in ALPHAS for r in RATIO for l in loss for p in penality]

loss = 'epsilon_insensitive', 'squared_epsilon_insensitive'
PAR = [dict(name='PassiveAggressiveRegressor_c%f_l%s' % (c, l),
            model=PassiveAggressiveRegressor, kwargs={'C': c, 'loss': l})
           for c in ALPHAS for l in loss]

RANSAC = [dict(name='RANSACRegressor_c%d' % (m),
               model=RANSACRegressor,
               kwargs={'base_estimator': LinearRegression(), 'min_samples': m})
           for m in (5, 10, 15, 20, 25, 30, 35, 37)]
# KNeighborsRegressor
KNN = [dict(name='KNeighborsRegressor_n%02d_w%s' % (n, w),
            model=KNeighborsRegressor,
            kwargs={'n_neighbors': n, 'weights': w})
       for n in (1, 3, 5) for w in ('uniform', 'distance')]

# RadiusNeighborsRegressor
RNN = [dict(name='RadiusNeighborsRegressor_r%f_w%s' % (r, w),
            model=RadiusNeighborsRegressor,
            kwargs={'radius': r, 'weights': w})
       for r in (0.01, 0.1, 0.5, 1.0, 1.5, 2.0, 4.0, 8.0)
       for w in ('uniform', 'distance')]

# GaussianProcess(regr='constant', corr='squared_exponential', beta0=None, storage_mode='full', verbose=False, theta0=0.1, thetaL=None, thetaU=None, optimizer='fmin_cobyla', random_start=1, normalize=True, nugget=2.2204460492503131e-15, random_state=None)
GAUPROC = [dict(name='GaussianProcess_r%s_c%s_o%s' % (r, c, o),
                model=GaussianProcess,
                kwargs={'regr': r, 'corr': c, 'optimizer': o})
           for r in ('constant', 'linear', 'quadratic')
           for c in ('absolute_exponential', 'squared_exponential',
                     'generalized_exponential', 'cubic', 'linear')
           for o in ('fmin_cobyla', 'Welch')]

# ExtraTreesRegressor(n_estimators=10, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features='auto', max_leaf_nodes=None, bootstrap=False, oob_score=False, n_jobs=1, random_state=None, verbose=0, min_density=None, compute_importances=None)
EXTRAT = [dict(name='ExtraTreesRegressor_e%03d_f%s' % (e, f),
               model=ExtraTreesRegressor,
               kwargs={'n_estimators': e, 'max_features': f, 'n_jobs': 1})
          for e in (10, 100, 500) for f in ('auto', 'sqrt', 'log2')]

# BaggingRegressor(base_estimator=None, n_estimators=10, max_samples=1.0, max_features=1.0, bootstrap=True, bootstrap_features=False, oob_score=False, n_jobs=1, random_state=None, verbose=0)
BAGGING = [dict(name='BaggingRegressor_e%02d_f%d' % (e, r),
                model=BaggingRegressor,
                kwargs={'n_estimators': e, 'max_features': r, 'n_jobs': 4})
           for e in (10, 100, 500) for r in (2, 3, 4, 5, 7, 10, 15)]#, 40, 60, 80, 100)]

# GradientBoostingRegressor(loss='ls', learning_rate=0.1, n_estimators=100, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False)
GRADBOOST = [dict(name='GradientBoostingRegressor_l%s_lr%f_e%03d_f%s' % (l, r, e, f),
                  model=GradientBoostingRegressor,
                  kwargs={'loss': l, 'learning_rate': r, 'n_estimators': e,
                  'max_features': f})
             for l in ('ls', 'lad', 'huber', 'quantile')
             for r in (0.01, 0.1, 0.5, 1.0, 1.5)
             for e in (10, 100, 500)
             for f in ('auto', 'sqrt', 'log2')]

# RandomForestRegressor(n_estimators=10, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features='auto', max_leaf_nodes=None, bootstrap=True, oob_score=False, n_jobs=1, random_state=None, verbose=0, min_density=None, compute_importances=None)
RANDFOR = [dict(name='RandomForestRegressor_e%03d_f%s' % (e, f),
                model=RandomForestRegressor,
                kwargs={'n_estimators': e, 'max_features': f, 'n_jobs': 4})
          for e in (10, 100, 500) for f in ('auto', 'sqrt', 'log2')]

# SVR(kernel='rbf', degree=3, gamma=0.0, coef0=0.0, tol=0.001, C=1.0, epsilon=0.1, shrinking=True, probability=False, cache_size=200, verbose=False, max_iter=-1, random_state=None)
SVRLIN = [dict(name='SVR_k%s_C%f' % (k, c), model=SVR,
               kwargs={'C': c, 'kernel': k, 'epsilon': y, 'probability': True})
          for c in ALPHAS for y in ALPHAS for k in ('linear', )]

SVRSIGRBF = [dict(name='SVR_k%s_C%f_g%f' % (k, c, g), model=SVR,
                  kwargs={'C': c, 'gamma': g, 'kernel': k, 'epsilon': y,
                          'probability': True})
             for c in ALPHAS
             for g in ALPHAS
             for y in ALPHAS
             for k in ('rbf', 'sigmoid')]


RCV = [{'name': 'ridgeCV', 'classifier': RidgeCV,
        'kwargs': {'alphas': ALPHAS, 'scoring': None, 'cv': None}}, ]

LCV = [{'name': 'LassoLarsCV', 'classifier': LassoLarsCV,
        'kwargs': {'cv': None, 'max_n_alphas': 10000, 'n_jobs': 4}}, ]

OCV = [{'name': 'OrthoMatchPurusuitCV',
        'classifier': OrthogonalMatchingPursuitCV, 'kwargs': dict(n_jobs=4)}, ]



ALL = (LINEAR + RIDGE + LASSO + ELAST + LARS + LLARS + BRIDGE + ARDR +
       LOGISTIC + SGD + PERCEPT + PAR + RANSAC + EXTRAT + BAGGING +
       GRADBOOST + RANDFOR  + SVRLIN + SVRSIGRBF)
       #(RCV + LCV + OCV) # + MTLASSO + KNN + RNN + GAUPROC


BEST = [

]
