#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : ex_simple_markov.py -- Example for Markov transitions
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-20
# Time-stamp: <Mon 2018-07-23 18:23 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import pandas

import numpy as np
from collections import defaultdict
from network2tikz import plot
from ex_networks import sioux_falls
import time

from joblib import Parallel, delayed


wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet as cn


class Scenario(object):
    """Generate a simulation scenario.

    """

    def __init__(self, removed=None, max_iter=10000):

        if removed is None:
            self.prefix = ''
            self.removed = None
        elif isinstance(removed, str):
            self.prefix = '_'+removed
            self.removed = [removed]
        elif isinstance(removed, list):
            self.prefix = '_'+'_'.join(removed)
            self.removed = removed

        self.max_iter = max_iter
        # file names
        network_data_file = './data/sioux_falls_network.tntp'
        trips_data_file = './data/sioux_falls_trips.tntp'
        original_network_file = './temp/markov/network.pkl'
        paths_file = './temp/markov/paths'+self.prefix+'.pkl'
        network_file = './temp/markov/network'+self.prefix+'.pkl'

        # generate data converter
        tntp = cn.TNTPConverter()

        # load initial data
        if os.path.isfile(original_network_file):
            self.original_network = cn.Network.load(original_network_file)
        else:
            self.original_network = tntp.network(
                network_data_file, prefix=('N', 'E'), zfill=2)

        self.od_flow = tntp.trips(trips_data_file, prefix='N', zfill=2)

        # load scenario data
        # if data is not available, generate new data
        if os.path.isfile(paths_file) and os.path.isfile(network_file):
            self.paths = cn.Paths.load(paths_file)
            self.network = cn.Network.load(network_file)
        else:
            self.paths, self.network = self.generate_paths(
                max_iter=self.max_iter)
            self.paths.save(paths_file)
            self.network.save(network_file)

        # generate list of nodes
        self.nodes = ['N'+str(i+1).zfill(2)
                      for i, n in enumerate(self.network.nodes)]

    def generate_paths(self, max_iter=100):
        """Generate flow paths from the traffic model"""
        network = self.original_network.copy()
        if self.removed:
            for edge in self.removed:
                network.remove_edge(edge)
        start_time = time.time()
        paths = cn.algorithms.msa_fast(network, self.od_flow, max_iter=max_iter)
        elapsed_time = time.time() - start_time
        print('Time of msa: ', elapsed_time)

        return paths, network

    def od_path_matrix(self, flow=False):
        """Some analysis of the paths"""
        n = self.network.number_of_nodes()
        od_path_matrix = np.zeros((n, n))
        for i, u in enumerate(self.nodes):
            for j, v in enumerate(self.nodes):
                P = self.paths.st_paths(
                    self.network.nodes[u], self.network.nodes[v])
                if flow:
                    value = sum([p['flow'] for p in P])
                else:
                    value = len(P)
                od_path_matrix[i][j] = value
        return od_path_matrix

    def od_matrix(self):
        """Returns the original od matrix"""
        n = self.network.number_of_nodes()
        od_matrix = np.zeros((n, n))
        for i, u in enumerate(self.nodes):
            for j, v in enumerate(self.nodes):
                od_matrix[i][j] = self.od_flow[u][v]

        return od_matrix


def _scenario(e):
    Scenario(e)


class MultiOrderModel(object):
    """Documentation for MultiOrderModel

    """

    def __init__(self, network=None, paths=None):

        # the underlying network for the multi-oder model
        self.network = network
        # the paths object from which this multi-order model was created
        # self.paths = paths

        # file names
        # TODO: fix this work around soon or later
        self.ksp_file = './temp/markov/ksp.pkl'

        # generate or load the k-shortest paths used in the model
        self.paths = self.ksp()

    def ksp(self, k=20):
        """Generate/load the k-shortest paths for the MOM"""

        # check if file exist already in the storage
        if os.path.isfile(self.ksp_file):
            KSP = cn.Paths.load(self.ksp_file)
        else:
            KSP = cn.Paths(name='k-shortest paths')
            for u in self.network.nodes:
                for v in self.network.nodes:
                    if u != v:
                        KSP.add_paths_from(
                            cn.ksp(self.network, u, v, k=k, weight=True))
            KSP.save(self.ksp_file)

        return KSP


