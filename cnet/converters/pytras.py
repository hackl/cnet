#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : pytras.py -- Converts pytras data to various other formats
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-10-11
# Time-stamp: <Don 2018-10-11 15:07 juergen>
#
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
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================

# NOTE: Finally the pytras module should be included in the cnet package!
import pickle
import cnet as cn
from cnet import logger

log = logger(__name__)


class PytrasConverter(object):
    """A class to convert pytras data [1]_ to various other formats.

    Parameters
    ----------

    References
    ----------
    .. [1] https://github.com/hackl/pytras

    """

    def __init__(self):
        pass

    def network(self, filename, node_map=None, edge_map=None, name='pytras', prefix='', zfill=0):
        """Generate a cnet network from tntp file.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.shp' format.

        edge_map: dictionary, optional (default = None)
            Dictionary wich maps two node ids to an edge id

        node_map: dictionary, optional (default = None)
            Dictionary wich maps x and y coordinates to a node id

        name : string, optional (default = 'pytras')
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

        # load file content
        # TODO: check file
        if filename is not None:
            if filename.endswith('.pkl'):
                content = pickle.load(open(filename, "rb"))

        # check prefix
        if isinstance(prefix, tuple):
            prefix_n = prefix[0]
            prefix_e = prefix[1]
        else:
            prefix_n = prefix
            prefix_e = prefix

        nodes = {}

        if node_map is not None:
            nodes = node_map

        for i, line in enumerate(content):
            p1 = line[0]
            p2 = line[1]

            j = len(nodes)+1
            if not p1 in nodes:
                nodes[p1] = prefix_n + str(j).zfill(zfill)

            j = len(nodes)+1
            if not p2 in nodes:
                nodes[p2] = prefix_n + str(j).zfill(zfill)

            u = nodes[p1]
            v = nodes[p2]
            e = line[2]

            # TODO: Make labeling more dynamical
            # TODO: Add default values for all attributes
            if edge_map is None:
                id = prefix_e + e.get('name', str(i)).zfill(zfill)
            else:
                id = edge_map[(u, v)]
            c = e.get('capacity')
            l = e.get('length')/1000
            sl = e.get('speedlimit')
            a = e.get('alpha', 0.15)
            b = e.get('beta', 4.0)
            ow = e.get('oneway', 1)
            ty = e.get('type', 'Road')
            fft = e.get('t_0', 0)

            edge = cn.RoadEdge(id, u, v, p1=p1, p2=p2, capacity=c, length=l,
                               free_flow_speed=sl, alpha=a, beta=b,
                               speed_limit=sl, oneway=ow, type=ty)
            edge.cost = e.get('t_k', 0)
            edge.volume = e.get('flow', 0)
            network.add_edge(edge)

        return network

    def paths(self, filename=None, network=None):
        """Converting raw pytras paths to cnet paths.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.pkl' format.

        network : :py:class:`RoadNetwork` (default = None)
            Underlying road network of the paths.

        Returns
        -------

        """
        # initialize variables
        P = cn.Paths()
        # load file content
        # TODO: check file
        if filename is not None:
            if filename.endswith('.pkl'):
                content = pickle.load(open(filename, "rb"))

        # initialze maps from the network
        n2e = network.nodes_to_edges_map()
        # TODO: add this mapping function to the spatial network class
        c2n = {(u.x, u.y): u.id for u in network.nodes()}

        # TODO: check content
        for line in content:
            p = cn.Path(flow=line.get('flow'), cost=line.get('cost'),
                        fft=line.get('fft'), weight=line.get('weight'))

            path = line.get('path')
            for i in range(len(path)-1):
                e_id = n2e[(c2n[path[i]], c2n[path[i+1]])][0]
                p.add_edge(network.edges[e_id])

            P.add_path(p)

        return P
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
