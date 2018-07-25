#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_path.py
# Creation  : 25 May 2018
# Time-stamp: <Son 2018-07-22 11:08 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : Algorithms to find the shortest path between two nodes
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

import heapq

from heapq import heappush, heappop
from itertools import count


from cnet import logger, Network, Path, Paths, Edge
from cnet.utils.exceptions import CnetError, CnetNotImplemented

from scipy.sparse import csgraph, find, isspmatrix
log = logger(__name__)


def shortest_path(network, source, sink, weight=None, mode='path', method='auto'):
    # check and format inputs
    adj, source, sink = _check_inputs(network, source, sink, weight=weight)

    # calculate shortest path
    try:
        cost, path = _shortest_path(adj, source, sink, method=method)
    except:
        cost = float('inf')
        path = []
        log.warn('No valid path was found!')
    # If network is a network object and type is path,
    # a Path object will be returned
    if isinstance(network, Network) and mode == 'path':
        p = Path(weight=cost)
        if len(path) > 0:
            for i in range(len(path)-1):
                u = network.nodes[path[i]].id
                v = network.nodes[path[i+1]].id
                e = network.edges[(u, v)]
                p.add_edge(e)
        return p
    elif isinstance(network, Network) and mode != 'path':
        path = [network.nodes[p].id for p in path]
        return cost, path
    else:
        return cost, path


def k_shortest_paths(network, source, sink, k, weight=None, mode='paths', method='auto'):
    # check inputs
    adj, source, sink = _check_inputs(network, source, sink, weight=weight)

    # calculate k shortest paths
    try:
        paths = _k_shortest_paths(adj, source, sink, k, method=method)
    except:
        paths = []
        log.warn('No valid paths were found!')

    # If network is a network object and type is path,
    # a Path object will be returned
    if isinstance(network, Network) and mode == 'paths':
        P = Paths()
        for path in paths:
            p = Path(weight=path[0])
            if len(path[1]) > 0:
                for i in range(len(path[1])-1):
                    u = network.nodes[int(path[1][i])].id
                    v = network.nodes[int(path[1][i+1])].id
                    e = network.edges[(u, v)]
                    p.add_edge(e)
                P.add_path(p)
        return P
    elif isinstance(network, Network) and mode != 'path':
        P = []
        for path in paths:
            cost = path[0]
            path = [network.nodes[int(p)].id for p in path[1]]
            P.append((cost, path))
        return P

    else:
        return paths


def _check_inputs(network, source, sink, weight=None):

    # check if a network object or a adjacency matrix is given
    if isinstance(network, Network):
        adj = network.adjacency_matrix(weight=weight)
    elif isspmatrix(network):
        adj = network
    else:
        log.error('Network is not defined properly! Only networks of type'
                  '<Network> or sparse scipy matrices can be handled.')
        raise CnetError

    # check source or sink nodes
    if isinstance(network, Network) and isinstance(source, str):
        source = network.nodes.index(source)
    if isinstance(network, Network) and isinstance(sink, str):
        sink = network.nodes.index(sink)
    if not isinstance(source, int) or not isinstance(sink, int):
        log.error('Nodes are not defined properly! Only the node ids or the '
                  'node indices are valid inputs!')
        raise CnetError

    return adj, source, sink


def _shortest_path(adj, source, sink, method='auto'):
    cost, predecessors = csgraph.shortest_path(adj, indices=source,
                                               method=method,
                                               return_predecessors=True)
    path = []
    i = sink
    while i != source:
        path.append(int(i))
        i = predecessors[i]
    path.append(source)
    return cost[sink], path[::-1]


def _k_shortest_paths(adj, source, sink, k, method='auto'):

    cost, sp = _shortest_path(adj, source, sink, method=method)

    top_k_path_set, paths, used, counter = [(cost, sp)], [sp], set(), 0
    for i in range(len(sp)-1):
        used.add((sp[i], sp[i+1]))

    # iteration
    for i in range(k-1):
        # get spur ring and rooting nodes
        for j in range(len(paths[counter])-1):
            root = paths[counter][j]
            root_cost = 0
            if j != 0:
                for r in range(j):
                    root_cost += adj[(paths[counter][r], paths[counter][r+1])]
            for n in find(adj[root])[1]:
                if (root, n) not in used:
                    spur_cost, spur_path = _shortest_path(
                        adj, n, sink, method=method)
                    p_cost = root_cost + adj[(root, n)] + spur_cost
                    p_path = paths[counter][:j+1]+spur_path
                    top_k_path_set.append((p_cost, p_path))
                    for p in range(len(p_path) - 1):
                        used.add((p_path[p], p_path[p+1]))
    sorted_paths = sorted(top_k_path_set)
    # return sorted_paths
    if k > len(sorted_paths):
        log.warn('Less then k={} paths were found!'.format(k))
        return sorted_paths
    else:
        return sorted_paths[:k]