class Analyzer(object):
    """Analyzer for the scenarios

    """

    def __init__(self, base_scenario, scenarios, multi_order_model):
        self.base = base_scenario
        self.scenarios = scenarios
        self.MOM = multi_order_model

        self.changes_file = './temp/changes.pkl'

    def changes(self):
        # generate/load changes
        # check if file exist already in the storage
        if os.path.isfile(self.changes_file):
            with open(self.changes_file, 'rb') as f:
                self.changes = pickle.load(f)
        else:
            self.changes = self.generate_changes()
            # Overwrites any existing file.
            with open(self.changes_file, 'wb') as f:
                pickle.dump(self.changes, f, pickle.HIGHEST_PROTOCOL)

        # analyze changes
        i = 0
        M = np.array([0, 0, 0])
        B = np.array([0, 0, 0])
        E = np.array([0, 0, 0])
        for c in self.changes:
            if c.T is not None and not c.has_subpath:
                # print('xxxxxxxxxx')
                s = c.move_statistic()
                # print(s)
                # # print(s[0])
                # print(c.T)
                # print(c.x0)
                # print(c.x1)
                # print(s[-1])
                # print(s[1:-1])
                M = np.vstack((M, s[1:-1]))
                B = np.vstack((B, s[0]))
                E = np.vstack((E, s[-1]))
                i += 1
            #     if c.has_subpath:
        #         i += 1
        #     if c.T is not None:
        #         j += 1
        print(i, len(self.changes))
        M = np.delete(M, 0, 0)
        B = np.delete(B, 0, 0)
        E = np.delete(E, 0, 0)
        print('m')
        M = M[~np.isnan(M).any(axis=1)]
        B = B[~np.isnan(B).any(axis=1)]
        E = E[~np.isnan(E).any(axis=1)]
        print(M.mean(axis=0))  # .sum(axis=1))
        print(M.std(axis=0))

        print('b')
        print(B.mean(axis=0))  # .sum(axis=1))
        print(B.std(axis=0))

        print('e')
        print(E.mean(axis=0))  # .sum(axis=1))
        print(E.std(axis=0))

        M = E
        print('m2')
        # M = M[M[:, 0] >= 0]
        # M = M[M[:, 0] <= 1]
        # M = M[M[:, 1] >= 0]
        # M = M[M[:, 1] <= 1]
        # M = M[M[:, 2] >= 0]
        # M = M[M[:, 2] <= 1]
        M = M[M[:, 2] == 0]

        print(M.mean(axis=0))  # .sum(axis=1))
        print(M.std(axis=0))

        # print(M)

        # plt.hist(M[:, 0], 50, density=True, facecolor='g', alpha=0.5)
        # plt.hist(M[:, 1], 50, density=True, facecolor='r', alpha=0.5)
        # plt.hist(M[:, 2], 50, density=True, facecolor='b', alpha=0.5)
        # plt.grid(True)
        # plt.xlim((0, 1))
        # plt.show()
        # plt.savefig('M.pdf')

        # plt.hist(B[:, 0], 50, density=True, facecolor='g', alpha=0.5)
        # plt.hist(B[:, 1], 50, density=True, facecolor='r', alpha=0.5)
        # plt.hist(B[:, 2], 50, density=True, facecolor='b', alpha=0.5)
        # plt.grid(True)
        # plt.xlim((0, 1))
        # plt.savefig('B.pdf')

        # plt.hist(E[:, 0], 50, density=True, facecolor='g', alpha=0.5)
        # plt.hist(E[:, 1], 50, density=True, facecolor='r', alpha=0.5)
        # plt.hist(E[:, 2], 50, density=True, facecolor='b', alpha=0.5)
        # plt.grid(True)
        # plt.xlim((0, 1))
        # plt.savefig('E.pdf')

        # plt.scatter(M[:, 1], M[:, 2])
        # plt.show()

        dtype = [('Col1', 'float32'), ('Col2', 'float32'), ('Col3', 'float32')]
        index = ['Row'+str(i) for i in range(1, len(M)+1)]

        df = pandas.DataFrame(M, index=index)
        sns.pairplot(df)
        plt.show()

    def generate_changes(self):
        """Analyze changes between the base and the other scenarios"""
        changes = []
        for S in self.scenarios:
            subpath = [self.base.network.edges[S.removed[0]].u.id,
                       self.base.network.edges[S.removed[0]].v.id]
            for u in self.base.nodes:  # ['N01']:  #
                for v in self.base.nodes:  # ['N02']:  #
                    P = self.MOM.paths.st_paths(u, v)
                    P0 = self.base.paths.st_paths(u, v)
                    PS = S.paths.st_paths(u, v)

                    x0 = np.zeros(len(P))
                    x1 = np.zeros(len(P))
                    has_subpath = False
                    for i, p in enumerate(P):
                        for p0 in P0:
                            # TODO: Enable also multiple subpaths
                            if p0.has_subpath(subpath):
                                has_subpath = True
                            if p.path == p0.path:
                                x0[i] = np.round(p0['flow'], 0)
                        for ps in PS:
                            if p.path == ps.path:
                                x1[i] = np.round(ps['flow'], 0)

                    if np.array_equal(x0, x1):
                        T = None
                    else:
                        C = cn.cost_matrix(n=len(x0), mode='quadratic')
                        T = cn.estimate_transition_matrix(x0, x1, C)
                    item = DataItem(scenario=S.prefix[1:],
                                    origin=u,
                                    destination=v,
                                    T=T,
                                    x0=x0,
                                    x1=x1,
                                    has_subpath=has_subpath)
                    changes.append(item)
        return changes


