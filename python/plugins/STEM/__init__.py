# -*- coding: utf-8 -*-
"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : December 2020
    Copyright            : (C) 2020 Trilogis
    Email                : info@trilogis.it
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from __future__ import absolute_import

__author__ = 'Trilogis srl'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


def classFactory(iface):
    from .stem_plugin import STEMPlugin
    return STEMPlugin(iface)
