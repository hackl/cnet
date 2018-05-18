#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network2tikz.py 
# Creation  : 08 May 2018
# Time-stamp: <Fre 2018-05-18 16:26 juergen>
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

import os
import subprocess
import errno
import numpy as np
from collections import OrderedDict
import webbrowser

from cnet import logger
from cnet.utils.exceptions import CnetError

log = logger(__name__)


DIGITS = 3
CANVAS = (6,6)


def plot(network, filename=None,type=None,**kwds):
    """Plots the network as a tikz-network."""

    result = Plot(network,**kwds)

    if filename is None:
        filename = 'default_network'
    if isinstance(filename,tuple) or isinstance(filename,list) or \
         filename.endswith('.csv') or type == 'csv' or \
         filename.endswith('.dat') or type == 'dat':
        log.debug('Create csv files')
        result.save_csv(filename)
    elif filename == 'default_network' and type is None:
        log.debug('Show the network')
        result.show(filename)
    elif filename.endswith('.tex') or type == 'tex':
        log.debug('Create tex file')
        standalone = kwds.get('standalone',True)
        result.save_tex(filename,standalone=standalone)
    elif filename.endswith('.pdf') or type == 'pdf':
        log.debug('Create pdf plot')
        result.save_pdf(filename)
    else:
        log.warn('No valid output option was chosen!')

class Plot(object):
    """Default class to create plots"""
    def __init__(self,network,**kwds):
        self.drawer = TikzNetworkDrawer(network,**kwds)

    def save_tex(self,filename,standalone=True):
        latex_header = '\\documentclass{standalone}\n' + \
                        '\\usepackage{tikz-network}\n' + \
                        '\\begin{document}\n'
        latex_begin_tikz = '\\begin{tikzpicture}\n'
        latex_end_tikz = '\\end{tikzpicture}\n'
        latex_footer = '\\end{document}'

        margins = self.drawer.margins
        canvas = self.drawer.canvas
        latex_canvas = '\\clip (0,0) rectangle ({},{});\n'.format(canvas[0],
                                                                  canvas[1])
        # latex_margins = '\\fill[orange!20] ({},{}) rectangle ({},{});\n'\
        #                 ''.format(margins['left'],margins['bottom'],
        #                           canvas[0] - margins['right'],
        #                           canvas[1] - margins['top'])

        with open(filename,'w') as f:
            if standalone:
                f.write(latex_header)
            f.write(latex_begin_tikz)
            f.write(latex_canvas)
            #f.write(latex_margins)

            for node in self.drawer.node_drawer:
                f.write(node.draw())
            for edge in self.drawer.edge_drawer:
                f.write(edge.draw())

            f.write(latex_end_tikz)
            if standalone:
                f.write(latex_footer)

    def save_csv(self,filename):
        # if file name is a string get base name
        if isinstance(filename,str):
            basename = os.path.splitext(os.path.basename(filename))[0]
            basename_n = basename + '_nodes'
            basename_e = basename + '_edges'
        elif isinstance(filename,tuple) or isinstance(filename,list):
            basename_n = os.path.splitext(os.path.basename(filename[0]))[0]
            basename_e = os.path.splitext(os.path.basename(filename[1]))[0]
        else:
            log.error('File name is not correct specified!')
            raise CnetError
        with open(basename_n+'.csv','w') as f:
            f.write(self.drawer.node_drawer[0].head())
            for node in self.drawer.node_drawer:
                f.write(node.draw(mode='csv'))

        with open(basename_e+'.csv','w') as f:
            f.write(self.drawer.edge_drawer[0].head())
            for edge in self.drawer.edge_drawer:
                f.write(edge.draw(mode='csv'))

    def save_pdf(self,filename,clean=True, clean_tex=True,
                 compiler=None, compiler_args=None, silent=True):

        if compiler_args is None:
            compiler_args = []

        # get directories and file name
        current_dir = os.getcwd()
        output_dir = os.path.dirname(filename)
        # check if output dir exists if not use the base dir
        if not os.path.exists(output_dir):
            output_dir = current_dir
        basename = os.path.splitext(os.path.basename(filename))[0]

        # change to output dir
        os.chdir(output_dir)

        # save the tex file
        self.save_tex(basename+'.tex',standalone=True)

        if compiler is not None:
            compilers = ((compiler, []),)
        else:
            latexmk_args = ['--pdf']

            compilers = (
                ('latexmk', latexmk_args),
                ('pdflatex', [])
            )

        main_arguments = ['--interaction=nonstopmode', basename + '.tex']

        os_error = None

        for compiler, arguments in compilers:
            command = [compiler] + arguments + compiler_args + main_arguments

            try:
                output = subprocess.check_output(command,
                                                 stderr=subprocess.STDOUT)
            except (OSError, IOError) as e:
                # Use FileNotFoundError when python 2 is dropped
                os_error = e

                if os_error.errno == errno.ENOENT:
                    # If compiler does not exist, try next in the list
                    continue
                raise
            except subprocess.CalledProcessError as e:
                # For all other errors print the output and raise the error
                print(e.output.decode())
                raise
            else:
                if not silent:
                    print(output.decode())

            if clean:
                try:
                    # Try latexmk cleaning first
                    subprocess.check_output(['latexmk', '-c', basename],
                                            stderr=subprocess.STDOUT)
                except (OSError, IOError, subprocess.CalledProcessError) as e:
                    # Otherwise just remove some file extensions.
                    extensions = ['aux', 'log', 'out', 'fls',
                                  'fdb_latexmk']

                    for ext in extensions:
                        try:
                            os.remove(basename + '.' + ext)
                        except (OSError, IOError) as e:
                            if e.errno != errno.ENOENT:
                                raise
            # remove the tex file
            if clean_tex:
                os.remove(basename + '.tex')
            # Compilation has finished, so no further compilers have to be tried
            break

        else:
            # Notify user that none of the compilers worked.
            log.error('No LaTex compiler was found! Either specify a LaTex '
                      'compiler or make sure you have latexmk or pdfLaTex'
                      ' installed.')
            raise CnetError

        # change back to current dir
        os.chdir(current_dir)


    def show(self,filename):
        # get current directory
        current_dir = os.getcwd()
        # create temp file name
        temp_filename = os.path.join(current_dir,filename)
        # save a pdf file
        self.save_pdf(temp_filename)
        # open the file
        webbrowser.open(r'file:///'+temp_filename+'.pdf')

