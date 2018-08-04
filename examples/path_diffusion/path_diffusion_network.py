#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : path_diffusion_network.py -- A network class for path diffusion
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-26
# Time-stamp: <Sam 2018-08-04 08:50 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
import itertools
import numpy as np
from scipy import sparse

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet as cn
from cnet import Network


class PathDiffusionNetwork_cnet(Network):
    """Documentation for PathDiffusionNetwork

    """

    def __init__(self, network, paths, min_length=1, directed=False, **attr):

        # minimum number of edges in order to be considered
        self.min_length = max(min_length, 1)

        # initializing the parent classes
        Network.__init__(self, directed=directed, **attr)

        # the underlying network for the higher-oder model
        self.original_network = network

        # temporary network where changes are applied
        self.network = self.original_network.copy()

        # add edge attribute to save paths using this edge
        for e in self.network.edges():
            e['paths'] = set()

        # the paths object from which this higher-order model is created
        self.paths = paths

        # sets of edges and paths which are deactivated
        self.deactivated_edges = set()
        self.deactivated_paths = set()
        self.modified = set()
        # sort the paths by weight (cost of the total path)
        #self.paths.sort('flow', reverse=True)

        # get od information
        self.od = set()
        for p in self.paths:
            self.od.add((p.path[0], p.path[-1]))

        # generate the network
        for s, t in self.od:
            net_1 = cn.HigherOrderNetwork(s+'='+t,
                                          modified=False,
                                          sub_edges=set(),
                                          common_edges=dict(),
                                          new_common_edges=dict(),
                                          self_loop=False)

            for p in self.paths.st_paths(s, t):

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
                                       active=True,
                                       original=True,
                                       estimate=0)

                # Copy the attributes of the path
                net_0.update(**p.attributes)

                # Add edges to the path and path id to the edge
                for e in _edges:
                    net_0.add_edge(self.network.edges[e])
                    self.network.edges[e]['paths'].add(net_0)
                # Add the higher order node to the higher order network
                net_1.add_node(net_0)

                # Collect the edge ids for the higher order network
                net_1['sub_edges'].update(
                    [self.network.edges[e] for e in _edges])

            for i in range(net_1.number_of_nodes()-1):
                u = net_1.nodes[i]
                v = net_1.nodes[i+1]
                net_1.add_edge(u.id+'|'+u.id, u, u)
                net_1.add_edge(u.id+'|'+v.id, u, v)
                net_1.add_edge(v.id+'|'+u.id, v, u)

            v = net_1.nodes[-1]
            net_1.add_edge(v.id+'|'+v.id, v, v)

            self.add_node(net_1)

        # use itertools to speed up the for loop over edge pairs
        # self loops are not considered here!
        _nodes = itertools.combinations(self.nodes(), 2)
        for s, t in _nodes:
            _common_edges = s['sub_edges'].intersection(t['sub_edges'])
            if len(_common_edges) >= self.min_length:
                s['common_edges'][t.id] = _common_edges
                t['common_edges'][s.id] = _common_edges
                # TODO: Speed up the edge class!!!
                # Right now it is very slow to add 20k+ edges
                # self.add_edge(s.id+'<>'+t.id, s, t)
                # self.add_edge(s.id+'<>'+t.id, s, t,
                #               common_edges=_common_edges,
                #               n_original=len(_common_edges),
                #               n_new=0)

    def deactivate_edges(self, edges):
        """Deactivates a single edge of the network."""

        # temporary set of edges which should be deactivated
        E = set()
        if isinstance(edges, str):
            edges = [edges]
        for e in edges:
            E.add(self.network.edges[e])

        self.deactivated_edges.update(E)

        # remove edge
        self.network.remove_edge(e)

        # go through the nodes of the graph and remove the edges
        for net_1 in self.nodes():
            if not E.isdisjoint(net_1['sub_edges']):
                # remove edge from the higher oder node
                net_1['sub_edges'] = net_1['sub_edges'] - E

                # label as modified
                net_1['modified'] = True
                self.modified.add(net_1)

                # clear dict of common edges
                net_1['common_edges'] = dict()
                for net_0 in net_1.nodes():
                    if not E.isdisjoint(set(net_0.edges())):
                        # deactivate the path
                        net_0['active'] = False
                        self.deactivated_paths.add(net_0)

                        # remove the path form the edges
                        for e in net_0.edges():
                            e['paths'].remove(net_0)

        # use itertools to speed up the for loop over edge pairs
        # self loops are not considered here!
        _nodes = itertools.combinations(self.nodes(), 2)
        for s, t in _nodes:
            _common_edges = s['sub_edges'].intersection(t['sub_edges'])
            if len(_common_edges) >= self.min_length:
                s['common_edges'][t.id] = _common_edges
                t['common_edges'][s.id] = _common_edges

    def rewire_paths(self):
        """Assign new connections bewteen nodes and paths."""
        # create a temporary network
        # This is needed for calculating the kspaths otherwise an error will
        # occur.
        # TODO: Fix the error
        _network = self.original_network.copy()
        for e in self.deactivated_edges:
            _network.remove_edge(e.id)

        for net_1 in self.modified:
            # add new path if all existing paths are deactivated
            if not any(net_1.nodes('active')):
                # get s t of the path
                s = net_1.nodes[0].nodes[0].id
                t = net_1.nodes[0].nodes[-1].id
                # generate k new shortest paths
                # NOTE: the ksp are based on the expected costs from the
                # initial run!
                # TODO: Add other ranking criteria
                # TODO: Allow multiple additional paths
                P_st = cn.ksp(_network, s, t, k=1)

                p = P_st[0]

                # Get the edge ids of the path
                _edges = p.path_to_edges(id=True)

                # Create higher oder Node
                net_0 = cn.NodeAndPath(p.id,
                                       active=True,
                                       original=False,
                                       estimate=0)

                # Copy the attributes of the path
                net_0.update(**p.attributes)
                net_0['flow'] = 0

                # Add edges to the path and path id to the edge
                for e in _edges:
                    net_0.add_edge(self.network.edges[e])
                    self.network.edges[e]['paths'].add(net_0)
                # Add the higher order node to the higher order network
                net_1.add_node(net_0)

                # Collect the edge ids for the higher order network
                net_1['sub_edges'].update(
                    [self.network.edges[e] for e in _edges])

                u = net_1.nodes[-1]
                v = net_1.nodes[-2]
                net_1.add_edge(u.id+'|'+u.id, u, u)
                net_1.add_edge(u.id+'|'+v.id, u, v)
                net_1.add_edge(v.id+'|'+u.id, v, u)

        _nodes = itertools.combinations(self.nodes(), 2)
        for s, t in _nodes:
            _new = s['sub_edges'].intersection(t['sub_edges'])
            if len(_new) >= self.min_length:
                _old = s['common_edges'].get(t.id, set())
                s['common_edges'][t.id] = _new
                t['common_edges'][s.id] = _new

                if _new != _old:
                    s['new_common_edges'][t.id] = _new - _old
                    t['new_common_edges'][s.id] = _new - _old

                    s_active = sum(s.nodes['active'].values())
                    t_active = sum(t.nodes['active'].values())
                    # if s['modified'] or t['modified']:
                    #     self.add_edge(s.id+'<>'+t.id, s, t)
                    # if s_active > 1 and t_active > 1:
                    #     self.add_edge(s.id+'<>'+t.id, s, t)

                    if (s['modified'] and t_active > 1) or \
                       (t['modified'] and s_active > 1):
                        # if not s['modified'] and t['modified']:
                        self.add_edge(s.id+'<>'+t.id, s, t,
                                      weight=len(_new-_old))

                    # self.add_edge(s.id+'<>'+t.id, s, t,
                    #               weight=len(_new-_old))

                    # if t['modified'] and s_active > 1:
                    #     self.add_edge(s.id+'<>'+t.id, s, t)

                    # if t['modified']:
                    #     self.add_edge(t.id+'<>'+s.id, t, s)
                # self.add_edge(s.id+'<>'+t.id, s, t,
                #               common_edges=_common_edges,
                #               n_original=len(_common_edges),
                #               n_new=0)

        # T = self.transition_matrix(weight=True)
        # deg = self.degree()
        # x = np.zeros(len(deg))
        # for i, n in enumerate(self.nodes):
        #     #x[i] = deg[n]
        #     if n in ['N01=N02']:
        #         x[i] = 1000

        # # # print(x)
        # # x = x / x.sum()
        # pt = (T**10000).transpose().dot(x)

        # # print(pt)

        # test_net = cn.Network(directed=False)
        # test_net.add_edges_from(list(self.edges()))
        # test_net.summary()
        # self.tn = test_net

        # rwd = cn.RandomWalkDiffusion(test_net)
        # T = test_net.transition_matrix(weight=True)
        # print(T)
        # pi = rwd.stationary_distribution(A=T, normalized=True)
        # print(np.real(pi)*1000)
        # for i, n in enumerate(self.nodes()):
        #     n['value'] = pt[i]

        #np.savetxt('M.csv', self.adjacency_matrix(weight=True).todense())
        # _count = 0
        # # use itertools to speed up the for loop over edge pairs
        # # self loops are not considered here!
        # _nodes = itertools.combinations(self.nodes(), 2)
        # for s, t in _nodes:
        #     _common_edges = s['sub_edges'].intersection(t['sub_edges'])
        #     _old = s['common_edges'].get(t.id, None)
        #     if _old:
        #         print(_old)
        #     # print(s['common_edges'][t.id])
        #     # if len(s['common_edges'][t.id]) > len(_common_edges):
        #     #     print(s, t)
        #     if len(_common_edges) >= self.min_length:
        #         s['common_edges'][t.id] = _common_edges
        #         t['common_edges'][s.id] = _common_edges
        #         _count += 1
        # print(_count)

    def deactivate_path(self, e):
        self.network.remove_edge(e)
        self.deactivated = e
        for net_1 in self.nodes():
            net_1['sub_edges'] = set()
            for net_0 in net_1.nodes():
                if net_0.has_edge(e):
                    net_0['active'] = False
                else:
                    net_1['sub_edges'].update([se for se in net_0.edges])

            # add new path if all existing paths are deactivated
            if not any(net_1.nodes('active')):
                # get s t of the path
                s = net_1.nodes[0].nodes[0].id
                t = net_1.nodes[0].nodes[-1].id

                # generate k new shortest paths
                # NOTE: the ksp are based on the expected costs from the
                # initial run!
                # TODO: Add other ranking criteria
                P_st = cn.ksp(self.network, s, t, k=5)
                net_0 = cn.NodeAndPath(P_st[0])
                net_0['active'] = True
                net_0['original'] = False
                net_0['flow'] = 0
                net_0['estimate'] = 0
                net_1.add_node(net_0)
                net_1['sub_edges'].update([se for se in net_0.edges])

                u = net_1.nodes[-1]
                v = net_1.nodes[-2]
                net_1.add_edge(u.id+'|'+u.id, u, u)
                net_1.add_edge(u.id+'|'+v.id, u, v)
                net_1.add_edge(v.id+'|'+u.id, v, u)

        _nodes = itertools.combinations_with_replacement(self.nodes(), 2)
        for s, t in _nodes:
            _e = s.id+'<>'+t.id
            if s != t:
                _common_edges = s['sub_edges'].intersection(t['sub_edges'])
                if len(_common_edges) > self.min_length:
                    if not self.has_edge(_e):
                        self.add_edge(_e, s, t, common_edges=_common_edges,
                                      n_original=0, n_new=len(_common_edges))
                    else:
                        self.edges[_e]['common_edges'] = _common_edges
                        self.edges[_e]['n_new'] = len(_common_edges)
            if s == t:
                if not all(s.nodes('active')):
                    self.add_edge(_e, s, s, common_edges=None, n_original=0,
                                  n_new=1)
                    s['self_loop'] = True
                    s['modified'] = True

        # delete edges which dont have any common edges anymore
        for e in self.edges():
            if e['n_new'] == 0:
                self.remove_edge(e.id)

    def volume(self, original=False):
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
        # return np.array(list(self.network.edges('volume')))
        # return {e.id: e['volume'] for e in self.network.edges()}
        return np.array([n for _, n in _vol])

    def vol(self, original=False):
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
        # return np.array(list(self.network.edges('volume')))
        return {e.id: e['volume'] for e in self.network.edges()}

    def assign_probabilities(self, p=None):
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

    def run_diffusion(self):

        for e in self.edges():
            if e['n_original'] > 0:
                self.remove_edge(e.id)
        # _px = self.px
        # A = self.transition_matrix(weight='n_new')

        # for i in np.argwhere(A.diagonal() > 0):
        #     _sum = A[i].sum()-A[i, i]
        #     value = (_px * _sum)/(1-_px)
        #     A[i, i] = value

        # with np.errstate(divide='ignore'):
        #     c = sparse.diags(1/A.sum(axis=1).A.ravel())

        # T = c.dot(A)

        # # T = self.transition_matrix(weight='n_new')
        # x = np.array(list(self.nodes('modified'))).astype(int)
        # # print(x)
        # x = x / x.sum()
        # pt_1 = (T**10000).transpose().dot(x)

        # pt_1 = np.nan_to_num(pt_1)
        # # print(pt_1)

        for i, net_1 in enumerate(self.nodes()):
            x = np.array(list(net_1.nodes('flow')))
            T = net_1.transition_matrix(weight=True)
            pt = (T**10000).transpose().dot(x)
            #x_est = pt
            if net_1['modified']:
                x_est = pt
            else:
                #x_est = pt * pt_1[i] + x * (1-pt_1[i])
                x_est = x
                # pt_x = .0
                # x_est = pt * pt_x + x * (1-pt_x)
            for j in range(len(pt)):
                net_1.nodes[j]['estimate'] = x_est[j]

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
