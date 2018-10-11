#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_matsim.py -- Test environment for the gis converter
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-15
# Time-stamp: <Don 2018-10-11 13:09 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================
import pytest
import os
import sys
import time
import pickle

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet

# Path to the test data files
filepath = wk_dir + '/data/shp/'


def test_network():
    sfc = cnet.SHPConverter()
    network = sfc.network(filepath + 'roads.shp', prefix=('N', 'E'), zfill=3)
    # network.summary()


def test_centroids():
    sfc = cnet.SHPConverter()
    network = sfc.network(filepath + 'roads.shp', prefix=('N', 'E'), zfill=3)
    centroides = sfc.centroids(filepath + 'centroids.shp', network=network)
    # print(centroides)


def test_trips():
    sfc = cnet.SHPConverter()
    network = sfc.network(filepath + 'roads.shp', prefix=('N', 'E'), zfill=3)
    centroids = sfc.centroids(filepath + 'centroids.shp', network=network)
    trips = sfc.trips(filepath + 'od.csv', centroids=centroids)
    # print(trips)

# test_network()
# test_centroids()
# test_trips()
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
