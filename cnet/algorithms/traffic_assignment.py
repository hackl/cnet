#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : traffic_assignment.py -- Module for flow based traffic assignment
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-06-25
# Time-stamp: <Die 2018-07-24 10:35 juergen>
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
from copy import deepcopy
from cnet import logger, Path, Paths
from cnet.algorithms.shortest_path import (shortest_path, _shortest_path,
                                           dijkstra)


log = logger(__name__)


def msa_fast(network, od_flow, limit=0.5, max_iter=float('inf'), enable_paths=True):

    _od_flow = {}
    for o, d in od_flow.items():
        _temp = {}
        for k, v in d.items():
            _temp[network.nodes.index(k)] = v
        _od_flow[network.nodes.index(o)] = _temp

    origins = list(_od_flow)
    destinations = list(set(n for k, v in _od_flow.items() for n in v))

    od_paths = defaultdict(dict)

    # create empty dict with edges as keys
    empty = {}

    # create a list with all edges described as pair of nodes
    _edges = []

    # get variables for BPN equation
    # TODO: find a better and faster method
    _fft = {}
    _c = {}
    _a = {}
    _b = {}

    for e, (u, v) in network.edges(nodes=True):
        x = network.nodes.index(u)
        y = network.nodes.index(v)
        _edges.append((x, y))
        empty[(x, y)] = 0
        _fft[(x, y)] = network.edges[e].free_flow_time
        _c[(x, y)] = network.edges[e].capacity
        _a[(x, y)] = network.edges[e].alpha
        _b[(x, y)] = network.edges[e].beta

    volume = deepcopy(empty)
    potential_volume = deepcopy(empty)

    adj = network.adjacency_matrix(weight='weight')

    # initial all-or-nothing assignment
    for o in origins:
        for d in destinations:
            cost, path = _shortest_path(adj, o, d)
            for i in range(len(path)-1):
                potential_volume[(path[i], path[i+1])] += _od_flow[o][d]

    # algorithm
    volume = deepcopy(potential_volume)
    potential_volume = deepcopy(empty)
    temp_volume = deepcopy(empty)
    n = 1

    if enable_paths:
        temp_path_list = []

    while calculate_limit(volume, temp_volume) > limit:
        n += 1

        # update adjacency matrix
        for (u, v), w in volume.items():
            adj[u, v] = _fft[(u, v)] * (1 + _a[(u, v)] *
                                        (w/_c[(u, v)]) ** _b[(u, v)])
        temp_volume = deepcopy(volume)

        if enable_paths:
            temp_paths = {}

        for o in origins:
            for d in destinations:
                cost, path = _shortest_path(adj, o, d)

                if enable_paths:
                    temp_paths[tuple(path)] = _od_flow[o][d]
                    od_paths[(o, d)][tuple(path)] = 0

                for i in range(len(path)-1):
                    potential_volume[(path[i], path[i+1])] += _od_flow[o][d]

        for u, v in _edges:
            volume[(u, v)] = (1-1/n) * volume[(u, v)] + \
                1/n * potential_volume[(u, v)]
        potential_volume = deepcopy(empty)

        if enable_paths:
            for path, value in temp_paths.items():
                temp_path_list.append([n, path, value * 1/n])

        if n >= max_iter:
            log.warn("Maximum number ({}) of iterations was reached!".format(n))
            break

    # update the network
    for e, vol in volume.items():
        u = network.nodes[e[0]].id
        v = network.nodes[e[1]].id
        network.edges[(u, v)].volume = vol
        w = network.edges[(u, v)].weight()

    # return paths if enabled
    if enable_paths:
        temp_path_list.sort(key=lambda x: x[0], reverse=True)
        for n, path, flow in temp_path_list:
            o = path[0]
            d = path[-1]

            if sum(od_paths[(o, d)].values()) <= _od_flow[o][d]:
                od_paths[(o, d)][path] += flow

        P = Paths()
        for od, paths in od_paths.items():
            for path, flow in paths.items():
                if flow > 0:
                    p = Path(flow=flow)
                    # cost = 0
                    # weight = 0
                    for i in range(len(path)-1):
                        u = network.nodes[path[i]].id
                        v = network.nodes[path[i+1]].id
                        e = network.edges[(u, v)]
                        # cost += e.cost * flow / e.volume
                        # weight += e.cost
                        p.add_edge(e)
                    # p['cost'] = cost
                    # p['weight'] = weight
                    P.add_path(p)

    if enable_paths:
        return P
    else:
        return None


