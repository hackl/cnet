#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network2tikz.py 
# Creation  : 08 May 2018
# Time-stamp: <Die 2018-05-08 16:00 juergen>
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

from cnet import logger

log = logger(__name__)

def plot(network, filename=None,**kwds):
    """Plots the network as a tikz-network."""
    drawer = TikzNetworkDrawer(network,filename=filename,**kwds)
    pass

class TikzNetworkDrawer(object):
    """Class which handles the drawing of the network"""
    def __init__(self,network,filename=None,**kwds):

        # initialize variables
        # dict of edges and list of nodes to be printed
        self.edges = None
        self.nodes = None

        # check type of network
        if 'cnet' in str(type(network)):
            log.debug('The network is of type "cnet".')
            self.edges = network.edge_to_nodes_map()
            self.nodes = list(network.nodes)

        elif 'networkx' in str(type(network)):
            log.debug('The network is of type "networkx".')

        elif 'igraph' in str(type(network)):
            log.debug('The network is of type "igraph".')

        elif 'pathpy' in str(type(network)):
            log.debug('The network is of type "pathpy".')

        elif isinstance(network,tuple):
            log.debug('The network is of type "list".')
        else:
            log.error('Type of the network could not be determined.'
                      ' Currently only "cnet", "networkx","igraph", "pathpy"'
                      ' and "node/edge list" is supported!')

        # try:
        #     isinstance(net,Network)
        # get list of nodes and edges from the network

        # get attributes
        pass

class TikzEdgeDrawer(object):
    """Class which handles the drawing of the edges"""
    def __init__(self,id,u,v,**attr):
        self.id
        self.u
        self.v
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
