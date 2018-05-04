#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py 
# Creation  : 11 Apr 2018
# Time-stamp: <Fre 2018-05-04 16:57 juergen>
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


class OrderedEdgeDict(OrderedDict):
    def index(self,idx):
        return list(OrderedDict(self).keys()).index(idx)

    def iter(self, nodes=False, data=False):
        for key,value in OrderedDict(self).items():
            if nodes and data:
                yield (key, value.u.id, value.v.id, value.attributes)
            elif nodes and not data:
                yield (key, value.u.id, value.v.id)
            elif not nodes and data:
                yield (key, value.attributes)
            else:
                yield key

class OrderedNodeDict(OrderedDict):
    def index(self,idx):
        return list(OrderedDict(self).keys()).index(idx)

    def iter(self,data=False):
        for key,value in OrderedDict(self).items():
            if data:
                yield (key, value.attributes)
            else:
                yield key
    @property
    def last(self):
        return next(reversed(OrderedDict(self)))

    @property
    def first(self):
        return next(iter(OrderedDict(self)))

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
        Attributes to add to network as key=value pairs.

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

        # an ordered dictionary containing nodes objects
        self.nodes = OrderedNodeDict()

        # an ordered dictionary containing edges objects
        self.edges = OrderedEdgeDict()

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
        return '<{} object {} at 0x{}x>'.format(self._desc(),self.name, id(self))

    def _desc(self):
        """Return a string *Network()*."""
        return '{}'.format(self.__class__.__name__)

    def __getitem__(self, key):
        """Returns a specific attribute of the network."""
        try:
            return self.attributes[key]
        except Exception as error:
            log.error('No attribute with key "{}" is defined for network'
                      ' "{}".'.format(key,self.id))
            raise

    def __setitem__(self, key, item):
        """Add a specific attribute to the network"""
        self.attributes[key] = item

    @property
    def shape(self):
        """Return the size of the Network as tuple of number of nodes and number
        of edges"""
        return self.number_of_nodes(),self.number_of_edges()

    @property
    def directed(self):
        """Return if the network id directed (True) or undirected (False)."""
        return self._directed

    @property
    def name(self):
        """Return the name of the network if defined, else an empty space."""
        return self.attributes.get('name', '')

    @name.setter
    def name(self, s):
        """Set the name of the network."""
        self.attributes['name'] = s

    def update(self,**attr):
        """Update the attributes of the network.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add or update for the edge as key=value pairs.

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
        return {k:(v.u.id,v.v.id) for k,v in self.edges.items()}

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
        for e,n in self.edge_to_nodes_map().items():
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
        for e,n in self.edge_to_nodes_map().items():
            _dict[n].append(e)
            if not self.directed:
                _dict[n[1],n[0]].append(e)
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
        if not isinstance(n,self.NodeClass):
            _node = self.NodeClass(n,**attr)
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
            self.add_node(n,**attr)

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
        if not isinstance(e,self.EdgeClass):
            if u is not None and v is not None:
                if u in self.nodes:
                    u = self.nodes[u]
                if v in self.nodes:
                    v = self.nodes[v]
                _edge = self.EdgeClass(e,u,v,**attr)
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

            self.nodes[_edge.u.id].heads.append((_edge.id,0))
            self.nodes[_edge.v.id].tails.append((_edge.id,0))

            if not self.directed:
                self.nodes[_edge.u.id].tails.append((_edge.id,1))
                self.nodes[_edge.v.id].heads.append((_edge.id,1))

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
            if not isinstance(_edge,self.EdgeClass):
                try:
                    e,u,v = _edge
                except:
                    log.error('Edge "{}" must be defined by an edge id "e" and two'
                              ' nodes "u" and "v"!'.format(_edge))
                    raise
                self.add_edge(e,u,v,**attr)
            else:
                self.add_edge(_edge,**attr)

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
        if isinstance(e,tuple):
            _edges = self.nodes_to_edges_map()[e]

            if len(_edges) < 1:
                log.error('Edge "{}" could not be removed, sine this edge is'
                          ' not in the network network'.format(e))
                raise CnetError
            elif len(_edges) > 1:
                log.error('From node "{}" to node "{}", {} edges exist with'
                          ' ids: {}! Please, us the correct edge id instead of'
                          ' the node ids!'.format(e[0],e[1],len(_edges),
                                                  ', '.join(_edges)))
                raise CnetError
            e = _edges[0]

        if e in self.edges:
            # remove edge from heads and tails counter of the nodes
            self.edges[e].u.heads.remove((e,0))
            self.edges[e].v.tails.remove((e,0))
            if not self.directed:
                self.edges[e].u.tails.remove((e,1))
                self.edges[e].v.heads.remove((e,1))
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
        if isinstance(e,tuple):
            if self.directed:
                _edges = self.nodes_to_edges_map()[e]
            else:
                u,v = e
                _edges = []
                _edges.extend(self.nodes_to_edges_map()[(u,v)])
                _edges.extend(self.nodes_to_edges_map()[(v,u)])
            if len(_edges) < 1:
                return False
            elif len(_edges) > 1:
                log.warn('From node "{}" to node "{}", {} edges exist with'
                         ' ids: {}! Please, us the correct edge id instead of'
                         ' the node ids!'.format(e[0],e[1],len(_edges),
                                                 ', '.join(_edges)))
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

    def weights(self,weight='weight'):
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
        for e,E in self.edges.items():
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
            for e, s, t in self.edges.iter(nodes=True):
                row.append(self.nodes.index(t))
                col.append(self.nodes.index(s))
                if not self.directed:
                    row.append(self.nodes.index(s))
                    col.append(self.nodes.index(t))

        else:
            for e, s, t in self.edges.iter(nodes=True):
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

        if mode == 'out':
            _degree = self.adjacency_matrix(weight=weight).sum(axis=1)
        elif mode == 'in':
            _degree = self.adjacency_matrix(weight=weight).sum(axis=0).T
        else:
            log.error('Mode "{}" is not supported. Only the modes "out"'
                      ' and "in" are supported.'.format(mode))

        # check if given nodes is a single node
        if nodes is not None and not isinstance(nodes,list):
            idx = self.nodes.index(nodes)
            return _degree.item(idx)
        elif nodes is not None and isinstance(nodes,list):
            idx = [self.nodes.index(n) for n in nodes]
        else:
            idx = list(range(self.number_of_nodes()))
            nodes = list(self.nodes.keys())

        return {nodes[i]:_degree.item(i) for i in idx}

    def transition_matrix(self,weight=None):
        A = self.adjacency_matrix(weight=weight)
        D = sparse.diags(1/A.sum(axis=1).A1)
        return D*A


    def laplacian_matrix(self):
        """
        Returns the transposed normalized Laplacian matrix corresponding to the network.

        Parameters
        ----------

        Returns
        -------

        """
        T = self.transition_matrix()
        I = sparse.identity(self.number_of_nodes())

        return I - T

    def save(self,filename,format=None):
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
    def load(cls,filename,format=None):
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
            log.error('The file "{}" does not contain a Network object'.format(filename))
            raise AttributeError

    def copy(self):
        """Return a copy of the network."""
        return deepcopy(self)

    def has_path(self,path):
        pass

class Edge(object):
    """Base class for an edge.

    Parameters
    ----------
    e : edge id
        The parameter e is the identifier (id) for the edge. Every edge should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving edge objects.

    u : node id or Node
        This parameter defines the origin of the edge (if directed), i.e. u->v.
        A node id can be entered, in this case a new Node will be created 
        (see py:class:Node), also an existing node can be used, here the
        attributes and properties of the node objects are used.

    v : node id or Node
        This parameter defines the destination of the edge (if directed)
        i.e. u->v. A node id can be entered, in this case a new Node will be
        created (see py:class:Node), also an existing node can be used, here the
        attributes and properties of the node objects are used.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to edge as key=value pairs.

    Properties
    ----------
    id : str
        Unique identifier for the edge. This property can only be called and not
        set or modified!

    u : Node
        Origin node of the edge. This property can only be called and not set or
        modified!

    v : Node
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
    def __init__(self,id,u,v,**attr):
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
        if not isinstance(u,self.NodeClass):
            self._u = self.NodeClass(u)
        if not isinstance(v,self.NodeClass):
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
                      ' "{}".'.format(key,self.id))
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

    def reverse(self,copy=True):
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

    def weight(self,weight='weight'):
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
        elif isinstance(weight,str) and weight !='weight':
            return self.attributes.get(weight, 1.0)
        else:
            return self.attributes.get('weight', 1.0)

    def update(self,**attr):
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

    Properties
    ----------
    id : str
        Unique identifier for the node. This property can only be called and not
        set or modified!

    Examples
    --------
    Create an empty node.

    >>> u = cn.Node('u')

    Get the id of the node.

    >>>u.id
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
    def __init__(self,u,**attr):
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

        # list of edges associated with the node
        self.heads = []
        self.tails = []

    def __getitem__(self, key):
        """Returns a specific attribute of the node."""
        try:
            return self.attributes[key]
        except Exception as error:# as error:
            log.error('No attribute with key "{}" is defined for node'
                      ' "{}".'.format(key,self.id))
            raise

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

    def update(self,**attr):
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