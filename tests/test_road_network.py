#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network.py 
# Creation  : 29 Mar 2018
# Time-stamp: <Mon 2018-05-07 15:59 juergen>
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
from cnet import RoadNode, RoadEdge, RoadNetwork

def test_road_node():
    """Test the spatial node class."""
    pass

def test_road_edge():
    """Test the edge class"""

    ab = RoadEdge('ab','a','b')

    assert isinstance(ab,RoadEdge)
    assert isinstance(ab.id,str)
    assert ab.id == 'ab'
    assert isinstance(ab.u,RoadNode) and ab.u.id == 'a'
    assert isinstance(ab.v,RoadNode) and ab.v.id == 'b'


    c = RoadNode('c',x=0,y=0)
    d = RoadNode('d',x=4,y=0)
    cd =RoadEdge('cd',c,d, capacity = 300, free_flow_speed = 20)

    assert cd.coordinates == [(0,0),(4,0)]
    assert cd.capacity == 300
    assert cd.free_flow_speed == 20

    assert cd.free_flow_time == cd.length()/cd.free_flow_speed

    ab = RoadEdge('ab','a','b',p1=(0,0),p2=(0,1000),
                  capacity=500, free_flow_speed=25,value=10)

    assert ab.weight('value') == 10
    assert ab.weight() == 40
    assert ab.weight('not_defined') == 1


    assert ab.cost_function(1000) == 136.0

    with pytest.raises(Exception):
        assert ab.cost_function(1000,mode='no valid cost function')

def test_road_network():
    """ Test basic functionalists of the network class."""
    pass

# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
