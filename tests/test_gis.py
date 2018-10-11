#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_matsim.py -- Test environment for the matsim converter
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-15
# Time-stamp: <Mit 2018-10-10 17:17 juergen>
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
import pytest
import os
import sys
import time
import pickle

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet


def test_network():
    print('-' * 30)
    sfc = cnet.SHPConverter()
    #network = sfc.network('test_network.xml.gz')
    #network = sfc.network('test_network.xml', prefix=('N', 'E'), zfill=3)
    network = sfc.network('./shp/roads_clean.shp', prefix=('N', 'E'), zfill=3)
    network.summary()


def test_centroids():
    sfc = cnet.SHPConverter()
    network = sfc.network('./shp/roads_clean.shp', prefix=('N', 'E'), zfill=3)
    centroides = sfc.centroids('./shp/centroids.shp', network=network)
    print(centroides)


# def test_trips():
#     sfc = cnet.SHPConverter()
#     network = sfc.network('./shp/roads.shp', prefix=('N', 'E'), zfill=3)
#     centroids = sfc.centroids('./shp/centroids.shp', network=network)
#     trips = sfc.trips('./shp/od.csv', centroids=centroids)
#     print(trips)

# def test_trips():
#     sfc = cnet.SHPConverter()
#     network = sfc.network('./xshp/roads.shp', prefix=('N', 'E'), zfill=3)
#     centroids = sfc.centroids('./xshp/centroids.shp', network=network)
#     trips = sfc.trips('./xshp/od.csv', centroids=centroids)
#     # print(trips)

#     cost, path = cnet.dijkstra(network, 'N012', 'N001')
#     print(cost, path)


def test_trips():
    sfc = cnet.SHPConverter()
    #network = sfc.network('./shp/chur_network.shp', prefix=('N', 'E'), zfill=3)
    network = sfc.network('./shp/edges.shp', prefix=('N', 'E'), zfill=3)
    network.summary()
    centroids = sfc.centroids('./shp/chur_centroids.shp', network=network)
    trips = sfc.trips('./shp/od.csv', centroids=centroids)

    network.save('chur_test.pkl')

    pickle.dump(trips, open("trips_test.pkl", "wb"))

    network = cnet.RoadNetwork.load('chur_test.pkl')
    trips = pickle.load(open("trips_test.pkl", "rb"))

    lt = list(trips)
    lt.sort()
    print(lt)

    print(centroids[10])  # 'N014'
    print(centroids[33])  # 'N431'
    u = 'N014'
    v = 'N431'
    print(network.nodes[u]['coordinate'])
    print(network.nodes[v]['coordinate'])
    # cost, path = cnet.dijkstra(network, u, v)
    # print(cost, path)

    # cost, path = cnet.shortest_path(network,  u, v)
    # print(cost, path)

    start_time = time.time()
    paths = cnet.algorithms.msa_fast(
        network, trips, max_iter=10, enable_paths=True)
    elapsed_time = time.time() - start_time
    print('time of f-w: ', elapsed_time)

    network.save('chur_test_calc.pkl')

    for p in paths:
        print(p['flow'])
    print(len(paths))


# test_network()
# test_centroids()
test_trips()
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
