# -*- coding: utf-8 -*-
from collections import namedtuple

CVResult = namedtuple('CVResult',
                      ['index', 'name', 'mean', 'max', 'min', 'std', 'time'])
TestResult = namedtuple('TestResult', ['index', 'name', 'score', ])

def return_argument(x):
    return x