def msa(network, od_flow, limit=0.5, max_iter=float('inf'), enable_paths=True):
    # initialze variables
    origins = list(od_flow)
    destinations = list(set(n for k, v in od_flow.items() for n in v))
    od_paths = defaultdict(dict)

    # create empty dict with edges as keys
    empty = {e: 0 for e in network.edges}

    # initialize variables
    volume = deepcopy(empty)
    potential_volume = deepcopy(empty)
    n2e = network.nodes_to_edges_map()

    # initial all-or-nothing assignment
    for o in origins:
        for d in destinations:
            cost, path = dijkstra(network, o, d)
            edges = [n2e[path[i], path[i+1]][0] for i in range(len(path)-1)]
            for e in edges:
                potential_volume[e] += od_flow[o][d]

    # algorithm
    volume = deepcopy(potential_volume)
    potential_volume = deepcopy(empty)
    temp_volume = deepcopy(empty)
    n = 1

    if enable_paths:
        temp_path_list = []

    while calculate_limit(volume, temp_volume) > limit:
        n += 1
        # update_volume(volume)
        for e, E in network.edges.items():
            E.volume = volume[e]

        temp_volume = deepcopy(volume)

        if enable_paths:
            temp_paths = {}

        for o in origins:
            for d in destinations:
                cost, path = dijkstra(network, o, d)
                edges = [n2e[path[i], path[i+1]][0]
                         for i in range(len(path)-1)]

                if enable_paths:
                    temp_paths[tuple(path)] = od_flow[o][d]
                    od_paths[(o, d)][tuple(path)] = 0

                for e in edges:
                    potential_volume[e] += od_flow[o][d]

        for e in network.edges:
            volume[e] = (1-1/n) * volume[e] + 1/n * potential_volume[e]
        potential_volume = deepcopy(empty)

        if enable_paths:
            for path, value in temp_paths.items():
                temp_path_list.append([n, path, value * 1/n])

        if n >= max_iter:
            log.warn("Maximum number ({}) of iterations was reached!".format(n))
            break

    if enable_paths:
        temp_path_list.sort(key=lambda x: x[0], reverse=True)
        for n, path, flow in temp_path_list:
            o = path[0]
            d = path[-1]

            if sum(od_paths[(o, d)].values()) <= od_flow[o][d]:
                od_paths[(o, d)][path] += flow

        P = Paths()
        for od, paths in od_paths.items():
            for path, flow in paths.items():
                if flow > 0:
                    p = Path(flow=flow)
                    _cost = 0
                    _weight = 0
                    for i in range(len(path)-1):
                        e = network.edges[(path[i], path[i+1])]
                        p.add_edge(e)
                        _weight += e.cost
                        _cost += e.cost * flow / e.volume

                    p['cost'] = _cost
                    p['weight'] = _weight
                    P.add_path(p)

    if enable_paths:
        return P
    else:
        return None


# def msa(network, od_flow, limit=0.5, max_iter=float('inf'), enable_paths=True):
#     # initialze variables
#     origins = list(od_flow)
#     destinations = list(set(n for k, v in od_flow.items() for n in v))
#     od_paths = defaultdict(dict)

#     # create empty dict with edges as keys
#     empty = {e: 0 for e in network.edges}

#     # initialize variables
#     volume = deepcopy(empty)
#     potential_volume = deepcopy(empty)
#     n2e = network.nodes_to_edges_map()

#     # initial all-or-nothing assignment
#     for o in origins:
#         for d in destinations:
#             path = shortest_path(network, o, d, weight='weight')
#             for e in path.edges:
#                 potential_volume[e] += od_flow[o][d]

#     # algorithm
#     volume = deepcopy(potential_volume)
#     potential_volume = deepcopy(empty)
#     temp_volume = deepcopy(empty)
#     n = 1

#     # if enable_paths:
#     #     temp_path_list = []

#     while calculate_limit(volume, temp_volume) > limit:
#         n += 1
#         update_volume(network, volume)
#         temp_volume = deepcopy(volume)

#         # if enable_paths:
#         #     temp_paths = {}

#         for o in origins:
#             for d in destinations:
#                 path = shortest_path(network, o, d, weight='weight')

#                 # if enable_paths:
#                 #     temp_paths[tuple(path)] = self.od_flow[o][d]
#                 #     self.od_paths[(o, d)][tuple(path)] = 0

#                 for e in path.edges:
#                     potential_volume[e] += od_flow[o][d]

#         for e in network.edges:
#             volume[e] = (1-1/n) * volume[e] + 1/n * potential_volume[e]
#         potential_volume = deepcopy(empty)

#         # if enable_paths:
#         #     for path, value in temp_paths.items():
#         #         temp_path_list.append([n, path, value * 1/n])

#         if n >= max_iter:
#             log.warn("Maximum number ({}) of iterations was reached!".format(n))
#             break

#     # if enable_paths:
#     #     temp_path_list.sort(key=lambda x: x[0], reverse=True)
#     #     for n, path, flow in temp_path_list:
#     #         o = path[0]
#     #         d = path[-1]
#     #         if sum(self.od_paths[(o, d)].values()) <= self.od_flow[o][d]:
#     #             self.od_paths[(o, d)][path] += flow

#     # update the network
#     for e, vol in volume.items():
#         network.edges[e].volume = vol
#         w = network.edges[e].weight()

#     pass


def update_volume(network, volume):
    for e, E in network.edges.items():
        E.volume = volume[e]


def calculate_limit(prior, posterior):
    limiter = 0
    for l in prior:
        limiter += abs(prior[l]-posterior[l])
    return limiter


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
