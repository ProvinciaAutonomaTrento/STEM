# -*- coding: utf-8 -*-
from functools import partial

from sklearn.externals import six
from sklearn.metrics import make_scorer
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics import (r2_score, median_absolute_error,
                             mean_absolute_error,
                             mean_squared_error, accuracy_score, f1_score,
                             roc_auc_score, average_precision_score,
                             precision_score, recall_score, log_loss)


def get_scorer(scoring):
    if isinstance(scoring, six.string_types):
        try:
            scorer = SCORERS[scoring]
        except KeyError:
            raise ValueError('%r is not a valid scoring value. '
                             'Valid options are %s'
                             % (scoring, sorted(SCORERS.keys())))
    else:
        scorer = scoring
    return scorer


def _passthrough_scorer(estimator, *args, **kwargs):
    """Function that wraps estimator.score"""
    return estimator.score(*args, **kwargs)


def check_scoring(estimator, scoring=None, allow_none=False):
    """Determine scorer from user options.

    A TypeError will be thrown if the estimator cannot be scored.

    Parameters
    ----------
    estimator : estimator object implementing 'fit'
        The object to use to fit the data.

    scoring : string, callable or None, optional, default: None
        A string (see model evaluation documentation) or
        a scorer callable object / function with signature
        ``scorer(estimator, X, y)``.

    allow_none : boolean, optional, default: False
        If no scoring is specified and the estimator has no score function, we
        can either return None or raise an exception.

    Returns
    -------
    scoring : callable
        A scorer callable object / function with signature
        ``scorer(estimator, X, y)``.
    """
    has_scoring = scoring is not None
    if not hasattr(estimator, 'fit'):
        raise TypeError("estimator should a be an estimator implementing "
                        "'fit' method, %r was passed" % estimator)
    elif has_scoring:
        return get_scorer(scoring)
    elif hasattr(estimator, 'score'):
        return _passthrough_scorer
    elif allow_none:
        return None
    else:
        raise TypeError(
            "If no scoring is specified, the estimator passed should "
            "have a 'score' method. The estimator %r does not." % estimator)


# Standard regression scores
r2_scorer = make_scorer(r2_score)
mean_squared_error_scorer = make_scorer(mean_squared_error,
                                        greater_is_better=False)
mean_absolute_error_scorer = make_scorer(mean_absolute_error,
                                         greater_is_better=False)
median_absolute_error_scorer = make_scorer(median_absolute_error,
                                           greater_is_better=False)

# Standard Classification Scores
accuracy_scorer = make_scorer(accuracy_score)
f1_scorer = make_scorer(f1_score)

# Score functions that need decision values
roc_auc_scorer = make_scorer(roc_auc_score, greater_is_better=True,
                             needs_threshold=True)
average_precision_scorer = make_scorer(average_precision_score,
                                       needs_threshold=True)
precision_scorer = make_scorer(precision_score)
recall_scorer = make_scorer(recall_score)

# Score function for probabilistic classification
log_loss_scorer = make_scorer(log_loss, greater_is_better=False,
                              needs_proba=True)

# Clustering scores
adjusted_rand_scorer = make_scorer(adjusted_rand_score)


SCORERS = dict(r2=r2_scorer,
               median_absolute_error=median_absolute_error_scorer,
               mean_absolute_error=mean_absolute_error_scorer,
               mean_squared_error=mean_squared_error_scorer,
               accuracy=accuracy_scorer, roc_auc=roc_auc_scorer,
               average_precision=average_precision_scorer,
               log_loss=log_loss_scorer,
               adjusted_rand_score=adjusted_rand_scorer)

for name, metric in [('precision', precision_score),
                     ('recall', recall_score), ('f1', f1_score)]:
    SCORERS[name] = make_scorer(metric)
    for average in ['macro', 'micro', 'samples', 'weighted']:
        qualified_name = '{0}_{1}'.format(name, average)
        SCORERS[qualified_name] = make_scorer(partial(metric, pos_label=None,
                                                      average=average))
