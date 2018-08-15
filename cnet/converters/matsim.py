#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : matsim.py -- Convert matsim data to various other formats
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-15
# Time-stamp: <Mit 2018-08-15 17:00 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
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
import gzip
from xml.dom.minidom import parse, parseString

import cnet as cn
from cnet import logger

log = logger(__name__)

# convert m/s to km/h
# TODO: Find better solution
MS_TO_KMH = 3.6


class MATSimConverter(object):
    """A class to convert MATSim [1]_ results to various other formats.

    Parameters
    ----------
    filename : file or string, optional (default = None)
        File or filename to load. The file must be in a '.tntp' format.

    References
    ----------
    .. [1] http://www.matsim.org/

    """

    def __init__(self, filename=None, *args):
        self.filename = filename

    def network(self, filename=None, name='matsim', prefix='', zfill=0):
        """Generate a cnet network from matsim xml file.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.tntp' format.

        name : string, optional (default = 'matsim')
            Name of the :py:class:`RoadNetwork`

        prefix : string or tuple of string, optional (default = '')
            Adds a string value in front of the node/edge id.

        zfill : integer, optional (default = 0)
            Fills the empty space in front of the node/edge ids with zeros. The
            number indicate the digets filled up, e.g. `zfill = 2` transforms
           '1' to '01'.

        Returns
        -------
        network : :py:class:`RoadNetwork`
            Returns a road network.

        """

        # initialize variables
        network = cn.RoadNetwork(name=name, directed=True)

        # check prefix
        if isinstance(prefix, tuple):
            prefix_n = prefix[0]
            prefix_e = prefix[1]
        else:
            prefix_n = prefix
            prefix_e = prefix

        # check the input file name
        if self.filename is None and filename is None:
            log.warn('No file name was defined,'
                     'hence, no output was created!')
            return None
        elif filename is not None:
            self.filename = filename

        # check if file is compressed or not
        if self.filename.endswith('.gz'):
            f = gzip.open(filename)
            content = parseString(f.read())

        elif self.filename.endswith('.xml'):
            content = parse(filename)

        else:
            log.warn('The file must be in a ".xml" or ".xml.gz" format.'
                     'Please use correct file format. No output was created!')
            return None

        # get nodes
        nodes = content.getElementsByTagName('node')

        # add nodes to the network
        for n in nodes:
            id = prefix_n + n.attributes['id'].value.zfill(zfill)
            x = float(n.attributes['x'].value)
            y = float(n.attributes['y'].value)
            node = cn.RoadNode(id, x=x, y=y)

            network.add_node(node)

        # get edges
        edges = content.getElementsByTagName('link')

        # add edges to the network
        for e in edges:
            id = prefix_e + e.attributes['id'].value.zfill(zfill)
            u = prefix_n + e.attributes['from'].value.zfill(zfill)
            v = prefix_n + e.attributes['to'].value.zfill(zfill)
            c = float(e.attributes['capacity'].value)
            l = float(e.attributes['length'].value)
            ffs = float(e.attributes['freespeed'].value) * MS_TO_KMH
            o = int(e.attributes['oneway'].value)
            p = float(e.attributes['permlanes'].value)

            network.add_edge(id, u, v, capacity=c, length=l,
                             free_flow_speed=ffs, oneway=o,
                             permlanes=p)

        # Check number of nodes
        log.debug('Number of MATSim nodes: \t {}'.format(len(nodes)))
        log.debug('Number of cnet nodes: \t\t {}'.format(
            network.number_of_nodes()))

        # Check number of edges
        log.debug('Number of MATSim edges: \t {}'.format(len(edges)))
        log.debug('Number of cnet edges: \t\t {}'.format(
            network.number_of_edges()))

        return network

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
