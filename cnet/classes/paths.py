#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : paths.py
# Creation  : 29 Mar 2018
# Time-stamp: <Don 2018-07-26 08:57 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : Base class for paths
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
from copy import deepcopy
from cnet import config, logger
from cnet.classes.network import Network, Node, Edge
from cnet.utils.exceptions import CnetError, CnetNotImplemented
log = logger(__name__)

MAX_NAME_LENGTH = 5


class Path(Network):
    """Base class for paths.

    A Path stores consecutive nodes and edges with optional data, or attributes.

    Instances of this class capture a path that can be directed, un-directed,
    un-weighted or weighted. The path class is a subclass of a network.

    Nodes are defined as :py:class:`Node` and edges are defined as
    :py:class:`Edge`

    Parameters
    ----------
    nodes : list of node ids or Nodes
        The parameter nodes must be a list with node ids or node
        objects. Every node within the list should have a unique id.
        The id is converted to a string value and is used as a key value for
        all dict which saving node objects.

    directed : Boole, optional  (default = True)
        Specifies if a network contains directed edges, i.e u->v or
        undirected edges i.d. u<->v. Per default the path is assumed to
        be directed.

    name : string, optional (default = '')
        An optional name for the path. If no name is assigned the network is
        called after the assigned nodes. e.g. if the path has nodes 'a', 'b' and
        'c', the network is named 'a-b-c'.

    separator : string, optional (default = '-')
        The separator used to separate the nodes in the node name.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to the path as key=value pairs.

    Attributes
    ----------
    name : string
        Name of the path. If no name is assigned the network is called after the
        assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the network
        is named 'a-b-c'. The maximum length of the name is defined by the
        constant `MAX_NAME_LENGTH`, which is per default 5. E.g. if the path has
        7 nodes (a,b,c,d,e,f,g) the name of the path is 'a-b-c-d-...-g'. Please,
        note the name of a path is NOT an unique identifier!

    id : string
        The identifier of the :py:class:`Path` object. Every path should
        have a unique id. The id is converted to a string value. If no attribute
        id is defined, the id is created by the nodes in the path. e.g. a path
        with such as (a,b,c,d,e,f,a) has the id 'a-b-c-d-e-f-g-a'.

    Examples
    --------
    Create an empty path with no nodes and no edges.

    >>> p = cn.Path()

    Some properties of the path are: the name, if directed or the shape

    >>> p.name = 'my test path'
    >>> p.name
    my test path

    Adding a singe new node to the network.

    >>> p.add_node('a',color='red')

    Adding an existing node object to the network.

    >>> b = cn.Node('b',color='green')
    >>> p.add_node(b)

    An edge was generated between a and b

    >>> p.name
    a-b

    Adding a singe new edge to the path.

    >>> p.add_edge('cd','c','d', length = 10)

    Adding an existing edge object to the path.

    >>> e = cn.Edge('da','d','a', length = 5)
    >>> p.add_edge(e)
    >>> p.name
    a-b-c-d-a

    See Also
    --------
    SpatialPath

    """

    def __init__(self, nodes=None, directed=True, separator='-', **attr):
        """Initialize a path with direction, name and attributes.

        Parameters
        ----------
        nodes : list of node ids or Nodes, optional (default = None)
            The parameter nodes must be a list with node ids or node
            objects. Every node within the list should have a unique id.
            The id is converted to a string value and is used as a key value for
            all dict which saving node objects.

        directed : Boole, optional  (default = True)
            Specifies if a network contains directed edges, i.e u->v or
            undirected edges i.d. u<->v. Per default the path is assumed to
            be directed.

        name : string, optional (default = '')
            An optional name for the path. If no name is assigned the network is
            called after the assigned nodes. e.g. if the path has nodes 'a', 'b'
            and 'c', the network is named 'a-b-c'.

        separator : string, optional (default = '-')
            The separator used to separate the nodes in the node name.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to the path as key=value pairs.

        """
        # Classes of the Path objects
        # TODO: Probably there is a better solution to have different Path
        # classes for different Path sub classes
        self._path_class()

        # an modified list object containing node and edge objects
        self.path = PathList()

        # initializing the separator
        self.separator = separator
        # initializing the parent network class
        super().__init__(directed=directed, **attr)

        # assign nodes to the path
        if isinstance(nodes, list):
            super().add_nodes_from(nodes)

    def _path_class(self):
        """Internal function to assign different Path classes."""
        self.PathClass = Path

    def __repr__(self):
        """Return the description of the path (see :meth:`_desc`) with the name
        of the path."""
        return '<{} object {} at 0x{}x>'.format(self._desc(), self.name, id(self))

    def _desc(self):
        """Return a string *Path()*."""
        return '{}'.format(self.__class__.__name__)

    def __len__(self):
        """Returns the number of nodes in the path"""
        return len(self.path)

    def __eq__(self, other):
        """Returns True if two paths are equal.

        Here equality is defined by the number and order of nodes in the path!

        """
        return self.id == other.id

    def __hash__(self):
        """Returns the unique hash of the path.

        Here the hash value is defined by the string of nodes in the path!

        """
        return hash(self.id)

    @property
    def name(self):
        """Returns the name of the path.

        Name of the path. If no name is assigned the network is called after the
        assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the network
        is named 'a-b-c'. The maximum length of the name is defined by the
        constant `MAX_NAME_LENGTH`, which is per default 5. E.g. if the path has
        7 nodes (a,b,c,d,e,f,g) the name of the path is 'a-b-c-d-...-g'. Please,
        note the name of a path is NOT an unique identifier!

        Returns
        -------
        name : string
            Returns the name of the path as a string.

        """
        max_name_length = MAX_NAME_LENGTH
        if len(self) > max_name_length:
            _name = self.separator.join(self.path[0:-2][0:max_name_length]) \
                + self.separator + '...' + self.separator + self.path[-1]
        else:
            _name = self.separator.join(self.path)

        return self.attributes.get('name', _name)

    @property
    def full_name(self):
        '''Returns the full name of the path

        Name of the path. If no name is assigned the network is called after the
        assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the network
        is named 'a-b-c'.

        Returns
        -------
        name : string
            Returns the name of the path as a string.

        '''
        _name = self.separator.join(self.path)

        return self.attributes.get('name', _name)

    @property
    def id(self):
        """Returns the id of the path.

        Id of the path. If no id is assigned the path is called after the
        assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the id is
        'a-b-c'.

        Returns
        -------
        id : string
            Returns the id of the path as a string.

        """
        _id = self.separator.join(self.path)

        return self.attributes.get('id', _id)

    def weight(self, weight='weight'):
        """Returns the weight of the path.

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
            the weight will be 1.0. Also any other attribute of the path can be
            used as a weight

        Returns
        -------
        weight : attribute
            Returns the attribute value associated with the keyword.

        Example
        -------
        Create new empty path and get the weight.

        >>> p = nc.Path()
        >>> p.weight()
        1.0

        Change the weight.

        >>> p['weight'] = 4
        >>> p.weight()
        4
        >>> p.weight(False)
        1.0

        Add an attribute and use this as weight.

        >>> p['length'] = 5
        >>> p.weight('length')
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

    def summary(self):
        """Returns a summary of the path.

        The summary contains the name, the used path class, if it is directed
        or not, the number of unique nodes and unique edges, and the number of
        nodes in the path.

        Since a path can multiple times pass the same node and edge objects, the
        length of the path (i.e. the consecutive nodes) might be larger then the
        number of unique nodes.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
            'Path length (# nodes):\t{}'.format(len(self))
        ]
        if config.logging.enabled:
            for line in summary:
                log.info(line.rstrip())
        else:
            return ''.join(summary)

    def add_node(self, n, **attr):
        """Add a single node n and update node attributes.

        Add a single node to the path object. If a second node is added,
        automatically an edge is created between these two nodes.

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

        >>> p = cn.Path()
        >>> p.add_node('a',color='red')

        Adding an existing node object to the network.

        >>> b = cn.Node('b',color='green')
        >>> p.add_node(b)

        An edge was generated between a and b

        >>> p.name
        a-b

        Note
        ----
        If the same node is entered twice in a row an warning will occur and the
        second node entry will be neglected.

        """
        # check if n is not a Node object
        if not isinstance(n, self.NodeClass):
            _node = self.NodeClass(n, **attr)
        else:
            _node = n
            _node.update(**attr)

        # check if node is the first node in the path
        if len(self) < 1:
            self.nodes[_node.id] = _node
            self.path.append(_node.id)
        # check if node is similar to previous node in the path
        elif self.path[-1] == _node.id:
            log.warn('The predecessor node is similar to node "{}"!'
                     ' No node was added to the path!'.format(_node.id))
            return None
        # check if node is connected to previous node in the path
        # elif self.has_edge((self.path[-1],_node.id)):
        #     log.debug('Can this happen? If you see this msg then yes :(')
        else:
            u = self.path[-1]
            self.nodes[_node.id] = _node
            self.path.append(_node.id)
            super().add_edge(str(u)+self.separator+str(_node.id), u, _node.id)
            self.path.edges.append(str(u)+self.separator+str(_node.id))

    def add_edge(self, e, u=None, v=None, **attr):
        """Add an edge e between u and v to the path.

        Add an single edge to the path object. The edge must be connected to the
        predecessor edge.

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
        Adding a singe new edge to the path.

        >>> p = cn.Path()
        >>> p.add_edge('ab','a','b', length = 10)

        Adding an existing edge object to the path.

        >>> e = cn.Edge('bc','b','c', length = 5)
        >>> p.add_edge(e)

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

        # check if nodes are already in the path
        if _edge.u.id not in self.nodes:
            self.nodes[_edge.u.id] = _edge.u
        if _edge.v.id not in self.nodes:
            self.nodes[_edge.v.id] = _edge.v

        # check if node is the first node in the path
        if len(self) < 1:
            self.path.append(_edge.u.id)
            self.path.append(_edge.v.id)
            self._add_edge(_edge)
        # check if edge is connected to previous edge in the path
        elif self.path[-1] == _edge.u.id:
            self.path.append(_edge.v.id)
            self._add_edge(_edge)
        elif not self.directed and \
                (self.path[-1] == _edge.u.id or self.path[-1] == _edge.v.id):
            if self.path[-1] == _edge.u.id:
                self.path.append(_edge.v.id)
                self._add_edge(_edge)
            else:
                self.path.append(_edge.u.id)
                self._add_edge(_edge)

        else:
            log.error('Edge "{}" with nodes "({},{})", is not connected to the'
                      ' previous edge with nodes "({},{})!"'
                      ''.format(_edge.id, _edge.u.id, _edge.v.id, self.path[-2], self.path[-1]))

            raise CnetError

    def _add_edge(self, _edge):
        """Help function to add an edge."""
        self.edges[_edge.id] = _edge
        self.path.edges.append(_edge.id)
        self.nodes[_edge.u.id].heads.add((_edge.id, 0))
        self.nodes[_edge.v.id].tails.add((_edge.id, 0))

        if not self.directed:
            self.nodes[_edge.u.id].tails.add((_edge.id, 1))
            self.nodes[_edge.v.id].heads.add((_edge.id, 1))

    def remove_node(self, n):
        """Remove node n and all adjacent edges."""
        raise CnetNotImplemented

    def remove_nodes_from(self, nodes):
        """Remove multiple nodes."""
        raise CnetNotImplemented

    def remove_edge(self, e):
        """Remove the edge e between u and v."""
        raise CnetNotImplemented

    def remove_edges_from(self, edges):
        """Remove all edges specified in edges."""
        raise CnetNotImplemented

    def has_subpath(self, subpath, mode='nodes'):
        """Return True if the path has a sub path.

        Parameters
        ----------
        subpath : list of node or edge ids or a path object
            The sub path is a list of consecutive nodes or edges describing the
            path.

        mode : string, 'nodes' or 'edges', optional (default = 'nodes')
            The mode defines how the sup path is defined, i.e. as a list of node
            ids or a list of edge ids. If the sub path is a path object, the
            mode does not matter.

        Examples:
        ---------
        >>> p = cn.Path(['a','b','c','d'])
        >>> p.has_subpath(['a','b'])
        True

        Test other path object

        >>> q = cn.Path(['d','e'])
        >>> p.has_subpath(q)
        False

        Test edges.

        >>> p.has_subpath(['a-b','b-c'], mode='edges')
        True

        """
        if isinstance(subpath, self.PathClass):
            _subpath = subpath.path
        else:
            # TODO: check also if nodes and edges are Node or Edge classes.
            if mode == 'edges':
                try:
                    _subpath = self.edges_to_path(subpath)
                except:
                    return False
            else:  # default mode == 'nodes'
                _subpath = subpath
        # check if all elements of the sub path are in the path
        if set(_subpath).issubset(set(self.path)):
            # check the order of the elements
            # consider also elements which appear multiple times in the path
            idx = [i for i, x in enumerate(self.path) if x == _subpath[0]]
            return any(all(self._check_path(i+j, v) for j, v in
                           enumerate(_subpath)) for i in idx)
        else:
            return False

    def _check_path(self, index, value):
        """Help function to check of the index exist"""
        try:
            return self.path[index] == value
        except:
            return False

    def edges_to_path(self, edges):
        """Returns a list of node ids representing the path.

        Parameters
        ----------
        edges : list of edge ids
            The path defined as a list of consecutive edges.

        Returns
        -------
        path : list of node ids
            Returns a list of node ids representing the path object

        Note
        ----
        An error will be raised if there is no corresponding path.

        """
        if isinstance(edges, str):
            edges = [edges]

        # TODO: Something is wrong here
        e2n = self.edge_to_nodes_map()
        try:
            # add first edge
            _path = [e2n[edges[0]][0], e2n[edges[0]][1]]
            # add remaining edges
            _path += [e2n[edges[e]][1] for e in range(1, len(edges))]
            # return path
            return _path
        except Exception as error:
            log.error('The edges "{}" could not be mapped to the path "{}"!'
                      ''.format('-'.join(edges), self.name))
            raise

    def subpath(self, subpath, mode='nodes'):
        """Returns a sup path of the path.

        Parameters
        ----------
        subpath : list of node or edge ids
            The sub path is a list of consecutive nodes or edges describing the
            path.

        mode : string, 'nodes' or 'edges', optional (default = 'nodes')
            The mode defines how the sup path is defined, i.e. as a list of node
            ids or a list of edge ids. If the sub path is a path object, the
            mode does not matter.

        Returns
        -------
        subpath : Path
            Returns a Path object containing the sub path and the attributes of
            the parent path object.

        Examples
        --------
        >>> p = cn.Path(['a','b','c','d'])
        >>> q = p.subpath(['a','b','c'])
        >>> q.name
        a-b-c

        Sub path from edge list

        >>> q = p.subpath(['c-d'])
        >>> q.name
        c-d

        """
        # check if the sub path is in the path
        if self.has_subpath(subpath, mode=mode):
            if mode == 'edges':
                _subpath = self.edges_to_path(subpath)
            else:  # default mode == 'nodes'
                _subpath = subpath
        else:
            log.error('Path "{}" has not sub path "{}"!'
                      ''.format(self.name, '-'.join(subpath)))
            raise ValueError

        # create a new path opject
        subpath = self.PathClass()
        # copy the attributes of the parent path
        subpath.update(**self.attributes)

        # get node dict to map the edges
        n2e = super().nodes_to_edges_map()

        # go thought the sub path and add the edges
        for i in range(len(_subpath)-1):
            _e = self.edges[n2e[_subpath[i], _subpath[i+1]][0]]
            subpath.add_edge(_e)

        return subpath

    def subpaths(self, min_length=None, max_length=None, include_path=False):
        """Returns a paths object with all sub paths.

        Parameters
        ----------

        min_length : int, optional (default = None)
            Parameter which defines the minimum length of the sub paths. This
            parameter has to be smaller then the maximum length parameter.

        max_length : int, optional (default = None)
            Parameter which defines the maximum  length of the sub paths. This
            parameter has to be greater then the minimum length parameter. If
            the parameter is also greater then the maximum length of the path,
            the maximum path length is used instead.

        include_path : Boole, optional (default = Flase)
            If this option is enabled also the current path is added as a
            sub path of it self.

        Returns
        -------
        subpaths : Paths
            Returns a paths object containing all the sub paths fulfilling the
            length criteria.

        Examples
        --------
        >>> p = cn.Path(['a','b','c','d','e'])
        >>> P = p.subpaths()
        >>> for q in P:
        >>>     print(q.name)
        a-b
        b-c
        c-d
        d-e
        a-b-c
        b-c-d
        c-d-e
        a-b-c-d
        b-c-d-e

        >>> P = p.subpaths(min_length = 3, max_length = 3)
        >>> for q in P:
        >>>     print(q.name)
        a-b-c
        b-c-d
        c-d-e

        Note
        ----
        If the minimum length is larger then the maximum length, an error will
        raised. If the maximum length is larger then the actual path length, the
        actual path length will be used.

        """
        if min_length is None:
            min_length = 1
        if max_length is None:
            max_length = len(self)-1
        if min_length > max_length:
            log.error('The minimum path length {} must be smaller then the '
                      'maximum path length {}!'.format(min_length, max_length))
            raise ValueError
        max_length = min(max_length, len(self)-1)
        min_length = max(min_length, 2)

        subpaths = Paths(name='sub paths of '+self.name)
        for i in range(min_length-1, max_length):
            for j in range(len(self)-i):
                subpaths.add_path(self.subpath(self.path[j:j+i+1]))

        if len(subpaths) == 0 and len(self) == 2:
            subpaths.add_path(self.copy())
        elif len(self) <= max_length+1 and include_path:
            subpaths.add_path(self.copy())

        return subpaths

    def shared_paths(self, other):
        """Returns the shared path with an other path object"""
        pass


class PathList(list):
    """An extended class of list to save the nodes and edges of the path."""

    def __init__(self):
        self.edges = []
        self.nodes = []

    def append(self, val):
        """Append value to the path list and the node list."""
        self.insert(len(self), val)
        self.nodes.append(val)


class Paths(object):
    """Basic class to store and handle multiple Path classes.

    Parameters
    ----------
    paths : list of :py:class:`Path` objects, optional (default = None)
        The parameter paths must be a list with :py:class:`Path` objects.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to the paths as key=value pairs.

    Attributes
    ----------
    name : string, optional (default='')
        An optional name for the network.

    """

    def __init__(self, paths=None, **attr):
        """Initialize the paths object with name and attributes.

        Parameters
        ----------
        paths : list of :py:class:`Path` objects, optional (default = None)
            The parameter paths must be a list with :py:class:`Path` objects.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to the paths as key=value pairs.

        Attributes
        ----------
        name : string, optional (default='')
            An optional name for the network.
        """
        # dictionary for the path objects
        self.paths = []
        # dictionary for paths attributes
        self.attributes = {}
        # add attributes to the paths
        self.attributes.update(attr)

        # assign path to the path list
        if isinstance(paths, list):
            self.add_paths_from(paths)

    @property
    def name(self):
        """Return the name of the paths if defined, else an empty space."""
        return self.attributes.get('name', '')

    @name.setter
    def name(self, s):
        """Set the name of the paths."""
        self.attributes['name'] = s

    def __repr__(self):
        """Return the description of the paths (see :meth:`_desc`) with the id
        of the paths."""
        return '<{} object {} at 0x{}x>'.format(self._desc(), self.name, id(self))

    def _desc(self):
        """Return a string *Paths()*."""
        return '{}'.format(self.__class__.__name__)

    def __len__(self):
        """Returns the number of paths"""
        return len(self.paths)

    def __getitem__(self, index):
        """Returns the path with the assigned index, or the attribute with the
        assigned keyword."""
        if isinstance(index, int):
            return self.paths[index]
        elif isinstance(index, str):
            return self.attributes[index]
        else:
            log.error('Index is not defined properly. Please use integer to'
                      'get the path at the index, or a string value to get'
                      'the attribute of the Paths object')
            raise CnetError

    def __iter__(self):
        """Iterating trough the path objects."""
        return (path for path in self.paths)

    def update(self, **attr):
        """Update the attributes of the paths.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add or update for the paths as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> P = nc.Paths(type = 'road travelers')
        >>> P.update(type = 'rail travelers', location = 'Swizerland')

        """
        self.attributes.update(attr)

    def add_path(self, p):
        """Add a single path to the path list.

        Parameters
        ----------
        p : Path
            Add a path object to the list of paths

        Examples
        --------
        >>> P = cn.Paths()
        >>> P.add_path(cn.Path(['a','b','c']))

        """
        if isinstance(p, Path):
            # if p is not None:
            self.paths.append(p)

    def add_paths_from(self, paths):
        """Add multiple paths from a list.

        Parameters
        ----------
        paths : list of path objects
            Add paths from a list of path objects.

        Examples
        --------
        >>> P = cn.Paths()
        >>> paths = [cn.Path(['a','b','c']),cn.Path(['b','c'])]
        >>> P.add_path(paths)

        """
        for p in paths:
            if isinstance(p, Path):
                self.paths.append(p)

    def summary(self):
        """Returns a summary of the paths.

        The summary contains the name, the used paths class, and the number of paths.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Number of paths:\t{}'.format(str(len(self.paths)))
        ]
        if config.logging.enabled:
            for line in summary:
                log.info(line.rstrip())
        else:
            return ''.join(summary)

    def save(self, filename, format=None, mode='nodes', weight=None):
        """Save the paths to file.

        Note
        ----
        Currently only the export to a pickle file or a ngram file is
        supported.

        Where pickles are a serialized byte stream of a Python object [1]_. This
        format will preserve Python objects used as nodes or edges.

        N-grams saves path data to a file containing multiple lines of n-grams
        of the form ``a,b,c,d,weight`` (where weight is optional). The default
        separating character ','. Each n-gram will be interpreted as a path.

        Parameters
        ----------
        filename : file or string
            File or filename to save. File ending such as '.pkl' is not
            necessary and will be added automatically if missing.

        format : string, optional (default = None)
            Format as which the network should be saved. Currently supported are
            '.pkl' files which are used by default, and 'ngram' files.

        mode : string, optional (default = 'nodes')
            Mode how the path should be saved. This option is not used when the
            paths are saved as a pickle file.

        weight : string or None, optional (default = None)
           The name of a path attribute that holds the numerical value used
           as a weight. If None or False, no weight will be assigned to the

        Examples
        --------
        >>> P = cn.Paths()
        >>> P.save('my_paths')

        References
        ----------
        .. [1] https://docs.python.org/3/library/pickle.html

        """
        # check paths
        if len(self.paths) > 0:
            # check mode
            if format is None:
                # check file ending and add .ngram if missing
                if not filename.endswith('.pkl'):
                    filename = filename + '.pkl'
                # write paths to output file
                with open(filename, 'wb') as f:
                    pickle.dump(deepcopy(self), f, pickle.HIGHEST_PROTOCOL)
            elif format == 'ngram':
                # check file ending and add .ngram if missing
                if not filename.endswith('.ngram'):
                    filename = filename + '.ngram'
                # write paths to output file
                with open(filename, 'w') as f:
                    for path in self.paths:
                        if weight is not None:
                            w = ','+str(path.weight(weight))
                        else:
                            w = ''
                        if mode == 'edges':
                            f.write(",".join(path.path.edges)+w+'\n')
                        elif mode == 'nodes':
                            f.write(",".join(path.path.nodes)+w+'\n')
                        else:
                            log.error("No mode '{}' is defined, hence no file"
                                      " was created.".format(format))

            else:
                log.warn("No format '{}' is defined, hence no file was"
                         "created.".format(path_format))

        else:
            log.warn("No 'paths' are defined, hence no file was created.")

    @classmethod
    def load(cls, filename, format=None):
        """Load paths from a file.

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
            Format of the paths file.

        Returns
        -------
        paths : Paths
            Returns a cnet path.

        Examples
        --------
        >>> P_1 = cn.Paths()
        >>> P_1.save('my_paths')
        >>> P_2 = Network.load('my_paths')

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
                paths = pickle.load(f)
        else:
            log.error('The format "{}" is currently not supported!'.format(format))
            raise NotImplementedError
        if isinstance(paths, Paths):
            return paths
        else:
            log.error(
                'The file "{}" does not contain a Network object'.format(filename))
            raise AttributeError

    def intersection(self, other):
        """Returns the paths which are common in both.

        Parameters
        ----------
        other : :py:class:`Paths`
            An Paths object storing paths.

        Returns
        -------
        paths : :py:class:`Paths`
            Returns a :py:class:`Paths` object with all parts common in this and
            the other object.

        Examples
        --------
        Create a list of paths.

        >>> p_1 = Path(['a', 'b'])
        >>> p_2 = Path(['a', 'b', 'c'])
        >>> P_1 = Paths([p_1])
        >>> P_2 = Paths([p_1, p_2])

        Get the interaction between P_1 and P_2.

        >>> P = P_1.interaction(P_2)
        >>> for p in P:
        >>>    print(p.name)
        a-b
        """
        paths = Paths(name='interaction between {} and {}'.format(
            self.name, other.name))
        paths.add_paths_from(list(set(self.paths).intersection(other.paths)))
        return paths

    def st_paths(self, source, target, mode='nodes'):
        """Returns all paths from the source to the target.

        Parameters
        ----------
        source : node id, edge id, Node object or Edge object
            Starting node or edge of the path.

        target : node id or edge id
            Ending node or edge for the path.

        mode : string, 'nodes' or 'edges', optional (default = 'nodes')
            The mode defines how the st-path is defined, i.e. as a list of node
            ids or a list of edge ids.

        Returns
        -------
        st_paths : :py:class:`Paths`
            Returns a :py:class:`Paths` object with all parts starting at the
            source and ending at the target.

        Examples
        --------
        Create a list of paths.

        >>> p_1 = Path(['a', 'b'])
        >>> p_2 = Path(['a', 'b', 'c'])
        >>> p_3 = Path(['a', 'c', 'b'])
        >>> P = Paths()
        >>> P.add_paths_from([p_1, p_2, p_3])

        Get the paths from node 'a' to 'b'.

        >>> P_ab = P.st_paths('a', 'b')
        >>> for p in P_ab:
        >>>     print(p.name)
        a-b
        a-c-b

        Get the paths from edge 'a-b' to 'b-c'.

        >>> P_ac = P.st_paths('a-b', 'b-c', mode='edges')
        >>> for p in P_ac:
        >>>     print(p.name)
        a-b-c

        """
        # check the source
        if mode == 'nodes':
            if isinstance(source, Node):
                _s = source.id
            else:
                _s = source
            if isinstance(target, Node):
                _t = target.id
            else:
                _t = target
        elif mode == 'edges':
            if isinstance(source, Edge):
                _s = source.id
            else:
                _s = source
            if isinstance(target, Edge):
                _t = target.id
            else:
                _t = target
        else:
            log.error('The mode "{}" is not supported!'.format(mode))
            raise NotImplementedError

        # create a new paths object
        st_paths = Paths(name='st-paths between {} and {}'.format(_s, _t))

        # go through the paths and add correct paths to the list
        if mode == 'nodes':
            for p in self.paths:
                if p.path[0] == _s and p.path[-1] == _t:
                    st_paths.add_path(p)

        if mode == 'edges':
            for p in self.paths:
                try:
                    _s_node = p.edge_to_nodes_map()[_s][0]
                    _t_node = p.edge_to_nodes_map()[_t][1]
                except:
                    _s_node = None
                    _t_node = None
                if p.path[0] == _s_node and p.path[-1] == _t_node:
                    st_paths.add_path(p)

        # return the st paths
        return st_paths

    def sort(self, key=None, reverse=False):
        """Sorts the paths in a specific order.

        Parameters
        ----------
        key : string, optional (default = None)
            Keyword that serves as a key for the sort comparison. Per default
            the list will be sorted by the length of the paths.

        reverse : Boole, optional (default = False)
            If true, the sorted list is reversed (or sorted in Descending order)

        Examples
        --------
        Create a list of paths.

        >>> p_1 = Path(['a', 'b', 'c'], cost=10)
        >>> p_2 = Path(['a', 'b'], cost=100)
        >>> p_3 = Path(['a', 'c', 'b'] cost=50)
        >>> P = Paths()
        >>> P.add_paths_from([p_1, p_2, p_3])

        Sort path by length

        >>> P.sort()
        >>> for p in P:
        >>>     print(p.name)
        a-b
        a-b-c
        a-c-b

        Sort by key value

        >>> P.sort('cost')
        >>> for p in P:
        >>>     print(p.name)
        a-b-c
        a-c-b
        a-b

        Reverse sort by key value

        >>> P.sort('cost', reverse=True)
        >>> for p in P:
        >>>     print(p.name)
        a-b
        a-c-b
        a-b-c

        """
        _list = []
        if key is None:
            for path in self.paths:
                _list.append((len(path), path))
        elif isinstance(key, str):
            for path in self.paths:
                try:
                    value = path[key]
                except:
                    log.error('The key {} is not defined for path {}'
                              ''.format(key, path.name))
                    raise
                _list.append((path[key], path))

        _list.sort(key=lambda x: x[0], reverse=reverse)
        for i, (value, path) in enumerate(_list):
            self.paths[i] = path

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