# # My pure Python implementation
def dijkstra(network, source, sink, weight=None):
    queue, checked = [(0, source, [])], set()
    while queue:
        (cost, v, path) = heapq.heappop(queue)
        if v not in checked:
            path = path + [v]
            checked.add(v)
            if v == sink:
                return cost, path
            for e, o in network.nodes[v].heads:
                _e = network.edges[e]
                if o == 0:
                    _v = _e.v.id
                elif o == 1:
                    _v = _e.u.id
                heapq.heappush(queue, (cost+_e.weight(weight), _v, path))
    return float('inf'), path


def yen_k_sp(network, source, sink, k, weight=None):

    cost, sp = dijkstra(network, source, sink, weight=weight)

    n2e = network.nodes_to_edges_map()

    top_k_path_set, paths, used, counter = [(cost, sp)], [sp], set(), 0
    for i in range(len(sp)-1):
        used.add((sp[i], sp[i+1]))
    # iteration
    for i in range(k-1):
        # get spur ring and rooting nodes
        for j in range(len(paths[counter])-1):
            root = paths[counter][j]
            root_cost = 0
            if j != 0:
                for r in range(j):
                    root_cost += network.edges[n2e[(paths[counter]
                                                    [r], paths[counter][r+1])][0]].weight(weight)
            for e, o in network.nodes[root].heads:
                # get spur path and spur cost
                _e = network.edges[e]
                if o == 0:
                    n = _e.v.id
                elif o == 1:
                    n = _e.u.id
                if (root, n) not in used:
                    spur_cost, spur_path = dijkstra(
                        network, n, sink, weight=weight)
                    p_cost = root_cost + \
                        network.edges[n2e[(root, n)][0]].weight(
                            weight) + spur_cost
                    p_path = paths[counter][:j+1]+spur_path
                    top_k_path_set.append((p_cost, p_path))
                    for p in range(len(p_path) - 1):
                        used.add((p_path[p], p_path[p+1]))
    sorted_paths = sorted(top_k_path_set)
    # return sorted_paths
    if k > len(sorted_paths):
        return sorted_paths
    else:
        return sorted_paths[:k]


def ksp(network, source, sink, k=1, weight=None, mode='paths', method='auto'):

    # check if source is equal the sink node
    if source == sink:
        log.error('Source node {} is equal to the sink node '
                  '{}'.format(source, sink))
        raise CnetError()

    cost, sp = dijkstra(network, source, sink, weight=weight)

    # TODO: Check if there is a valid connection between two nodes.
    if sink not in sp:
        log.error('Node {} not reachable from {}'.format(sink, source))
        raise CnetError()

    # initialize variables
    costs = [cost]
    paths = [sp]
    c = count()
    B = []
    network_original = network.copy()

    # network.summary()
    for i in range(1, k):
        for j in range(len(paths[-1])-1):
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]

            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if network.has_edge((u, v)):
                        _edge = network.edges[(u, v)]
                        network.remove_edge((u, v))
                        edges_removed.append(_edge)

            for n in range(len(root_path) - 1):
                node = root_path[n]
                heads = [e[0] for e in network.nodes[node].heads]
                for e in heads:
                    edges_removed.append(network.edges[e])
                network.remove_edges_from(heads)

            spur_path_cost, spur_path = dijkstra(
                network, spur_node, sink, weight=weight)

            if sink in spur_path:
                total_path = root_path[:-1] + spur_path
                root_path_cost = 0
                for i in range(len(root_path)-1):
                    root_path_cost += network_original.edges[(
                        root_path[i], root_path[i+1])].weight(weight)
                total_path_cost = root_path_cost + spur_path_cost
                heappush(B, (total_path_cost, next(c), total_path))

            for e in edges_removed:
                network.add_edge(e)

        if B:
            (l, _, p) = heappop(B)
            if p not in paths:
                costs.append(l)
                paths.append(p)
        else:
            break

    if isinstance(network, Network) and mode == 'paths':
        P = Paths()
        for i, path in enumerate(paths):
            p = Path(weight=costs[i])
            if len(path) > 0:
                for i in range(len(path)-1):
                    # u = network.nodes[int(path[1][i])].id
                    # v = network.nodes[int(path[1][i+1])].id
                    # e = network.edges[(u, v)]
                    e = network.edges[(path[i], path[i+1])]
                    p.add_edge(e)
                P.add_path(p)
        return P
    else:
        return costs, paths


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
