#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : gis.py -- Convert gis data to various other formats
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-10-10
# Time-stamp: <Fre 2018-10-12 16:53 juergen>
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
#
# =============================================================================

import fiona
import numpy as np
#from shapely.geometry import shape, mapping

from collections import defaultdict
import cnet as cn
from cnet import logger

log = logger(__name__)


class SHPConverter(object):
    """A class to convert Shapefiles [1]_ to various other formats.

    Parameters
    ----------
    filename : file or string, optional (default = None)
        File or filename to load. The file must be in a '.shp' format.

    References
    ----------
    .. [1] https://de.wikipedia.org/wiki/Shapefile

    """

    def __init__(self, filename=None):
        self.filename = filename

    def network(self, filename=None, name='gis', prefix='', zfill=0):
        """Generate a cnet network from tntp file.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.shp' format.

        name : string, optional (default = 'gis')
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
        content = self._load_file(filename)

        # end function if no file was loaded
        if content is None:
            return None

        # check prefix
        if isinstance(prefix, tuple):
            prefix_n = prefix[0]
            prefix_e = prefix[1]
        else:
            prefix_n = prefix
            prefix_e = prefix

        nodes = {}

        for i, line in enumerate(content):
            _p1 = line['geometry']['coordinates'][0]
            _p2 = line['geometry']['coordinates'][-1]

            p1 = (round(_p1[0], 2), round(_p1[1], 2))
            p2 = (round(_p2[0], 2), round(_p2[1], 2))
            j = len(nodes)+1
            if not p1 in nodes:
                nodes[p1] = prefix_n + str(j).zfill(zfill)

            j = len(nodes)+1
            if not p2 in nodes:
                nodes[p2] = prefix_n + str(j).zfill(zfill)

            u = nodes[p1]
            v = nodes[p2]
            e = line['properties']

            # TODO: Make labeling more dynamical
            # TODO: Add default values for all attributes
            id = prefix_e + str(e.get('name', i)).zfill(zfill)
            c = e.get('capacity')
            l = e.get('length')
            sl = e.get('speedlimit')
            a = e.get('alpha', 0.15)
            b = e.get('beta', 4.0)
            ow = e.get('oneway')
            ty = e.get('type')

            edge = cn.RoadEdge(id, u, v, p1=p1, p2=p2, capacity=c, length=l,
                               free_flow_speed=sl, alpha=a, beta=b,
                               speed_limit=sl, oneway=ow, type=ty)
            network.add_edge(edge)

        return network

    def centroids(self, filename=None, network=None):
        """Assign the zone centroids to the nearest node in the network.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.shp' format.

        network : :py:class:`RoadNetwork` (default = None)
            Road network where the centroids should be added.

        Returns
        -------
        centroids : dictionary
            Returns a dictionary with the centroide name and the node id.

        """
        # load file content
        content = self._load_file(filename)

        # end function if no file was loaded
        if content is None:
            return None

        centroids = {}
        for line in content:
            p = line['geometry']['coordinates']
            n = line['properties']['name']
            centroids[p] = n

        node_map = network.nodes['coordinate']
        nodes = {v: k for k, v in node_map.items()}

        centroids_to_nodes = {}
        for p, n in centroids.items():
            c = self.closest_node(p, list(nodes))
            centroids_to_nodes[n] = nodes[c]

        return centroids_to_nodes

    def _load_file(self, filename):
        """Function to check and lode the input file."""
        # check the input file name
        if self.filename is None and filename is None:
            log.warn('No file name was defined,'
                     'hence, no output was created!')
            return None
        elif filename is not None:
            self.filename = filename

        # load the file if the ending is correct
        if self.filename.endswith('.shp'):
            content = []
            with fiona.open(filename) as f:
                for feature in f:
                    content.append(feature)
                return content
        else:
            log.warn('The file must be in a ".shp" format.'
                     'Please use correct file format. No output was created!')
            return None

    def trips(self, filename=None, centroids=None, delimiter=','):
        """Converts od trips to a dictionary format.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.csv' format.

        centroids : dictionary (default = None)
            A dictionary wich mapps the centroide id and the node id.

        Returns
        -------
        trips : defaultdict
            Returns the od trips as a dictionary of dictionaries, where the
            first key defines the origin node of the flow, and the second key
            the destination node, the value is the traffic flow between origin
            and destination in vehicles per time unit.

        """
        # initialize variables
        trips = defaultdict(dict)

        # TODO: add checks for the filename
        # load the file if the ending is correct
        if filename.endswith('.csv'):
            od_matrix = np.genfromtxt(filename, delimiter=delimiter)

        for i in range(od_matrix.shape[0]):
            for j in range(od_matrix.shape[1]):
                trips[centroids[i]][centroids[j]] = od_matrix[i][j]

        return trips

    @staticmethod
    def closest_node(node, nodes):
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_2 = np.einsum('ij,ij->i', deltas, deltas)
        return tuple(nodes[np.argmin(dist_2)])

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
