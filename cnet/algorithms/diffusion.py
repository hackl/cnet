#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : diffusion.py -- Diffusion processes
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-06-27
# Time-stamp: <Don 2018-07-05 08:35 juergen>
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
from scipy import sparse
import scipy.sparse.linalg as sla
from cnet import logger
from cnet.utils.exceptions import CnetError

log = logger(__name__)


class RandomWalkDiffusion(object):
    """A class to simulate a 'normal' diffusion process using random walkers.

    Parameters
    ----------
    network : Network
       A :py:class:`Network` object.

    walkers : int, optional (default = 5)
       Number of random walkers

    epsilon : float, optional (default = 0.01)
       Acceptable difference between the simulation and the analytically
       solution

    maxiter : integer, optional (default = 1000)
       The maximum number of iterations used to find a the stationary
       distribution.

    """

    def __init__(self, network, walkers=5, epsilon=0.01, maxiter=1000, weight=None):

        self.network = network
        self.walkers = walkers
        self.epsilon = epsilon
        self.maxiter = maxiter

        self.T = self.network.transition_matrix(weight)
        self.pi = None

    def stationary_distribution(self, A=None, normalized=True, lanczos_vecs=15, maxiter=1000):
        """Compute normalized leading eigenvector of a given matrix A.

        Parameters
        ----------
        A : None or scipy.sparse.coo_matrix, optional (default = None)
            Sparse matrix for which leading eigenvector will be computed. If no
            matrix is defined the transition matrix of the network will be used.

        normalized: bool, optional (default =  True)
            It True the result will be normalized, otherwise not.

        lanczos_vecs: int, optional (default = 15) The number of Lanczos vectors
            is used in the approximate calculation of eigenvectors and
            eigenvalues. This maps to the ncv parameter scipy's underlying
            function eigs.

        maxiter: int, option (default = True) Scaling factor for the number of
            iterations to be used in the approximate calculation of eigenvectors
            and eigenvalues. The number of iterations passed to scipy's
            underlying eigs function will be n*maxiter where n is the number of
            rows/columns of the Laplacian matrix.

        Returns
        -------
        pi : numpy.array
           A vector of the leading eigenvector

        """
        if A is None:
            A = self.T.transpose()
        if not sparse.issparse(A):  # pragma: no cover
            log.error("The matrix A must be a sparse matrix!")
            raise CnetError

        # NOTE: ncv sets additional auxiliary eigenvectors that are computed
        # NOTE: in order to be more confident to find the one with the largest
        # NOTE: magnitude, see https://github.com/scipy/scipy/issues/4987
        w, pi = sla.eigs(A, k=1, which="LM", ncv=lanczos_vecs, maxiter=maxiter)
        pi = pi.reshape(pi.size, )
        if normalized:
            pi /= sum(pi)
        return pi

    def step(self, time, node=None):
        """Computes the diffusion process at a certain time step.

        Parameters
        ----------
        time: integer
           Time step at which the diffusion process should be evaluated.

        node: string, optional (default = None)
           Node id of the node where the diffusion process should be
           initialized. If no node id is defined a random node will be chosen
           instead.

        Returns
        -------
        p_t : dict
           A dictionary with the node ids as key values and the diffusion output
           as values.

        """
        T = self.T
        n = self.network.number_of_nodes()
        x = np.zeros(n)

        if node is None:
            x[np.random.randint(n)] = 1
        else:
            x[self.network.nodes.index(node)] = 1

        p_t = (T**time).transpose().dot(x)

        return {self.network.nodes[i].id: v for i, v in enumerate(p_t)}

    def speed(self):
        """ Computes the speed of the diffusion process.

        Computes the average number of steps requires by a random walk
        process to fall below a total variation distance below epsilon (TVD
        computed between the momentary visitation probabilities \pi^t and the
        stationary distribution \pi = \pi^{\infty}. This time can be used to
        measure diffusion speed in a given (weighted and directed) network.

        """
        T = self.T
        pi = self.stationary_distribution()
        n = self.network.number_of_nodes()

        avg_speed = []
        for w in range(self.walkers):
            _avg_speed = 0
            x = np.zeros(n)
            seed = np.random.randint(n)
            x[seed] = 1
            while self.TVD(x, pi) > self.epsilon:
                _avg_speed += 1
                x = T.transpose().dot(x)  # (T.dot(x.transpose())).transpose()
                if _avg_speed > self.maxiter:
                    raise RuntimeError(
                        'Maximal number of iteration was reached')
            avg_speed.append(_avg_speed)
        return np.mean(avg_speed)

    @staticmethod
    def TVD(p1, p2):
        """Compute total variation distance between two stochastic column vectors"""
        assert p1.shape == p2.shape
        return 0.5 * np.sum(np.absolute(np.subtract(p1, p2)))


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
