#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_paths.py
# Creation  : 29 Mar 2018
# Time-stamp: <Mit 2018-07-25 13:36 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : A test environment for the path classes
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

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import cnet
from cnet import Node, Edge
from cnet import Path, Paths


def test_path():
    """ Test basic functionalists of the path class."""
    p = Path()

    assert isinstance(p, Path)
    assert len(p) == 0

    p = Path(name='my path')

    assert p.name == 'my path'

    p = Path(['a', 'b', 'c'])
    assert len(p) == 3

    p1 = Path(['a', 'b'])
    p2 = Path(['a', 'b'])

    assert p1 == p2

    s = set()

    s.add(p1)
    s.add(p2)

    assert len(s) == 1
    assert list(s)[0].name == 'a-b'


def test_weight():
    p = Path()

    assert p.weight() == 1

    p['weight'] = 4

    assert p.weight() == 4
    assert p.weight(False) == 1

    p['length'] = 5

    assert p.weight('length') == 5


def test_add_node():
    p = Path()
    p.add_node('a', color='red')

    assert len(p) == 1
    assert p.path[0] == 'a'
    assert p.nodes['a'].id == 'a'
    assert p.nodes['a']['color'] == 'red'

    b = Node('b', color='green')
    p.add_node(b)

    assert len(p) == 2
    assert p.path[-1] == 'b'
    assert p.nodes['b'].id == 'b'
    assert p.nodes['b']['color'] == 'green'

    assert p.name == 'a-b'
    assert p.edges['a-b'].id == 'a-b'
    assert p.path.edges[0] == 'a-b'

    p.add_node(b)

    assert len(p) == 2


def test_add_edge():
    p = Path()
    p.add_edge('ab', 'a', 'b', length=10)

    assert len(p) == 2
    assert p.path.edges[0] == p.edges['ab'].id
    assert p.path == ['a', 'b']

    bc = Edge('bc', 'b', 'c', length=5)
    p.add_edge(bc)

    assert len(p) == 3
    assert p.path.edges[1] == p.edges['bc'].id
    assert p.path == ['a', 'b', 'c']

    with pytest.raises(Exception):
        p.add_edge('de')

    with pytest.raises(Exception):
        p.add_edge('de', 'd', 'e')


def test_has_subpath():
    p = Path()
    p.add_nodes_from(['a', 'b', 'c', 'd'])

    assert p.has_subpath(['a', 'b']) == True
    assert p.has_subpath(['a', 'c']) == False

    q = Path()
    q.add_nodes_from(['c', 'd'])

    assert p.has_subpath(q) == True

    q.add_node('e')

    assert p.has_subpath(q) == False

    p.add_nodes_from(['a', 'e', 'f'])

    assert p.has_subpath(['a', 'b', 'c']) == True
    assert p.has_subpath(['a', 'e', 'f']) == True

    assert p.has_subpath(['a-b', 'b-c'], mode='edges') == True
    assert p.has_subpath(['a-b', 'x-y'], mode='edges') == False


def test_subpath():
    p = Path(color='red')
    p.add_nodes_from(['a', 'b', 'c', 'd'])

    q = p.subpath(['a', 'b', 'c'])

    assert q.name == 'a-b-c'
    assert q['color'] == 'red'

    with pytest.raises(Exception):
        assert p.subpath(['a', 'c'])

    r = p.subpath(['c-d'], mode='edges')

    assert len(r) == 2


def test_subpaths():
    p = Path(color='red')
    p.add_nodes_from(['a', 'b', 'c', 'd', 'e'])

    P = p.subpaths()
    assert len(P) == 9
    assert isinstance(P[0], Path)
    assert len(p.subpaths(min_length=-5)) == 9
    assert len(p.subpaths(max_length=100)) == 9
    assert len(p.subpaths(min_length=3, max_length=3)) == 3

    with pytest.raises(Exception):
        assert p.subpaths(min_length=100, max_length=0)


def test_paths():
    P = Paths(name='my paths', location='Austria')

    assert isinstance(P, Paths)
    assert P.name == 'my paths'

    P.update(location='Switzerland', type='road travelers')
    assert P['location'] == 'Switzerland'
    assert P['type'] == 'road travelers'

    p_1 = Path()
    p_2 = Path()
    p_1.add_nodes_from(['a', 'b'])
    p_2.add_nodes_from(['a', 'b', 'c'])

    P.add_path(p_1)
    assert len(P) == 1
    assert P[0].name == 'a-b'

    P.add_path(p_2)
    assert len(P) == 2

    Q = Paths()
    Q.add_paths_from([p_1, p_2])
    assert len(Q) == 2

    R = Paths([p_1, p_2])
    assert len(R) == 2


def test_od_paths():
    p_1 = Path(['a', 'b'])
    p_2 = Path(['a', 'b', 'c'])
    p_3 = Path(['a', 'c', 'b'])

    P = Paths()
    P.add_paths_from([p_1, p_2, p_3])

    P_ac = P.st_paths('a-b', 'b-c', mode='edges')
    assert len(P_ac) == 1
    assert P_ac[0].path == ['a', 'b', 'c']

    P_ab = P.st_paths('a', 'b')
    assert len(P_ab) == 2


def test_intersection():
    p_1 = Path(['a', 'b'])
    p_2 = Path(['a', 'b', 'c'])
    P_1 = Paths([p_1])
    P_2 = Paths([p_1, p_2])

    P = P_1.intersection(P_2)
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
