#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : spatialnetwork.py
# Creation  : 01 May 2018
# Time-stamp: <Mit 2018-07-25 12:38 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : Basic class for spatially embedded networks
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
from cnet.classes.paths import Path

from cnet import logger
from cnet.utils.helpers import haversine
from cnet.utils.exceptions import CnetError, CnetNotImplemented
log = logger(__name__)


class SpatialNetwork(Network):
    """ Base class for spatially embedded networks.

    A Network stores nodes and edges with optional data, or attributes.

    Instances of this class capture a network that can be directed, undirected,
    unweighted or weighted. Self loops and multiple (parallel) edges are
    allowed.

    Nodes are defined as :py:class:`SpatialNode` and edges are defined as
    :py:class:`SpatialEdge`

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

    See Also
    --------
    Network, RoadNetwork

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
        self.NodeClass = SpatialNode

    def _edge_class(self):
        """Internal function to assign different Edge classes."""
        self.EdgeClass = SpatialEdge


class SpatialEdge(Edge):
    """Base class for an edge.

    Parameters
    ----------
    e : edge id
        The parameter e is the identifier (id) for the edge. Every edge should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving edge objects.

    u : node id or py:class:`SpatialNode`
        This parameter defines the origin of the edge (if directed), i.e. u->v.
        A node id can be entered, in this case a new Node will be created
        (see py:class:`SpatialNode`), also an existing node can be used, here the
        attributes and properties of the node objects are used.

    v : node id or py:class:`SpatialNode`
        This parameter defines the destination of the edge (if directed)
        i.e. u->v. A node id can be entered, in this case a new Node will be
        created (see py:class:`SpatialNode`), also an existing node can be used,
        here the attributes and properties of the node objects are used.

    p1 : tuple of floats, optional (default = (0,0))
        Coordinate of the origin node, if origin node is not a
        py:class:`SpatialNode` object.

    p2 : tuple of floats, optional (default = (0,0))
        Coordinate of the destination node, if destination node is not a
        py:class:`SpatialNode` object.

    geometry : list of coordinate tuples, optional (default = None)
        Describing the geometry of the edge between the origin and destination
        nodes. Start and endpoint can be similar to the coordinates of the
        origin destination nodes.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to edge as key=value pairs.

    Attributes
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

    coordinates : list of coordinates
        List of coordinates, describing the shape of the edge, beginning with
        the origin node coordinate and ending with the destination node
        coordinate. This property can only be called and not set or modified!

    Examples
    --------
    Create an empty edge with out coordinates (not recommended but possible).

    >>> ab = cn.SpatialEdge('ab','a','b')
    [WARNING] No suitable coordinate was found for node "a"! Coordinate was set to "(0,0)"!
    [WARNING] No suitable coordinate was found for node "b"! Coordinate was set to "(0,0)"!

    Create a proper edge

    >>> ab =  cn.SpatialEdge('ab','a','b', p1=(0,0), p2=(4,0))
    >>> ab.coordinates
    [(0,0),(4,0)]

    Create edge with predefined spatial nodes

    >>> c = cn.SpatialNode('c',x=2,y=4)
    >>> d = cn.SpatialNode('d',x=3,y=1)
    >>> cd = cn.SpatialEdge('cd',c,d)
    >>> cd.coordinates
    [(2,4),(3,1)]

    Create edge with geometry.

    >>> cd_geom = cn.SpatialEdge('cd',c,d,geometry=[(2,4),(4,3),(5,2)])
    >>> cd_geom.coordinates
    [(2,4),(4,3),(5,2),(3,1)]

    Calculating the euclidean length of the edge

    >>> cd.length()
    3.1622776601683795
    >>> cd_geom.length()
    5.8863495173726745

    See Also
    --------
    Edge, RoadEdge

    """

    def __init__(self, id, u, v, **attr):
        """Initialize the spatial edge object.

        Parameters
        ----------
        e : edge id
            The parameter e is the identifier (id) for the edge. Every edge
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving edge objects.

        u : node id or py:class:`SpatialNode`
            This parameter defines the origin of the edge (if directed),
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:`SpatialNode`), also an existing node can be
            used, here the attributes and properties of the node objects are
            used.

        v : node id or py:class:`SpatialNode`
            This parameter defines the destination of the edge (if directed)
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:`SpatialNode`), also an existing node can be
            used, here the attributes and properties of the node objects are
            used.

        p1 : tuple of floats, optional (default = (0,0))
            Coordinate of the origin node, if origin node is not a
            py:class:`SpatialNode` object.

        p2 : tuple of floats, optional (default = (0,0))
            Coordinate of the destination node, if destination node is not a
            py:class:`SpatialNode` object.

        geometry : list of coordinate tuples, optional (default = None)
            Describing the geometry of the edge between the origin and
            destination nodes. Start and endpoint can be similar to the
            coordinates of the origin destination nodes.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to edge as key=value pairs.

        Attributes
        ----------
        id : str
            Unique identifier for the edge. This property can only be called and
            not set or modified!

        u : Node
            Origin node of the edge. This property can only be called and not
            set or modified!

        v : Node
            Destination node of the edge. This property can only be called and
            not set or modified!

        coordinates : list of coordinates
            List of coordinates, describing the shape of the edge, beginning
            with the origin node coordinate and ending with the destination node
            coordinate. This property can only be called and not set or
            modified!

        """
        # Class of the Node object
        # TODO: Probably there is a better solution to have different Node
        # classes for different Edges sub classes
        self._node_class()

        # check the type of node object and if additional coordinates are defined
        if not isinstance(u, self.NodeClass) and 'p1' in attr:
            u = self.NodeClass(u, coordinate=attr['p1'])
        if not isinstance(v, self.NodeClass) and 'p2' in attr:
            v = self.NodeClass(v, coordinate=attr['p2'])

        # initialize the parent edge class
        Edge.__init__(self, id, u, v, **attr)

    def _node_class(self):
        """Internal function to assign different Node classes to the edge"""
        self.NodeClass = SpatialNode

    @property
    def coordinates(self):
        """Returns the associated coordinates of the edge.

        If an attribute geometry exist, the coordinates are extended with the
        coordinates stored in the the geometry attribute. Thereby, the origin
        coordinate is always at the first position and the destination
        coordinate is always at the last position.

        Returns
        -------
        coordinates : list of coordinate tuples
            Returns a list with all coordinates associated with the edge.

        """
        if 'geometry' in self.attributes:
            _coordinates = [self.u.coordinate]
            _coordinates += [c for c in self.attributes['geometry']]
            _coordinates += [self.v.coordinate]
            if _coordinates[0] == _coordinates[1]:
                _coordinates.pop(0)
            if _coordinates[-2] == _coordinates[-1]:
                _coordinates.pop(-1)
            return _coordinates
        else:
            return [self.u.coordinate, self.v.coordinate]

    def length(self, coordinates_type='euclidean'):
        """Returns the length of the edge.

        Parameters
        ----------
        coordinates_type : string, optional (default = 'euclidean')
            This parameter defines how the length of the edge is calculated. Per
            default the euclidean distance is calculated. With the option
            'topological' the topological length 1 is returned. With the option
            'geographic' the geographical distance measured along the surface of
            the earth (GPS) is calculated. If the option is None the edge
            attribute  "length" will be returned.

        Returns
        -------
        lenght : float
            Returns the length of the edge.

        Examples
        --------
        >>> ab = SpatialEdge('ab','a','b',p1=(0,0),p2=(5,0),length=13)
        >>> ab.length()
        5.0
        >>> ab.length(None)
        13
        >>> ab.lenght('topological')
        1
        >>> ab.lenght('geographic')

        The geographical distance is calculated based on GPS coordinates, where
        x corresponds to the latitude and y to the longitude coordinate. The
        length will be returned in meters.

        >>> gps = SpatialEdge('uv','u','v',p1=(47.409589, 8.502555),
        >>>                   p2=(47.410344, 8.503037),length=13)
        91.45243924583434

        """
        length = 0
        if coordinates_type is None:
            try:
                length = self.attributes['length']
            except:
                log.error('No attribute with the name "length" is defined!')
                raise CnetError
        elif coordinates_type is 'topological':
            length = 1
        elif coordinates_type is 'euclidean':
            coordinates = [complex(p[0], p[1]) for p in self.coordinates]
            for i in range(1, len(coordinates)):
                length += abs(coordinates[i] - coordinates[i-1])
        elif coordinates_type is 'geographic':
            # [complex(p[0],p[1]) for p in self.coordinates]
            coordinates = self.coordinates
            for i in range(1, len(coordinates)):
                length += haversine(coordinates[i-1], coordinates[i])
        else:
            log.error('The coordinates type "{}" is not defined! Only'
                      '"topological", "euclidean" and "geographic" are valid '
                      'values to enter.'.format(coordinates_type))
            raise CnetNotImplemented

        return length


class SpatialNode(Node):
    """Base class for a spatially embedded node.

    Parameters
    ----------
    u : node id
        The parameter u is the identifier (id) for the node. Every node should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving node objects.

    x : float, optional (default = 0.0)
        The attribute x describes the x position of the node.

    y : float, optional (default = 0.0)
        The attribute y describes the y position of the node.

    coordinate : tuple of x and y, optional (default = (0.0,0.0))
        This attribute describes the coordinate as a tuple of x and y value.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to node as key=value pairs.

    Attributes
    ----------
    id : str
        Unique identifier for the node. This property can only be called and not
        set or modified!

    x : float
        x position of the node. This property can be called, modified and set.

    y : float
        y position of the node. This property can be called, modified and set.

    coordinate : tuple of floats
        Tuple in form of (x,y), where x and y describe the position of the
        node. This property can be called, modified and set.

    Examples
    --------
    Create an empty node with out coordinate (not recommended but possible).

    >>> u = cn.SpatialNode('u')
    [WARNING] No suitable coordinate was found for node "u"! Coordinate was set to "(0,0)"!

    Create a proper node

    >>> v = cn.SpatialNode('u',x=1,y=2)
    >>> v.coordinate
    (1,2)
    >>> v.x
    1
    >>> v.y
    2

    Changing the coordinate

    >>> v.x = 3
    >>> v.coordinate
    (3,2)
    >>> v.coordinate = (4,4)
    >>> v.coordinate
    (4,4)

    See Also
    --------
    Node, RoadNode

    """

    def __init__(self, u, **attr):
        """Initialize the node object.

        Parameters
        ----------
        u : node id
            The parameter u is the identifier (id) for the node. Every node
            should have a unique id. The id is converted to a string value and
            is used as a key value for all dict which saving node objects.

        x : float, optional (default = 0.0)
            The attribute x describes the x position of the node.

        y : float, optional (default = 0.0)
            The attribute y describes the y position of the node. 

        coordinate : tuple of x and y, optional (default = (0.0,0.0))
            This attribute describes the coordinate as a tuple of x and y value.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to node as key=value pairs.

        Attributes
        ----------
        id : str
            Unique identifier for the node. This property can only be called and
            not set or modified!

        x : float
            x position of the node. This property can be called, modified and
            set.

        y : float
            y position of the node. This property can be called, modified and
            set.

        coordinate : tuple of floats
            Tuple in form of (x,y), where x and y describe the position of the
            node. This property can be called, modified and set.

        """
        # initialize parent class
        Node.__init__(self, u, **attr)

        # check if attributes x and y are defined
        if 'x' in self.attributes and 'y' in self.attributes:
            self.coordinate = (self.attributes['x'], self.attributes['y'])
        elif 'x' in self.attributes and not 'y' in self.attributes:
            self.coordinate = (self.attributes['x'], 0)
        elif not 'x' in self.attributes and 'y' in self.attributes:
            self.coordinate = (0, self.attributes['y'])
        elif 'coordinate' in self.attributes:
            # TODO: add a check if coordinate is a tuple of floats
            None
        else:
            log.warn('No suitable coordinate was found for node "{}"!'
                     ' Coordinate was set to "(0,0)"!'.format(self.id))
            self.attributes['coordinate'] = (0.0, 0.0)

    @property
    def x(self):
        """Returns the x coordinate of the node."""
        return self.attributes['coordinate'][0]

    @x.setter
    def x(self, x):
        """Change the x coordinate of the node."""
        self.attributes['coordinate'] = (float(x), self.y)

    @property
    def y(self):
        """Returns the y coordinate of the node."""
        return self.attributes['coordinate'][1]

    @y.setter
    def y(self, y):
        """Change the y coordinate of the node."""
        self.attributes['coordinate'] = (self.x, float(y))

    @property
    def coordinate(self):
        """Returns the node coordinate as a tuple (x,y)."""
        return self.attributes['coordinate']

    @coordinate.setter
    def coordinate(self, coordinate):
        """Change the tuple (x,y) of the node coordinate."""
        self.attributes['coordinate'] = coordinate


class SpatialPath(Path, SpatialNetwork):
    """Base class for spatial embedded paths.

    A Path stores consecutive nodes and edges with optional data, or attributes.

    Instances of this class capture a path that can be directed, un-directed,
    un-weighted or weighted. The path class is a subclass of a
    :py:class:`SpatialNetwork`.

    Nodes are defined as :py:class:`SpatialNode` and edges are defined as
    :py:class:`SpatialEdge`

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

    Examples
    --------
    >>> p = cn.SpatialPath()
    >>> p.add_node(cn.SpatialNode('a', x=0, y=1))
    >>> p.add_node(cn.SpatialNode('b', x=2, y=3))

    See Also
    --------
    Path

    """

    def __init__(self, nodes=None, directed=True, separator='-', **attr):
        """Initialize a spatial path with direction, name and attributes.

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
            called after the assigned nodes. e.g. if the path has nodes 'a', 'b'
            and 'c', the network is named 'a-b-c'.

        separator : string, optional (default = '-')
            The separator used to separate the nodes in the node name.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to the path as key=value pairs.

        """
        # initialize the parent class of the path
        Path.__init__(self, nodes=None, directed=True, separator='-', **attr)
        # initialize the parent class of the network
        SpatialNetwork.__init__(self, directed=directed, **attr)
        # assign nodes to the path
        if isinstance(nodes, list):
            super().add_nodes_from(nodes)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