class DataItem(object):
    """Documentation for DataItem

    """

    def __init__(self, scenario, origin, destination, T, x0, x1, has_subpath):
        self.scenario = scenario
        self.origin = origin
        self.destination = destination
        self.T = T
        self.x0 = x0
        self.x1 = x1
        self.has_subpath = has_subpath

    def move_statistic(self):

        if self.T is not None:
            down = np.triu(self.T, 1).sum(axis=1)
            up = np.tril(self.T, -1).sum(axis=1)
            stay = np.diag(np.diag(self.T)).sum(axis=1)

            c = np.vstack((up, stay, down)).transpose()
            c = c[~np.all(c == 0, axis=1)]
            c = c/c.sum(axis=1)[:, None]
            return c
        else:
            return None


def main():
    # generate base scenario (i.e. network in default condition)
    S0 = Scenario()

    # Generate scenarios where 1 edge was removed
    # Parallel(n_jobs=7)(delayed(_scenario)(args) for args in S0.network.edges)

    # scenarios = []
    # for e in S0.network.edges:
    #     scenarios.append(Scenario(e))

    # generate multi-order model from the base scenario
    # NOTE: Right now the data is loaded from the hard drive
    MOM = MultiOrderModel()

    # generate test scenario (i.e. a singe scenario to test the analyze)
    S1 = Scenario('E01')

    # generate analyzer object
    A = Analyzer(S0, [S1], MOM)
    # A = Analyzer(S0, scenarios, MOM)

    # Analyze the changes between the base and the scenarios
    A.changes()


def main_old():
    # generate base scenario (i.e. network in default condition)
    S0 = Scenario()

    # Generate scenarios where 1 edge was removed
    # Parallel(n_jobs=7)(delayed(_scenario)(args) for args in S1.network.edges)

    # # print overview of some results
    # C0 = sum([e.cost for e in S0.network.edges()])
    # M0 = S0.od_path_matrix()
    # F0 = np.round(S0.od_path_matrix(flow=True), 0)
    # print(C0)

    # paths_sum = 0
    # paths_max = []
    # for e in S0.network.edges:
    #     #print('Scenario: {}'.format(e))
    #     S = Scenario(e)
    #     C = sum([e.cost for e in S.network.edges()])
    #     M = S.od_path_matrix()
    #     paths_max.append(np.max(M))
    #     paths_sum += np.sum(M)
    #     F = np.round(S.od_path_matrix(flow=True), 0)
    #     print('Scenario: {}'.format(e), C-C0, np.sum(F) -
    #           np.sum(F0), np.max(M), np.mean(M))

    # print(paths_sum)
    # print(max(paths_max))

    # ksp_1_2 = cn.ksp(S0.network, 'N01', 'N02', k=3, weight=True)
    # for p in ksp_1_2:
    #     print(p)

    # S1 = Scenario('E01')

    # M0 = S0.od_path_matrix(flow=True)
    # # print(M0)
    # print(np.round(M0.sum(axis=1), 0))

    # OD0 = S0.od_matrix()
    # print(OD0.sum(axis=1))

    # C0 = sum([e.cost for e in S0.network.edges()])
    # C1 = sum([e.cost for e in S1.network.edges()])
    # print(C0)
    # print(C1)
    # print(np.round(M0.sum(axis=1), 0)-OD0.sum(axis=1))
    # print((M0.sum()-OD0.sum())/OD0.sum()*100)
    # print(OD0.sum())
    # print(S1.prefix)
    # S2 = Scenario('E01')
    # print(S2.prefix)
    # S3 = Scenario(['E01', 'E20'])
    # print(S3.prefix)

    # print(S3.od_path_matrix())

    # M = od_path_matrix(paths, network, flow=True)
    # print(M)
    # print(M.sum(axis=1))

    # s = 0
    # for k, v in od_flow['N01'].items():
    #     s += v

    # print(s)
    # run analysis with deleted edge


def test():
    S0 = Scenario()
    S1 = Scenario('E01')

    # F0 = S0.od_path_matrix(flow=True)
    # F1 = S1.od_path_matrix(flow=True)

    # P0 = S0.od_path_matrix()
    # P1 = S1.od_path_matrix()
    # print(P0)
    # print(P1)
    # #np.savetxt('p.csv', P1-P0, delimiter=',')

    # for e in S0.network.edges:
    #     V0 = int(S0.network.edges[e].volume)
    #     if e != 'E01':
    #         V1 = int(S1.network.edges[e].volume)
    #     else:
    #         V1 = 0
    #     print(e, V0, V1, V1-V0, round(100*((V1-V0) / V0), 2))

    i = 0
    for p in S0.paths:
        if p.has_subpath(['N01', 'N02']):
            print(p.path, p.weight())
            i += 1

    u = 'N01'
    v = 'N02'
    print(i)
    P0_uv = S0.paths.st_paths(u, v)
    for p in S0.paths.st_paths(u, v):
        print(p.path, np.round(p['flow'], 0))

    print('xxxxxxxx')
    for p in S1.paths.st_paths(u, v):
        print(p.path, np.round(p['flow'], 0))

    print('yyyyyy')
    KSP = cn.ksp(S0.network, u, v, k=10, weight=True)
    for p in KSP:
        print(p.path, p.weight())

    P0_uv = S0.paths.st_paths(u, v)
    P1_uv = S1.paths.st_paths(u, v)

    x0 = np.zeros(len(KSP))
    x1 = np.zeros(len(KSP))
    for i, p in enumerate(KSP):
        for p0 in P0_uv:
            if p.path == p0.path:
                x0[i] = np.round(p0['flow'], 0)
        for p1 in P1_uv:
            if p.path == p1.path:
                x1[i] = np.round(p1['flow'], 0)

    print(x0, x1)
    C = cn.cost_matrix(n=len(x0), mode='quadratic')
    T = cn.estimate_transition_matrix(x0, x1, C)
    print(T)


def generate_ksp(S, k=20):
    """Generate/load the k-shortest paths for a scenario"""
    ksp_file = './temp/markov/ksp.pkl'
    if os.path.isfile(ksp_file):
        KSP = cn.Paths.load(ksp_file)
    else:
        KSP = cn.Paths(name='k-shortest paths')
        for u in S.nodes:
            for v in S.nodes:
                if u != v:
                    KSP.add_paths_from(
                        cn.ksp(S.network, u, v, k=k, weight=True))
        KSP.save(ksp_file)

    return KSP


def analyze_scenarios():
    S0 = Scenario()
    S = Scenario('E01')
    KSP = generate_ksp(S0)
    print(len(KSP))

    changes = defaultdict(dict)
    for u in S0.nodes:
        for v in S0.nodes:
            P = KSP.st_paths(u, v)
            P0 = S0.paths.st_paths(u, v)
            PS = S.paths.st_paths(u, v)

            x0 = np.zeros(len(P))
            x1 = np.zeros(len(P))
            for i, p in enumerate(P):
                for p0 in P0:
                    if p.path == p0.path:
                        x0[i] = np.round(p0['flow'], 0)
                for ps in PS:
                    if p.path == ps.path:
                        x1[i] = np.round(ps['flow'], 0)

            if np.array_equal(x0, x1):
                changes[u][v] = None
            else:
                C = cn.cost_matrix(n=len(x0), mode='quadratic')
                T = cn.estimate_transition_matrix(x0, x1, C)

                up = np.triu(T, 1).sum(axis=1)
                lo = np.tril(T, -1).sum(axis=1)
                di = np.diag(np.diag(T)).sum(axis=1)

                c = np.vstack((lo, di, up)).transpose()
                c = c[~np.all(c == 0, axis=1)]
                changes[u][v] = c

    print(changes)

    changes_file = './temp/changes.pkl'
    with open(changes_file, 'wb') as f:  # Overwrites any existing file.
        pickle.dump(changes, f, pickle.HIGHEST_PROTOCOL)

    # with open(changes_file, 'rb') as f:
    #     data = pickle.load(f)


