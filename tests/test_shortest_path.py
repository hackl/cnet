#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_shortest_path.py 
# Creation  : 25 May 2018
# Time-stamp: <Fre 2018-05-25 14:22 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : A test environment for shortest path algorithm
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

from cnet import Network
from cnet.algorithms.shortest_path import dijkstra, dijkstra_scipy, dijkstra_scipy_2
from scipy import sparse
import timeit


@pytest.fixture#(params=[True,False])
def net():
    net = Network(directed=False)

    net.add_node('a',x=0, y=0)
    net.add_node('b',x=4000, y=3000)
    net.add_node('c',x=8000, y=0)
    net.add_node('d',x=4000, y=7000)
    net.add_node('e',x=8000, y=10000)
    net.add_node('f',x=4000, y=10000)
    net.add_node('g',x=0, y=10000)

    net.add_edge('ab','a','b', length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('ac','a','c', length=8000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('bc','b','c', length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('bd','b','d', length=4000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('de','d','e', length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('df','d','f', length=3000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('dg','d','g', length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('ef','e','f', length=4000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('fg','f','g', length=4000.0, capacity=3600, free_flow_speed=27.78)
    return net



def test_dijkstra(net):
    net.summary()
    cost, path = dijkstra(net,'a','f')
    cost, path = dijkstra(net,'f','a')
    print(cost)
    print(path)


    t = timeit.Timer(lambda: dijkstra(net,'a','f'))
    print(t.timeit(number=1000))

    
def test_dijkstra_scipy(net):

    cost, path = dijkstra_scipy(net,'a','f')
    print(cost)
    print(path)


    t = timeit.Timer(lambda: dijkstra_scipy(net,'a','f'))
    print(t.timeit(number=1000))

    graph = net.adjacency_matrix()
    i1 = net.nodes.index('a')
    i2 = net.nodes.index('f')
    t = timeit.Timer(lambda: dijkstra_scipy_2(graph,i1,i2))
    print(t.timeit(number=1000))



def test_larger_network():

    import gzip
    from xml.dom.minidom import parse, parseString

    net = Network(directed=True)
    input_file = gzip.open('network.xml.gz')
    content = input_file.read()

    # parse xml file content
    network = parseString( content )

    # get edges
    edge_list = network.getElementsByTagName('link')

    # add edges to the graph
    for e in edge_list:
        id = e.attributes['id'].value
        u = e.attributes['from'].value
        v = e.attributes['to'].value
        net.add_edge(id,u,v)

    net.summary()

    u = '1751873987'
    v = '237065489_1L1'
    num = 10

    t = timeit.Timer(lambda: dijkstra_scipy(net,u,v))
    print(t.timeit(number=num))


    t = timeit.Timer(lambda: dijkstra_scipy(net,u,v))
    print(t.timeit(number=num))

    t = timeit.Timer(lambda: net.adjacency_matrix())
    print(t.timeit(number=1))
    
    graph = net.adjacency_matrix()
    i1 = net.nodes.index(u)
    i2 = net.nodes.index(v)

    t = timeit.Timer(lambda: dijkstra_scipy_2(graph,i1,i2))
    print(t.timeit(number=num))

# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
