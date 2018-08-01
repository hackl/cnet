#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : scenario.py -- Scenario generator for the example
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-01
# Time-stamp: <Mit 2018-08-01 11:15 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
import csv
import time
import numpy as np
from collections import defaultdict
from setup_example import SetupExample
wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '../..')))
import cnet as cn


class Scenario(SetupExample):
    """Generator for simulation scenarios.

    """

    def __init__(self, modified=None, max_iter=10000, *args, **kwds):
        SetupExample.__init__(self, *args, **kwds)
        self.initialize()
        # initialize variables
        if modified is None:
            self.prefix = ''
            self.modified = None
        elif isinstance(modified, str):
            self.prefix = '_'+modified
            self.modified = [modified]
        elif isinstance(modified, list):
            self.prefix = '_'+'_'.join(modified)
            self.modified = modified

        self.max_iter = max_iter

        # initialize path to the original data files
        network_file = self.data_dir + \
            kwds.get('network_file', 'network.tntp')
        trips_file = self.data_dir + \
            kwds.get('trips_file', 'trips.tntp')

        # initialize temporla file names
        original_network = '{}network.pkl'.format(self.temp_dir)
        temp_network = '{}network{}.pkl'.format(self.temp_dir, self.prefix)
        temp_paths = '{}paths{}.pkl'.format(self.temp_dir, self.prefix)

        # generate data converter
        tntp = cn.TNTPConverter()

        # load temp data if available
        if os.path.isfile(original_network):
            self.original_network = cn.Network.load(original_network)
        else:
            if network_file.endswith('.tntp'):
                self.original_network = tntp.network(network_file,
                                                     prefix=('N', 'E'),
                                                     zfill=2)
            else:
                print('The network format is not yet supported!')
                raise NotImplementedError

        if trips_file.endswith('.tntp'):
            self.od_flow = tntp.trips(trips_file, prefix='N', zfill=2)
        elif trips_file.endswith('.csv'):
            self.od_flow = self.od_from(trips_file)

        # load scenario data
        # if data is not available, generate new data
        if os.path.isfile(temp_paths) and os.path.isfile(temp_network):
            self.paths = cn.Paths.load(temp_paths)
            self.network = cn.Network.load(temp_network)
        else:
            self.paths, self.network = self.generate_paths(
                max_iter=self.max_iter)
            self.paths.save(temp_paths)
            self.network.save(temp_network)

        # generate list of nodes
        self.nodes = [n for n in self.network.nodes]
        self.nodes.sort()

    def od_from(self, filename):
        """Load od matrix from csv file."""
        od_dict = defaultdict(dict)
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            data = [r for r in reader]

        for i, o in enumerate(headers):
            for j, d in enumerate(headers):
                od_dict[o][d] = float(data[i][j])
        return od_dict

    def generate_paths(self, max_iter=100):
        """Generate flow paths from the traffic model"""
        network = self.original_network.copy()
        if self.modified:
            for edge in self.modified:
                network.remove_edge(edge)
        start_time = time.time()
        paths = cn.algorithms.msa_fast(network, self.od_flow,
                                       max_iter=max_iter)
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


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
