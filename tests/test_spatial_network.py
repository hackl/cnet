#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network.py 
# Creation  : 29 Mar 2018
# Time-stamp: <Son 2018-05-06 11:22 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : A test environment for the network classes
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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cnet
from cnet import SpatialNode, SpatialEdge, SpatialNetwork

def test_spatial_node():
    """Test the spatial node class."""

    u = SpatialNode('u')

    assert isinstance(u,SpatialNode)
    assert isinstance(u.id,str)
    assert u.id == 'u'
    assert u.coordinate == (0,0)
    assert u.x == 0
    assert u.y == 0

    u.x = 1.0

    assert u.coordinate == (1,0)
    assert u.x == 1

    u.y = 2.0

    assert u.coordinate == (1,2)
    assert u.y == 2

    u.coordinate = (3,3)

    assert u.coordinate == (3,3)

    v = SpatialNode('v', x=1)

    assert v.coordinate == (1,0)

    v = SpatialNode('v', y=1)

    assert v.coordinate == (0,1)

    v = SpatialNode('v',x=1,y=1)

    assert v.coordinate == (1,1)

    v = SpatialNode('v',coordinate=(2,2))

    assert v.coordinate == (2,2)

    v = SpatialNode('v',x=1,y=1,coordinate=(2,2))

    assert v.coordinate == (1,1)


def test_spatial_edge():
    """Test the edge class"""

    ab = SpatialEdge('ab','a','b')

    assert isinstance(ab,SpatialEdge)
    assert isinstance(ab.id,str)
    assert ab.id == 'ab'
    assert isinstance(ab.u,SpatialNode) and ab.u.id == 'a'
    assert isinstance(ab.v,SpatialNode) and ab.v.id == 'b'


    c = SpatialNode('c',x=0,y=0)
    d = SpatialNode('d',x=4,y=0)
    cd =SpatialEdge('cd',c,d)

    assert cd.coordinates == [(0,0),(4,0)]


    cd_2 = SpatialEdge('cd',c,d,geometry=[(0,0),(0,3),(4,3)])

    assert cd_2.coordinates == [(0, 0), (0, 3), (4, 3), (4, 0)]


    assert cd.length() == 4.0
    assert cd_2.length() == 10.0

    ef = SpatialEdge('ef','e','f',p1=(0,0),p2=(5,0),length=13)
    assert ef.length() == 5
    assert ef.length(None) == 13
    assert ef.length('topological') == 1



    
    with pytest.raises(Exception):
        assert ef.length('no valid coordinate type')
    with pytest.raises(Exception):
        assert cd.length(None)
    
    gh = SpatialEdge('gh','g','h',p1=(47.409589, 8.502555),
                     p2=(47.410344, 8.503037))
    assert gh.length('geographic') > 90

def test_spatial_network():
    """ Test basic functionalists of the network class."""

    net = SpatialNetwork()
    assert isinstance(net,SpatialNetwork)
    assert net.name == ''
    assert net.directed == True

    net.name = 'my network'
    assert net.name == 'my network'

    net['type'] = 'road network'
    assert net['type'] == 'road network'

    net.update(type = 'rail network', location = 'Swizerland')
    assert net['type'] == 'rail network'

    assert net.shape == (0,0)

    a = SpatialNode('a',x=3,y=3)
    b = SpatialNode('b',coordinate = (3,6))
    c = SpatialNode('c',coordinate = (0,2))

    bc = SpatialEdge('bc',b,c)

    net.add_node(a)
    net.add_edge('ab','a',b)
    net.add_edge(bc)

    assert net.number_of_nodes() == 3
    assert net.number_of_edges() == 2

    net.add_edge('cd','c','d')
    assert net.nodes['d'].coordinate == (0,0)


# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
