#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network2tikz.py 
# Creation  : 08 May 2018
# Time-stamp: <Don 2018-05-10 09:50 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : Test functions for converting networks to tikz-networks
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
from cnet.visualization.network2tikz import (plot, TikzNetworkDrawer, TikzEdgeDrawer,
                                             TikzNodeDrawer)
from cnet import Node, Edge, Network

import igraph as ig
import networkx as nx


@pytest.fixture#(params=[True,False])
def net():
    net = Network(name = 'my tikz test network')# ,directed=request.param)
    net.add_node('a', name='Alice', age=25, gender='f')
    net.add_node('b', name='Bob', age=31, gender='m')
    net.add_node('c', name='Claire', age=18, gender='f')
    net.add_node('d', name='Dennis', age=47, gender='m')
    net.add_node('e', name='Esther', age=22, gender='f')
    net.add_node('f', name='Frank', age=23, gender='m')
    net.add_node('g', name='George', age=50, gender='m')

    net.add_edge('ab','a','b',is_formal=False)
    net.add_edge('ac','a','c',is_formal=False)
    net.add_edge('cd','c','d',is_formal=True)
    net.add_edge('de','d','e',is_formal=True)
    net.add_edge('ec','e','c',is_formal=True)
    net.add_edge('cf','c','f',is_formal=False)
    net.add_edge('fa','f','a',is_formal=True)
    net.add_edge('fg','f','g',is_formal=False)
    net.add_edge('gg','g','g',is_formal=False)
    net.add_edge('gd','g','d',is_formal=False)
    return net

@pytest.fixture
def netx():
    net = nx.DiGraph()
    net.add_node('a', name='Alice', age=25, gender='f')
    net.add_node('b', name='Bob', age=31, gender='m')
    net.add_node('c', name='Claire', age=18, gender='f')
    net.add_node('d', name='Dennis', age=47, gender='m')
    net.add_node('e', name='Esther', age=22, gender='f')
    net.add_node('f', name='Frank', age=23, gender='m')
    net.add_node('g', name='George', age=50, gender='m')

    net.add_edge('a','b',is_formal=False)
    net.add_edge('a','c',is_formal=False)
    net.add_edge('c','d',is_formal=True)
    net.add_edge('d','e',is_formal=True)
    net.add_edge('e','c',is_formal=True)
    net.add_edge('c','f',is_formal=False)
    net.add_edge('f','a',is_formal=True)
    net.add_edge('f','g',is_formal=False)
    net.add_edge('g','g',is_formal=False)
    net.add_edge('g','d',is_formal=False)

    # net.add_edges_from([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3),
    #                   (5,6), (6,6)])

    
    return net

@pytest.fixture
def neti():
    net = ig.Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3),
                    (5,6), (6,6)],directed=True)

    net.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
    net.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
    net.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
    net.es["is_formal"] = [False, False, True, True, True, False, True, False,
                           False, False]
    return net

def test_plot(net):
    # print the summary of the graph (only for debugging)
    plot(net)

    for e in net.edges(data=True):
        print(e)

    for n in net.nodes(data=True):
        print(n)

    print(net.nodes['b']['age'])
    net.nodes()
    
def test_plot_networkx(netx):
    plot(netx)
    for e in netx.edges(data=True):
        print(e)

    for n in netx.nodes(data=True):
        print(n)

def test_plot_igraph(neti):
    plot(neti)

    for e in neti.es:
        print(e)

    for n in neti.vs:
        print(n)

    print(neti.vs.attributes())
    print(list(neti.vs.select(1,2)))
    print(neti.vs[1]['age'])



# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
