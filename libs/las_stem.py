# -*- coding: utf-8 -*-
"""
Created on Mon Dec  1 10:56:52 2014

@author: lucadelu

***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import subprocess

PIPE = subprocess.PIPE


class stemLAS():

    def __init__(self):
        self.pdal = None
        self.liblas = None
        self._check()

    def _check(self):
        self.pdal = self._checkLibs('pdal-config --version')
        self.liblas = self._checkLibs('liblas-config --version')

    def _checkLibs(self, command):
        lasout = subprocess.Popen(command, shell=True,
                                  stdout=PIPE).stdout.readlines()[0].strip()
        if lasout:
            return True
        else:
            return False

    def clip(self, inp, out, bbox=None, forced=False, compressed=False):
        """
        parameter inp str: input
        parameter out str: output
        parameter bbox list: bbox to cut the las file
        parameter forced str: liblas o pdal as value
        parameter compressed bool: True to obtain a LAZ file
        """
        if forced == 'liblas' and self.liblas:
            command = ['las2las']
        elif forced == 'liblas' and not self.liblas:
            raise Exception("LibLAS non trovato")
        elif forced == 'pdal' and self.pdal:
            command = ['pdal translate']
        elif forced == 'pdal' and not self.pdal:
            raise Exception("pdal non trovato")
        elif self.liblas:
            command = ['las2las']
        else:
            command = ['pdal translate']

        if 'las2las' in command:
            command.extend(['-i', inp, '-o', out])
            if bbox:
                command.extend(['-e', " ".join(bbox)])
