#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_diffusion.py -- Test environment for diffusion processes
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-06-27
# Time-stamp: <Don 2018-06-28 14:14 juergen>
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
import numpy as np

import pytest
import os
import sys

from scipy import sparse
import scipy.linalg as spl
import scipy.sparse.linalg as sla

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))
import cnet
from cnet import Network
from cnet.algorithms.diffusion import RandomWalkDiffusion


@pytest.fixture  # (params=[True,False])
def net():
    net = Network(directed=False)

    net.add_node('a', x=0, y=0)
    net.add_node('b', x=4000, y=3000)
    net.add_node('c', x=8000, y=0)
    net.add_node('d', x=4000, y=7000)
    net.add_node('e', x=8000, y=10000)
    net.add_node('f', x=4000, y=10000)
    net.add_node('g', x=0, y=10000)

    net.add_edge('ab', 'a', 'b', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('ac', 'a', 'c', length=8000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('bc', 'b', 'c', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('bd', 'b', 'd', length=4000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('de', 'd', 'e', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('df', 'd', 'f', length=3000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('dg', 'd', 'g', length=5000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('ef', 'e', 'f', length=4000.0,
                 capacity=3600, free_flow_speed=27.78)
    net.add_edge('fg', 'f', 'g', length=4000.0,
                 capacity=3600, free_flow_speed=27.78)
    return net


def test_random_walk_diffusion(net):
    # net.summary()

    rwd = RandomWalkDiffusion(net)
    assert rwd.walkers == 5

    pi = rwd.stationary_distribution()
    assert len(pi) == net.number_of_nodes()

    p_1 = rwd.step(1, node='a')
    assert p_1['b'] == 0.5
    assert p_1['c'] == 0.5

    p_2 = rwd.step(2, node='a')
    assert round(p_2['a'], 5) == round(5/12, 5)
    assert round(p_2['b'], 5) == round(1/4, 5)
    assert round(p_2['c'], 5) == round(1/6, 5)
    assert round(p_2['d'], 5) == round(1/6, 5)


def test_random_walk_diffusion_speed(net):
    rwd = RandomWalkDiffusion(net)
    s = rwd.speed()
    assert 15 < s < 25


test_random_walk_diffusion_speed(net())

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
