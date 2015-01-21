# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 16:22:54 2014

@author: pietro
"""
import imp


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
