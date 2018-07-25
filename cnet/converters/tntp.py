#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : tntp.py -- Convert tntp data to various other formats
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-20
# Time-stamp: <Sam 2018-07-21 16:06 juergen>
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

from collections import defaultdict
import cnet as cn
from cnet import logger

log = logger(__name__)


class TNTPConverter(object):
    """A class to convert TNTP [1]_ data to various other formats.

    Parameters
    ----------
    filename : file or string, optional (default = None)
        File or filename to load. The file must be in a '.tntp' format.

    References
    ----------
    .. [1] https://github.com/bstabler/TransportationNetworks

    """

    def __init__(self, filename=None):
        self.filename = filename

    def trips(self, filename=None, prefix='', zfill=0):
        """Converts od trips to a dictionary format.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.tntp' format.

        prefix : string, optional (default = '')
            Adds a string value in front of the node id.

        zfill : integer, optional (default = 0)
            Fills the empty space in front of the node ids with zeros. The
            number indicate the digets filled up, e.g. `zfill = 2` transforms
           '1' to '01'.

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
        zones = 0

        # load file content
        content = self._load_file(filename)

        # end function if no file was loaded
        if content is None:
            return None

        destinations = []
        # iterate through the content and get origin nodes
        for i, line in enumerate(content):

            # If text origin is observed or the end of the document reached,
            # do something.
            if 'Origin' in line or (i+1) == len(content):
                if destinations:
                    destinations = list(
                        filter(None, ''.join(destinations).split(';')))

                # get destination nodes and trips
                # in order to add them to the dict
                for d in destinations:
                    D = prefix+d.split(':')[0].strip(' \t\n\r').zfill(zfill)
                    V = float(d.split(':')[1].strip(' \t\n\r'))
                    trips[O][D] = V

                # check if the end of the file is reached,
                # otherwise go to next origin node
                if (i+1) != len(content):
                    # add new origin node
                    O = prefix+line.split('Origin',
                                          1)[1].split()[0].zfill(zfill)
                    # update temporal variables
                    zones += 1
                    destinations = []

            # add lines to temporal list
            if zones > 0 and 'Origin' not in line:
                destinations.append(line)

        return trips

    def network(self, filename=None, name='tntp', prefix='', zfill=0):
        """Generate a cnet network from tntp file.

        Parameters
        ----------
        filename : file or string, optional (default = None)
            File or filename to load. The file must be in a '.tntp' format.

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

        edges = False

        for i, line in enumerate(content):
            if edges:
                id = prefix_e + str(i-j).zfill(zfill)
                e = line.split('\t')
                u = prefix_n + e[0].zfill(zfill)
                v = prefix_n + e[1].zfill(zfill)
                c = float(e[2])
                l = float(e[3])
                fft = float(e[4])
                ffs = l/fft
                a = float(e[5])
                b = float(e[6])
                sl = float(e[7])
                to = float(e[8])
                ty = float(e[9])

                edge = cn.RoadEdge(id, u, v, p1=(0, 0), p2=(0, 0), capacity=c,
                                   length=l, free_flow_speed=ffs, alpha=a,
                                   beta=b, speed_limit=sl, toll=to, type=ty)
                network.add_edge(edge)
            # set edges to True after reading the header.
            if '~' in line:
                j = i
                edges = True

        return network

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
        if self.filename.endswith('.tntp'):
            # log.debug('Read tntp file.')
            with open(filename, 'r') as f:
                content = f.readlines()
                # remove ' \t\n\r' form the file
                content = [x.strip() for x in content]
                return content
        else:
            log.warn('The file must be in a ".tntp" format.'
                     'Please use correct file format. No output was created!')
            return None

        # =============================================================================
        # eof
        #
        # Local Variables:
        # mode: python
        # mode: linum
        # mode: auto-fill
        # fill-column: 80
        # End:
