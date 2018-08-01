#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : path_diffusion_network.py -- A network class for path diffusion
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-26
# Time-stamp: <Mit 2018-08-01 12:36 juergen>
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

    def __init__(self, network, paths, n_edges=0, directed=False, **attr):

        # minimum number of edges in order to be considered
        self.n_edges = n_edges

        # initializing the parent classes
        Network.__init__(self, directed=directed, **attr)

        # the underlying network for the higher-oder model
        self.network = network

        # temporary network where changes are applied
        self._network = self.network.copy()

        # the paths object from which this higher-order model is created
        self.paths = paths

        # sort the paths by weight (cost of the total path)
        #self.paths.sort('flow', reverse=True)

        # get od information
        self.od = set()
        for p in self.paths:
            self.od.add((p.path[0], p.path[-1]))

        # generate the network
        for s, t in self.od:
            net_1 = cn.HigherOrderNetwork(s+'='+t, modified=False,
                                          sub_edges=set(), self_loop=False)

            for p in self.paths.st_paths(s, t):
                net_0 = cn.NodeAndPath(p)
                net_0['active'] = True
                net_0['original'] = True
                net_0['estimate'] = 0
                net_1.add_node(net_0)
                net_1['sub_edges'].update([e for e in p.edges])

            for i in range(net_1.number_of_nodes()-1):
                u = net_1.nodes[i]
                v = net_1.nodes[i+1]
                net_1.add_edge(u.id+'|'+u.id, u, u)
                net_1.add_edge(u.id+'|'+v.id, u, v)
                net_1.add_edge(v.id+'|'+u.id, v, u)

            v = net_1.nodes[-1]
            net_1.add_edge(v.id+'|'+v.id, v, v)

            self.add_node(net_1)

        _nodes = itertools.combinations(self.nodes(), 2)
        for s, t in _nodes:
            _common_edges = s['sub_edges'].intersection(
                t['sub_edges'])
            if len(_common_edges) > self.n_edges:
                self.add_edge(s.id+'<>'+t.id, s, t, common_edges=_common_edges,
                              n_original=len(_common_edges), n_new=0)

    def deactivate_path(self, e):
        self._network.remove_edge(e)
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
                P_st = cn.ksp(self._network, s, t, k=5)
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
                if len(_common_edges) > self.n_edges:
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
        for e in self._network.edges():
            e['volume'] = 0
            for net_1 in self.nodes():
                for net_0 in net_1.nodes():
                    if net_0.has_edge(e):
                        if original:
                            e['volume'] += net_0['flow']
                        else:
                            e['volume'] += net_0['estimate']
        _vol = [(e.id, e['volume']) for e in self._network.edges()]
        _vol.sort()
        # return np.array(list(self._network.edges('volume')))
        # return {e.id: e['volume'] for e in self._network.edges()}
        return np.array([n for _, n in _vol])

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

        _px = self.px
        A = self.transition_matrix(weight='n_new')

        for i in np.argwhere(A.diagonal() > 0):
            _sum = A[i].sum()-A[i, i]
            value = (_px * _sum)/(1-_px)
            A[i, i] = value

        with np.errstate(divide='ignore'):
            c = sparse.diags(1/A.sum(axis=1).A.ravel())

        T = c.dot(A)

        # T = self.transition_matrix(weight='n_new')
        x = np.array(list(self.nodes('modified'))).astype(int)
        x = x / x.sum()
        pt_1 = (T**10000).transpose().dot(x)

        pt_1 = np.nan_to_num(pt_1)

        for i, net_1 in enumerate(self.nodes()):
            x = np.array(list(net_1.nodes('flow')))
            T = net_1.transition_matrix(weight=True)
            pt = (T**10000).transpose().dot(x)
            #x_est = pt
            if net_1['modified']:
                x_est = pt
            else:
                x_est = pt * pt_1[i] + x * (1-pt_1[i])
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