def some_stats():
    S0 = Scenario()
    changes_file = './temp/changes.pkl'
    with open(changes_file, 'rb') as f:
        data = pickle.load(f)

    # print(data)
    X = np.array([0, 0, 0])
    for u in S0.nodes:
        for v in S0.nodes:
            if data[u][v] is not None:
                print(data[u][v])
                X = np.vstack((X, data[u][v]))
    Y = X.transpose()
    # print(Y.mean(axis=1))
    # np.savetxt('x.csv', Y, delimiter=',')

    val0 = []
    for y in Y[0]:
        if y > -50:
            val0.append(y)

    val1 = []
    for y in Y[1]:
        if y > -50:
            val1.append(y)

    val2 = []
    for y in Y[2]:
        if y > -50:
            val2.append(y)

            # a = Y[0]
    # print(a)
    # Y0 = np.trim_zeros(Y[0])
    # print(Y0)
    # the histogram of the data
    n, bins, patches = plt.hist(
        val0, 50, density=True, facecolor='g', alpha=0.5)
    n, bins, patches = plt.hist(
        val1, 50, density=True, facecolor='r', alpha=0.5)
    n, bins, patches = plt.hist(
        val2, 50, density=True, facecolor='b', alpha=0.5)

    # plt.xlabel('Smarts')
    # plt.ylabel('Probability')
    # plt.title('Histogram of IQ')
    # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    # plt.axis([40, 160, 0, 0.03])
    plt.grid(True)
    plt.show()


def create_net(n):
    net = cn.Network(directed=True)
    if n == 2:
        net.add_edge('0-0', '0', '0', weight=.8)
        net.add_edge('0-1', '0', '1', weight=.2)
        net.add_edge('1-1', '1', '1', weight=.8)
        net.add_edge('1-0', '1', '1', weight=.2)
    elif n > 2:
        # p_beta = np.random.beta(0.1553965, 1.3506398)
        # net.add_edge('0-0', '0', '0', weight=1-p_beta)
        # net.add_edge('0-1', '0', '1', weight=p_beta)
        net.add_edge('0-0', '0', '0', weight=.9)
        net.add_edge('0-1', '0', '1', weight=.1)

        for i in range(1, n-1):

            # beta_10 = 1
            # beta_12 = 1
            # while (beta_10+beta_12) > 1:
            #     beta_10 = np.random.beta(0.1286189, 0.802977)
            #     beta_12 = np.random.beta(0.1041097, 0.9622697)
            # net.add_edge(str(i)+'-'+str(i-1), str(i), str(i-1), weight=beta_10)
            # net.add_edge(str(i)+'-'+str(i), str(i), str(i),
            #              weight=1-(beta_10+beta_12))
            # net.add_edge(str(i)+'-'+str(i+1), str(i), str(i+1), weight=beta_12)

            net.add_edge(str(i)+'-'+str(i-1), str(i), str(i-1), weight=.2)
            net.add_edge(str(i)+'-'+str(i), str(i), str(i), weight=.6)
            net.add_edge(str(i)+'-'+str(i+1), str(i), str(i+1), weight=.2)

        net.add_edge(str(n-1)+'-'+str(n-2), str(n-1), str(n-2), weight=.2)
        net.add_edge(str(n-1)+'-'+str(n-1), str(n-1), str(n-1), weight=.8)
        # p_beta = np.random.beta(0.126337, 0.5771517)
        # net.add_edge(str(n-1)+'-'+str(n-2), str(n-1), str(n-2), weight=p_beta)
        # net.add_edge(str(n-1)+'-'+str(n-1), str(n-1), str(n-1), weight=1-p_beta)

    return net


