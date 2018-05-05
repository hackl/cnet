#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_paths.py 
# Creation  : 29 Mar 2018
# Time-stamp: <Sam 2018-05-05 10:41 juergen>
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
from cnet.classes.network import Node, Edge, Network

def test_node():
    """Test the node class."""

    u = Node('u')

    assert isinstance(u,Node)
    assert isinstance(u.id,str)
    assert u.id == 'u'

    v = Node('v',color='green')

    assert v['color'] == 'green'

    v['color'] = 'blue'

    assert v['color'] == 'blue'

    v.update(color='red',shape='circle')
    assert v['color'] == 'red'
    assert v['shape'] == 'circle'

    v['label'] = 'Node v'
    assert v['label'] == 'Node v'

    w = v.copy()
    assert isinstance(w,Node)
    assert w.id == v.id

    with pytest.raises(Exception):
        a = w['attribute not in dict']

def test_edge():
    """Test the edge class"""

    ab = Edge('ab','a','b')

    assert isinstance(ab,Edge)
    assert isinstance(ab.id,str)
    assert ab.id == 'ab'
    assert isinstance(ab.u,Node) and ab.u.id == 'a'
    assert isinstance(ab.v,Node) and ab.v.id == 'b'

    c = Node('c',color='red')
    bc = Edge('bc','b',c)

    assert isinstance(bc.v,Node)
    assert bc.v['color'] == 'red'

    d = Node('d',color='blue')
    cd = Edge('cd',c,d,length=100)

    assert cd['length'] == 100

    cd['length'] = 2.2

    assert cd['length'] == 2.2

    cd.update(length=10,capacity=.5)

    assert cd['length'] == 10
    assert cd['capacity'] == .5

    assert cd.weight() == 1.0
    assert cd.weight(weight='length') == 10

    cd['weight'] = 3
    assert cd.weight() == 3.0
    assert cd.weight(weight=None) == 1.0
    assert cd.weight(weight=False) == 1.0

    dc = cd.reverse()
    assert dc.u.id == cd.v.id
    assert dc.v.id == cd.u.id
    assert dc.id == 'r_'+cd.id

    cd.reverse(copy=False)
    assert cd.u.id == 'd'
    assert cd.v.id == 'c'

    with pytest.raises(Exception):
        a = cd['attribute not in dict']

@pytest.fixture(params=[True,False])
def net(request):
    net = Network(directed=request.param)
    net.add_edge('ab','a','b')
    net.add_edge('bc','b','c')
    net.add_edge('cd','c','d')
    net.add_edge('ab2','a','b')
    return net

def test_network():
    """ Test basic functionalists of the network class."""

    net = Network()
    assert isinstance(net,Network)
    assert net.name == ''
    assert net.directed == True

    net.name = 'my network'
    assert net.name == 'my network'

    net['type'] = 'road network'
    assert net['type'] == 'road network'

    net.update(type = 'rail network', location = 'Swizerland')
    assert net['type'] == 'rail network'

    assert net.shape == (0,0)

def test_edge_to_nodes_map(net):
    e2n = net.edge_to_nodes_map()
    assert e2n['ab'] == ('a','b')

def test_node_to_edges_map(net):
    n2e = net.node_to_edges_map()
    assert len(n2e['b']) == 3
    assert 'ab' in n2e['b']


def test_nodes_to_edges_map(net):
    n2e = net.nodes_to_edges_map()
    assert len(n2e[('a','b')]) == 2
    assert 'ab' in n2e[('a','b')] and 'ab2' in n2e[('a','b')]

def test_add_node():
    net = Network()
    net.add_node('a')

    assert net.number_of_nodes() == 1
    assert isinstance(net.nodes['a'],Node)
    assert net.nodes['a'].id == 'a'

    b = Node('b')
    net.add_node(b)

    assert net.number_of_nodes() == 2
    assert isinstance(net.nodes['b'],Node)
    assert net.nodes['b'].id == 'b'

def test_add_nodes_from():
    net = Network()
    a = Node('a')
    net.add_nodes_from([a,'b','c'],color='green')

    assert net.number_of_nodes() == 3
    assert net.nodes['a']['color'] == 'green'

def test_remove_node(net):
    non = net.number_of_nodes()
    noe = net.number_of_edges()
    # number of edges sharing the node b
    n2e = len(net.node_to_edges_map()['b'])

    net.remove_node('b')

    assert net.number_of_nodes() == non - 1
    assert net.number_of_edges() == noe - n2e

    net.remove_node('not a node')

def test_remove_nodes_from(net):
    non = net.number_of_nodes()
    noe = net.number_of_edges()
    # number of edges sharing node a and b
    a2e = net.node_to_edges_map()['a']
    b2e = net.node_to_edges_map()['b']
    n2e = len(set(a2e+b2e))

    net.remove_nodes_from(['a','b'])

    assert net.number_of_nodes() == non - 2
    assert net.number_of_edges() == noe - n2e

def test_has_node(net):
    assert net.has_node('a') == True
    assert net.has_node('not a node') == False


def test_add_edge():
    net = Network()
    net.add_edge('ab','a','b')

    assert net.number_of_nodes() == 2
    assert net.number_of_edges() == 1
    assert isinstance(net.edges['ab'],Edge)
    assert net.edges['ab'].id == 'ab'

    c = Node('c')
    net.add_edge('bc','b',c)
    assert net.number_of_edges() == 2

    cd = Edge('cd',c,'d')
    net.add_edge(cd)
    assert net.number_of_edges() == 3
    assert net.edges['cd'].u.id == 'c'

    with pytest.raises(Exception):
        net.add_edge('de')
    
def test_add_edges_from():
    net = Network()
    ab = Edge('ab','a','b')

    net.add_edges_from([ab,('bc','b','c')])

    assert net.number_of_edges() == 2
    assert net.edges['ab'].id == 'ab'


    with pytest.raises(Exception):
        net.add_edges_from([('c','d')])

def test_remove_edge(net):
    with pytest.raises(Exception):
        net.remove_edge(('a','b'))

    noe = net.number_of_edges()

    net.remove_edge('ab')

    assert net.number_of_edges() == noe - 1

    with pytest.raises(Exception):
        net.remove_edge(('e','f'))

def test_remove_edges_from(net):
    noe = net.number_of_edges()

    net.remove_edges_from(['ab','ab2'])

    assert net.number_of_edges() == noe - 2

def test_has_edge(net):
    assert net.has_edge('ab') == True
    assert net.has_edge('not an edge') == False
    assert net.has_edge(('a','b'))

def test_weights(net):
    for w in net.weights():
        assert w == 1.0

    for E in net.edges.values():
        E['weight'] = 2
        E['length'] = 4

    for w in net.weights():
        assert w == 2

    for w in net.weights(weight='length'):
        assert w == 4

    for w in net.weights(None):
        assert w == 1.0

def test_adjacency_matrix(net):
    adj = net.adjacency_matrix()

    assert adj.shape == (net.number_of_nodes(),net.number_of_nodes())

def test_degree():
    net = Network(directed = True)
    net.add_edges_from([('ab','a','b'),('cb','c','b'),('bd','b','d')])

    assert sum(net.degree().values()) == 3
    assert net.degree('b',mode='in') == 2
    assert net.degree(['a','b'])['a'] == 1

    net.edges['ab']['weight'] = 2

    assert net.degree(['a','b'],weight=True)['a'] == 2
    assert net.degree(['a','b'],mode='in',weight=True)['b'] == 3

    assert net.degree(['a','b'],mode='no valid mode',weight=True)['b'] == 1

def transition_matrix(net):
    pass

def laplacian_matrix(net):
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
