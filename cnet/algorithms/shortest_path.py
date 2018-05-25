#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_path.py 
# Creation  : 25 May 2018
# Time-stamp: <Fre 2018-05-25 13:59 juergen>
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

from scipy.sparse import csgraph

def dijkstra(network, source, sink, weight=None):

    queue, checked = [(0, source, [])], set()
    while queue:
        (cost, v, path) = heapq.heappop(queue)
        if v not in checked:
            path = path + [v]
            checked.add(v)
            if v == sink:
                return cost, path
            for e,o in network.nodes[v].heads:
                _e = network.edges[e]
                if o == 0:
                    _v = _e.v.id
                elif o == 1:
                    _v = _e.u.id
                heapq.heappush(queue, (cost+_e.weight(weight), _v, path))

def dijkstra_scipy(network, source, sink, weight=None):

    graph = network.adjacency_matrix()

    i1 = network.nodes.index(source)
    i2 = network.nodes.index(sink)

    cost, predecessors = csgraph.dijkstra(graph, indices = i1, return_predecessors = True)

    path = []
    i = i2
    while i != i1:
        path.append(i)
        i = predecessors[i]
    path.append(i1)
    path = [network.nodes[int(i)].id for i in path[::-1]]

    return cost[i2], path


def dijkstra_scipy_2(graph, i1, i2, weight=None):

    cost, predecessors = csgraph.dijkstra(graph, indices = i1, return_predecessors = True)

    path = []
    i = i2
    while i != i1:
        path.append(i)
        i = predecessors[i]
    path.append(i1)

    return cost[i2], path


# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