def create_net_random(n):
    net = cn.Network(directed=True)
    if n == 2:
        net.add_edge('0-0', '0', '0', weight=.8)
        net.add_edge('0-1', '0', '1', weight=.2)
        net.add_edge('1-1', '1', '1', weight=.8)
        net.add_edge('1-0', '1', '1', weight=.2)
    elif n > 2:
        p_beta = np.random.beta(0.1553965, 1.3506398)
        net.add_edge('0-0', '0', '0', weight=1-p_beta)
        net.add_edge('0-1', '0', '1', weight=p_beta)
        # net.add_edge('0-0', '0', '0', weight=.9)
        # net.add_edge('0-1', '0', '1', weight=.1)

        for i in range(1, n-1):

            beta_10 = 1
            beta_12 = 1
            while (beta_10+beta_12) > 1:
                beta_10 = np.random.beta(0.1286189, 0.802977)
                beta_12 = np.random.beta(0.1041097, 0.9622697)
            net.add_edge(str(i)+'-'+str(i-1), str(i), str(i-1), weight=beta_10)
            net.add_edge(str(i)+'-'+str(i), str(i), str(i),
                         weight=1-(beta_10+beta_12))
            net.add_edge(str(i)+'-'+str(i+1), str(i), str(i+1), weight=beta_12)

            # net.add_edge(str(i)+'-'+str(i-1), str(i), str(i-1), weight=.2)
            # net.add_edge(str(i)+'-'+str(i), str(i), str(i), weight=.6)
            # net.add_edge(str(i)+'-'+str(i+1), str(i), str(i+1), weight=.2)

        # net.add_edge(str(n-1)+'-'+str(n-2), str(n-1), str(n-2), weight=.2)
        # net.add_edge(str(n-1)+'-'+str(n-1), str(n-1), str(n-1), weight=.8)
        p_beta = np.random.beta(0.126337, 0.5771517)
        net.add_edge(str(n-1)+'-'+str(n-2), str(n-1), str(n-2), weight=p_beta)
        net.add_edge(str(n-1)+'-'+str(n-1), str(n-1), str(n-1), weight=1-p_beta)

    return net


