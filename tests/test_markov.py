#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_markov.py -- Test environment for markov processes
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-20
# Time-stamp: <Fre 2018-07-20 10:48 juergen>
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

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet
from cnet.algorithms.markov import cost_matrix, estimate_transition_matrix


def test_cost_matrix():
    C_ref = np.array([[0, 1, 2],
                      [1, 0, 1],
                      [2, 1, 0]])

    C = cost_matrix(n=3)

    assert np.array_equal(C, C_ref)

    C_ref = np.array([[0, 1, 4],
                      [1, 0, 1],
                      [4, 1, 0]])

    C = cost_matrix(n=3, mode='quadratic')

    assert np.array_equal(C, C_ref)


def test_estimate_transition_matrix():

    C = cost_matrix(n=3)
    x_1 = [2, 5, 1]
    x_2 = np.array([3, 3, 2])
    T = estimate_transition_matrix(x_1, x_2, C)

    T_ref = np.array([[1.0, 0.0, 0.0],
                      [0.2, 0.6, 0.2],
                      [0.0, 0.0, 1.0]])

    assert np.array_equal(T, T_ref)

    # start vector
    x_1 = np.array([531, 436, 292, 240, 0, 0])
    # end vector
    x_2 = np.array([0, 645, 0, 358, 322, 174])
    C = cost_matrix(n=len(x_1), mode='quadratic')
    T = estimate_transition_matrix(x_1, x_2, C)
    print(T)


# test_cost_matrix()
test_estimate_transition_matrix()
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
