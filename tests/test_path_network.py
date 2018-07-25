#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test environment for path network
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-25
# Time-stamp: <Mit 2018-07-25 16:01 juergen>
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
from cnet.classes.path_network import PathNetwork, PathEdge, PathNode


def test_path_network():
    net = PathNetwork()

    assert isinstance(net, cn.Network)

    net = PathNetwork(name='my path network')

    assert net.name == 'my path network'


def test_path_node():
    p1 = cn.Path(['a', 'b'])
    p2 = cn.Path(['a', 'b', 'c'])
    P = cn.Paths([p1, p2])

    u = PathNode('a-b')
    assert u.id == 'a-b'

    with pytest.raises(Exception):
        assert PathNode()

    u = PathNode(p1)
    assert u.id == 'a-b'

    with pytest.raises(Exception):
        assert PathNode(P)

    P.name = 'p1,p2'
    u = PathNode(P)
    assert u.id == 'p1,p2'

    u = PathNode('a-b', path=p1)
    assert u.id == 'a-b'


def test_subpaths():
    p1 = cn.Path(['a', 'b'])
    p2 = cn.Path(['a', 'b', 'c'])
    u = PathNode('u', path=[p1, p2])

    P = u.subpaths()
    assert len(P) == 2


def test_path_edge():

    ab = PathEdge('ab', 'a', 'b')

    assert isinstance(ab, PathEdge)
    assert isinstance(ab.id, str)
    assert ab.id == 'ab'
    assert isinstance(ab.u, PathNode) and ab.u.id == 'a'
    assert isinstance(ab.v, PathNode) and ab.v.id == 'b'
    assert isinstance(ab.u.paths, cn.Paths)
    assert isinstance(ab.v.paths, cn.Paths)

    p1 = cn.Path(['a', 'b'])
    p2 = cn.Path(['a', 'b', 'c'])

    u = PathNode('u', p1)
    v = PathNode('v', p2)

    e = PathEdge('u-v', u, v)
    assert e.u.path.name == 'a-b'
    assert e.v.path.name == 'a-b-c'
    assert isinstance(ab.u.paths, cn.Paths)
    assert isinstance(ab.v.paths, cn.Paths)

    e = PathEdge('p1-p2', p1, p2)
    assert e.u.id == 'a-b'
    assert e.v.id == 'a-b-c'

    e = PathEdge(None, u, v)
    assert e.id == 'u|v'

    e = PathEdge(None, p1, p2)
    assert e.id == 'a-b|a-b-c'


def test_common_paths():
    p1 = cn.Path(['a', 'b'])
    p2 = cn.Path(['a', 'b', 'c'])
    e = PathEdge(None, p1, p2)

    assert len(e.common_paths()) == 0

    e = PathEdge('ab', 'a', 'b', p1=p1, p2=p1)
    P = e.common_paths()
    assert len(P) == 1
    assert P[0].name == 'a-b'


def test_common_subpaths():
    p1 = cn.Path(['a', 'b'])
    p2 = cn.Path(['a', 'b', 'c'])
    e = PathEdge(None, p1, p2)

    P = e.common_subpaths()
    assert len(P) == 1
    assert P[0].name == 'a-b'
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