class TikzNetworkDrawer(object):
    """Class which handles the drawing of the network"""
    def __init__(self,network,**kwds):

        # initialize variables
        # dict of edges and list of nodes to be printed
        self.edges = None
        self.nodes = None
        self.directed = False
        self.digits = DIGITS
        # check type of network
        if 'cnet' in str(type(network)):
            log.debug('The network is of type "cnet".')
            self.edges = network.edge_to_nodes_map()
            self.nodes = list(network.nodes)
            self.directed = network.directed

        elif 'networkx' in str(type(network)):
            log.debug('The network is of type "networkx".')
            self.edges = {e:e for e in network.edges()}
            self.nodes = list(network.nodes())
            self.directed = network.is_directed()

        elif 'igraph' in str(type(network)):
            log.debug('The network is of type "igraph".')
            self.edges = {i:network.es[i].tuple for i in range(len(network.es))}
            self.nodes = list(range(len(network.vs)))
            self.directed = network.is_directed()

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

        # assign attributes to the class
        self.attributes = kwds
        # draw the network in the memory
        self.draw()

    def draw(self):

        # format attributes
        self.format_attributes(**self.attributes)

        # check if network is directed and nothing other is defined
        if self.directed and \
           self.edge_attributes.get('edge_directed',None) is None:
            self.edge_attributes['edge_directed'] = self.format_edge_value(True)

        # get unit converter
        _units = self.general_attributes.get('units',('cm','pt'))
        if isinstance(_units,tuple):
            self.unit2cm = UnitConverter(_units[0],'cm')
            self.unit2pt = UnitConverter(_units[1],'pt')
        else:
            self.unit2cm = UnitConverter(_units,'cm')
            self.unit2pt = UnitConverter(_units,'pt')

        units = (self.unit2cm,self.unit2pt)

        # get layout specifications
        self.margins = self.get_margins()
        if self.general_attributes.get('canvas',None) is not None:
            _canvas = self.general_attributes['canvas']
            self.canvas = (self.unit2cm(_canvas[0]),self.unit2cm(_canvas[1]))
        else:
            self.canvas = CANVAS

        # configure the layout
        # check if a layout is defined
        if self.attributes.get("layout", None) is not None:
            self.layout = self.format_node_value(self.attributes['layout'])
        else:
            log.warn('No layout was assigned! '
                     'Hence a random layout was chosen!')
            self.layout = {}
            for node in self.nodes:
                self.layout[node] = (np.random.rand(),np.random.rand())

        # fit the node position to the chosen canvas
        self.layout = self.fit_layout(self.layout,self.canvas,self.margins)

        # assign layout to the nodes
        self.node_attributes['layout'] = self.layout
        # # assign unit converter to the nodes
        # self.node_attributes['units'] = self.general_attributes['units']

        # bend the edges if enabled
        if self.edge_attributes.get('edge_curved',None) is not None:
            self.edge_attributes['edge_curved'] = self.curve()

        # # assign unit converter to the edges
        # self.edge_attributes['units'] = self.general_attributes['units']

        # initialize vertices
        self.node_drawer = []
        for node in self.nodes:
            _attr = {}
            for key in self.node_attributes:
                _attr[key] = self.node_attributes[key][node]
            self.node_drawer.append(TikzNodeDrawer(node,units,**_attr))

        # initialize edges
        self.edge_drawer = []
        for edge,(u,v) in self.edges.items():
            _attr = {}
            for key in self.edge_attributes:
                _attr[key] = self.edge_attributes[key][edge]
            self.edge_drawer.append(TikzEdgeDrawer(edge,u,v,units,**_attr))

    def get_margins(self):
        margins = self.general_attributes.get('margins',None)
        if margins is None:
            _node_size = self.node_attributes.get('node_size',None)
            if _node_size is not None:
                _margin = self.unit2cm(max(_node_size.values())/2+.05)
            else:
                _margin = 0.35
            _margins = {'top':_margin,'bottom':_margin,'left':_margin,'right':_margin}

        elif isinstance(margins,int) or isinstance(margins,float):
            _m = self.unit2cm(margins)
            _margins = {'top':_m, 'left':_m, 'bottom':_m,'right':_m}

        elif isinstance(margins,dict):
            _margins = {'top':self.unit2cm(margins.get('top',0)),
                        'left':self.unit2cm(margins.get('left',0)),
                        'bottom':self.unit2cm(margins.get('bottom',0)),
                        'right':self.unit2cm(margins.get('right',0))}
        else:
            log.error('Margins are not proper defined!')
            raise CnetError

        return _margins

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
                    _curved[key] = np.round(np.sign(curved) * angle * -1,self.digits)
        return _curved

    @staticmethod
    def fit_layout(layout,canvas, margins=None, keep_aspect_ratio=False):

        # get canvas size
        _width = canvas[0]
        _height = canvas[1]

        # check size of the margins
        if margins['top'] + margins['bottom'] >= _height or \
           margins['left'] + margins['right'] >= _width:
            log.error('Margins are larger than the canvas size!')
            raise CnetError

        # find min and max values of the points
        min_x = min(layout.items(),key = lambda item: item[1][0])[1][0]
        max_x = max(layout.items(),key = lambda item: item[1][0])[1][0]
        min_y = min(layout.items(),key = lambda item: item[1][1])[1][1]
        max_y = max(layout.items(),key = lambda item: item[1][1])[1][1]

        # calculate the scaling ratio
        ratio_x = (_width-margins['left']-margins['right']) / (max_x-min_x)
        ratio_y = (_height-margins['top']-margins['bottom']) / (max_y-min_y)

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
        translation = (((_width-margins['left']-margins['right'])/2 \
                        +margins['left']) - ((max_x-min_x)/2 + min_x),
                       ((_height-margins['top']-margins['bottom'])/2 \
                        + margins['bottom'])- ((max_y-min_y)/2 + min_y))

        # apply translation to the points
        for n,(x,y) in _layout.items():
            _x = (x)+translation[0]
            _y = (y)+translation[1]
            _layout[n] = (_x,_y)

        return _layout

    @staticmethod
    def rename_attributes(**kwds):
        names = {'node_':['vertex_','v_','n_'],
                 'edge_':['edge_','link_','l_','e_'],
                 'margins':['margin'],
                 'canvas':['bbox','figure_size'],
                 'units':['units','unit']
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
           isinstance(value,float) or isinstance(value,bool):
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
    def __init__(self,id,u,v,units,**attr):
        self.id = id
        self.u = u
        self.v = v
        self.digits = DIGITS
        self.attributes = attr
        self.unit2cm = units[0]
        self.unit2pt = units[1]
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

        self.convert_units()


    def convert_units(self):
        for k in ['edge_width']:
            if  k in self.attributes:
                self.attributes[k] = self.unit2pt(self.attributes[k])

        for k in ['edge_loop_size']:
            if  k in self.attributes:
                self.attributes[k] = str(self.unit2cm(self.attributes[k]))+'cm'

        for k in ['edge_label_size']:
            if  k in self.attributes:
                self.attributes[k] = np.round(self.unit2pt(self.attributes[k])/7,self.digits)


    def format_style(self):
        if 'edge_arrow_size' in self.attributes:
            arrow_size = 'length=' + str(15*self.unit2cm(self.attributes['edge_arrow_size']))+'cm,'
        else:
            arrow_size = ''

        if 'edge_arrow_size' in self.attributes:
            arrow_width = 'width=' + str(10*self.unit2cm(self.attributes['edge_arrow_width']))+'cm'
        else:
            arrow_width = ''

        if arrow_size != '' or arrow_width != '':
            self.attributes['edge_style'] = '{{-{{Latex[{}{}]}}, {} }}'.format(arrow_size,arrow_width,self.attributes.get('edge_style',''))
        
    def draw(self,mode='tex'):
        if mode == 'tex':
            self.format_style()
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

        return string + '\n'

    def head(self):
        string = 'u,v'
        for k in self.tikz_kwds:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_kwds[k])
        for k in self.tikz_args:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_args[k])

        return string + '\n'

    

