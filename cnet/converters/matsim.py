#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : matsim.py -- Convert matsim data to various other formats
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-15
# Time-stamp: <Fre 2018-10-12 08:25 juergen>
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
import csv
from xml.dom.minidom import parse, parseString
from itertools import groupby
from collections import defaultdict
import numpy as np


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
        prefix_n, prefix_e = self._check_prefix(prefix)

        # check the input file name
        self._check_filename(filename)

        # check if file is compressed or not
        if self.filename is None:
            return None
        elif self.filename.endswith('.gz'):
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

    def paths(self, filename=None, network=None, prefix='', zfill=0,
              public_transport=False, start_time=None, end_time=None,
              edge_map=None):
        """Converting raw MATSim paths to cnet paths.

        """
        # initialize variables
        paths = []
        P = cn.Paths()
        # if network:
        #     n2e = network.nodes_to_edges_map()

        if start_time is None:
            start_time = 0
        if end_time is None:
            end_time = float('inf')

        # check prefix
        prefix_n, prefix_e = self._check_prefix(prefix)

        # check the input file name
        self._check_filename(filename)

        # check file
        if self.filename is None:
            return None
        elif not self.filename.endswith('.csv'):
            log.warn('The file must be in a ".csv" format.'
                     'Please use correct file format. No output was created!')
            return None

        # load file and go through all lines
        with open(self.filename) as f:
            reader = csv.reader(f)
            headers = next(reader, None)  # extract the headers

            # get column number for agent ids and link ids
            # TODO: find a more elegant method to do this
            agent_id = headers.index('agentId')
            link_id = headers.index('linkId')
            event_id = headers.index('eventType')
            activity_id = headers.index('actType')
            t_id = headers.index('t')

            # initialize the local variables
            person_id = None
            data = []

            # iterate over the list
            for last_row, row in self._is_last_row(reader):
                # if disabled ignore public transport
                if not public_transport:
                    if row[agent_id][:3].isalpha():
                        continue

                # identify to which person the path is assigned to
                if person_id is None:
                    person_id = row[agent_id]

                # add data to the person
                if person_id == row[agent_id]:
                    data.append({
                        'link': str(row[link_id]),
                        'event': str(row[event_id]),
                        'time': float(row[t_id])
                    })

                # if a new person_id is detected the data is stored as a path
                if person_id != row[agent_id] or last_row:

                    # split the path if an action is performed in between
                    paths = self._split_paths(data)

                    for path in paths:
                        times = []
                        edges = []
                        _considered = False

                        # consider paths which have a node within the time
                        # intervall
                        for e in path:
                            if start_time <= e['start_time'] <= end_time or \
                               start_time <= e['end_time'] <= end_time:
                                _considered = True
                        if _considered:
                            for e in path:
                                times.append(e['start_time'])
                                times.append(e['end_time'])
                                edges.append(e['link'])

                        # # consider only sub-paths within the time intervall
                        # for e in path:
                        #     if e['start_time'] >= start_time and \
                        #        e['end_time'] <= end_time:
                        #         times.append(e['start_time'])
                        #         times.append(e['end_time'])
                        #         edges.append(e['link'])

                        if len(times) > 2:
                            t0 = times[0]
                            del times[0]
                            del times[1::2]
                            time = [t0] + times

                        if edges:
                            p = cn.Path(agent_id=person_id,
                                        time=times[-1]-times[0],
                                        times=times)

                            if edge_map:
                                nodes = [edge_map[e] for e in edges]
                                nodes = self.remove_duplicates(nodes)
                                if len(nodes) > 1:
                                    for i in range(len(nodes)-1):
                                        e = network.edges[(nodes[i],
                                                           nodes[i+1])]
                                        p.add_edge(e)
                            else:
                                raise NotImplementedError

                            if len(p) > 0:
                                P.add_path(p)

                    # reset the local variables
                    data = []
                    person_id = row[agent_id]

        return P

    @staticmethod
    def remove_duplicates(sequence):
        lst = [sequence[0]]
        for i in range(1, len(sequence)):
            if lst[-1] != sequence[i]:
                lst.append(sequence[i])
        return lst

    def _split_paths(self, data):
        """ Split the parts according to the trips taken."""
        temp_path = []
        for i in range(1, len(data)):
            if (data[i-1]['event'] == "actend"
                    or data[i-1]['event'] == "vehicle enters traffic") \
                    and data[i]['event'] == "left link":
                temp_path.append(data[i-1])
                temp_path.append(data[i])
            elif data[i]['event'] == "left link" \
                    or data[i]['event'] == "entered link":
                temp_path.append(data[i])
            elif data[i-1]['event'] == "entered link" \
                and (data[i]['event'] == "actstart"
                     or data[i]['event'] == "vehicle leaves traffic"):
                temp_path.append(data[i])
                temp_path.append(None)
        temp_paths = [list(group) for k, group in groupby(
            temp_path, lambda x: x == None) if not k]

        paths_dict = []
        # paths_list = []
        for p in temp_paths:
            path_dict = []
            # path_list = []
            for i, n in enumerate(p):
                if i == 0:
                    continue
                if (not p[i-1]['event'] == 'left link' and
                        not p[i]['event'] == 'entered link'):

                    node = n.copy()
                    del node['time']
                    del node['event']
                    node['start_time'] = p[i-1]['time']
                    node['end_time'] = p[i]['time']
                    path_dict.append(node)
                    # path_list.append(node['link'])

            paths_dict.append(path_dict)
            # paths_list.append(path_list)

        return paths_dict  # paths_list,paths_dict

    @staticmethod
    def _simplify(network, prefix='', zfill=0):

        # check prefix
        if isinstance(prefix, tuple):
            prefix_n = prefix[0]
            prefix_e = prefix[1]
        else:
            prefix_n = prefix
            prefix_e = prefix

        edge_map = {}

        e2n = network.edge_to_nodes_map()

        edges = defaultdict(list)

        l = list(network.edges)
        for e in l:
            v = e.split('_')
            edges[v[0]].append(int(v[1]))

        for i, e in edges.items():
            e_u = str(i) + '_' + str(min(e))
            e_w = str(i) + '_' + str(max(e))
            u = e2n[e_u][0]
            w = e2n[e_w][1]
            m = np.median(e)

            for j in e:
                e_v = str(i) + '_' + str(j)
                if j <= m:
                    edge_map[e_v] = prefix_n + str(u).zfill(zfill)
                else:
                    edge_map[e_v] = prefix_n + str(w).zfill(zfill)

        return edge_map

    @staticmethod
    def _check_prefix(prefix):
        if isinstance(prefix, tuple):
            return prefix[0], prefix[1]
        else:
            return prefix, prefix

    def _check_filename(self, filename):
        if self.filename is None and filename is None:
            log.warn('No file name was defined,'
                     'hence, no output was created!')
            return None
        elif filename is not None:
            self.filename = filename

    @staticmethod
    def _is_last_row(itr):
        old = next(itr)
        for new in itr:
            yield False, old
            old = new
        yield True, old

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
