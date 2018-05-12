#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network2tikz.py 
# Creation  : 08 May 2018
# Time-stamp: <Sam 2018-05-12 15:05 juergen>
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
from collections import OrderedDict

from cnet import logger
from cnet.utils.exceptions import CnetError

log = logger(__name__)

def plot(network, filename=None,**kwds):
    """Plots the network as a tikz-network."""
    drawer = TikzNetworkDrawer(network,filename=filename,**kwds)
    # drawer.draw(**kwds)
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
        self.filename = filename
        self.digit = 3
        # check type of network
        if 'cnet' in str(type(network)):
            log.debug('The network is of type "cnet".')
            self.edges = network.edge_to_nodes_map()
            self.nodes = list(network.nodes)
            self.directed = network.directed
            if self.directed:
                kwds['edge_directed'] = True
            if kwds.get("layout", None) is not None:
                self.layout = self.format_node_value(kwds['layout'])

        elif 'networkx' in str(type(network)):
            log.debug('The network is of type "networkx".')
            self.edges = {e:e for e in network.edges()}
            self.nodes = list(network.nodes())
            self.directed = network.is_directed()
            if self.directed:
                kwds['edge_directed'] = True

            if kwds.get("layout", None) is not None:
                self.layout = self.format_node_value(kwds['layout'])


        elif 'igraph' in str(type(network)):
            log.debug('The network is of type "igraph".')
            self.edges = {i:network.es[i].tuple for i in range(len(network.es))}
            self.nodes = list(range(len(network.vs)))
            self.directed = network.is_directed()
            if self.directed:
                kwds['edge_directed'] = True

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

        self.draw(**kwds)
        
    def draw(self,**kwds):
        # format attributes
        self.format_attributes(**kwds)

        # configure the layout
        if self.layout is None:
            log.warn('No layout was assigned!')

        margins = self.general_attributes.get('margins',None)
        canvas = self.general_attributes.get('canvas',(6,6))
        self.layout = self.fit_layout(self.layout,canvas,margins)

        # assign layout to the nodes
        self.node_attributes['layout'] = self.layout

        # bend the edges if enabled
        self.edge_attributes['edge_curved'] = self.curve()

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

        latex_header = '\\documentclass{standalone}\n' + \
                        '\\usepackage{tikz-network}\n' + \
                        '\\begin{document}\n' + \
                        '\\begin{tikzpicture}\n'

        latex_canvas = '\\clip (0,0) rectangle ({},{});'.format(canvas[0],canvas[1])
        latex_margins = '\\fill[orange!20] ({},{}) rectangle ({},{});'\
                        ''.format(margins['left'],margins['bottom'],
                                  canvas[0] - margins['right'],
                                  canvas[1] - margins['top'])
        latex_footer = '\\end{tikzpicture}\n\\end{document}'
        with open(self.filename,'w') as f:
            f.write(latex_header)
            f.write(latex_canvas)
            f.write(latex_margins)
            for node in node_drawers:
                f.write(node.draw())
            for edge in edge_drawers:
                f.write(edge.draw())


            f.write(latex_footer)
        # draw nodes
            # node.head()
            # node.draw(mode='csv')
            # break

        # for edge in edge_drawers:
        #     print(edge.draw())
        pass

    def curve(self):
        if 'edge_curved' in self.edge_attributes:
            _curved = {}
            for key,value in self.edge_attributes['edge_curved'].items():
                curved = value

                if curved == 0:
                    _curved[key] = 0
                else:
                    v1 = np.array([0,0])
                    v2 = np.array([1,1])
                    v3 = np.array([(2*v1[0]+v2[0]) / 3.0 - curved * 0.5 * (v2[1]-v1[1]),
                                   (2*v1[1]+v2[1]) / 3.0 + curved * 0.5 * (v2[0]-v1[0])
                    ])
                    vec1 = v2-v1
                    vec2 = v3 -v1
                    angle = np.rad2deg(np.arccos(np.dot(vec1,vec2) / np.sqrt((vec1*vec1).sum()) / np.sqrt((vec2*vec2).sum())))
                    _curved[key] = np.round(np.sign(curved) * angle * -1,self.digit)
        return _curved

    @staticmethod
    def fit_layout(layout,canvas, margins=None, keep_aspect_ratio=False):

        # get canvas size
        _width = canvas[0]
        _height = canvas[1]

        # convert margins in the right format
        if margins is None:
            _margins = {'top':0,'left':0,'bottom':0,'right':0}
        elif isinstance(margins,int) or isinstance(margins,float):
            _margins = {'top':margins, 'left':margins, 'bottom':margins,
                        'right':margins}
        elif isinstance(margins,dict):
            _margins = {'top':margins.get('top',0),
                        'left':margins.get('left',0),
                        'bottom':margins.get('bottom',0),
                        'right':margins.get('right',0)}
        else:
            log.error('Margins are not proper defined!')
            raise CnetError

        # check size of the margins
        if _margins['top'] + _margins['bottom'] >= _height or \
           _margins['left'] + _margins['right'] >= _width:
            log.error('Margins are larger than the canvas size!')
            raise CnetError

        # find min and max values of the points
        min_x = min(layout.items(),key = lambda item: item[1][0])[1][0]
        max_x = max(layout.items(),key = lambda item: item[1][0])[1][0]
        min_y = min(layout.items(),key = lambda item: item[1][1])[1][1]
        max_y = max(layout.items(),key = lambda item: item[1][1])[1][1]

        # calculate the scaling ratio
        ratio_x = (_width-_margins['left']-_margins['right']) / (max_x-min_x)
        ratio_y = (_height-_margins['top']-_margins['bottom']) / (max_y-min_y)

        if keep_aspect_ratio:
            scaling = (min(ratio_x,ratio_y),min(ratio_x,ratio_y))
        else:
            scaling = (ratio_x,ratio_y)

        # apply scaling to the points
        _layout = {}
        for n,(x,y) in layout.items():
            _x = (x)*scaling[0]
            _y = (y)*scaling[1]
            _layout[n] = (_x,_y)

        # find min and max values of new the points
        min_x = min(_layout.items(),key = lambda item: item[1][0])[1][0]
        max_x = max(_layout.items(),key = lambda item: item[1][0])[1][0]
        min_y = min(_layout.items(),key = lambda item: item[1][1])[1][1]
        max_y = max(_layout.items(),key = lambda item: item[1][1])[1][1]

        # calculate the translation
        translation = (((_width-_margins['left']-_margins['right'])/2 \
                        +_margins['left']) - ((max_x-min_x)/2 + min_x),
                       ((_height-_margins['top']-_margins['bottom'])/2 \
                        + _margins['bottom'])- ((max_y-min_y)/2 + min_y))

        # apply translation to the points
        for n,(x,y) in _layout.items():
            _x = (x)+translation[0]
            _y = (y)+translation[1]
            _layout[n] = (_x,_y)

        return _layout

    def rename_attributes(self,**kwds):
        names = {'node_':['vertex_','v_','n_'],
                 'edge_':['edge_','link_','l_','e_'],
                 'margins':['margin'],
                 'canvas':['bbox','figure_size']
        }
        _kwds = {}
        del_keys = []
        for key,value in kwds.items():
            for attr,name_list in names.items():
                for name in name_list:
                    if name in key and name[0] == key[0]:
                        _kwds[key.replace(name,attr)] = value
                        del_keys.append(key)
                        break
        # remove the replaced keys from the dict
        for key in del_keys:
            del kwds[key]

        return {**_kwds, **kwds}
    
    def format_attributes(self,**kwds):

        kwds = self.rename_attributes(**kwds)
        self.node_attributes = {}
        self.edge_attributes = {}
        self.general_attributes = {}
        # go through all attributes and assign them to nodes, edges or general
        _flag = True
        for key,value in kwds.items():
            if 'node_' in key:
                self.node_attributes[key] = self.format_node_value(value)
            elif 'edge_' in key:
                self.edge_attributes[key] = self.format_edge_value(value)
            else:
                self.general_attributes[key] = value
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
        self.digits = 3
        self.attributes = attr
        # all options from the tikz-network library
        self.tikz_kwds =  OrderedDict()
        self.tikz_kwds["edge_width"] = 'lw'
        self.tikz_kwds["edge_color"] = 'color'
        self.tikz_kwds["edge_opacity"] = 'opacity'
        self.tikz_kwds["edge_curved"] = 'bend'
        self.tikz_kwds["edge_label"] = 'label'
        self.tikz_kwds["edge_label_position"] = 'position'
        self.tikz_kwds["edge_label_distance"] = 'distance'
        self.tikz_kwds["edge_label_color"] = 'fontcolor'
        self.tikz_kwds["edge_label_size"] = 'fontscale'
        self.tikz_kwds["edge_style"] = 'style'
        # self.tikz_kwds["edge_arrow_size"] = 'length'
        # self.tikz_kwds["edge_arrow_width"] = 'width'
        # self.tikz_kwds["edge_path"] = 'path'
        self.tikz_kwds["edge_loop_size"] = 'loopsize'
        self.tikz_kwds["edge_loop_position"] = 'loopposition'
        self.tikz_kwds["edge_loop_shape"] = 'loopshape'

        self.tikz_args = OrderedDict()
        self.tikz_args['edge_directed'] = 'Direct'
        self.tikz_args['edge_math_mode'] = 'Math'
        self.tikz_args['edge_rgb'] = 'RGB'
        self.tikz_args['edge_not_in_bg'] = 'NotInBG'

        pass

    def draw(self,mode='tex'):
        if mode == 'tex':
            string = '\\Edge['

            for k in self.tikz_kwds:
                if k in self.attributes and \
                   self.attributes.get(k,None) is not None:
                    string += ',{}={}'.format(self.tikz_kwds[k],
                                              self.attributes[k])
            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k] == True:
                        string += ',{}'.format(self.tikz_args[k])

            string += ']({})({})\n'.format(self.u,self.v)

        elif mode == 'csv':
            string = '{},{}'.format(self.u,self.v)

            for k in self.tikz_kwds:
                if k in self.attributes:
                    string += ',{}'.format(self.attributes[k])

            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k] == True:
                        string += ',true'
                    else:
                        string += ',false'

            string += '\n'

        return string

    