def testxxx():
    np.set_printoptions(suppress=True)
    changes_file = './temp/changes_all.pkl'
    with open(changes_file, 'rb') as f:
        changes = pickle.load(f)

    print(len(changes))

    ET1 = np.array([[0.94430099, 0.05512928, 0.00010288],
                    [0.05899295, 0.90208739, 0.03667965],
                    [0.,         0.23861384, 0.67215412]])

    ET2 = np.array([[0.88919314, 0.10238225, 0.00629525],
                    [0.14395017, 0.74011793, 0.10065299],
                    [0.02551428, 0.20216671, 0.69839375]])

    ET = ET2
    V = np.zeros((3, 3))
    v11 = []
    i = 0
    X = []
    Z = []
    error_1 = 0
    error_2 = 0
    error_3 = 0
    error_4 = 0
    error_5 = 0
    for c in changes:
        if c.T is not None and not c.has_subpath:
            n = len(c.move_statistic())
            if n == 3 and c.T[0, 0] > 0:
                print(c.origin, c.destination, 'xxxxxxxxxxx')
                a = c.x0[:n]
                b = c.x1[:n]

                print(a)
                print(b)
                # _error = []
                # for j in range(10):
                net = create_net(n)
                T = net.transition_matrix(weight=True).todense()
                Tn = np.asarray(T)
                # print(type(T))
                # print(type(ET))
                Z.append(Tn)
                x = a.dot(np.linalg.matrix_power(Tn, 1000))
                print('net ---------------')
                #print('est', x)
                # print('dif', b-x)
                print('dif', 1-x/b)
                # _error.append(np.sum((b-x)**2))
                #error_1 += np.mean(_error)
                error_1 += np.sum((b-x)**2)
                #error_1 += np.sum((b-x))
                print('stat ---------------')
                x = a.dot(ET)
                print('dif', 1-x/b)
                #print('dif', np.abs(b-x)/b*100)
                # print('est', x)
                # print('dif', b-x)
                error_2 += np.sum((b-x)**2)
                #error_2 += np.sum((b-x))

                _x = []
                _e = []
                print('net random ---------------')
                for j in range(10):
                    net = create_net_random(n)
                    T = net.transition_matrix(weight=True).todense()
                    Tn = np.asarray(T)
                    x = a.dot(np.linalg.matrix_power(Tn, 1))
                    #print('est', x)
                    #print('dif', b-x)
                    _x.append(x)
                    _e.append(np.sum((b-x)**2))
                #print('dif', b-np.mean(_x))
                #error_3 += np.sum((b-np.mean(_x))**2)
                error_3 += min(_e)
                error_4 += max(_e)
                error_5 += np.mean(_e)
                # x = a.dot(np.linalg.matrix_power(ET, 1000))
                # print('s stat')
                # print(x)
                # print(b-x)
                # error_3 += np.sum((b-x)**2)
                #error_3 += np.sum((b-x))
                # #print(c.T[:n, :n])
                # V += c.T[:n, :n]
                X.append(c.T[:n, :n])
                # v11.append(c.T[0, 0])
                i += 1
    print(i)
    print('total error')
    print(error_1/i)
    print(error_2/i)
    print(error_3/i)
    print(error_4/i)
    print(error_5/i)

    print('error per od paths')
    print(np.sqrt(error_1/i))
    print(np.sqrt(error_2/i))
    print(np.sqrt(error_3/i))
    print(np.sqrt(error_4/i))
    print(np.sqrt(error_5/i))

    Y = np.dstack(X)
    # print(Y.shape)
    print(np.mean(Y, axis=2))
    #print(np.mean(Y, axis=2)[0, 1])
    print(np.std(Y, axis=2))

    print('dddddd')
    Q = np.dstack(Z)
    print(np.mean(Q, axis=2))
    print(np.std(Q, axis=2))
    print('ssssdddddd')
    print(np.mean(Y, axis=2)-np.mean(Q, axis=2))
    print(np.mean(Y, axis=2)-np.std(Q, axis=2))

    # print(V/i)
    # print(i)
    # # print(v11)
    # print(np.mean(v11))
    # print(np.std(v11))
    # S = Scenario('E01')
    # S0 = Scenario()
    # for p in S0.paths.st_paths('N07', 'N03'):
    #     print(p.path)

    # a12 = Y[0, 1, :]
    # a12 = a12[a12 >= 0]
    # a12 = a12[a12 <= 1]

    # a32 = Y[2, 1, :]
    # print('ddddddd', np.mean(a32))
    # a32 = a32[a32 >= 0]
    # a32 = a32[a32 <= 1]

    # a21 = Y[1, 0, :]
    # print('ddddddd', np.mean(a21))
    # a21 = a21[a21 >= 0]
    # a21 = a21[a21 <= 1]

    # a23 = Y[1, 2, :]
    # print('ddddddd', np.mean(a23))
    # a23 = a23[a23 >= 0]
    # a23 = a23[a23 <= 1]

    # beta_10 = np.random.beta(0.1286189, 0.802977)
    # beta_12 = np.random.beta(0.1041097, 0.9622697)

    # beta = np.random.beta(0.1553965, 1.3506398, size=10000)
    # print(np.mean(beta))
    # print(np.std(beta))
    # # plt.hist(a11, 100, density=True, facecolor='g', alpha=0.5)
    # # plt.hist(beta, 100, density=True, facecolor='r', alpha=0.5)
    # # plt.grid(True)
    # # # plt.xlim((0, 1))
    # # plt.show()

    # np.savetxt('a12.csv', a12, delimiter=',')
    # np.savetxt('a32.csv', a32, delimiter=',')
    # np.savetxt('a21.csv', a21, delimiter=',')
    # np.savetxt('a23.csv', a23, delimiter=',')

    # net = create_net(n=5)

    # for e in net.edges:
    #     print(e)

    # for n in net.nodes:
    #     print(n)

    # layout = {n: (int(n), 0) for n in net.nodes}

    # visual_style = {}
    # visual_style['layout'] = layout
    # visual_style['node_label_as_id'] = True
    # visual_style['edge_curved'] = 0.1
    # visual_style['canvas'] = (10, 10)
    # plot(net, **visual_style)

    # T = net.transition_matrix(weight=True)
    # print(T)

    # T = np.array([[0.8, 0.2, 0],
    #               [0.1, 0.8, 0.1],
    #               [0, 0.2, 0.8]])

    # pi = np.array([1, 0, 0])

    # print(pi.dot(np.linalg.matrix_power(T, 1000)))


def testxx():

    beta_10 = 1
    beta_12 = 1
    while (beta_10+beta_12) > 1:
        beta_10 = np.random.beta(0.1286189, 0.802977)
        beta_12 = np.random.beta(0.1041097, 0.9622697)
    print(beta_10, beta_12)


if __name__ == '__main__':
    # main()
    testxxx()
    # test()
    # analyze_scenarios()
    # some_stats()
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