class TikzNodeDrawer(object):
    """Class which handles the drawing of the nodes"""
    def __init__(self,id,units,**attr):
        self.id = id
        self.x = attr.get('layout',(0,0))[0]
        self.y = attr.get('layout',(0,0))[1]
        self.unit2cm = units[0]
        self.unit2pt = units[1]
        self.attributes = attr
        self.digits = DIGITS
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

        self.convert_units()

    def convert_units(self):
        for k in ['node_size','node_label_distance']:
            if  k in self.attributes:
                self.attributes[k] = self.unit2cm(self.attributes[k])

        for k in ['node_label_size']:
            if  k in self.attributes:
                self.attributes[k] = np.round(self.unit2pt(self.attributes[k])/7,self.digits)

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

        return string + '\n'

    def head(self):
        string = 'id,x,y'
        for k in self.tikz_kwds:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_kwds[k])
        for k in self.tikz_args:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_args[k])

        return string + '\n'


class UnitConverter(object):
    def __init__(self, input_unit='px',output_unit='px'):
        self.digits = DIGITS
        self.input_unit = input_unit
        self.output_unit = output_unit

    def __call__(self,value):
        return self.convert(value)
        
    def px_to_mm(self,measure):
        return measure * 0.26458333333719

    def px_to_pt(self,measure):
        return measure * 0.75

    def pt_to_mm(self,measure):
        return measure * 0.352778

    def mm_to_px(self,measure):
        return measure * 3.779527559

    def mm_to_pt(self,measure):
        return measure * 2.83465

    def convert(self,value):
        measure = float(value)
        # to cm
        if self.input_unit == 'mm' and self.output_unit == 'cm':
            value = measure/10
        if self.input_unit == 'pt' and self.output_unit == 'cm':
            value = self.pt_to_mm(measure)/10
        if self.input_unit == 'px' and self.output_unit == 'cm':
            value = self.px_to_mm(measure)/10
        if self.input_unit == 'cm' and self.output_unit == 'cm':
            value = measure
        # to pt
        if self.input_unit == 'px' and self.output_unit == 'pt':
            value = self.px_to_pt(measure)
        if self.input_unit == 'mm' and self.output_unit == 'pt':
            value = self.mm_to_pt(measure)
        if self.input_unit == 'cm' and self.output_unit == 'pt':
            value = self.mm_to_pt(measure)*10
        if self.input_unit == 'pt' and self.output_unit == 'pt':
            value = measure
        # to px
        if self.input_unit == 'mm' and self.output_unit == 'px':
            value = self.mm_to_px(measure)
        if self.input_unit == 'cm' and self.output_unit == 'px':
            value = self.mm_to_px(10*measure)
        if self.input_unit == 'pt' and self.output_unit == 'px':
            value = measure*4/3
        if self.input_unit == 'px' and self.output_unit == 'px':
            value = measure
        # else:
        #     raise NotImplementedError("The units are not supported!")
        return np.round(value,self.digits)





    
# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
