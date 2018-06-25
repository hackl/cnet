#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_traffic_assignment.py -- Test function for the traffic assignment
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-06-25
# Time-stamp: <Mon 2018-06-25 15:09 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================

import pytest
import os
import sys
import time

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import cnet
from cnet import Network
from cnet.algorithms.traffic_assignment import msa, msa_fast
from cnet.classes.road_network import RoadNetwork

import timeit


@pytest.fixture  # (params=[True,False])
def net():

    net = RoadNetwork()
    net.add_edge('E001', 'N001', 'N005', free_flow_speed=1,
                 length=12.0, capacity=250.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E002', 'N001', 'N007', free_flow_speed=1,
                 length=4.00, capacity=150.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E003', 'N002', 'N006', free_flow_speed=1,
                 length=11.0, capacity=250.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E004', 'N002', 'N007', free_flow_speed=1,
                 length=4.00, capacity=150.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E005', 'N005', 'N003', free_flow_speed=1,
                 length=12.0, capacity=250.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E006', 'N005', 'N008', free_flow_speed=1,
                 length=3.00, capacity=150.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E007', 'N006', 'N004', free_flow_speed=1,
                 length=11.0, capacity=250.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E011', 'N006', 'N008', free_flow_speed=1,
                 length=5.00, capacity=150.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E009', 'N007', 'N008', free_flow_speed=1,
                 length=10.0, capacity=250.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E010', 'N008', 'N005', free_flow_speed=1,
                 length=4.00, capacity=150.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E008', 'N008', 'N006', free_flow_speed=1,
                 length=4.00, capacity=150.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E012', 'N008', 'N009', free_flow_speed=1,
                 length=12.0, capacity=250.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E013', 'N009', 'N003', free_flow_speed=1,
                 length=4.00, capacity=150.0, p1=(0, 0), p2=(0, 0))
    net.add_edge('E014', 'N009', 'N004', free_flow_speed=1,
                 length=3.00, capacity=150.0, p1=(0, 0), p2=(0, 0))

    return net


@pytest.fixture  # (params=[True,False])
def od_flow():
    return {"N002": {"N004": 185, "N003": 140}, "N001": {"N004": 150, "N003": 200}}


def test_msa(net, od_flow):
    start_time = time.time()
    msa(net, od_flow)
    elapsed_time = time.time() - start_time
    print('time of f-w: ', elapsed_time)

    # msa(net, od_flow)

    # num = 10
    # t = timeit.Timer(lambda: msa(net, od_flow))
    # print(t.timeit(number=num))
    # pass


def test_msa_fast(net, od_flow):
    start_time = time.time()
    P = msa_fast(net, od_flow)
    elapsed_time = time.time() - start_time
    print('time of f-w: ', elapsed_time)

    for p in P:
        print(p['flow'])
    # for e in net.edges('length'):
    #     print(e)

    # for e in net.edges(data=True):
    #     print(e)

    # print(net.edges['E001'].volume)
    # print(net.edges['E001'].cost)
    # print(net.edges['E001'].weight())
    # num = 10
    # t = timeit.Timer(lambda: msa_fast(net, od_flow))
    # print(t.timeit(number=num))


test_msa_fast(net(), od_flow())

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
