#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : path_diffusion_network.py -- A network class for path diffusion
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-26
# Time-stamp: <Son 2018-08-05 16:56 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
import itertools
import numpy as np
from scipy import sparse
from collections import defaultdict, Counter
wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet as cn
from cnet import Network


class PathDiffusionNetwork_cnet(Network):
    """Documentation for PathDiffusionNetwork

    """

    def __init__(self, network, paths, min_length=1, directed=False, **attr):
        """Initializing the network."""
        # minimum number of edges in order to be considered
        self.min_length = max(min_length, 1)

        # initializing the parent classes
        Network.__init__(self, directed=directed, **attr)

        # the underlying network for the higher-oder model
        self.original_network = network

        # network where changes are applied
        self.network = self.original_network.copy()

        # temporal network used for the k shortest path calculation
        # This is nessessary since an error occurs when self.network is used
        # TODO: fix this error!
        self._network = self.original_network.copy()

        # add edge attribute to save paths using this edge
        for e in self.network.edges():
            e['paths'] = set()
            e['od'] = set()

        # the paths object from which this higher-order model is created
        self.original_paths = paths
        self.paths = dict()

        # sets of edges and paths which are deactivated
        self.deactivated_edges = set()
        self.deactivated_paths = set()
        self.modified = set()
        # sort the paths by weight (cost of the total path)
        # self.original_paths.sort('flow', reverse=True)

        # get od information
        self.od = set()
        for p in self.original_paths:
            self.od.add((p.path[0], p.path[-1]))

        # maximum number of considered k-shortest paths
        self.max_k = 5

        # threshold to switch to an other (existing) path
        self.switching_threshold = 3

        # generate network
        self.generate_network()

    def generate_network(self, k=None):
        """Generates the topology of the path diffusion network."""
        # generate higher oder node
        # representing the origin destination relationship.
        for s, t in self.od:
            net_1 = cn.HigherOrderNetwork(s+'='+t,
                                          modified=False,
                                          sub_edges=set(),
                                          common_edges=dict(),
                                          new_common_edges=dict(),
                                          source=s,
                                          target=t)
            # Add node to the network
            self.add_node(net_1)

            # Add paths to the network
            self.generate_paths(net_1)
            # Add additionally k-shortest paths
            if k:
                self.generate_paths(net_1, k=k)

            # Assign common edges
            # self.assign_common_edges()

            # Connect the higher order network
            # self.connect_network()
        pass

    def generate_paths(self, net_1, k=1):
        """Generates node|path objects for the network."""
        s = net_1['source']
        t = net_1['target']
        # check if there is already a node|path assigned to the node
        if net_1.number_of_nodes() == 0:
            P_st = self.original_paths.st_paths(s, t)
            # Generate a node|paths
            for p in P_st:
                self._generate_path(net_1, p, active=True, original=True)

        else:
            P_st = []
            i = k
            while len(P_st) < k:
                P_k = cn.ksp(self._network, s, t, k=net_1.number_of_nodes()+i)
                for _p in P_k:
                    if _p.id not in net_1.nodes:
                        P_st.append(_p)
                        if len(P_st) == k:
                            break
                i += 1
                if i >= self.max_k:
                    print('Number of max k was reached!')
                    break
            # Generate a node|paths
            for p in P_st:
                self._generate_path(net_1, p, active=True, original=False)

        # connect the paths:
        self.connect_paths(net_1)

    def _generate_path(self, net_1, p, active=True, original=True):
        """Generates a node|path object."""

        # NOTE: this is done here in this way since the edges and nodes
        # of the path should be an instance of the edges and nodes of
        # the underlying network and no copy of them. i.e. changes in
        # of the edges and nodes in the path will effect also the
        # network. An easier implementation will be:
        # net_0 = cn.NodeAndPath(p), however the objects will be only a
        # copy and no instance.

        # Get the edge ids of the path
        _edges = p.path_to_edges(id=True)

        # Create higher oder Node
        net_0 = cn.NodeAndPath(p.id,
                               active=active,
                               original=original,
                               estimate=0,
                               flow=0)

        # Copy the attributes of the path
        net_0.update(**p.attributes)

        # Add edges to the path and path id to the edge
        for e in _edges:
            net_0.add_edge(self.network.edges[e])
            self.network.edges[e]['paths'].add(net_0)
            self.network.edges[e]['od'].add(net_1)

        # Add the node|path to the set of paths
        self.paths[net_0.id] = net_0

        # Collect the edge ids for the higher order network
        net_1['sub_edges'].update(
            [self.network.edges[e] for e in _edges])

        # Add the higher order node to the higher order network
        net_1.add_node(net_0)

    def connect_paths(self, net_1):
        """Assign connections bewteen node|paths objects."""
        for i in range(net_1.number_of_nodes()-1):
            u = net_1.nodes[i]
            v = net_1.nodes[i+1]
            if not net_1.has_edge(u.id+'|'+u.id):
                net_1.add_edge(u.id+'|'+u.id, u, u, weight=1)
            if not net_1.has_edge(u.id+'|'+v.id):
                net_1.add_edge(u.id+'|'+v.id, u, v, weight=1)
            if not net_1.has_edge(v.id+'|'+u.id):
                net_1.add_edge(v.id+'|'+u.id, v, u, weight=1)

        v = net_1.nodes[-1]
        if not net_1.has_edge(v.id+'|'+v.id):
            net_1.add_edge(v.id+'|'+v.id, v, v, weight=1)

    def deactivate_paths(self, paths):
        """Deactivates node|paths of the network."""
        # temporary set of paths which should be deactivated
        P = set()
        # if isinstance(paths, str):
        #     paths = [paths]
        # for p in paths:
        #     P.add(self.paths[p])
        P.update(paths)

        # go through the nodes of the graph and deactivate paths
        for net_1 in self.nodes():
            nodes = P.intersection(set(net_1.nodes()))
            if nodes:
                # label as modified
                net_1['modified'] = True
                self.modified.add(net_1)

                for net_0 in nodes:
                    # deactivate the path
                    net_0['active'] = False
                    self.deactivated_paths.add(net_0)
                    del self.paths[net_0.id]

                    # remove the path form the edges
                    for e in net_0.edges():
                        e['paths'].remove(net_0)
                        e['od'].discard(net_1)

                    # remove edge from the higher oder node
                    net_1['sub_edges'] = net_1['sub_edges'] - \
                        set(net_0.edges())

    def deactivate_edges(self, edges):
        """Deactivates edges of the underlying network."""
        # temporary set of edges which should be deactivated
        E = set()
        # temporary set of paths containing the edges
        P = set()
        if isinstance(edges, str):
            edges = [edges]
        for e in edges:
            E.add(self.network.edges[e])

        # add deactivated edges to the global set
        self.deactivated_edges.update(E)

        # remove edge
        self.network.remove_edge(e)
        self._network.remove_edge(e)

        for e in E:
            P.update(e['paths'])

        self.deactivate_paths(P)

    def connect_network(self):
        """Assign connections bewteen higher oder nodes."""
        _old = defaultdict(dict)
        _nodes = itertools.product(self.nodes(), repeat=2)

        for s, t in _nodes:
            _old[s][t] = s['common_edges'].get(t.id, set())

        _edges = set()
        _nodes = itertools.combinations(self.nodes(), 2)
        for s, t in _nodes:
            _common_edges = s['sub_edges'].intersection(t['sub_edges'])
            if len(_common_edges) >= self.min_length:
                s['common_edges'][t.id] = _common_edges
                t['common_edges'][s.id] = _common_edges

                s_active = sum(s.nodes['active'].values())
                t_active = sum(t.nodes['active'].values())
                if (s['modified'] and t_active > 1) or \
                   (t['modified'] and s_active > 1):  # or \
                   # (s_active > 1 and t_active > 1):
                    if not self.has_edge(s.id+'<>'+t.id):
                        self.add_edge(s.id+'<>'+t.id, s, t)
                    _edges.add(self.edges[s.id+'<>'+t.id])

        for e in set(self.edges())-_edges:
            self.remove_edge(e.id)

        # assign the weigths of the edges
        for e in self.edges():
            s = e.u
            t = e.v

            _o = _old[s][t] | _old[t][s]
            _n = s['common_edges'][t.id] | t['common_edges'][s.id]

            e['weight'] = len(_n-_o)
            s['new_common_edges'][t.id] = _n-_o
            t['new_common_edges'][s.id] = _n-_o

    def assign_common_edges(self):
        """Assign common edges between the st nodes i.e. betweent the paths."""
        # use itertools to speed up the for loop over edge pairs
        # self loops are not considered here!
        _nodes = itertools.combinations(self.nodes(), 2)
        for s, t in _nodes:
            _common_edges = s['sub_edges'].intersection(t['sub_edges'])
            if len(_common_edges) >= self.min_length:
                s['common_edges'][t.id] = _common_edges
                t['common_edges'][s.id] = _common_edges

    def assign_probabilities(self, p=None):
        """Assign probabilities to the node|paths."""
        if p is not None:
            # case 1: path of best solution
            # options: stay (a), move down (b)
            pa = p[0]
            pb = 1 - p[0]
            # case 2: path of a solution
            # options: move up (c), stay (d), move down (e)
            pc = p[1]/2
            pd = 1-p[1]
            pe = p[1]/2
            # case 3: path of the worst solution
            # options: move up (f), stay (g)
            pf = p[2]
            pg = 1-p[2]
            # case 4: on best path but deactivated
            # options move down (h)
            ph = 1
            # case 5: in between but deactivated:
            # options: move up (i) move down (j)
            pi = p[3]
            pj = 1-p[3]
            # case 6: on worst path:
            # options: move up (k)
            pk = 1
            # case 7: the only path is deactivated
            # TODO: add new path

            # probably for the od diffusion
            self.px = p[4]
        else:
            pa = .9
            pb = .1
            pc = .2
            pd = .6
            pe = .2
            pf = .1
            pg = .9
            ph = 1
            pi = .2
            pj = .8
            pk = 1
            self.px = .9

        options_1 = {(True, True): (pa, pb),
                     (True, False): (ph, 1-ph),
                     (False, True): (1-ph, ph),
                     (False, False): (1-ph, ph)}

        options_2 = {(True, True, True): (pc, pd, pe),
                     (False, True, True): (0, pa, pb),
                     (True, False, True): (pi, 0, pj),
                     (True, True, False): (pf, pg, 0),
                     (False, True, False): (0, ph, 1-ph),
                     (True, False, False): (pk, 1-pk, 0),
                     (False, False, True): (0, 1-ph, ph),
                     (False, False, False): (0, 1-ph, ph)}

        options_3 = {(True, True): (pf, pg),
                     (True, False): (pk, 1-pk),
                     (False, True): (1-pk, pk),
                     (False, False): (pk, 1-pk)}

        for net_1 in self.nodes():
            if net_1.number_of_nodes() == 1:
                v = net_1.nodes[0]
                net_1.edges[(v, v)]['weight'] = 1
            else:
                v = net_1.nodes[0]
                w = net_1.nodes[1]

                _pa, _pb = options_1[(v['active'], w['active'])]

                net_1.edges[(v, v)]['weight'] = _pa
                net_1.edges[(v, w)]['weight'] = _pb

                for i in range(1, net_1.number_of_nodes()-1):
                    u = net_1.nodes[i-1]
                    v = net_1.nodes[i]
                    w = net_1.nodes[i+1]

                    _pc, _pd, _pe = options_2[(u['active'],
                                               v['active'],
                                               w['active'])]

                    net_1.edges[(v, u)]['weight'] = _pc
                    net_1.edges[(v, v)]['weight'] = _pd
                    net_1.edges[(v, w)]['weight'] = _pe

                u = net_1.nodes[-2]
                v = net_1.nodes[-1]

                _pf, _pg = options_3[(u['active'], v['active'])]

                net_1.edges[(v, u)]['weight'] = _pf
                net_1.edges[(v, v)]['weight'] = _pg

    def rewiring(self):
        """Assign new connections bewteen node|paths."""
        for net_1 in self.modified:
            # add new path if all existing paths are deactivated
            if not any(net_1.nodes('active')):
                self.generate_paths(net_1, k=1)

    def switching(self):
        """Evaluate if new configuration influences other paths."""
        # temporary set of paths which should be deactivated
        P = set()
        # get the nodes which have additional shared edges
        # i.e. the weighted degree is the number of additional shared edges.
        _degree = {k: v for k, v in self.degree(weight=True).items() if v > 0}

        for n in _degree:
            net_1 = self.nodes[n]
            if not net_1['modified']:
                counter = Counter([e for edges in net_1['new_common_edges'].values()
                                   for e in edges])
                nodes = {}
                for net_0 in net_1.nodes():
                    nodes[net_0] = sum([counter[e] for e in net_0.edges()])
                nodes = sorted(nodes.items(), key=lambda kv: kv[1],
                               reverse=True)
                if nodes[0][1] - nodes[1][1] >= self.switching_threshold:
                    P.add(nodes[0][0])
        self.deactivate_paths(P)

    def spreading(self):
        """Evaluate the costs of switching to a new path."""
        # temporary set of paths to add_edge
        P = set()
        vol = self.volume(vector=False)
        # TODO: Move this section to the init of the network,
        # with an option to enable switching
        for net_1 in self.nodes():
            s = net_1.nodes[0].nodes[0].id
            t = net_1.nodes[0].nodes[-1].id

            P_st = cn.ksp(self._network, s, t, k=net_1.number_of_nodes()+1)

            p = None
            for _p in P_st:
                if _p.id not in net_1.nodes:
                    p = _p
                    break
            if p is None:
                continue
            _edges = p.path_to_edges(id=True)

            _costs = []
            for net_0 in net_1.nodes():
                if net_0['active']:
                    _costs.append(sum([self.cost_function(e, vol[e.id])
                                       for e in net_0.edges()]))
            _e = [self.network.edges[e] for e in _edges]
            _new_costs = sum([self.cost_function(e, vol[e.id]) for e in _e])

            if _new_costs < _costs[-1]:
                P.add(net_1)

        for net_1 in P:
            self.generate_paths(net_1, k=1)

    def diffusion(self):
        """Run the diffusion process on node|paths."""
        for net_1 in self.nodes():
            x = np.array(list(net_1.nodes('flow')))
            if net_1['modified']:
                T = net_1.transition_matrix(weight=True)
                pt = (T**10000).transpose().dot(x)
                x_est = pt
            else:
                x_est = x
            for i in range(len(x_est)):
                net_1.nodes[i]['estimate'] = x_est[i]

    def volume(self, original=False, vector=True):
        """Returns the volume per edge in the road network based on the path
        flows"""
        for e in self.network.edges():
            e['volume'] = 0
            for net_1 in self.nodes():
                for net_0 in net_1.nodes():
                    if net_0.has_edge(e):
                        if original:
                            e['volume'] += net_0['flow']
                        else:
                            e['volume'] += net_0['estimate']
        _vol = [(e.id, e['volume']) for e in self.network.edges()]
        _vol.sort()

        if vector:
            return np.array([n for _, n in _vol])
        else:
            return {e.id: e['volume'] for e in self.network.edges()}

    @staticmethod
    def cost_function(edge, volume):
        """BPR function to evaluate the costs of a path."""
        cost = edge.free_flow_time * \
            (1 + edge.alpha * (volume/edge.capacity) ** edge.beta)
        return cost

    def run(self):
        """Function to run the path diffusion process."""
        self.rewiring()
        self.connect_network()
        # remove paths
        self.switching()
        self.assign_probabilities()
        self.diffusion()
        # add paths
        self.spreading()


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
