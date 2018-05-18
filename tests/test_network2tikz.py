#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network2tikz.py 
# Creation  : 08 May 2018
# Time-stamp: <Fre 2018-05-18 16:16 juergen>
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
    net = Network(name = 'my tikz test network',directed=False)
    net.add_node('a', name='Alice', age=25, gender='f')
    net.add_node('b', name='Bob', age=31, gender='m')
    net.add_node('c', name='Claire', age=18, gender='f')
    net.add_node('d', name='Dennis', age=47, gender='m')
    net.add_node('e', name='Esther', age=22, gender='f')
    net.add_node('f', name='Frankg', age=23, gender='m')
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

@pytest.fixture
def netl():
    nodes = ['a','b','c','d','e','f','g']

    edges = [('a','b'), ('a','c'), ('c','d'), ('d','e'), ('e','c'), ('c','f'),
             ('f','a'), ('f','g'), ('g','g'), ('g','d')]
    return nodes,edges

@pytest.fixture
def color_dict():
    return {"m": "blue", "f": "red"}

@pytest.fixture
def layer_dict():
    return {"m": 1, "f": 2}


def test_plot(net,color_dict):
    # print the summary of the graph (only for debugging)

    # style dictionary
    visual_style = {}

    # node styles
    # -----------
    visual_style["vertex_size"] = .5
    visual_style["vertex_color"] = [color_dict[g] for g in net.nodes('gender')]
    visual_style['node_opacity'] = .5
    visual_style["vertex_label"] = net.nodes['name']
    visual_style['node_label_position'] = .5
    visual_style["node_label_distance"] = 1.5
    visual_style["vertex_label_color"] = "green"
    visual_style["vertex_label_size"] = 7
    visual_style["vertex_shape"] = 'rectangle'
    visual_style["vertex_style"] = '{dashed,color=yellow}'
    visual_style["node_math_mode"] = [True, False]
    #visual_style["vertex_layer"] = [layer_dict[gender] for gender in g.vs["gender"]]

    # visual_style['node_label_off'] = True
    # visual_style['node_label_as_id'] = True
    # visual_style['node_math_mode'] = True
    # visual_style['node_rgb'] = True
    # visual_style['node_pseudo'] = True

    # edge styles
    # -----------
    visual_style["edge_width"] = .7
    visual_style["edge_color"] = "red"
    visual_style["edge_opacity"] = .5
    visual_style["edge_curved"] = 0.1
    visual_style["edge_label"] = "blue"
    visual_style["edge_label_position"] = 'above'
    visual_style["edge_label_distance"] = .7
    visual_style["edge_label_color"] = "blue"
    #visual_style["edge_label_size"] = .3
    visual_style["edge_style"] = 'dashed'
    visual_style["edge_arrow_size"] = .2
    visual_style["edge_arrow_width"] = .2

    visual_style["edge_loop_size"] = 3
    visual_style["edge_loop_position"] = 90
    visual_style["edge_loop_shape"] = 45

    visual_style['edge_directed'] = True#{'ab':True}# [False,True,True,False]
    # visual_style['edge_math_mode'] = False
    # visual_style['edge_rgb'] = True
    visual_style['edge_not_in_bg'] = True

    # general options
    # ---------------
    visual_style['layout'] = {'e': (0.24905178, -0.0713952),
                              'g': (0.1208607, -0.6029225),
                              'c': (0.10903764, -0.28264217),
                              'a': (-0.2249151 ,  0.37137553),
                              'd': (0.40078133, -0.29063567),
                              'b': (-0.5414963,  1.),
                              'f': (-0.11332007, -0.12377998)}

    visual_style['units'] = 'mm'#('mm','mm')
    visual_style["autocurve"] = True
    visual_style["bbox"] = (100, 55)
    visual_style["margin"] = {'top':.5,'bottom':.5,'left':.5,'right':.5}

    # vs = {}
    # vs["vertex_size"] = .5
    #plot(net,'./xxx/test',type='pdf',**visual_style)
    plot(net,**visual_style)
    #plot(net,'test.tex',**visual_style)
    #plot(net)
    #plot(net,'net.csv',**visual_style)
    #plot(net,'net',type='csv',**visual_style)
    #plot(net,('nodes','edges'),**visual_style)
    #plot(net,'test',type='pdf',**visual_style)
    pass

def test_plot_networkx(netx,color_dict):
    visual_style = {}
    visual_style["vertex_id"] = nx.get_node_attributes(netx,'name')
    visual_style["vertex_size"] = 20
    visual_style["vertex_color"] = {n:color_dict[g] for n,g in nx.get_node_attributes(netx,'gender').items()}
    visual_style["edge_color"] = 'red'

    visual_style["autocurve"] = True

    visual_style['layout'] = nx.spring_layout(netx)
    #print(visual_style)
    # for e in netx.edges(data=True):
    #     print(e)

    # for n in netx.nodes(data=True):
    #     print(n)
    # age = nx.get_node_attributes(netx,'age')
    # print(age)
    #plot(netx,**visual_style)
    pass

def test_plot_igraph(neti,color_dict):
    visual_style = {}
    visual_style["vertex_id"] = neti.vs["name"]
    visual_style["vertex_size"] = 20
    visual_style["node_color"] = [color_dict[gender] for gender in neti.vs["gender"]]

    visual_style["link_color"] = 'red'

    visual_style["autocurve"] = True

    visual_style['layout'] = neti.layout('kk')
    #print(list(neti.layout('kk')))
    #print(visual_style)

    # for e in neti.es:
    #     print(e)
    # for n in neti.vs:
    #     print(n)

    # visual_style = {}
    # visual_style["vertex_id"] = neti.vs["name"]
    #plot(neti,**visual_style)
    pass

def test_plot_list(netl):
    #plot(netl)
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