#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py • cnet -- Basic classes for path networks
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-25
# Time-stamp: <Mit 2018-07-25 16:00 juergen>
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

from cnet.classes.network import Node, Edge, Network
from cnet.classes.paths import Path, Paths
from cnet.utils.exceptions import CnetError, CnetNotImplemented
from cnet import config, logger
log = logger(__name__)


class PathNetwork(Network):
    """Base class for path networks.

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

        # initialize parent class of the network
        Network.__init__(self, directed=directed, **attr)

        # Classes of the Node and Edge objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()

    def _node_class(self):
        """Internal function to assign different Node classes."""
        self.NodeClass = PathNode

    def _edge_class(self):
        """Internal function to assign different Edge classes."""
        self.EdgeClass = PathEdge


class PathEdge(Edge):
    """Base class for an edge.

    Parameters
    ----------
    e : edge id
        The parameter e is the identifier (id) for the edge. Every edge should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving edge objects.

    u : node id or py:class:`PathNode`
        This parameter defines the origin of the edge (if directed), i.e. u->v.
        A node id can be entered, in this case a new Node will be created
        (see py:class:`PathNode`), also an existing node can be used, here the
        attributes and properties of the node objects are used.

    v : node id or py:class:`PathNode`
        This parameter defines the destination of the edge (if directed)
        i.e. u->v. A node id can be entered, in this case a new Node will be
        created (see py:class:`PathNode`), also an existing node can be used,
        here the attributes and properties of the node objects are used.

    p1 : :py:class:`Path` object or :py:class:`Paths` object
        The path(s) associated with the node u. If no path is defined an empty
        path will be assigned to the node.

    p2 : :py:class:`Path` object or :py:class:`Paths` object
        The path(s) associated with the node v. If no path is defined an empty
        path will be assigned to the node.

    separator : string, optional (default = '|')
        The separator used to separate the nodes ids if the edge id is
        generated automatically (see edge id above).

    Examples
    --------

    """

    def __init__(self, id, u, v, **attr):
        """Initialize the edge object.

        Parameters
        ----------
        e : edge id
            The parameter e is the identifier (id) for the edge. Every edge
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving edge objects.

        u : node id or py:class:`PathNode`
            This parameter defines the origin of the edge (if directed),
            i.e. u->v.  A node id can be entered, in this case a new Node will
            be created (see py:class:`PathNode`), also an existing node can be
            used, here the attributes and properties of the node objects are
            used.

        v : node id or py:class:`PathNode`
            This parameter defines the destination of the edge (if directed)
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:`PathNode`), also an existing node can be
            used, here the attributes and properties of the node objects are
            used.

        p1 : :py:class:`Path` object or :py:class:`Paths` object
            The path(s) associated with the node u. If no path is defined an
            empty path will be assigned to the node.

        p2 : :py:class:`Path` object or :py:class:`Paths` object
            The path(s) associated with the node v. If no path is defined an
            empty path will be assigned to the node.

        separator : string, optional (default = '|')
            The separator used to separate the nodes ids if the edge id is
            generated automatically (see edge id above).

        """
        # Class of the Node object
        # TODO: Probably there is a better solution to have different Node
        # classes for different Edges sub classes
        self._node_class()

        # check the type of node object and if additional paths are defined
        if not isinstance(u, self.NodeClass) and 'p1' in attr:
            u = self.NodeClass(u, path=attr['p1'])
        if not isinstance(v, self.NodeClass) and 'p2' in attr:
            v = self.NodeClass(v, path=attr['p2'])

        # Create edge id based on the node ids
        if id is None:
            separator = attr.get('separator', '|')
            if isinstance(u, str):
                _u = u
            elif isinstance(u, self.NodeClass) or isinstance(u, Path):
                _u = u.id
            elif isinstance(u, Paths):
                if u.name == '' or u.name is None:
                    log.error('A unique node id has to be defined for node '
                              '{}!'.format(u))
                    raise CnetError
                else:
                    _u = u.name
            else:
                log.error('No valid node id for node {} was found'.format(u))
                raise CnetError

            if isinstance(v, str):
                _v = v
            elif isinstance(u, self.NodeClass) or isinstance(v, Path):
                _v = v.id
            elif isinstance(v, Paths):
                if v.name == '' or v.name is None:
                    log.error('A unique node id has to be defined for node '
                              '{}!'.format(v))
                    raise CnetError
                else:
                    _v = v.name
            else:
                log.error('No valid node id for node {} was found'.format(v))
                raise CnetError

            id = _u + separator + _v

        # initialize the parent edge class
        Edge.__init__(self, id, u, v, **attr)

    def _node_class(self):
        """Internal function to assign different Node classes to the edge"""
        self.NodeClass = PathNode

    def common_paths(self):
        """Returns the common paths between u and v."""
        return self.u.paths.intersection(self.v.paths)

    def common_subpaths(self, min_length=None, max_length=None, include_path=False):
        """Returns a paths object with a set of sub paths of u and v.

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
            Returns a paths object containing a set of the sub paths fulfilling
            the length criteria.

        See Also
        --------
        :py:method:`Path.subpaths`
        """
        _subpaths_u = self.u.subpaths(min_length=min_length,
                                      max_length=max_length,
                                      include_path=include_path)
        _subpaths_v = self.v.subpaths(min_length=min_length,
                                      max_length=max_length,
                                      include_path=include_path)
        return _subpaths_u.intersection(_subpaths_v)


class PathNode(Node):
    """Base class for a path node.

    Thereby a path node represents one or multiple paths.

    Parameters
    ----------
    u : node id, :py:class:`Path` object or :py:class:`Paths` object
        The parameter u is the identifier (id) for the node. Every node should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving node objects.  The path name is used
        as node id, if only a :py:class:`Path` object is given.  If only a
        :py:class:`Paths` object is given a valid name has to be defined.
        ATTENTION: IT IS RECOMMENDED TO USE A UNIQUE NODE ID INSTEAD OF PATHS!

    path : :py:class:`Path` object or :py:class:`Paths` object
        The path(s) associated with the node.

    Examples
    --------


    """

    def __init__(self, u=None, path=None, **attr):
        """Initialize the node object.

        Parameters
        ----------
        u : node id, :py:class:`Path` object or :py:class:`Paths` object
            The parameter u is the identifier (id) for the node. Every node
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving node objects.  The
            path name is used as node id, if only a :py:class:`Path` object is
            given.  If only a :py:class:`Paths` object is given a valid name has
            to be defined.  ATTENTION: IT IS RECOMMENDED TO USE A UNIQUE NODE ID
            INSTEAD OF PATHS!

        path : :py:class:`Path` object or :py:class:`Paths` object
            The path(s) associated with the node.

        """
        # initialize variables
        _path = None
        _paths = None
        # check if path or paths are defined
        # if no node id or path is defined return an error message
        if u is None and path is None:
            log.error('Either the node id a single "path" or a list of "paths"'
                      ' must be defined!')
            raise CnetError
        # if no path is defined print a warning and add an empty path object
        elif isinstance(u, str) and path is None:
            log.warn('Either a single "path" or a list of "paths" must be '
                     'defined. Neither was found. Therefore an empty path was'
                     ' created for node {}.'.format(u))
        # if u is a path object, the node id will be the path id
        elif isinstance(u, Path):
            _path = u
            u = u.id
        # if u is a Paths object with valid name,
        # the node id will be the name of the Paths list
        elif isinstance(u, Paths):
            if u.name == '' or u.name is None:
                log.error('A unique path node id has to be defined!')
                raise CnetError
            else:
                _paths = u
                u = u.name
        # if node id and path is defined in the right format,
        # add them tho the node
        elif isinstance(u, str) and isinstance(path, Path):
            _path = path
        # if node id and paths are defined in the right format,
        # add them to the node
        elif isinstance(u, str) and \
                (isinstance(path, Paths) or isinstance(path, list)):
            if isinstance(path, Paths):
                _paths = path
            elif isinstance(path, list):
                _paths = Paths(path)
        # if non of the cases above a valid return an error message
        else:
            log.error('A PathNode must be defined with an id and a Path or '
                      ' Paths object!')
            raise CnetError

        # assign path and paths to the node object
        if _paths is None:
            self.paths = Paths([_path], name=u)
        else:
            self.paths = _paths
        self.path = _path

        # initialize parent class
        Node.__init__(self, u, **attr)

    def subpaths(self, min_length=None, max_length=None, include_path=False):
        """Returns a paths object with a set of sub paths.

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
            Returns a paths object containing a set of the sub paths fulfilling
            the length criteria.

        See Also
        --------
        :py:method:`Path.subpaths`
        """
        _subpaths = set()
        for path in self.paths:
            for subpath in path.subpaths(min_length=min_length,
                                         max_length=max_length,
                                         include_path=include_path):
                _subpaths.add(subpath)
        subpaths = Paths(name='sub paths of node '+self.id)
        for path in _subpaths:
            subpaths.add_path(path)

        return subpaths
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
