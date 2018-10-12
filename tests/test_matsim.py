#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_matsim.py -- Test environment for the matsim converter
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-15
# Time-stamp: <Fre 2018-10-12 08:46 juergen>
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


wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet

# Path to the test data files
filepath = wk_dir + '/data/matsim/'


def test_network():
    msc = cnet.MATSimConverter()
    network = msc.network(filepath + 'network.xml.gz')
    network.summary()


def test_paths():
    msc = cnet.MATSimConverter()

    network = msc.network(filepath + 'network.xml.gz')
    edge_map = msc._simplify(network, prefix='N', zfill=2)

    network = cnet.RoadNetwork.load(filepath + 'network.pkl')
    paths = msc.paths(filepath + 'paths.csv', network=network,
                      start_time=39650, end_time=39860, edge_map=edge_map)

    # paths = msc.paths(filepath + 'paths.csv',
    #                   network=network, edge_map=edge_map)

    paths.summary()


# test_network()
test_paths()
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
