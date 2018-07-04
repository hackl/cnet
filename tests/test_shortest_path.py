#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_shortest_path.py
# Creation  : 25 May 2018
# Time-stamp: <Mit 2018-07-04 15:33 juergen>
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

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import cnet
from cnet import Network, Path, Paths
from cnet.algorithms.shortest_path import shortest_path, k_shortest_paths, ksp, dijkstra

#from scipy import sparse
import timeit

# Test data
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
NETWORK = os.path.join(BASE_DIR, 'test_data/network.xml.gz')


@pytest.fixture  # (params=[True,False])
def net():
    net = Network(directed=False)

    net.add_node('a', x=0, y=0)
    net.add_node('b', x=4000, y=3000)
    net.add_node('c', x=8000, y=0)
    net.add_node('d', x=4000, y=7000)
    net.add_node('e', x=8000, y=10000)
    net.add_node('f', x=4000, y=10000)
    net.add_node('g', x=0, y=10000)

    net.add_edge('ab', 'a', 'b', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('ac', 'a', 'c', length=8000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('bc', 'b', 'c', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('bd', 'b', 'd', length=4000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('de', 'd', 'e', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('df', 'd', 'f', length=3000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('dg', 'd', 'g', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('ef', 'e', 'f', length=4000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('fg', 'f', 'g', length=4000.0,
                 capacity=3600, free_flow_speed=27.78)
    return net


@pytest.fixture
def large_net():
    import gzip
    from xml.dom.minidom import parse, parseString

    net = Network(directed=True)
    input_file = gzip.open(NETWORK)
    content = input_file.read()

    # parse xml file content
    network = parseString(content)

    # get edges
    edge_list = network.getElementsByTagName('link')

    # add edges to the graph
    for e in edge_list:
        id = e.attributes['id'].value
        u = e.attributes['from'].value
        v = e.attributes['to'].value
        net.add_edge(id, u, v)
    return net


# def test_shortest_path(net):

#     p = shortest_path(net, 'a', 'f', weight='length')

#     assert isinstance(p, Path)
#     assert p.weight() == 12000
#     assert len(p) == 4
#     assert p.edges['ab']['length'] == 5000.0

#     p = shortest_path(net, 'a', 'f', weight='length', mode=None)

#     assert isinstance(p, tuple)
#     assert p[0] == 12000
#     assert len(p[1]) == 4
#     assert 'a' in p[1]
#     assert p[1] == ['a', 'b', 'd', 'f']

#     adj = net.adjacency_matrix(weight='length')
#     s = net.nodes.index('a')
#     t = net.nodes.index('f')

#     p = shortest_path(adj, s, t)

#     assert isinstance(p, tuple)
#     assert p[0] == 12000
#     assert len(p[1]) == 4
#     assert p[1] == [0, 1, 3, 5]  # 'a'=0,'b'=1,'d'=3,'f'=5

#     p = shortest_path(net, 'f', 'a', weight='length')

#     if net.directed:
#         assert isinstance(p, Path)
#         assert p.weight() == float('inf')
#         assert len(p) == 0

#     # TODO implement sp also for spatial networks


# def test_k_shortest_paths(net):
#     k_p = k_shortest_paths(net, 'a', 'f', k=4, weight='length')

#     assert isinstance(k_p, Paths)
#     assert isinstance(k_p[0], Path)
#     assert len(k_p) == 4

#     k_p = k_shortest_paths(net, 'a', 'f', k=4, weight='length', mode=None)

#     assert isinstance(k_p, list)
#     assert isinstance(k_p[0], tuple)
#     assert len(k_p) == 4


# def test_larger_network(large_net):
#     large_net.summary()

#     u = '1751873987'
#     v = '237065489_1L1'
#     num = 10
#     k = 3

#     t = timeit.Timer(lambda: shortest_path(large_net, u, v))
#     print(t.timeit(number=num))

#     adj = large_net.adjacency_matrix()
#     a = large_net.nodes.index(u)
#     b = large_net.nodes.index(v)

#     t = timeit.Timer(lambda: shortest_path(adj, a, b))
#     print(t.timeit(number=num))

#     t = timeit.Timer(lambda: k_shortest_paths(large_net, u, v, k))
#     print(t.timeit(number=num))

#     t = timeit.Timer(lambda: k_shortest_paths(adj, a, b, k))
#     print(t.timeit(number=num))

def test_ksp(net):
    print('--- Start ---')
    k_p = ksp(net, 'a', 'e', k=8, weight='length')
    print(k_p)

    for p in k_p:
        print(p, p.weight())

    print('--- End ---')

    #p = dijkstra(net, 'e', 'a')
    # print(k_p)


test_ksp(net())
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
