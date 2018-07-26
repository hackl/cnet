#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py
# Creation  : 11 Apr 2018
# Time-stamp: <Don 2018-07-26 09:14 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : Basic class for networks
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

import pickle
import numpy as np
from scipy import sparse
from copy import deepcopy
from collections import OrderedDict, defaultdict

from cnet import config, logger
from cnet.utils.exceptions import CnetError
log = logger(__name__)


class Network(object):
    """ Base class for networks.

    A Network stores nodes and edges with optional data, or attributes.

    Instances of this class capture a network that can be directed, undirected,
    unweighted or weighted. Self loops and multiple (parallel) edges are
    allowed.

    Nodes are defined as :py:class:`Node` and edges are defined as
    :py:class:`Edge`

    Parameters
    ----------
    directed : Boole, optional  (default = True)
        Specifies if a network contains directed edges, i.e u->v or
        undirected edges i.d. u<->v. Per default the network is assumed to
        be directed.

    name : string, optional (default='')
        An optional name for the network.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to the network as key=value pairs.

    Examples
    --------
    Create an empty network structure with no nodes and no edges.

    >>> net = cn.Network()

    Some properties of the network are: the name, if directed or the shape

    >>> net.name = 'my test network'
    >>> net.name
    my test network

    >>> net.directed
    True

    >>> net.shape
    (0,0)

    The network can be grown in several ways.

    **Nodes:**

    Add single node to the network.

    >>> net.add_node('a')

    Also a node object can be added to the network.

    >>> b = cn.Node('b)
    >>> net.add_node(b)

    In addition to single nodes, also nodes from a list can added to the network
    at once. Attributes are assigned to all nodes. 

    >>> net.add_nodes_from(['c','d','e'],color='green')
    >>> net.nodes['c']['color']
    green

    Single nodes can be removed.

    >>> net.remove_node('c')

    While multiple nodes can be removed from a list of nodes.

    >>> net.remove_nodes_from(['a','b'])

    **Edges**

    Adding a singe new edge to the network.

    >>> net = cn.Network()
    >>> net.add_edge('ab','a','b', length = 10)

    Adding an existing edge object to the network.

    >>> e = cn.Edge('bc','b','c', length = 5)
    >>> net.add_edge(e)

    See Also
    --------
    SpatialNetwork
    RoadNetwork


    """

    def __init__(self, directed=True, **attr):
        """Initialize a network with direction, name and attributes.

        Parameters
        ----------
        directed : Boole, optional (default = True)
            Specifies if a network contains directed edges, i.e u->v or
            undirected edges i.d. u<->v. Per default the network is assumed
            to be directed.

        name : string, optional (default='')
            An optional name for the graph.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        """
        # type of the network
        self._directed = directed
        # dictionary for network attributes
        self.attributes = {}
        # add attributes to the network
        self.attributes.update(attr)

        # an ordered dictionary containing node objects
        self.nodes = NodeDict()

        # an ordered dictionary containing edge objects
        self.edges = EdgeDict()
        self.edges.directed = directed

        # Classes of the Node and Edge objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()

    def _node_class(self):
        """Internal function to assign different Node classes."""
        self.NodeClass = Node

    def _edge_class(self):
        """Internal function to assign different Edge classes."""
        self.EdgeClass = Edge

    def __repr__(self):
        """Return the description of the network (see :meth:`_desc`) with the id
        of the network."""
        return '<{} object {} at 0x{}x>'.format(self._desc(), self.name, id(self))

    def _desc(self):
        """Return a string *Network()*."""
        return '{}'.format(self.__class__.__name__)

    def __getitem__(self, key):
        """Returns a specific attribute of the network."""
        try:
            return self.attributes[key]
        except Exception as error:
            log.error('No attribute with key "{}" is defined for network'
                      ' "{}".'.format(key, self.id))
            raise

    def __setitem__(self, key, item):
        """Add a specific attribute to the network"""
        self.attributes[key] = item

    @property
    def shape(self):
        """Return the size of the Network as tuple of number of nodes and number
        of edges"""
        return self.number_of_nodes(), self.number_of_edges()

    @property
    def directed(self):
        """Return if the network id directed (True) or undirected (False)."""
        return self._directed

    @property
    def name(self):
        """Return the name of the network if defined, else an empty space."""
        _name = self.attributes.get('name', '')
        if _name is None:
            _name = ''
        return _name

    @name.setter
    def name(self, s):
        """Set the name of the network."""
        self.attributes['name'] = s

    def update(self, **attr):
        """Update the attributes of the network.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add or update for the network as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> net = nc.Network(type = 'road network')
        >>> net.update(type = 'rail network', location = 'Swizerland')

        """
        self.attributes.update(attr)

    def summary(self):
        """Returns a summary of the network.

        The summary contains the name, the used network class, if it is directed
        or not, the number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}'.format(self.number_of_edges())
        ]
        if config.logging.enabled:
            for line in summary:
                log.info(line.rstrip())
        else:
            return ''.join(summary)

    def edge_to_nodes_map(self):
        """Returns a dictionary which maps the edge ids to there node ids.

        Returns
        -------
        map : dict
           Returns a dict where the key is the edge id and the values are a
           tuple of associated node ids.

        Example
        -------
        >>> net = cn.Network()
        >>> net.add_edges_from([('ab','a','b'),('bc','b','c')])
        >>> net.edge_to_nodes_map()
        {'bc': ('b', 'c'), 'ab': ('a', 'b')}

        """
        return {k: (v.u.id, v.v.id) for k, v in self.edges.items()}

    def node_to_edges_map(self):
        """Returns a dictionary which maps the node id to the connected edge
        ids.

        Returns
        -------
        map : dict
           Returns a dict where the key is the node id and the values are a list
           of edges which are associated with the node. 

        Example
        -------
        >>> net = cn.Network()
        >>> net.add_edges_from([('ab','a','b'),('bc','b','c')])
        >>> net.node_to_edges_map()
        {'c': ['bc'], 'b': ['ab', 'bc'], 'a': ['ab']}

        """
        _dict = defaultdict(list)
        for e, n in self.edge_to_nodes_map().items():
            _dict[n[0]].append(e)
            _dict[n[1]].append(e)
        return _dict

    def nodes_to_edges_map(self):
        """Returns a dictionary which maps the node ids to associated edge
        ids.

        Contrary to :py:meth:`node_to_edges_map`, this method has the node tuple
        e.g. ('a','b') as a key. Since multiple edges are allowed, a node tuple
        can be corresponding to multiple edges.

        Returns
        -------
        map : dict
           Returns a dict where the key is a tuple of node ids and the values are a list
           of edges which are associated with these nodes.

        Example
        -------
        >>> net = cn.Network()
        >>> net.add_edges_from([('ab1','a','b'),('ab2','a','b'),('bc','b','c')])
        >>> net.nodes_to_edges_map()
        {('a', 'b'): ['ab1', 'ab2'], ('b', 'c'): ['bc']})

        """
        _dict = defaultdict(list)
        for e, n in self.edge_to_nodes_map().items():
            _dict[n].append(e)
            if not self.directed:
                _dict[n[1], n[0]].append(e)
        return _dict

    def add_node(self, n, **attr):
        """Add a single node n and update node attributes.

        Parameters
        ----------
        u : node id or Node
            The parameter u is the identifier (id) for the node. Every node
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving node objects.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to node as key=value pairs.

        Example
        -------
        Adding a singe new node to the network.

        >>> net = cn.Network()
        >>> net.add_node('a',color='red')

        Adding an existing node object to the network.
        >>> b = cn.Node('b',color='green')
        >>> net.add_node(b)

        Note
        ----
        If the node is already defined in the network. The new node will not
        be added to the network, instead a warning will be printed.

        """
        # check if n is not a Node object
        if not isinstance(n, self.NodeClass):
            _node = self.NodeClass(n, **attr)
        else:
            _node = n
            _node.update(**attr)

        # check if nodes are already in the network
        if _node.id not in self.nodes:
            self.nodes[_node.id] = _node
        else:
            log.warn('The node with id: {} is already part of the'
                     'network. Please, check network consistency. The node id'
                     ' must be unique.'.format(_node.id))

    def add_nodes_from(self, nodes, **attr):
        """Add multiple nodes from a list.

        Parameters
        ----------
        nodes : list of node ids or Nodes
            The parameter nodes must be a list with node ids or node
            objects. Every node within the list should have a unique id.
            The id is converted to a string value and is used as a key value for
            all dict which saving node objects.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to all nodes in the list as key=value pairs.

        Example
        -------
        Adding a multiple nodes to the network.

        >>> net = cn.Network()
        >>> a = cn.Node('a')
        >>> net.add_nodes_from([a,'b','c'],shape='circle')

        Note
        ----
        If the node is already defined in the network. The new node will not
        be added to the network, instead a warning will be printed.

        """
        for n in nodes:
            self.add_node(n, **attr)

    def remove_node(self, n):
        """Remove node n and all adjacent edges.

        Parameters
        ----------
        n : node id
            The parameter n is the identifier (id) for the node.

        """
        if n in self.nodes:
            # get list of adjacent edges
            _edges = self.node_to_edges_map()[n]
            # remove edges
            for e in _edges:
                del self.edges[e]
            # remove node
            del self.nodes[n]

    def remove_nodes_from(self, nodes):
        """Remove multiple nodes.

        Parameters
        ----------
        nodes : list of node ids
            The parameter nodes must be a list with node ids.

        """
        for n in nodes:
            self.remove_node(n)

    def has_node(self, n):
        """Return True if the network contains the node n.

        Parameters
        ----------
        n : node id
            The parameter n is the identifier (id) for the node.

        Returns
        -------
        has_node : Boole
            Returns True if the network has a node n otherwise False.

        """
        return n in self.nodes

    def number_of_nodes(self):
        """Return the number of nodes in the network.

        Returns
        -------
        number_of_nodes : int
            Returns the number of nodes in the network.

        """
        return len(self.nodes)

    def add_edge(self, e, u=None, v=None, **attr):
        """Add an edge e between u and v.

        Parameters
        ----------
        e : edge id or Edge object
            The parameter e is the identifier (id) for the edge. Every edge
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving edge objects.
            If e is already an edge object, no nodes have to be assigned. If e
            is a edge id, u and v have to be defined. If not an error will occur.

        u : node id or Node, optional (default = None)
            This parameter defines the origin of the edge (if directed),
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:Node), also an existing node can be used, here
            the attributes and properties of the node objects are used.

        v : node id or Node, optional (default = None)
            This parameter defines the destination of the edge (if directed)
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:Node), also an existing node can be used, here
            the attributes and properties of the node objects are used.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to edge as key=value pairs.

        Example
        -------
        Adding a singe new edge to the network.

        >>> net = cn.Network()
        >>> net.add_edge('ab','a','b', length = 10)

        Adding an existing edge object to the network.

        >>> e = cn.Edge('bc','b','c', length = 5)
        >>> net.add_edge(e)

        Note
        ----

        If an edge id is added without nodes, an error will be raised and stop
        the code.

        If the edge is already defined in the network. The new edge will not
        be added to the network, instead a warning will be printed.

        """
        # check if e is not an Edge object
        if not isinstance(e, self.EdgeClass):
            if u is not None and v is not None:
                if u in self.nodes:
                    u = self.nodes[u]
                if v in self.nodes:
                    v = self.nodes[v]
                _edge = self.EdgeClass(e, u, v, **attr)
            else:
                log.error('No nodes are defined for new edge "{}!"'.format(e))
                raise CnetError
        else:
            _edge = e
            _edge.update(**attr)

        # check if nodes are already in the network
        if _edge.u.id not in self.nodes:
            self.nodes[_edge.u.id] = _edge.u
        if _edge.v.id not in self.nodes:
            self.nodes[_edge.v.id] = _edge.v

        # check if edge is already in the network
        if _edge.id not in self.edges:
            self.edges[_edge.id] = _edge

            self.nodes[_edge.u.id].heads.add((_edge.id, 0))
            self.nodes[_edge.v.id].tails.add((_edge.id, 0))

            if not self.directed:
                self.nodes[_edge.u.id].tails.add((_edge.id, 1))
                self.nodes[_edge.v.id].heads.add((_edge.id, 1))

        else:
            log.warn('The edge with id: {} is already part of the'
                     'network. Please, check network consistency. The edge id'
                     ' must be unique.'.format(_edge.id))

    def add_edges_from(self, edges, **attr):
        """Add multiple edges from a list.

        Parameters
        ----------
        edges : list of edge ids or Edges
            The parameter edges must be a list with edge ids or edge
            objects. Every edge within the list should have a unique id.
            The id is converted to a string value and is used as a key value for
            all dict which saving node objects.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to all edges in the list as key=value pairs.

        Example
        -------
        Adding a multiple edges to the network.

        >>> net = cn.Network()
        >>> ab = cn.Edge'ab','a','b')
        >>> net.add_edges_from([ab,('bc',b','c')],length=10)

        Note
        ----
        If an edge id is added without nodes, an error will be raised and stop
        the code.

        If the edge is already defined in the network. The new edge will not
        be added to the network, instead a warning will be printed.

        """
        for _edge in edges:
            if not isinstance(_edge, self.EdgeClass):
                try:
                    e, u, v = _edge
                except:
                    log.error('Edge "{}" must be defined by an edge id "e" and two'
                              ' nodes "u" and "v"!'.format(_edge))
                    raise
                self.add_edge(e, u, v, **attr)
            else:
                self.add_edge(_edge, **attr)

    def remove_edge(self, e):
        """Remove the edge e between u and v.

        Parameters
        ----------
        e : edge id or tuple of node ids
            The parameter e is the identifier (id) for the edge. It can be the
            edge id, or a tuple of node ids of the associated nodes.

        Note
        ----
        If the tuple of node ids is used to remove edges, it is possible that
        multiple edges might be effected. In this situation an error will be
        raised and instead of the tuple the actual edge id should be used.

        """
        # check if e is given in terms of (u,v)
        if isinstance(e, tuple):
            _edges = self.nodes_to_edges_map()[e]

            if len(_edges) < 1:
                log.error('Edge "{}" could not be removed, sine this edge is'
                          ' not in the network network'.format(e))
                raise CnetError
            elif len(_edges) > 1:
                log.error('From node "{}" to node "{}", {} edges exist with'
                          ' ids: {}! Please, us the correct edge id instead of'
                          ' the node ids!'.format(e[0], e[1], len(_edges),
                                                  ', '.join(_edges)))
                raise CnetError
            e = _edges[0]

        if e in self.edges:
            # remove edge from heads and tails counter of the nodes
            self.nodes[self.edges[e].u.id].heads.remove((e, 0))
            self.nodes[self.edges[e].v.id].tails.remove((e, 0))
            # TODO: figure out why this command is not working properly
            # self.edges[e].u.heads.remove((e, 0))
            # self.edges[e].v.tails.remove((e, 0))
            if not self.directed:
                # self.edges[e].u.tails.remove((e, 1))
                # self.edges[e].v.heads.remove((e, 1))
                self.nodes[self.edges[e].u.id].tails.remove((e, 1))
                self.nodes[self.edges[e].v.id].heads.remove((e, 1))
            # delete the edge
            del self.edges[e]

    def remove_edges_from(self, edges):
        """Remove multiple edges.

        Parameters
        ----------
        edges : list of edge ids or tuples of node ids,
            The parameter edges must be a list with edge ids or tuples of node
            ids.

        """
        for e in edges:
            self.remove_edge(e)

    def has_edge(self, e):
        """Return True if the edge e or (u,v) is in the network.

        Parameters
        ----------
        e : edge id or tuple of node ids
            The parameter e is the identifier (id) for the edge, or a tuple
            (u,v) describing the associated node ids.

        Returns
        -------
        has_edge : Boole
            Returns True if the network has an edge e otherwise False.

        Note
        ----
        If the tuple of node ids is used to find the edge, it is possible that
        multiple edges might be effected. In this situation a warning will be
        raised additionally to the has_edge.

        """
        if isinstance(e, tuple):
            if self.directed:
                _edges = self.nodes_to_edges_map()[e]
            else:
                u, v = e
                _edges = []
                _edges.extend(self.nodes_to_edges_map()[(u, v)])
                _edges.extend(self.nodes_to_edges_map()[(v, u)])
            if len(_edges) < 1:
                return False
            elif len(_edges) > 1 and self.directed:
                log.warn('From node "{}" to node "{}", {} edges exist with'
                         ' ids: {}! Please, us the correct edge id instead of'
                         ' the node ids!'.format(e[0], e[1], len(_edges),
                                                 ', '.join(_edges)))
                return sum([e in self.edges for e in _edges]) > 0
            elif len(_edges) > 1 and not self.directed:
                return sum([e in self.edges for e in _edges]) > 0
            else:
                return _edges[0] in self.edges
        else:
            return e in self.edges

    def number_of_edges(self):
        """Return the number of edges in the network.

        Returns
        -------
        number_of_edges : int
            Returns the number of edges in the network.

        """
        return len(self.edges)

    def weights(self, weight='weight'):
        """Return an iterator over the weights of the edges.

        Parameters
        ----------
        weight : str, optional (default = 'weight')
            The weight parameter defines which attribute is used as weight. Per
            default the attribute 'weight' is used. If None or False is chosen,
            the weight will be 1.0. Also any other attribute of the edge can be
            used as a weight

        Returns
        -------
        weights : iterator
            An iterator over the weight of the edges.

        Example
        -------
        >>> net = cn.Network()
        >>> net.add_edges_from([('ab','a','b'),('bc','b','c')],weight=4,length=3)
        >>> for w in net.weights():
        >>>    print(w)
        4
        4

        >>> for w in net.weights('length'):
        >>>    print(w)
        3
        3

        """
        for e, E in self.edges.items():
            yield E.weight(weight=weight)

    def adjacency_matrix(self, weight=None, transposed=False):
        """Returns a sparse adjacency matrix of the network.

        By default, the entry corresponding to a directed link u->v is stored in
        row u and column v and can be accessed via A[u,v].

        Parameters
        ----------
        weight: bool, str or None, optional (default = None)
            The weight parameter defines which attribute is used as weight. Per
            default an un-weighted network is used, i.e. None or False is chosen,
            the weight will be 1.0. Any other attribute of the edge can be
            used as a weight. Hence if set to None or False, the function
            returns a binary adjacency matrix. If set to True, or any other
            attribute, the adjacency matrix entries will contain the weight of
            an edge.

        transposed: bool, optional (default = False)
            Whether to transpose the matrix or not.

        Returns
        -------
        adjacency_matrix : scipy.sparse.coo_matrix
            Returns a space scipy matrix.

        """
        row = []
        col = []
        data = []

        if transposed:
            for e, (s, t) in self.edges(nodes=True):
                row.append(self.nodes.index(t))
                col.append(self.nodes.index(s))
                if not self.directed:
                    row.append(self.nodes.index(s))
                    col.append(self.nodes.index(t))

        else:
            for e, (s, t) in self.edges(nodes=True):
                row.append(self.nodes.index(s))
                col.append(self.nodes.index(t))
                if not self.directed:
                    row.append(self.nodes.index(t))
                    col.append(self.nodes.index(s))

        # create array with non-zero entries
        if self.directed:
            if weight is None:
                data = np.ones(self.number_of_edges())
            else:
                data = np.array([w for w in self.weights(weight=weight)])
        else:
            if weight is None:
                data = np.ones(2*self.number_of_edges())
            else:
                data = []
                for w in self.weights(weight=weight):
                    data.append(w)
                    data.append(w)

        shape = (self.number_of_nodes(), self.number_of_nodes())
        return sparse.coo_matrix((data, (row, col)), shape=shape).tocsr()

    def degree(self, nodes=None, weight=None, mode='out'):
        """Returns the node degrees.

        The node degree is the number of edges adjacent to the node.
        The weighted node degree is the sum of the edge weights for
        edges incident to that node.

        Parameters
        ----------
        nodes : list of node ids, or all nodes (default = all nodes)
            The parameter nodes must be a list with node ids. If not, the degree
            of all nodes is considered.

        weight: bool, str or None, optional (default = None)
            The weight parameter defines which attribute is used as weight. Per
            default an un-weighted network is used, i.e. None or False is chosen,
            the weight will be 1.0. Any other attribute of the edge can be
            used as a weight. Hence if set to None or False, the function
            returns un-weighted node degrees. If set to True, or any other
            attribute, the node degree entries will be weighted.

        mode : string ('out' or 'in'), optional (default = 'out')
            If the network is directed, either the in degree or out degree can
            be calculated. Thereby:

            The node in degree is the number of edges pointing to the node.
            The weighted node degree is the sum of the edge weights for
            edges incident to that node.

            The node out_degree is the number of edges pointing out of the node.
            The weighted node degree is the sum of the edge weights for
            edges incident to that node.


        Returns
        -------
        degrees : dict
            If more then a single degree is requested, a dictionary with the
            node degrees will be returned, where the key is the node id and the
            value the (un) weighted degree.

        OR

        degree : int
            If only the degree of a single node is requested, this note degree
            will be returned.

        Examples
        --------
        >>> net = cn.Network(directed = True)
        >>> net.add_edges_from([('ab','a','b'),('cb','c','b'),('bd','b','d')])
        >>> net.degree() # calculate the out degree
        {'b': 1.0, 'a': 1.0, 'c': 1.0, 'd': 0.0}
        >>> net.degree(mode='in)
        {'c': 0.0, 'b': 2.0, 'd': 1.0, 'a': 0.0}
        >>> net.degree('b')
        1.0

        Weighted degree

        >>> net.edges['ab']['weight'] = 2
        >>> net.degree(['a','b'],weight=True)
        {'a': 2.0, 'b': 1.0}

        >>>net.degree(['a','b'],mode='in',weight=True)
        {'a': 0.0, 'b': 3.0}

        """
        if mode != 'out' and mode != 'in':
            log.warn('Mode "{}" is not supported. Only the modes "out"'
                     ' and "in" are supported! User input was ignored and'
                     ' default option "out" was calculated.'.format(mode))
            mode = 'out'
        if mode == 'out':
            _degree = self.adjacency_matrix(weight=weight).sum(axis=1)
        else:
            _degree = self.adjacency_matrix(weight=weight).sum(axis=0).T

        # check if given nodes is a single node
        if nodes is not None and not isinstance(nodes, list):
            idx = self.nodes.index(nodes)
            return _degree.item(idx)
        elif nodes is not None and isinstance(nodes, list):
            idx = [self.nodes.index(n) for n in nodes]
        else:
            idx = list(range(self.number_of_nodes()))
            nodes = list(self.nodes.keys())

        return {nodes[i]: _degree.item(i) for i in idx}

    def transition_matrix(self, weight=None):
        """Returns a transition matrix of the network.

        The transition matrix is the matrix

        .. math::

            T = 1/D * A

        where `D` is a matrix with the node out degrees on the diagonal and `A`
        is the adjacency matrix of the network.

        Parameters
        ----------
        weight : string or None, optional (default=None)
           The name of an edge attribute that holds the numerical value used
           as a weight.  If None or False, then each edge has weight 1.

        Returns
        -------
        transition_matrix : scipy.sparse.coo_matrix
            Returns the transition matrix, corresponding to the network.

        """
        A = self.adjacency_matrix(weight=weight)
        D = sparse.diags(1/A.sum(axis=1).A1)
        return D*A

    def laplacian_matrix(self, weight=None):
        """
        Returns the transposed normalized Laplacian matrix.

        The transposed normalized Laplacian is the matrix

        .. math::

            N = I - T

        where `I` is the identity matrix and `T` the transition matrix.

        Parameters
        ----------
        weight : string or None, optional (default=None)
           The name of an edge attribute that holds the numerical value used
           as a weight.  If None or False, then each edge has weight 1.

        Returns
        -------
        laplacian_matrix : scipy.sparse.coo_matrix
            Returns the transposed normalized Laplacian matrix, corresponding to
            the network.

        """
        T = self.transition_matrix(weight=weight)
        I = sparse.identity(self.number_of_nodes())

        return I - T

    def save(self, filename, format=None):
        """Save the network to file.

        Note
        ----
        Currently only the export to a pickle file is supported. Where pickles
        are a serialized byte stream of a Python object [1]_. This format will
        preserve Python objects used as nodes or edges.

        Parameters
        ----------
        filename : file or string
            File or filename to save. File ending such as '.pkl' is not
            necessary and will be added automatically if missing.

        format : string, optional (default = None)
            Format as which the network should be saved.

        Examples
        --------
        >>> net = cn.Network()
        >>> net.add_edges_from([('ab','a','b'),('bc','b','c')])
        >>> net.save('my_network')

        References
        ----------
        .. [1] https://docs.python.org/3/library/pickle.html

        """
        if format is None:
            # check file ending and add .pkl if missing
            if not filename.endswith('.pkl'):
                filename = filename + '.pkl'
            # write paths to output file
            with open(filename, 'wb') as f:
                pickle.dump(deepcopy(self), f, pickle.HIGHEST_PROTOCOL)
        else:
            log.error('The format "{}" is currently not supported!'.format(format))
            raise NotImplementedError

    @classmethod
    def load(cls, filename, format=None):
        """Load network from a file.

        Note
        ----
        Currently only the import from a pickle file is supported. Where pickles
        are a serialized byte stream of a Python object [1]_. This format will
        preserve Python objects used as nodes or edges.

        Parameters
        ----------
        filename : file or string
            File or filename to load. File ending such as '.pkl' is not
            necessary and will be added automatically if missing.

        format : string, optional (default = None)
            Format of the network file.

        Returns
        -------
        network : Network
            Returns a cnet network.

        Examples
        --------
        >>> net_1 = cn.Network()
        >>> net_1.save('my_network')
        >>> net_2 = Network.load('my_network')

        References
        ----------
        .. [1] https://docs.python.org/3/library/pickle.html

        """
        if format is None:
            # check file ending and add .pkl if missing
            if not filename.endswith('.pkl'):
                filename = filename + '.pkl'
            # write paths to output file
            with open(filename, 'rb') as f:
                network = pickle.load(f)
        else:
            log.error('The format "{}" is currently not supported!'.format(format))
            raise NotImplementedError
        if isinstance(network, Network):
            return network
        else:
            log.error(
                'The file "{}" does not contain a Network object'.format(filename))
            raise AttributeError

    def copy(self):
        """Return a copy of the network.

        Returns
        -------
        net : Network
            A copy of the network.

        Examples
        --------
        >>> net_1 = cn.Network()
        >>> net_2 = net_1.copy()

        """
        return deepcopy(self)

    def has_path(self, path):
        pass


class EdgeDict(OrderedDict):
    """A container to save the edges.

    This class is based on an OrderedDict with some additional modifications to
    store, call and modify edges in different kinds.

    Examples
    --------

    Creating some edges with attributes

    >>> ab = cn.Edge('ab','a','b',length=10, type='road')
    >>> bc = cn.Edge('bc','b','c',length=15)

    Creating empty EdgeDict and adding the nodes with id as key and
    :py:class:`Edge` as value.

    >>> edges = cn.EdgeDict()

    >>> edges[ab.id] = ab
    >>> edges[bc.id] = bc

    The :py:class:`EdgeDict` behaves like a 'normal' dict, e.g. for accessing
    items, iterating adding or deleting.

    >>> edges['ab']
    Edge ab

    Iterating through the dictionary, returning the keys.

    >>> for e in edges:
    >>>    print(e)
    ab
    bc

    >>> for e,E in edges.items():
    >>>     print(e,E)
    ab, Edge ab
    bc, Edge bc

    However new features are:

    Entering a number as key is interpreted as an index.

    >>> edges[1]
    Edge bc

    Entering a tuple of node ids returns also the associated edge(s). If there
    is only one edge this will be returned, otherwise a list of edges will be
    returned.

    >>> edges[('a','b')]
    Edge ab

    >>> edges['ab2'] = cn.Edge('ab2','a','b')
    >>> edges[('a','b')]
    [Edge ab, Edge ab2]

    An single edge can be deleted with

    >>> del edges['ab2']

    Edge attributes can be entered, modified and accessed via:

    >>> edge['ab']['length']
    10

    >>> edges['ab']['length'] = 5
    >>> edges['ab']['length']
    5

    If no edge is defined, only the attribute, a dictionary with the edge id as
    key and the corresponding attribute as value is returned.

    >>> edges['length']
    {'bc': 15, 'ab': 5}

    If an edge does not have such an attribute, the value None will be returned.

    >>> edges['type']
    {'bc': None, 'ab': 'road'}

    New attributes for all edges can be added like for a normal dict. Thereby
    the order of the attributes correspond to the order of the edges in the
    OrderedDict.

    >>> edges['capacity'] = [100,200]

    If a sequence of attributes is shorter than the number of edges in the
    Network, the same sequence is reused.

    >>> edges['speed'] = 30
    >>> edges['speed']
    {ab:30, bc:30}

    If the attributes are given as a dictionary with the edge ids as keys, each
    value is assigned to the corresponding edge. Edges where no edge ids are
    given in the dictionary get a None value as entry.

    >>> edges['crossing'] = {'ab': True}
    >>> edges['crossing']
     {'ab': True, 'bc': None}

    If the keys used in the dictionary do not correspond to the edge ids, the
    dictionary is added as an edge attribute instead.

    >>> edges['vehicles'] = {'a': 'cars', 'b': 'trucks'}
    >>> edges['vehicles']
    {'ab': {'b': 'trucks', 'a': 'cars'}, 'bc': {'b': 'trucks', 'a': 'cars'}}

    Also the :py:class:`EdgeDict` can be used as an iterator function.

    Iterating through all edge objects.

    >>> for e in edges()
    >>>     print(e)
    Edge ab
    Edge bc

    Iterate trough specific attributes

    >>> for e in edges('lenght')
    >>>     print(e)
    5
    15

    >>> for e in edges('length','type')
    >>>     print(e)
    (5, 'road')
    (15, None)

    With data enabled also the edge id is returned 

    >>> for e,a in edges('length', data=True)
    >>>     print(e,a)
    (ab, 5)
    (bc, 15)

    Is no argument given but data enabled, the edge id and all their associated
    attributes are returned.

    >>> for e,a in edges(data=True)
    >>>     print(e,a)
    ab {'length': 5, 'speed': 30, 'type': 'road', 'capacity': 100}
    bc {'length': 15, 'speed': 30, 'capacity': 200}

    Additionally to the attributes the associated node ids of the edge can be
    returned by enabling the option nodes.

    >>> for e,n in edges(nodes=True):
    >>>     print(e,n)
    ab ('a', 'b')
    bc ('b', 'c')

    >>> for e,n,a in edges(nodes=True, data=True):
    >>>     print(e,n,a)
    ab ('a', 'b') {'speed': 30, 'capacity': 100, 'length': 5, 'type': 'road'}
    bc ('b', 'c') {'capacity': 200, 'length': 15, 'speed': 30}

    """

    def __init__(self, *args, **kwds):
        super().__init__(self, *args, **kwds)
        self.directed = True

    def __call__(self, *args, nodes=False, data=False, **kwds):
        """Returns an iterator over all nodes.

        Parameters
        ----------
        args : arguments
            The arguments are the key words for the node attributes. If an
            argument is given, the node attributed associate with this (these)
            arguments are returned.

        nodes : bool, optional (default = False)
            If true also the node ids of the edges are added to the iterator.

        data : bool, optional (default = False)
            If true the attributes associated with the nodes are in the iterator.

        Returns
        -------
        node_iter : iterator
            An iterator over all nodes in the network, with their associated
            attributes and node ids.

        Examples
        --------
        >>> edges = cn.EdgeDict()
        >>> edges['ab'] = cn.Edge('ab','a','b',length=10, type='road')
        >>> edges['bc'] = cn.Edge('bc','b','c',length=15)

        Iterate trough specific attributes

        >>> for e in edges('lenght')
        >>>     print(e)
        5
        15

        >>> for e in edges('length','type')
        >>>     print(e)
        (5, 'road')
        (15, None)

        With data enabled also the edge id is returned 

        >>> for e,a in edges('length', data=True)
        >>>     print(e,a)
        (ab, 5)
        (bc, 15)

        Is no argument given but data enabled, the edge id and all their
        associated attributes are returned.

        >>> for e,a in edges(data=True)
        >>>     print(e,a)
        ab {'length': 5, 'speed': 30, 'type': 'road', 'capacity': 100}
        bc {'length': 15, 'speed': 30, 'capacity': 200}

        Additionally to the attributes the associated node ids of the edge can
        be returned by enabling the option nodes.

        >>> for e,n in edges(nodes=True):
        >>>     print(e,n)
        ab ('a', 'b')
        bc ('b', 'c')

        >>> for e,n,a in edges(nodes=True, data=True):
        >>>     print(e,n,a)
        ab ('a', 'b') {'speed': 30, 'capacity': 100, 'length': 5, 'type': 'road'}
        bc ('b', 'c') {'capacity': 200, 'length': 15, 'speed': 30}

        """
        for key, value in OrderedDict(self).items():
            _yield = []
            # check if data enabled
            if data or nodes:
                _yield.append(key)
            # check if nodes are enabled
            if nodes:
                _yield.append((value.u.id, value.v.id))
            # check if arguments are defined
            if len(args) > 0:
                _attributes = []
                keys = [a for a in args if (a in self.attributes())]
                for i in keys:
                    if i in value.attributes:
                        _attributes.append(value[i])
                    else:
                        _attributes.append(None)

                if len(_attributes) == 1:
                    _yield.append(_attributes[0])
                elif len(_attributes) > 1:
                    _yield.append(tuple(_attributes))
                else:
                    log.error('The defined attribute(s) are not defined!')
                    raise CnetError

            elif data and len(args) == 0:
                _yield.append(value.attributes)
            elif nodes:
                pass
            else:
                _yield.append(value)
            if len(_yield) == 1:
                yield _yield[0]
            else:
                yield tuple(_yield)

    def __getitem__(self, key):
        """Returns an item dependent on the key value.

        If the key is associated with an edge id, the :py:class:`Edge` will be
        returned.

        If the key is associated with an attribute of any edge, a dictionary
        with edge ids as key and the requested attribute as value will be
        returned. If an edge does not contain such an attribute a None value will
        be returned instead.

        If a integer value is entered as key, the :py:class:`Edge` stored at
        this index will be returned.

        And if a tuple of node ids is entered as key, the corresponding edge is
        returned.

        Examples
        --------
        >>> edges = cn.EdgeDict()
        >>> edges['ab'] = cn.Edge('ab','a','b',length=10, type='road')
        >>> edges['bc'] = cn.Edge('bc','b','c',length=15)

        The normal use of the dictionary.

        >>> edges['ab']
        Edge ab

        Entering a number as key is interpreted as an index.

        >>> edges[1]
        Edge bc

        If no edge is defined, only the attribute, a dictionary with the edge id
        as key and the corresponding attribute as value is returned.

        >>> edges['length']
        {'bc': 15, 'ab': 10}

        If an edge does not have such an attribute, the value None will be returned.

        >>> edges['type']
        {'bc': None, 'ab': 'road'}

        Entering a tuple of node ids returns also the associated edge(s). If
        there is only one edge this will be returned, otherwise a list of edges
        will be returned.

        >>> edges[('a','b')]
        Edge ab

        >>> edges['ab2'] = cn.Edge('ab2','a','b')
        >>> edges[('a','b')]
        [Edge ab, Edge ab2]

        """
        # check if key is an edge id and return the Edge object
        if key in OrderedDict(self):
            return OrderedDict(self)[key]
        # if key is a tuple, check if there are edges with these node ids
        elif isinstance(key, tuple):
            _edges = []
            for e in OrderedDict(self).values():
                if key == (e.u.id, e.v.id):
                    _edges.append(e)
                # return also edge if Network is undirected and node tuple has
                # the wrong order
                if not self.directed and key == (e.v.id, e.u.id):
                    _e = deepcopy(e)
                    _e._u = e.v
                    _e._v = e.u
                    _edges.append(_e)

            if len(_edges) == 1:
                return _edges[0]
            elif len(_edges) > 1:
                return _edges
            else:
                log.error('There is no edge with nodes {}!'.format(key))
                raise CnetError
        # if key is a int, return the Edge at the index
        elif isinstance(key, int):
            return list(OrderedDict(self).values())[key]
        # check if there is an attribute with the name and return a dict of
        # attribute values for the edges
        elif key in self.attributes():
            _dict = {}
            for k, v in OrderedDict(self).items():
                if key in v.attributes:
                    _dict[k] = v[key]
                else:
                    _dict[k] = None
            return _dict
        # else raise an error
        else:
            log.error('No edge or edge attribute with the key "{}" is defined!'
                      ''.format(key))
            raise CnetError

    def __setitem__(self, key, value):
        """Set and modify items of the EdgeDict values.

        If the value is an instance of a :py:class:`Edge` class the edge is
        added to the dictionary with the edge id as key value.

        If the key is not an edge id, a new attribute will be added to all edges
        in the dictionary.

        Examples
        --------
        Adding edges to the dictionary

        >>> edges = cn.EdgeDict()
        >>> edges['ab'] = cn.Edge('ab','a','b',length=10, type='road')
        >>> edges['bc'] = cn.Edge('bc','b','c',length=15)

        New attributes for all edges can be added like for a normal
        dict. Thereby the order of the attributes correspond to the order of the
        edges in the OrderedDict.

        >>> edges['capacity'] = [100,200]

        If a sequence of attributes is shorter than the number of edges in the
        Network, the same sequence is reused.

        >>> edges['speed'] = 30
        >>> edges['speed']
        {ab:30, bc:30}

        If the attributes are given as a dictionary with the edge ids as keys,
        each value is assigned to the corresponding edge. Edges where no edge
        ids are given in the dictionary get a None value as entry.

        >>> edges['crossing'] = {'ab': True}
        >>> edges['crossing']
         {'ab': True, 'bc': None}

        If the keys used in the dictionary do not correspond to the edge ids,
        the dictionary is added as an edge attribute instead.

        >>> edges['vehicles'] = {'a': 'cars', 'b': 'trucks'}
        >>> edges['vehicles']
        {'ab': {'b': 'trucks', 'a': 'cars'}, 'bc': {'b': 'trucks', 'a': 'cars'}}


        """
        # check if value is a Node class.
        # if so, add node to the Ordered dict
        if isinstance(value, Edge):
            super().__setitem__(key, value)

        elif isinstance(value, list):
            # check if list is shorter then the dict
            # if so repeat the dict until it is longer then the dict
            if len(value) < len(self):
                value = value * -(-len(self)//len(value))
            for i, (k, v) in enumerate(OrderedDict(self).items()):
                v[key] = value[i]
        elif isinstance(value, dict):
            # check if the keys in the dict correspond to edge ids.
            # if so add the value to the EdgeDict

            # Case 1: all keys are related to edge ids
            if set(value) == set(self):
                for k, v in OrderedDict(self).items():
                    v[key] = value[k]
            # Case 2: all keys are edge ids but there are less keys than edges.
            elif len(set(value)) < len(set(self)) and \
                    set(value).issubset(set(self)):
                for k, v in OrderedDict(self).items():
                    if k in value:
                        v[key] = value[k]
                    else:
                        v[key] = None
            # Case 3: all keys are edge ids but there a more keys than edges.
            elif len(set(value)) > len(set(self)) and \
                    set(self).issubset(set(value)):
                for k, v in OrderedDict(self).items():
                    v[key] = value[k]
                log.warn('More edge ids are defined as in the network '
                         'available!')
            # Case 4: keys are not equal to edge ids
            else:
                for k, v in OrderedDict(self).items():
                    v[key] = value
        else:
            for k, v in OrderedDict(self).items():
                v[key] = value

    @property
    def last(self):
        """Returns the last edge added to the network"""
        return next(reversed(OrderedDict(self)))

    @property
    def first(self):
        """Returns the first edge added to the network"""
        return next(iter(OrderedDict(self)))

    def attributes(self):
        """Returns the list of all the edge attributes in the network."""
        _attributes = set()
        for v in OrderedDict(self).values():
            _attributes.update(list(v.attributes.keys()))
        return list(_attributes)

    def index(self, idx):
        """Returns the list index of an edge.

        Parameters
        ----------
        index : edge id
            The index is the identifier (id) for the edge. Every edge
            should have a unique id. The id has to be a string value.

        Returns
        -------
        index : integer
            the index in the list, where the edge object is stored.

        Examples
        --------
        >>> net = cn.Network()
        >>> net.add_edges_from([('ab','a','b'),('bc','b','c')])
        >>> net.edges.index('ab')
        0

        """
        return list(OrderedDict(self).keys()).index(idx)


class NodeDict(OrderedDict):
    """A container to save the nodes.

    This class is based on an OrderedDict with some additional modifications to
    store, call and modify nodes in different kinds.

    Examples
    --------

    Creating some nodes with attributes

    >>> u = cn.Node('u',color='red')
    >>> v = cn.Node('v',color='red',shape='circle')
    >>> w = cn.Node('w',color='blue',type='node')

    Creating empty NodeDict and adding the nodes with id as key and
    :py:class:`Node` as value.

    >>> nodes = cn.NodeDict()

    >>> nodes[u.id] = u
    >>> nodes[v.id] = v
    >>> nodes[w.id] = w

    The :py:class:`NodeDict` behaves like a 'normal' dict, e.g. for accessing
    items, iterating adding or deleting.

    >>> nodes['u']
    Node u

    Iterating through the dictionary, returning the keys.

    >>> for n in nodes:
    >>>    print(n)
    u
    v
    w

    >>> for n,N in nodes.items():
    >>>     print(n,N)
    u, Node u
    v, Node v
    w, Node w

    However new features are:

    Entering a number as key is interpreted as an index.

    >>> nodes[1]
    Node v

    Node attributes can be entered, modified and accessed via:

    >>> nodes['u']['color']
    'red'

    >>> nodes['u']['color'] = 'green'
    >>> nodes['u']['color']
    'green'

    If no node is defined, only the attribute, a dictionary with the node id as
    key and the corresponding attribute as value is returned.

    >>> nodes['color']
    {u:'green', w:'blue', v:'red'}

    If a node does not have such an attribute, the value None will be returned.

    >>> nodes['shape']
    {u:None, w:None, v:'circle'}

    New attributes for all nodes can be added like for a normal dict. Thereby
    the order of the attributes correspond to the order of the nodes in the
    OrderedDict.

    >>> nodes['age'] = [21,32,33]

    If a sequence of attributes is shorter than the number of nodes in the
    Network, the same sequence is reused.

    >>> nodes['gender'] = ['m','f']
    >>> nodes['gender']
    {u:'m', v:'f', w:'m'}

    If the attributes are given as a dictionary with the node ids as keys, each
    value is assigned to the corresponding node. Nodes where no node ids are
    given in the dictionary get a None value as entry.

    >>> nodes['school'] = {'u': 'ETH', 'v': 'UZH'}
    >>> nodes['school']
    {'u': 'ETH', 'v': 'UZH', 'w': None}

    If the keys used in the dictionary do not correspond to the node ids, the
    dictionary is added as a node attribute instead.

    >>> nodes['affiliation'] = {'a': 'ETH', 'b': 'UZH'}
    >>> print(nodes['affiliation'])
    {'u': {'a': 'ETH', 'b': 'UZH'}, 'v': {'a': 'ETH', 'b': 'UZH'}, 'w': {'a': 'ETH', 'b': 'UZH'}}

    Also the :py:class:`NodeDict` can be used as an iterator function.

    Iterating through all node objects.

    >>> for n in nodes()
    >>>     print(n)
    Node u
    Node v
    Node w

    Iterate trough specific attributes

    >>> for n in nodes('age')
    >>>     print(n)
    21
    32
    33

    >>> for n in nodes('age','gender')
    >>>     print(n)
    (21, m)
    (32, f)
    (33, m)

    With data enabled also the node id is returned

    >>> for n in nodes('age', data=True)
    >>>     print(n)
    (u, 21)
    (v, 32)
    (w, 33)

    Is no argument given but data enabled, the node id and all their associated
    attributes are returned.

    >>> for n in nodes(data=True)
    >>>     print(n)
    ('u', {'gender': 'm', 'age': 21, 'color': 'red'})
    ('v', {'age': 32, 'gender': 'f', 'shape': 'circle', 'color': 'red'})
    ('w', {'gender': 'm', 'type': 'node', 'age': 33, 'color': 'blue'})

    """

    def __call__(self, *args, data=False, **kwds):
        """Returns an iterator over all nodes.

        Parameters
        ----------
        args : arguments
            The arguments are the key words for the node attributes. If an
            argument is given, the node attributed associate with this (these)
            arguments are returned.

        data : bool, optional (default = False)
            If true the attributes associated with the nodes are in the iterator.

        Returns
        -------
        node_iter : iterator
            An iterator over all nodes in the network, with their associated
            attributes.

        Examples
        --------
        Creating some nodes with attributes

        >>> nodes = cn.NodeDict()
        >>> nodes['u'] = cn.Node('u', age=21, gender='m')
        >>> nodes['v'] = cn.Node('v', age=32, gender='f')
        >>> nodes['w'] = cn.Node('w', age=33, gender='m')

        Iterating through all node objects.

        >>> for n in nodes()
        >>>     print(n)
        Node u
        Node v
        Node w

        Iterate trough specific attributes

        >>> for n in nodes('age')
        >>>     print(n)
        21
        32
        33

        >>> for n in nodes('age','gender')
        >>>     print(n)
        (21, m)
        (32, f)
        (33, m)

        With data enabled also the node id is returned

        >>> for n in nodes('age', data=True)
        >>>     print(n)
        (u, 21)
        (v, 32)
        (w, 33)

        Is no argument given but data enabled, the node id and all their
        associated attributes are returned.

        >>> for n in nodes(data=True)
        >>>     print(n)
        ('u', {'gender': 'm', 'age': 21})
        ('v', {'age': 32, 'gender': 'f'})
        ('w', {'gender': 'm', 'age': 33})

        """
        for key, value in OrderedDict(self).items():
            if len(args) > 0:
                _attributes = []
                keys = [a for a in args if (a in self.attributes())]
                for i in keys:
                    if i in value.attributes:
                        _attributes.append(value[i])
                    else:
                        _attributes.append(None)

                if not data and len(_attributes) == 1:
                    yield _attributes[0]
                elif not data and len(_attributes) > 1:
                    yield tuple(_attributes)
                elif data and len(_attributes) == 1:
                    yield key, _attributes[0]
                elif data and len(_attributes) > 1:
                    yield tuple([key] + _attributes)
                else:
                    log.error('The defined attribute(s) are not defined!')
                    raise CnetError
            elif data and len(args) == 0:
                yield key, value.attributes
            else:
                yield value

    def __getitem__(self, key):
        """Returns an item dependent on the key value.

        If the key is associated with a node id, the :py:class:`Node` will be
        returned.

        If the key is associated with an attribute of any node, a dictionary
        with node ids as key and the requested attribute as value will be
        returned. If a node does not contain such an attribute a None value will
        be returned instead.

        If a integer value is entered as key, the :py:class:`Node` stored at
        this index will be returned.

        Examples
        --------
        >>> nodes = cn.NodeDict()
        >>> nodes['u'] = cn.Node('u',color='green')
        >>> nodes['v'] = cn.Node('v',color='red',shape='circle')
        >>> nodes['w'] = cn.Node('w',color='blue',type='node')

        The normal use of the dictionary.

        >>> nodes['u']
        Node u

        Entering a number as key is interpreted as an index.

        >>> nodes[1]
        Node v

        If no node is defined, only the attribute, a dictionary with the node id
        as key and the corresponding attribute as value is returned.

        >>> nodes['color']
        {u:'green', w:'blue', v:'red'}

        If a node does not have such an attribute, the value None will be returned.

        >>> nodes['shape']
        {u:None, w:None, v:'circle'}

        """
        # check if key is a node id and return the node object
        if key in OrderedDict(self):
            return OrderedDict(self)[key]
        # if key is a int, return the Node at the index
        elif isinstance(key, int):
            return list(OrderedDict(self).values())[key]
        # check if there is an attribute with the name and return a dict of
        # attribute values for the nodes
        elif key in self.attributes():
            _dict = {}
            for k, v in OrderedDict(self).items():
                if key in v.attributes:
                    _dict[k] = v[key]
                else:
                    _dict[k] = None
            return _dict
        # else raise an error
        else:
            log.error('No node or node attribute with the key "{}" is defined!'
                      ''.format(key))
            raise CnetError

    def __setitem__(self, key, value):
        """Set and modify items of the NodeDict values.

        If the value is an instance of a :py:class:`Node` class the node is
        added to the dictionary with the node id as key value.

        If the key is not a node id, a new attribute will be added to all nodes
        in the dictionary.

        Examples
        --------
        Adding nodes to the dictionary.

        >>> nodes = cn.NodeDict()
        >>> nodes['u'] = cn.Node('u',color='green')
        >>> nodes['v'] = cn.Node('v')
        >>> nodes['w'] = cn.Node('w',color='blue')

        New attributes for all nodes can be added like for a normal
        dict. Thereby the order of the attributes correspond to the order of the
        nodes in the OrderedDict.

        >>> nodes['age'] = [21,32,33]

        If a sequence of attributes is shorter than the number of nodes in the
        Network, the same sequence is reused.

        >>> nodes['gender'] = ['m','f']
        >>> nodes['gender']
        {u:'m', v:'f', w:'m'}

        If the attributes given as a dictionary with the node ids as keys, each
        value is assigned to the corresponding node. Nodes where no node ids are
        given in the dictionary get a None value as entry.

        >>> nodes['school'] = {'u': 'ETH', 'v': 'UZH'}
        >>> nodes['school']
        {'u': 'ETH', 'v': 'UZH', 'w': None}

        If the keys used in the dictionary do not correspond to node ids, the
        dictionary is added as a node attribute instead.

        >>> nodes['affiliation'] = {'a': 'ETH', 'b': 'UZH'}
        >>> print(nodes['affiliation'])
        {'u': {'a': 'ETH', 'b': 'UZH'}, 'v': {'a': 'ETH', 'b': 'UZH'}, 'w': {'a': 'ETH', 'b': 'UZH'}}

        """
        # check if value is a Node class.
        # if so, add node to the Ordered dict
        if isinstance(value, Node):
            super().__setitem__(key, value)
        elif isinstance(value, list):
            # check if list is shorter then the dict
            # if so repeat the dict until it is longer then the dict
            if len(value) < len(self):
                value = value * -(-len(self)//len(value))
            for i, (k, v) in enumerate(OrderedDict(self).items()):
                v[key] = value[i]
        elif isinstance(value, dict):
            # check if the keys in the dict correspond to node ids.
            # if so add the value to the NodeDict

            # Case 1: all keys are related to node ids
            if set(value) == set(self):
                for k, v in OrderedDict(self).items():
                    v[key] = value[k]
            # Case 2: all keys are node ids but there are less keys than nodes.
            elif len(set(value)) < len(set(self)) and \
                    set(value).issubset(set(self)):
                for k, v in OrderedDict(self).items():
                    if k in value:
                        v[key] = value[k]
                    else:
                        v[key] = None
            # Case 3: all keys are node ids but there a more keys than nodes.
            elif len(set(value)) > len(set(self)) and \
                    set(self).issubset(set(value)):
                for k, v in OrderedDict(self).items():
                    v[key] = value[k]
                log.warn('More node ids are defined as in the network '
                         'available!')
            # Case 4: keys are not equal to node ids
            else:
                for k, v in OrderedDict(self).items():
                    v[key] = value
        else:
            for k, v in OrderedDict(self).items():
                v[key] = value

    @property
    def last(self):
        """Returns the last node added to the network."""
        return next(reversed(OrderedDict(self)))

    @property
    def first(self):
        """Returns the first node added to the network."""
        return next(iter(OrderedDict(self)))

    @property
    def directed(self):
        """Returns True if the Network is directed."""
        return self._directed

    @directed.setter
    def directed(self, directed):
        """Setts the EdgeList to directed or undirected."""
        self._directed = directed

    def attributes(self):
        """Returns the list of all the nodes attributes in the network."""
        _attributes = set()
        for v in OrderedDict(self).values():
            _attributes.update(list(v.attributes.keys()))
        return list(_attributes)

    def index(self, idx):
        """Returns the list index of a node.

        Parameters
        ----------
        index : node id
            The index is the identifier (id) for the node. Every node
            should have a unique id. The id has to be a string value.

        Returns
        -------
        index : integer
            the index in the list, where the node object is stored.

        Examples
        --------
        >>> net = cn.Network()
        >>> net.add_edges_from([('ab','a','b'),('bc','b','c')])
        >>> net.nodes.index('b')
        1

        """
        return list(OrderedDict(self).keys()).index(idx)


class Edge(object):
    """Base class for an edge.

    Parameters
    ----------
    e : edge id
        The parameter e is the identifier (id) for the edge. Every edge should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving edge objects.

    u : node id or py:class:`Node`
        This parameter defines the origin of the edge (if directed), i.e. u->v.
        A node id can be entered, in this case a new Node will be created
        (see py:class:Node), also an existing node can be used, here the
        attributes and properties of the node objects are used.

    v : node id or py:class:`Node`
        This parameter defines the destination of the edge (if directed)
        i.e. u->v. A node id can be entered, in this case a new Node will be
        created (see py:class:Node), also an existing node can be used, here the
        attributes and properties of the node objects are used.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to edge as key=value pairs.

    Attributes
    ----------
    id : str
        Unique identifier for the edge. This property can only be called and not
        set or modified!

    u : py:class:`Node`
        Origin node of the edge. This property can only be called and not set or
        modified!

    v : py:class:`Node`
        Destination node of the edge. This property can only be called and not
        set or modified!

    Examples
    --------
    Create an empty edge.

    >>> ab = cn.Edge('ab','a','b')

    Get the id of the edge.

    >>> ab.id
    ab

    Create an edge with given nodes.

    >>> c = cn.Node('c')
    >>> d = cn.Node('d')
    >>> cd = cn.Edge('cd',c,d)

    Create a node with attached attribute.

    >>> ab = cn.Edge('ab','a','b', length=10)

    Add attribute to the edge.

    >>> ab[capacity] = 5.5

    Change attribute.

    >>> ab['length'] = 5

    Update attributes (and add new).

    >>> ab.update(length = 2, capacity = 3, speed = 10)

    Get the weight of the edge. Per default the attribute with the key 'weight'
    is used as weight. Should there be no such attribute, a new one will be
    crated with weight = 1.0.

    >>>ab.weight()
    1.0

    If an other attribute should be used as weight, the option weight has to be
    changed.

    >>> ab.weight('length')
    2

    If a weight is assigned but for calculation a weight of 1.0 is needed, the
    weight can be disabled with False or None.

    >>> ab['weight'] = 4
    >>> ab.weight()
    4
    >>> ab.weight(False)
    1.0

    Make copy of the edge.

    >>> ef = ab.copy()

    Get a reversed version of the edge.

    >>> ba = ab.reverse()
    >>> ba.id
    ba
    >>> ab.id
    ab

    Reverse the edge itself.

    >>> ab.reverse(copy=False)
    >>> ab.id
    r_ab

    """

    def __init__(self, id, u, v, **attr):
        """Initialize the node object.

        Parameters
        ----------
        e : edge id
            The parameter e is the identifier (id) for the edge. Every edge
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving edge objects.

        u : node id or Node
            This parameter defines the origin of the edge (if directed),
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:Node), also an existing node can be used, here
            the attributes and properties of the node objects are used.

        v : node id or Node
            This parameter defines the destination of the edge (if directed)
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:Node), also an existing node can be used, here
            the attributes and properties of the node objects are used.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to edge as key=value pairs.

        """

        # Class of the Node object
        # TODO: Probably there is a better solution to have different Node
        # classes for different Edges sub classes
        self._node_class()
        # edge id
        self._id = str(id)
        # node id for node u
        self._u = u
        # node id for node v
        self._v = v
        # dictionary for edge attributes
        self.attributes = {}
        # add attributes to the edge
        self.attributes.update(attr)

        # check type of the nodes and add new nodes
        if not isinstance(u, self.NodeClass):
            self._u = self.NodeClass(u)
        if not isinstance(v, self.NodeClass):
            self._v = self.NodeClass(v)

    def _node_class(self):
        """Internal function to assign different Node classes to the edge"""
        self.NodeClass = Node

    def __repr__(self):
        """Return the description of the edge (see :meth:`_desc`) with the id
        of the edge."""
        return '{} {}'.format(self._desc(), self.id)

    def _desc(self):
        """Return a string *Edge()*."""
        return '{}'.format(self.__class__.__name__)

    def __getitem__(self, key):
        """Returns a specific attribute of the edge."""
        try:
            return self.attributes[key]
        except Exception as error:
            log.error('No attribute with key "{}" is defined for edge'
                      ' "{}".'.format(key, self.id))
            raise

    def __setitem__(self, key, item):
        """Add a specific attribute to the edge"""
        self.attributes[key] = item

    @property
    def id(self):
        """Return the id of the node."""
        return self._id

    @property
    def u(self):
        """Return the origin node u of the edge"""
        return self._u

    @property
    def v(self):
        """Return the destination node v of the edge"""
        return self._v

    def reverse(self, copy=True):
        """Returns a reversed version of the edge.

        Parameters
        ----------
        copy : bool, optional (default= True)
            If copy is True, a reversed copy of the edge will be returned.
            If copy is False, the nodes of the edge itself will be reversed.

        Returns
        -------
        e : Edge or None
            If copy is True, an Edge object will be returned with reversed nodes
            and 'r_' will be added to the edge id to indicate that this edge was
            reversed. If copy is False, noting will be returned.

        Example
        -------
        Get a reversed version of the edge.

        >>> ab = cn.Edge('ab','a','b')
        >>> ba = ab.reverse()
        >>> ba.id
        ba
        >>> ab.id
        ab

        Reverse the edge itself.

        >>> ab.reverse(copy=False)
        >>> ab.id
        r_ab

        """
        if copy:
            _edge = self.copy()
            _edge._u = self.v
            _edge._v = self.u
            _edge._id = 'r_'+str(self.id)
            return _edge
        else:
            u = self.u
            v = self.v
            self._u = v
            self._v = u

    def weight(self, weight='weight'):
        """Returns the weight of the edge.

        Per default the attribute with the key 'weight' is used as
        weight. Should there be no such attribute, a new one will be crated with
        weight = 1.0.

        If an other attribute should be used as weight, the option weight has to
        be changed.

        If a weight is assigned but for calculation a weight of 1.0 is needed,
        the weight can be disabled with False or None.

        Parameters
        ----------
        weight : str, optional (default = 'weight')
            The weight parameter defines which attribute is used as weight. Per
            default the attribute 'weight' is used. If None or False is chosen,
            the weight will be 1.0. Also any other attribute of the edge can be
            used as a weight

        Returns
        -------
        weight : attribute
            Returns the attribute value associated with the keyword.

        Example
        -------
        Create new edge and get the weight.

        >>> ab = nc.Edge('ab','a','b')
        >>> ab.weight()
        1.0

        Change the weight.

        >>> ab['weight'] = 4
        >>> ab.weight()
        4
        >>> ab.weight(False)
        1.0

        Add an attribute and use this as weight.

        >>> ab['length'] = 5
        >>> ab.weight('length')
        5

        """
        if weight is None:
            weight = False
        if not weight:
            return 1.0
        elif isinstance(weight, str) and weight != 'weight':
            return self.attributes.get(weight, 1.0)
        else:
            return self.attributes.get('weight', 1.0)

    def update(self, **attr):
        """Update the attributes of the edge.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add or update for the edge as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> ab = nc.Edge('ab','a','b',length = 5)
        >>> ab.update(length = 10, capacity = 5)

        """
        self.attributes.update(attr)

    def copy(self):
        """Return a copy of the edge.

        Returns
        -------
        u : Edge
            A copy of the edge.

        Examples
        --------
        >>> ab = cn.Edge('ab','a','b')
        >>> cd = ab.copy()
        """
        return deepcopy(self)


class Node(object):
    """Base class for a node.

    Parameters
    ----------
    u : node id
        The parameter u is the identifier (id) for the node. Every node should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving node objects.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to node as key=value pairs.

    Attributes
    ----------
    id : str
        Unique identifier for the node. This property can only be called and not
        set or modified!

    Examples
    --------
    Create an empty node.

    >>> u = cn.Node('u')

    Get the id of the node.

    >>> u.id
    u

    Create a node with attached attribute.

    >>> v = cn.Node('v',color='red')

    Add attribute to the node.

    >>> v['shape'] = 'circle'

    Change attribute.

    >>> v['color'] = 'blue'

    Update attributes.

    >>> v.update(color='green',shape='rectangle')

    Make a copy of the node.

    >>> w = v.copy()

    """

    def __init__(self, u, **attr):
        """Initialize the node object.

        Parameters
        ----------
        u : node id
            The parameter u is the identifier (id) for the node. Every node
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving node objects.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to node as key=value pairs.

        """
        # node id
        self._id = str(u)
        # dictionary for node attributes
        self.attributes = {}
        # add attributes to the node
        self.attributes.update(attr)

        # set of edges associated with the node
        self.heads = set()
        self.tails = set()

    def __getitem__(self, key):
        """Returns a specific attribute of the node."""
        try:
            return self.attributes[key]
        except Exception as error:  # as error:
            log.error('No attribute with key "{}" is defined for node'
                      ' "{}".'.format(key, self.id))
            raise CnetError

    def __setitem__(self, key, item):
        """Add a specific attribute to the node."""
        self.attributes[key] = item

    def __repr__(self):
        """Return the description of the node (see :meth:`_desc`) with the id
        of the node."""
        return '{} {}'.format(self._desc(), self.id)

    def _desc(self):
        """Return a string *Node()*."""
        return '{}'.format(self.__class__.__name__)

    @property
    def id(self):
        """Return the id of the node."""
        return self._id

    def update(self, **attr):
        """Update the attributes of the node.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add or update for the node as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> v = cn.Node('v',color='red')
        >>> v.update(color='green',shape='rectangle')

        """
        self.attributes.update(attr)

    def copy(self):
        """Return a copy of the node.

        Returns
        -------
        u : Node
            A copy of the node.

        Examples
        --------
        >>> u = cn.Node('u')
        >>> v = u.copy()

        """
        return deepcopy(self)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
