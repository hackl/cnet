#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network2tikz.py 
# Creation  : 08 May 2018
# Time-stamp: <Fre 2018-05-11 16:14 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : Module to plot networks as tikz-network
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

import numpy as np

from cnet import logger
from cnet.utils.exceptions import CnetError

log = logger(__name__)

def plot(network, filename=None,**kwds):
    """Plots the network as a tikz-network."""
    drawer = TikzNetworkDrawer(network,filename=filename,**kwds)
    drawer.draw(**kwds)
    # print(drawer.edges)
    # print(drawer.nodes)
    #print(drawer.directed)
    #print(drawer.layout)
    pass

class TikzNetworkDrawer(object):
    """Class which handles the drawing of the network"""
    def __init__(self,network,filename=None,**kwds):

        # initialize variables
        # dict of edges and list of nodes to be printed
        self.edges = None
        self.nodes = None
        self.layout = None
        self.directed = False
        # check type of network
        if 'cnet' in str(type(network)):
            log.debug('The network is of type "cnet".')
            self.edges = network.edge_to_nodes_map()
            self.nodes = list(network.nodes)
            self.directed = network.directed
            if kwds.get("layout", None) is not None:
                self.layout = self.format_node_value(kwds['layout'])

        elif 'networkx' in str(type(network)):
            log.debug('The network is of type "networkx".')
            self.edges = {e:e for e in network.edges()}
            self.nodes = list(network.nodes())
            self.directed = network.is_directed()
            if kwds.get("layout", None) is not None:
                self.layout = self.format_node_value(kwds['layout'])


        elif 'igraph' in str(type(network)):
            log.debug('The network is of type "igraph".')
            self.edges = {i:network.es[i].tuple for i in range(len(network.es))}
            self.nodes = list(range(len(network.vs)))
            self.directed = network.is_directed()
            if kwds.get("layout", None) is not None:
                self.layout = self.format_node_value(list(kwds['layout']))


        elif 'pathpy' in str(type(network)):
            log.debug('The network is of type "pathpy".')

        elif isinstance(network,tuple):
            log.debug('The network is of type "list".')
            self.nodes = network[0]
            self.edges = {e:e for e in network[1]}
        else:
            log.error('Type of the network could not be determined.'
                      ' Currently only "cnet", "networkx","igraph", "pathpy"'
                      ' and "node/edge list" is supported!')


    def draw(self,**kwds):
        # format attributes
        self.format_attributes(**kwds)

        # configure the layout
        if self.layout is None:
            log.warn('No layout was assigned!')

        self.fit_layout((10,8))

        # initialize vertices
        node_drawers = []
        for node in self.nodes:
            _attr = {}
            for key in self.node_attributes:
                _attr[key] = self.node_attributes[key][node]
            node_drawers.append(TikzNodeDrawer(node,**_attr))

        # initialize edges
        edge_drawers = []
        for edge,(u,v) in self.edges.items():
            _attr = {}
            for key in self.edge_attributes:
                _attr[key] = self.edge_attributes[key][edge]
            edge_drawers.append(TikzEdgeDrawer(edge,u,v,**_attr))

        pass

    def fit_layout(self,canvas, keep_aspect_ratio=False):
        print(canvas)

        #print(self.layout)

        _width = canvas[0]
        _height = canvas[1]

        min_x = min(self.layout.items(),key = lambda item: item[1][0])[1][0]
        max_x = max(self.layout.items(),key = lambda item: item[1][0])[1][0]

        min_y = min(self.layout.items(),key = lambda item: item[1][1])[1][1]
        max_y = max(self.layout.items(),key = lambda item: item[1][1])[1][1]

        ratio_x = _width / (max_x-min_x)
        ratio_y = _height / (max_y-min_y)

        if keep_aspect_ratio:
            #scaling =
            #np.array([[min(ratio_x,ratio_y),0],[0,min(ratio_x,ratio_y)]])
            scaling = (min(ratio_x,ratio_y),min(ratio_x,ratio_y))
        else:
            #scaling = np.array([[ratio_x,0],[0,ratio_y]])
            scaling = (ratio_x,ratio_y)

        print(scaling)

        print(min_x)

        print((max_x - min_x) * scaling[0])
        print((max_y - min_y) * scaling[1])
        #print(scaling.dot(np.array(min_x)))
            
        # print(min_x)
        # print(max_x)
        # print(min_y)
        # print(max_y)

        # print(canvas[0]/(max_x[1][0] - min_x[1][0]))
        # print(canvas[1]/(max_y[1][1] - min_y[1][1]))
        
        pass

    def format_attributes(self,**kwds):
        self.node_attributes = {}
        self.edge_attributes = {}
        self.general_attributes = {}
        # go through all attributes and assign them to nodes, edges or general
        _flag = True
        for key,value in kwds.items():
            if _flag:
                for _name in ['vertex_','node_','v_','n_']:
                    if _name in key and _name[0] == key[0]:
                        _v = self.format_node_value(value)
                        self.node_attributes[key.replace(_name,'node_')] = _v
                        _flag = False
                        break
            if _flag:
                for _name in ['edge_','link_','l_','e_']:
                    if _name in key and _name[0] == key[0]:
                        _v = self.format_edge_value(value)
                        self.edge_attributes[key.replace(_name,'edge_')] = _v
                        _flag = False
                        break
            if _flag:
                self.general_attributes[key] = value
            _flag = True

        # print(self.node_attributes)
        # print(self.edge_attributes)
        # print(self.general_attributes)

        # try:
        #     isinstance(net,Network)
        # get list of nodes and edges from the network

        # get attributes
        pass

    def format_node_value(self,value):
        """Returns a dict with node ids and assigned value."""
        # check if value is string, list or dict
        _values = {}
        if isinstance(value,str) or isinstance(value,int) or \
           isinstance(value,float):
            for n in self.nodes:
                _values[n] = value
        elif isinstance(value,list):
            for i,n in enumerate(self.nodes):
                try:
                    _values[n] = value[i]
                except:
                    _values[n] = None
        elif isinstance(value,dict):
            for n in self.nodes:
                try:
                    _values[n] = value[n]
                except:
                    _values[n] = None
        else:
            log.error('Something went wrong!')
            raise CnetError
        return _values

    def format_edge_value(self,value):
        """Returns a dict with edge ids and assigned value."""
        # check if value is string, list or dict
        _values = {}
        if isinstance(value,str) or isinstance(value,int) or \
           isinstance(value,float):
            for n in self.edges:
                _values[n] = value
        elif isinstance(value,list):
            for i,n in enumerate(self.edges):
                try:
                    _values[n] = value[i]
                except:
                    _values[n] = None
        elif isinstance(value,dict):
            for n in self.edges:
                try:
                    _values[n] = value[n]
                except:
                    _values[n] = None
        else:
            log.error('Something went wrong!')
            raise CnetError
        return _values

class TikzEdgeDrawer(object):
    """Class which handles the drawing of the edges"""
    def __init__(self,id,u,v,**attr):
        self.id = id
        self.u = u
        self.v = v
        self.attributes = attr
        # all options from the tikz-network library
        self.tikz_kwds =  [
            'lw', 'color', 'opacity', 'bend', 'label', 'position', 'distance',
            'style', 'fontcolor', 'fontscale', 'length', 'width', 'path',
            'loopsize', 'loopposition', 'loopshape']
        self.tikz_args = ['Direct', 'Math', 'RGB', 'NotInBG']


        pass


class TikzNodeDrawer(object):
    """Class which handles the drawing of the nodes"""
    def __init__(self,id,**attr):
        self.id = id
        self.attributes = attr
        # all options from the tikz-network library
        self.tikz_kwds =  [
            'x', 'y', 'size', 'color', 'opacity', 'label', 'position',
            'distance', 'fontcolor', 'fontscale', 'shape', 'style', 'layer']
        self.tikz_args = ['NoLabel', 'IdAsLabel', 'Math', 'RGB', 'Pseudo']

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
