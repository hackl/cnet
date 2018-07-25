#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test environment for HONs
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-25
# Time-stamp: <Mit 2018-07-25 17:17 juergen>
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
import cnet as cn
from cnet.classes.higher_order_network import (
    HigherOrderNetwork, HigherOrderPathNetwork)
from cnet.classes.path_network import PathEdge, PathNode, PathNetwork


def test_higher_order_network():

    a = HigherOrderNetwork('a')
    b = HigherOrderNetwork('b', color='blue')
    N = HigherOrderNetwork('N')

    N.add_edge('ab', a, b)
    N.nodes['a'].add_node(b)
    print(N.nodes['a'].nodes['b']['color'])
    b['color'] = 'red'
    print(N.nodes['a'].nodes['b']['color'])
    print('dddddddddd')
    print(N.id)
    print(N)
    print(N.name)

    p1 = cn.Path(['a', 'b', 'c'])
    p2 = cn.Path(['a', 'b'])
    ac = HigherOrderPathNetwork('ac', p1)
    ab = HigherOrderPathNetwork('ab', p2)

    net = HigherOrderPathNetwork('net', p1)
    net.add_node(ab)
    net.add_node(ac)
    net.add_edge(None, ab, ac)
    net.nodes['ab'].add_node(ac)
    net.summary()


test_higher_order_network()
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
