## -*- coding: utf-8 -*-
#"""
#Authors: Pietro Zambelli
#
#This file contains some lists of scikit-learn classifiers.
#For each algoritms a list of dictionary with different options is created,
#to identify the set of parameters with better performance for each classifier.
#
#Each model is builded by a dictionary with the following keys:
#
#* name: is a string to define the identification name
#* model: definition of a class
#* kwargs: is a dictionary with the parameters to use for the initialization
#          of the classification.
#
#An example could be:
#
#::
#
#    KNN = [{'name': 'knn%d_w%s' % (n, w),
#            'model': KNeighborsClassifier,
#            'kwargs': {'n_neighbors': n, 'weights': w}}
#           for n in (1, 2, 3, 4, 8, 16) for w in ('uniform', 'distance')]
#
#
#Please look the source code to know more  about classifiers.
#"""
#
#from sklearn.linear_model import SGDClassifier
#from sklearn.ensemble import (AdaBoostClassifier,
#                              ExtraTreesClassifier,
#                              GradientBoostingClassifier,
#                              RandomForestClassifier)
#from sklearn.neighbors import (KNeighborsClassifier,
#                               NearestCentroid)
#from sklearn.tree import DecisionTreeClassifier
#from sklearn.naive_bayes import GaussianNB
#from sklearn.svm import SVC
#from sklearn.covariance import EmpiricalCovariance
#
## number of estimators
#ESTIMATORS = 100
## Nnumber of jobs
#NJOBS = 4
## min samples split
#MSS = (1, 2, 3, 4, 5)
## min samples leaf
#MSL = (1, 2, 3, 4, 5)
## max feature
#MF = ('auto', 'sqrt', 'log2', 0.05, 0.25, 0.5, 0.75, 0.95, 0.98)
## SVC C range
#CRANGE = 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e-0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6
## SVC gamma range
#GRANGE = CRANGE
##
#BOOLS = [True, False]
#
#
#SGD = [{'name': 'sgd_l%s_p%s' % (l, p),
#        'model': SGDClassifier,
#        'kwargs': {'loss': l, 'penalty': p}}
#       for l in ('hinge', 'modified_huber', 'log')
#       for p in ('l2', 'l1', 'elasticnet')]
#
#
#KNN = [{'name': 'knn%d_w%s' % (n, w),
#        'model': KNeighborsClassifier,
#        'kwargs': {'n_neighbors': n, 'weights': w}}
#       for n in (1, 2, 3, 4, 8, 16) for w in ('uniform', 'distance')]
#
#
#NCENT = [{'name': 'ncentroid_m%s_t%r' % (m, t),
#          'model': NearestCentroid,
#          'kwargs': {'metric': m, 'shrink_threshold': t}}
#         for m in ('euclidean', 'l2', 'l1', 'manhattan', 'cityblock')
#         for t in (None, )]  # TODO: check shrink_threshold
#
#
#DTTEMPL = 'dtree_c%s_s%s_mss%02d_msl%02d_mf%s'
#DECTREE = [{'name': DTTEMPL % (c, s, mss, msl,
#                               mf if isinstance(mf, str) else repr(mf)),
#            'model': DecisionTreeClassifier,
#            'kwargs': {'criterion': c, 'splitter': s, 'max_depth': None,
#                       'min_samples_split': mss, 'min_samples_leaf': msl,
#                       'max_features': mf, 'random_state': None,
#                       'min_density': None}}
#           for c in ('gini', 'entropy') for s in ('best', )
#           for mss in MSS for msl in MSL for mf in MF]
#
#
#RFTEMPL = 'randforest_c%s_mss%d_msl%d_mf%s'
#RNDFOREST = [{'name': RFTEMPL % (c, mss, msl,
#                                 mf if isinstance(mf, str) else repr(mf)),
#              'model': RandomForestClassifier,
#              'kwargs': {'n_estimators': ESTIMATORS, 'n_jobs': NJOBS,
#                         'criterion': c,
#                         'max_depth': None,
#                         'min_samples_split': mss, 'min_samples_leaf': msl,
#                         'max_features': mf, 'random_state': None,
#                         'min_density': None}}
#             for c in ('gini', 'entropy')
#             for mss in MSS for msl in MSL for mf in MF]
#
#ADATEMPL = 'ada_DTC_c%s_s%s_mss%d_msl%d_mf%s'
#ADABOOST = [{'name': ADATEMPL % (c, s, mss, msl,
#                                 mf if isinstance(mf, str) else repr(mf)),
#             'model': AdaBoostClassifier,
#             'kwargs': dict(base_estimator=DecisionTreeClassifier(
#                            criterion=c, max_depth=1, max_features=mf,
#                            min_samples_leaf=msl,
#                            min_samples_split=mss, random_state=None,
#                            splitter=s),
#                            n_estimators=ESTIMATORS, learning_rate=1.0,
#                            algorithm='SAMME.R', random_state=None)}
#            for c in ('gini', 'entropy') for s in ('best', )
#            for mss in MSS for msl in MSL for mf in MF]
#
#
#ETEMPL = 'etree_c%s_mss%d_msl%d_mf%s'
#EXTRATREE = [{'name': ETEMPL % (c, mss, msl,
#                                mf if isinstance(mf, str) else repr(mf)),
#              'model': ExtraTreesClassifier,
#              'kwargs': dict(n_estimators=ESTIMATORS, criterion=c,
#                             max_depth=None, min_samples_split=mss,
#                             min_samples_leaf=msl, max_features=mf,
#                             bootstrap=False, oob_score=False,
#                             n_jobs=NJOBS, random_state=None, verbose=0,
#                             min_density=None, compute_importances=None)}
#             for c in ('gini', 'entropy')
#             for mss in MSS for msl in MSL for mf in MF]
#
#
#GRDTEMPL = 'gradboost_mss%d_msl%d_mf%s'
#GRDBOOST = [{'name': GRDTEMPL % (mss, msl,
#                                 mf if isinstance(mf, str) else repr(mf)),
#             'model': GradientBoostingClassifier,
#             'kwargs': dict(loss='deviance', learning_rate=0.1,
#                            n_estimators=ESTIMATORS,
#                            subsample=1.0,
#                            min_samples_split=mss, min_samples_leaf=msl,
#                            max_depth=3, init=None, random_state=None,
#                            max_features=mf, verbose=0)}
#            for mss in MSS for msl in MSL for mf in MF]
#
#
#GAUSSIAN = [
#    {'name': 'gaussianNB', 'model': GaussianNB},
#]
#
#
#SVCRBFSIG = [
#    {'name': 'SVC_k%s_C%f_g%f' % (k, c, g), 'model': SVC,
#     'kwargs': {'kernel': k, 'C': c, 'gamma': g,
#                'probability': True}}
#    for c in CRANGE for g in GRANGE for k in ('sigmoid', 'rbf')]
#
#SVCLIN = [
#    {'name': 'SVC_k%s_C%f' % (k, c), 'model': SVC,
#     'kwargs': {'kernel': k, 'C': c, 'probability': True}}
#    for c in CRANGE for k in ('linear', )]
#
#SVCPOL = [{'name': 'SVC_k%s_d%02d_C%f_g%f' % (k, d, c, g), 'model': SVC,
#           'kwargs': {'kernel': k, 'C': c, 'gamma': g, 'degree': d,
#                      'probability': True}}
#          for c in CRANGE
#          for g in GRANGE
#          for d in (2, 3)
#          for k in ('poly', )]
#
#EMCOV = [{'name': 'EMCOV_ac%s_sp%s' % (a, s), 'model': EmpiricalCovariance,
#          'kwargs': {'store_precision': a, 'assume_centered': s}}
#         for a in BOOLS
#         for s in BOOLS]
#
#ALL = (SGD + KNN + DECTREE + RNDFOREST + ADABOOST +
#       EXTRATREE + GRDBOOST + GAUSSIAN +
#       SVCRBFSIG + SVCLIN + SVCPOL)
#
#BEST = [
#    {'name': 'gradient_boost_500_meanleaf3', 'model': GradientBoostingClassifier,
#     'kwargs': dict(loss='deviance', learning_rate=0.1, n_estimators=500,
#                    subsample=1.0, min_samples_split=2, min_samples_leaf=3,
#                    max_depth=3, init=None, random_state=None,
#                    max_features=None, verbose=0)},
#    {'name': 'SVC_rbf', 'model': SVC,
#     'kwargs': {'kernel': 'rbf', 'C': 1000., 'gamma': 0.0001,
#                'probability': True}},
#    {'name': 'extra_tree_500_1', 'model': ExtraTreesClassifier,
#     'kwargs': dict(n_estimators=500, criterion='gini', max_depth=None,
#                    min_samples_split=2, min_samples_leaf=1,
#                    max_features='auto', bootstrap=False, oob_score=False,
#                    n_jobs=4, random_state=None, verbose=0, min_density=None,
#                    compute_importances=None)},
#    {'name': 'rand_tree_entropy_0p50_500', 'model': RandomForestClassifier,
#     'kwargs': {'n_estimators': 500, 'n_jobs': 4, 'criterion': 'entropy',
#                'max_features': 0.5}},
#    {'name': 'SVC_linear', 'model': SVC,
#     'kwargs': {'kernel': 'linear', 'C': 1.,
#                'probability': True}},
#    {'name': 'SVC_sigmoid', 'model': SVC,
#     'kwargs': {'kernel': 'sigmoid', 'C': 10**5, 'gamma': 10**-5,
#                'probability': True}},
#]
#