class TikzNodeDrawer(object):
    """Class which handles the drawing of the nodes"""
    def __init__(self,id,**attr):
        self.id = id
        self.x = attr.get('layout',(0,0))[0]
        self.y = attr.get('layout',(0,0))[1]
        self.attributes = attr
        self.digits = 3
        # all options from the tikz-network library
        self.tikz_kwds = OrderedDict()
        self.tikz_kwds['node_size'] = 'size'
        self.tikz_kwds['node_color'] = 'color'
        self.tikz_kwds['node_opacity'] = 'opacity'
        self.tikz_kwds['node_label'] = 'label'
        self.tikz_kwds['node_label_position'] = 'position'
        self.tikz_kwds['node_label_distance'] = 'distance'
        self.tikz_kwds['node_label_color'] = 'fontcolor'
        self.tikz_kwds['node_label_size'] = 'fontscale'
        self.tikz_kwds['node_shape'] = 'shape'
        self.tikz_kwds['node_style'] = 'style'
        self.tikz_kwds['node_layer'] = 'layer'

        self.tikz_args = OrderedDict()
        self.tikz_args['node_label_off'] = 'NoLabel'
        self.tikz_args['node_label_as_id'] = 'IdAsLabel'
        self.tikz_args['node_math_mode'] = 'Math'
        self.tikz_args['node_rgb'] = 'RGB'
        self.tikz_args['node_pseudo'] = 'Pseudo'

    def draw(self,mode='tex'):
        if mode == 'tex':
            string = '\\Vertex[x={x:.{n}f},y={y:.{n}f}'\
                     ''.format(x=self.x,y=self.y,n=self.digits)

            for k in self.tikz_kwds:
                if k in self.attributes and \
                   self.attributes.get(k,None) is not None:
                    string += ',{}={}'.format(self.tikz_kwds[k],
                                              self.attributes[k])
            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k] == True:
                        string += ',{}'.format(self.tikz_args[k])

            string += ']{{{}}}\n'.format(self.id)

        elif mode == 'csv':
            string = '{id},{x:.{n}f},{y:.{n}f}'\
                     ''.format(id=self.id,x=self.x,y=self.y,n=self.digits)

            for k in self.tikz_kwds:
                if k in self.attributes:
                    string += ',{}'.format(self.attributes[k])

            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k] == True:
                        string += ',true'
                    else:
                        string += ',false'

            string += '\n'

        return string

    def head(self):
        string = 'id,x,y'
        for k in self.tikz_kwds:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_kwds[k])
        for k in self.tikz_args:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_args[k])

        return string
        
# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
