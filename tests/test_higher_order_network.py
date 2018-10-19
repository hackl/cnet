#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test environment for HONs
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-25
# Time-stamp: <Fre 2018-10-19 10:42 juergen>
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
from network2tikz import plot as tikz

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))
import cnet as cn
from cnet.classes.higher_order_network import HigherOrderNetwork


@pytest.fixture  # (params=[True,False])
def net():

    net = cn.Network(directed=True)
    net.add_node('a', x=0, y=0)
    net.add_node('b', x=4000, y=3000)
    net.add_node('c', x=8000, y=0)
    net.add_node('d', x=4000, y=7000)
    net.add_node('e', x=8000, y=10000)
    net.add_node('f', x=4000, y=10000)
    net.add_node('g', x=0, y=10000)

    net.add_edge('ab', 'a', 'b', color='red')
    net.add_edge('ac', 'a', 'c', color='red')
    net.add_edge('bc', 'b', 'c', color='red')
    net.add_edge('bd', 'b', 'd', color='red')
    net.add_edge('de', 'd', 'e', color='red')
    net.add_edge('df', 'd', 'f', color='red')
    net.add_edge('dg', 'd', 'g', color='red')
    net.add_edge('ef', 'e', 'f', color='red')
    net.add_edge('fg', 'f', 'g', color='red')
    return net


def test_higher_order_network(net):
    #    net.summary()
    layout = {
        'a': (0, 0),
        'b': (4000, 3000),
        'c': (8000, 0),
        'd': (4000, 7000),
        'e': (8000, 10000),
        'f': (4000, 10000),
        'g': (0, 10000)}

    tikz(net, layout=layout, node_label_as_id=True)
    hon = HigherOrderNetwork(net, k=2)
    hon.summary()

    layout = {
        'ac': (0, 1),
        'ab': (1, 0),
        'bc': (1, 2),
        'bd': (2, 1),
        'de': (3, 2),
        'df': (3.5, 1),
        'dg': (3, 0),
        'ef': (4, 2),
        'fg': (4, 0)}
    tikz(hon, node_label_as_id=True, layout=layout)

    # for n, a in hon.nodes(data=True):
    #     print(n, a)
    # tikz(hon, node_label_as_id=True, layout=layout)

    # hon2 = HigherOrderNetwork(hon, k=1)
    # hon2.summary()

    hon3 = HigherOrderNetwork(net, k=3)
    hon3.summary()

    # # for n, a in hon2.nodes(data=True):
    # #     print(n, a['edge'].u['edge'].u)

    tikz(hon3, node_label_as_id=True, layout='fr')
    pass


test_higher_order_network(net())
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
