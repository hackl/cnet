#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py • cnet -- Basic classes for HONs
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-25
# Time-stamp: <Fre 2018-10-19 10:31 juergen>
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

from copy import deepcopy
from cnet.classes.network import Node, Edge, Network
from cnet.utils.exceptions import CnetError, CnetNotImplemented
from cnet import config, logger
log = logger(__name__)


class HigherOrderNetwork(Network):
    """Base class for Higher Order Networks (HONs).

    Parameters
    ----------
    network : :py:class:`Network`
        An instance of the :py:class:`Network`, which contain the network used
        to generate the k-th-order representation. The network can either be
        directed or undirected, accordingly the HON is created.

    k: int, optional (default = 1)
        The order of the network representation to generate. For the default
        case of k=1, the resulting representation corresponds to the usual
        (first-order) aggregate network, i.e. links connect nodes and link
        weights are given by the frequency of each interaction. For k>1, a k-th
        order node corresponds to a sequence of k nodes. The weight of a k-th
        order link captures the frequency of a path of length k.

    separator: str, optional (default = '-')
        The separator character to be used in higher-order node names. If this
        parameter is not specified, the separator character of the underlying
        paths object will be used.

    name : string, optional (default='')
        An optional name for the network.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to the network as key=value pairs.

    Examples
    --------

    See Also
    --------
    Network
    """

    def __init__(self, network, k=1, separator='-', **attr):
        """Initialize a hon with sub network, order, name and attributes.

        Parameters
        ----------
        network : :py:class:`Network`
            An instance of the :py:class:`Network`, which contain the network
            used to generate the k-th-order representation. The network can
            either be directed or undirected, accordingly the HON is created.

        k: int, optional (default = 1)
            The order of the network representation to generate. For the default
            case of k=1, the resulting representation corresponds to the usual
            (first-order) aggregate network, i.e. links connect nodes and link
            weights are given by the frequency of each interaction. For k>1, a
            k-th order node corresponds to a sequence of k nodes. The weight of
            a k-th order link captures the frequency of a path of length k.

        separator: str, optional (default = '-')
            The separator character to be used in higher-order node names. If
            this parameter is not specified, the separator character of the
            underlying paths object will be used.

        name : string, optional (default='')
            An optional name for the network.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to the network as key=value pairs.

        """
        # Initialize parent class
        Network.__init__(self, directed=network.directed, **attr)

        # The order of this HigherOrderNetwork
        self.order = k

        # The separator character used to label higher-order nodes.
        # For separator '-', the name of a second-order node will be 'a-b'.
        self.separator = separator

        # The network object used to generate this instance
        self.network = network

        if k == 1:
            self.add_nodes_from(network.nodes())
            self.add_edges_from(network.edges())

        # If k=1 this is the higher oder network
        elif k == 2:
            self.generate_higer_order_network(self.network)

        # If k>1, k-1 higher order network will be generated
        elif k > 2:
            for i in range(2, k):
                self.network = HigherOrderNetwork(self.network, k=2)
                self.network.order = i
            self.generate_higer_order_network(self.network)

    def generate_higer_order_network(self, network):
        # add nodes to the hon:
        for e in network.edges():
            self.add_node(e.id, edge=e)

        # add edges to the hon
        # if the network is directed
        if self.directed:
            for e in network.edges():
                v = e.id
                x = e.u
                for u, _ in x.tails:
                    e_id = '{}{}{}'.format(u, self.separator, v)
                    self.add_edge(e_id, u, v)  # , node=x.id, **x.attributes)
        else:
            edges = set()
            for e in network.edges():
                v = e.id
                x = e.u
                y = e.v
                for u, _ in x.tails.union(x.heads).union(y.tails).union(y.heads):
                    n = [u, v]
                    n.sort()
                    # don't consider self loops
                    if n[0] != n[1] and (n[0], n[1]) not in edges \
                       and (n[0], n[1]) not in edges:
                        edges.add((n[0], n[1]))

            for u, v in edges:
                e_id = '{}{}{}'.format(u, self.separator, v)
                # TODO: Find a way to add the associated nodes to the edges
                self.add_edge(e_id, u, v)

    def summary(self):
        """Returns a summary of the higher order network.

        The summary contains the name, the used network class, if it is directed
        or not, the number of nodes and edges, and the order of the network.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Order:\t\t\t{}\n'.format(self.order),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}'.format(self.number_of_edges())
        ]
        if config.logging.enabled:
            for line in summary:
                log.info(line.rstrip())
        else:
            return ''.join(summary)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
