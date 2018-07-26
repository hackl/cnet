#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py • cnet -- Basic classes for HONs
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-25
# Time-stamp: <Don 2018-07-26 10:21 juergen>
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
from cnet.classes.paths import Path, Paths
from cnet.utils.exceptions import CnetError, CnetNotImplemented
from cnet import config, logger
log = logger(__name__)


class HigherOrderNetwork(Network, Node):
    """Documentation for HigherOrderNetwork

    """

    def __init__(self, u, directed=True, **attr):
        Node.__init__(self, u, **attr)
        Network.__init__(self, name=u, directed=directed, **attr)


class NodeAndPath(Node, Path):
    """Base class of a higher order node which is also a path.

    Parameters
    ----------
    u : node id, list of path node ids or :py:class:`Path` object
        The parameter u is the identifier (id) for the node. Every node should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving node objects. The path name is used
        as node id, if only a :py:class:`Path` object or a list of path node ids
        is given.

    path : list of node ids or :py:class:`Path` object, optional (default = None)
        The parameter nodes must be a list with node ids or a path
        objects. Every node within the list should have a unique id.  The id is
        converted to a string value and is used as a key value for all dict
        which saving node objects.

    directed : Boole, optional  (default = True)
        Specifies if a network contains directed edges, i.e u->v or undirected
        edges i.d. u<->v. Per default the path is assumed to be directed.

    name : string, optional (default = '')
        An optional name for the path. If no name is assigned the network is
        called after the assigned nodes. e.g. if the path has nodes 'a', 'b' and
        'c', the network is named 'a-b-c'.

    separator : string, optional (default = '-')
        The separator used to separate the nodes in the node name.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to node as key=value pairs.

    Attributes
    ----------
    id : str
        Unique identifier for the node. This property can only be called and not
        set or modified!

    name : string
        Name of the path. If no name is assigned the network is called after the
        assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the network
        is named 'a-b-c'. The maximum length of the name is defined by the
        constant `MAX_NAME_LENGTH`, which is per default 5. E.g. if the path has
        7 nodes (a,b,c,d,e,f,g) the name of the path is 'a-b-c-d-...-g'. Please,
        note the name of a path is NOT an unique identifier!

    Examples
    --------
    Create a new NodeAndPath object:

    >>> u = cn.NodeAndPath('u', path=['a', 'b', 'c'])

    Getting some properties

    >>> u.id
    u
    >>> u.name
    a-b-c

    Adding a new node to the path

    >>> u.add_node('d')
    >>> u.name
    a-b-c-d

    Using an existing path and no predefined node id.

    >>> p = cn.Path(['a','b'], color = 'green')
    >>> v = cn.NodeAndPath(p)
    >>> v.id
    a-b
    >>> v['color']
    green

    ATTENTION: the id is not changing when a new node or edge is added to the
    path.

    >>> v.add_node('c')
    >>> v.id
    a-b
    >>> v.name
    a-b-c

    See Also
    --------
    Node
    Path

    """

    def __init__(self, u, path=None, directed=True, separator='-', **attr):
        """Initialize the node-path object

        Parameters
        ----------
        u : node id, list of path node ids or :py:class:`Path` object
            The parameter u is the identifier (id) for the node. Every node
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving node objects. The
            path name is used as node id, if only a :py:class:`Path` object or a
            list of path node ids is given.

        path : list of node ids or :py:class:`Path` object, optional (default = None)
            The parameter nodes must be a list with node ids or a path
            objects. Every node within the list should have a unique id.  The id
            is converted to a string value and is used as a key value for all
            dict which saving node objects.

        directed : Boole, optional  (default = True)
            Specifies if a network contains directed edges, i.e u->v or
            undirected edges i.d. u<->v. Per default the path is assumed to be
            directed.

        name : string, optional (default = '')
            An optional name for the path. If no name is assigned the network is
            called after the assigned nodes. e.g. if the path has nodes 'a', 'b'
            and 'c', the network is named 'a-b-c'.

        separator : string, optional (default = '-')
            The separator used to separate the nodes in the node name.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to node as key=value pairs.

        """
        # check the inputs
        # initialize temporal variables
        _u = u
        _nodes = None
        _path = None
        if isinstance(u, str) and isinstance(path, list):
            if all([isinstance(n, str) for n in path]):
                _nodes = path
        elif isinstance(u, list):
            if all([isinstance(n, str) for n in u]):
                _u = separator.join(u)
                _nodes = u
        elif isinstance(u, str) and isinstance(path, Path):
            _path = path
        elif isinstance(u, Path):
            _u = u.id
            _path = u
        else:
            log.error('Inputs are not defined correctly! '
                      'Please, check the types of inputs!')
            raise CnetError
        # initializing the parent classes
        Node.__init__(self, _u, **attr)
        Path.__init__(self, nodes=_nodes, directed=directed,
                      separator=separator, **attr)

        if _path is not None:
            self.inherit_from_path(_path)

    def __eq__(self, other):
        """Returns True if two node-paths are equal.

        """
        if isinstance(other, str):
            return self.id == other
        elif isinstance(other, Path):
            return self.id == other.id
        else:
            log.error('This type of equality is not jet implemented!')
            raise CnetNotImplemented

    def __hash__(self):
        """Returns the unique hash of the node-path.

        Here the hash value is defined by the string of the node id!

        """
        return hash(self.id)

    def inherit_from_path(self, path, copy=True):
        """Inherit attributes and properties from an other path object
        Parameters
        ----------
        path : :py:class:`Path` object
            The :py:class:`Path` object which bequest their attributes and
            properties.

        copy : Boole, optional (default = True)
            If enabled the attributes and properties are copied.

        """

        if isinstance(path, Path) and copy:
            self.path = deepcopy(path.path)
            self.nodes = deepcopy(path.nodes)
            self.edges = deepcopy(path.edges)
            self.seperator = deepcopy(path.separator)
            self._directed = deepcopy(path._directed)
            self.attributes = deepcopy(path.attributes)
        elif isinstance(path, Path) and not copy:
            self.path = path.path
            self.nodes = path.nodes
            self.edges = path.edges
            self.seperator = path.separator
            self._directed = path._directed
            self.attributes = path.attributes
        else:
            log.error('The object must be of type Path!')
            raise CnetError

    def summary(self):
        """Returns a summary of the node-path object.

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
            'Node id:\t\t{}\n'.format(self.id),
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


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
