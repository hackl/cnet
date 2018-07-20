#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : markov.py -- Markov processes
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-20
# Time-stamp: <Fre 2018-07-20 10:29 juergen>
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
from cnet import logger
from cnet.utils.exceptions import CnetError, CnetNotImplemented
import cvxpy as cvx
log = logger(__name__)


def cost_matrix(n, mode='linear'):
    """Cost matrix indicating the costs for changing paths.

    The cost matrix C = (c_ij) is an indicator for some kind of degree of
    difficulty to transfer from path i to path j. This can be interpreted as the
    drivers utility to change from its preferable path.

    Parameters
    ----------
    n : int
        Number of paths which can be chosen.

    mode : str, optional (default = 'linear') Type of the cost function. Per
        default the costs increase linear, i.e. from node 1 to 2 the cost is 1
        and for 1 to 3 is 2. With mode = 'quadratic' the costs increase
        quadratic i.e. from 1 to 3 the costs are 2**2 = 4.

    Returns
    -------
    C : numpy.array
        A cost matrix indicating the costs of changing paths.

    TODO
    ----
    Add cost function dependent on the path travel costs.

    """
    # set up empty cost matrix
    C = np.zeros((n, n))

    # iterate through the elements of the matrix and assign cost values
    for i in range(0, n-1):
        for j in range(i+1, n):
            # TODO: replace j-i with the actual cost function.
            if mode == 'linear':
                C[i, j] = (j-i)
            else:
                C[i, j] = (j-i)**2
    # make the cost matrix symmetric
    C += C.T
    # return the cost matrix
    return C


def estimate_transition_matrix(x_1, x_2, C, verbose=False):
    """Estimation of the transition matrix given two states and a cost matrix.

    The estimation of the transition matrix expressed as a minimization
    problem, minimizing the costs for the user changing the paths.

    .. math::
       \min \sum_i \sum_j x_ij \cdot c_ij

    subjected to the constrains

    .. math::
       \sum_j x_ij &= x_1\\
       \sum_i x_ij &= x_2\\
       x_ij &\leg 0

    Matrix X is normalized to a row sum = 1

    .. math::
       x_ij / x_{1,i}

    Parameters
    ----------
    x_1 : list or numpy.array
        A vector with the initial state (e.g. at time t).

    x_2 : list or numpy.array
        A vector with the final state (e.g. at time t+1)

    C : numpy.array
        A cost matrix indicating the costs of changing paths.

    verbose : Boole, optional (default = False)
        If this option is enabled, information of the optimization problem is
        printed to the terminal. Per default this option is disabled.

    Returns
    -------
    T : numpy.array (or spare a matrix?)
        A Transition matrix describing the transition from x_1 to x_2.

    """

    # initialize vectors
    if isinstance(x_1, list):
        x_1 = np.asarray(x_1)
    elif not isinstance(x_1, np.ndarray):
        log.error('x_1 is not a vector in the proper format. '
                  'Please use a list or a numpy.array!')
        raise CnetError

    if isinstance(x_2, list):
        x_2 = np.asarray(x_2)
    elif not isinstance(x_2, np.ndarray):
        log.error('x_2 is not a vector in the proper format. '
                  'Please use a list or a numpy.array!')
        raise CnetError

    # number of nodes
    n = len(x_1)

    # check size of the other elements
    if len(x_2) != n:
        log.error('Size of the vectors does not match {} != {}.'
                  ''.format(len(x_2), n))
        raise CnetError
    if C.shape != (n, n):
        log.error('Size of the cost matrix does not match {} != ({}, {}).'
                  ''.format(C.shape, n, n))
        raise CnetError

    # Normalize vector x_1 to a row sum of 1
    # TODO: figure out if normalization is an advantage or not?
    # x_1 = x_1 / np.sum(x_1)

    # Scale vector to the same row sum as x_1
    # Otherwise no optimal solution can be found
    if np.sum(x_1) != np.sum(x_2):
        x_2 = x_2 / np.sum(x_2) * np.sum(x_1)

    # Transition matrix to estimate
    X = cvx.Variable((n, n))

    # Objective function
    objective = cvx.Minimize(cvx.sum(cvx.multiply(C, X)))

    # Constraints
    constraints = [X >= 0,
                   cvx.sum(X, axis=1) == x_1,
                   cvx.sum(X, axis=0) == x_2]

    # Minimization problem
    prob = cvx.Problem(objective, constraints)

    # Result form the optimization process
    res = prob.solve(verbose=verbose)

    # create temporary result matrix
    _X = np.round(X.value, 0)

    # log.debug(np.sum(_X, axis=1) == x_1)
    # log.debug(np.sum(_X, axis=0) == x_2)

    # Convert estimated matrix X to probabilities
    T = np.divide(_X, x_1[:, None], out=np.zeros_like(_X),
                  where=x_1[:, None] != 0)
    # TODO: add additional checks for the transition matrix.
    # TODO: try out to return a sparse matrix
    return T

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
