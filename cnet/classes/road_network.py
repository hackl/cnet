#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : road_network.py
# Creation  : 03 May 2018
# Time-stamp: <Sam 2018-07-21 11:49 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : Basic class for road networks
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

#import numpy as np

from cnet.classes.spatial_network import SpatialNode, SpatialEdge, SpatialNetwork

from cnet import config, logger
log = logger(__name__)

ALPHA = 0.15
BETA = 4.00
CAPACITY = 1000
FREE_FLOW_SPEED = 25


class RoadNetwork(SpatialNetwork):
    """ Base class for road networks.

    A Network stores nodes and edges with optional data, or attributes.

    Instances of this class capture a network that can be directed, undirected,
    unweighted or weighted. Self loops and multiple (parallel) edges are
    allowed.

    Nodes are defined as :py:class:`RoadNode` and edges are defined as
    :py:class:`RoadEdge`

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
    Network, SpatialNetwork

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
        SpatialNetwork.__init__(self, directed=directed, **attr)

        # Classes of the Node and Edge objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()

    def _node_class(self):
        """Internal function to assign different Node classes."""
        self.NodeClass = RoadNode

    def _edge_class(self):
        """Internal function to assign different Edge classes."""
        self.EdgeClass = RoadEdge


class RoadEdge(SpatialEdge):
    """Base class for a road section (edge).

    Parameters
    ----------
    e : edge id
        The parameter e is the identifier (id) for the edge. Every edge should
        have a unique id. The id is converted to a string value and is used as a
        key value for all dict which saving edge objects.

    u : node id or py:class:`RoadNode`
        This parameter defines the origin of the edge (if directed), i.e. u->v.
        A node id can be entered, in this case a new Node will be created
        (see py:class:`SpatialNode`), also an existing node can be used, here the
        attributes and properties of the node objects are used.

    v : node id or py:class:`RoadNode`
        This parameter defines the destination of the edge (if directed)
        i.e. u->v. A node id can be entered, in this case a new Node will be
        created (see py:class:`SpatialNode`), also an existing node can be used,
        here the attributes and properties of the node objects are used.

    alpha : float, optional (default = 0.15)
        Parameter for the cost calculation based on the BPR cost function.

    beta : float, optional (default = 4.0)
        Parameter for the cost calculation based on the BPR cost function.

    capacity : float, optional (default = 1000)
        Capacity of the road segment. Normally given in [veh/hour]. Per default
        the value is set to 1000, which can be changed in the config file. If no
        attribute 'capacity' is defined a warning message will be printed.

    free_flow_speed : float, optional (default = 25)
        The free flow speed is the speed a car can travel on the road segment
        without considering other traffic and driving the maximum allowed
        speed. Per default 25 [m/sec] are used (corresponds to 90
        [km/hour]). The default value can be changed in the config file. If no
        attribute 'free_flow_speed' is defined a warning message will be printed.

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

    alpha : float
        Parameter for the cost calculation based on the BPR cost function. This
        property can be called, modified and set.

    beta : float
        Parameter for the cost calculation based on the BPR cost function. This
        property can be called, modified and set.

    free_flow_time : float
        Time a vehicle needs for the road segment driving the maximum allowed
        speed. This property can only be called and not set or modified!

    free_flow_speed : float
        Maximum allowed speed on the road section. This property can be called,
        modified and set.

    capacity : float
        Capacity of the road section. This property can be called, modified and
        set.

    costs : float
        Cost for traveling on the road section. This can be time, money
        etc. This property can be called, modified and set.

    volume : float
        Traffic volume on the road section. This property can be called, modified and
        set, also this value is used for the traffic assignment model.

    Examples
    --------
    Create an empty edge with out coordinates and attributes (not recommended
    but possible).

    >>> ab = cn.RoadEdge('ab','a','b')
    [WARNING] No suitable coordinate was found for node "a"! Coordinate was set to "(0,0)"!
    [WARNING] No suitable coordinate was found for node "b"! Coordinate was set to "(0,0)"!
    [WARNING] No "capacity" attribute was found for edge ab! Default capacity value "1000" was used instead!
    [WARNING] No "free_flow_speed" attribute was found for edge ab! Default free flow speed value "25" was used instead!

    Create a proper edge

    >>> ab =  cn.SpatialEdge('ab','a','b', p1=(0,0), p2=(4,0), capacity=300, free_flow_speed=20)
    >>> ab.coordinates
    [(0,0),(4,0)]
    >>> ab.capacity
    300
    >>> ab.free_flow_speed
    20
    >>> ab.free_flow_time # length / free flow speed
    0.2

    Create edge with predefined spatial nodes

    >>> c = cn.SpatialNode('c',x=2,y=4)
    >>> d = cn.SpatialNode('d',x=3,y=1)
    >>> cd = cn.SpatialEdge('cd',c,d, capacity=500, free_flow_speed = 30)
    >>> cd.coordinates
    [(2,4),(3,1)]

    Travel costs (i.e. edge weight).


    See Also
    --------
    Edge, RoadEdge

    """

    def __init__(self, id, u, v, alpha=ALPHA, beta=BETA, **attr):
        """Initialize the road edge object.
        Parameters
        ----------
        e : edge id
            The parameter e is the identifier (id) for the edge. Every edge should
            have a unique id. The id is converted to a string value and is used as a
            key value for all dict which saving edge objects.

        u : node id or py:class:`RoadNode`
            This parameter defines the origin of the edge (if directed), i.e. u->v.
            A node id can be entered, in this case a new Node will be created
            (see py:class:`SpatialNode`), also an existing node can be used, here the
            attributes and properties of the node objects are used.

        v : node id or py:class:`RoadNode`
            This parameter defines the destination of the edge (if directed)
            i.e. u->v. A node id can be entered, in this case a new Node will be
            created (see py:class:`SpatialNode`), also an existing node can be used,
            here the attributes and properties of the node objects are used.

        alpha : float, optional (default = 0.15)
            Parameter for the cost calculation based on the BPR cost function.

        beta : float, optional (default = 4.0)
            Parameter for the cost calculation based on the BPR cost function.

        capacity : float, optional (default = 1000)
            Capacity of the road segment. Normally given in [veh/hour]. Per default
            the value is set to 1000, which can be changed in the config file. If no
            attribute 'capacity' is defined a warning message will be printed.

        free_flow_speed : float, optional (default = 25)
            The free flow speed is the speed a car can travel on the road segment
            without considering other traffic and driving the maximum allowed
            speed. Per default 25 [m/sec] are used (corresponds to 90
            [km/hour]). The default value can be changed in the config file. If no
            attribute 'free_flow_speed' is defined a warning message will be printed.

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

        alpha : float
            Parameter for the cost calculation based on the BPR cost function. This
            property can be called, modified and set.

        beta : float
            Parameter for the cost calculation based on the BPR cost function. This
            property can be called, modified and set.

        free_flow_time : float
            Time a vehicle needs for the road segment driving the maximum allowed
            speed. This property can only be called and not set or modified!

        free_flow_speed : float
            Maximum allowed speed on the road section. This property can be called,
            modified and set.

        capacity : float
            Capacity of the road section. This property can be called, modified and
            set.

        costs : float
            Cost for traveling on the road section. This can be time, money
            etc. This property can be called, modified and set.

        volume : float
            Traffic volume on the road section. This property can be called, modified and
            set, also this value is used for the traffic assignment model.

        """
        # Class of the Node object
        # TODO: Probably there is a better solution to have different Node
        # classes for different Edges sub classes
        self._node_class()

        # initialize the parent edge class
        SpatialEdge.__init__(self, id, u, v, **attr)

        # initialize the parameters
        self._alpha = alpha
        self._beta = beta
        self._volume = 0
        self._cost = float('inf')

        # check the input
        if not 'capacity' in self.attributes:
            log.warn('No "capacity" attribute was found for edge {}!'
                     ' Default capacity value "{}" was used instead!'
                     ''.format(self.id, CAPACITY))
            self.attributes['capacity'] = CAPACITY

        if not 'free_flow_speed' in self.attributes:
            log.warn('No "free_flow_speed" attribute was found for edge {}!'
                     ' Default free flow speed value "{}" was used instead!'
                     ''.format(self.id, FREE_FLOW_SPEED))
            self.attributes['free_flow_speed'] = FREE_FLOW_SPEED

    def _node_class(self):
        """Internal function to assign different Node classes to the edge"""
        self.NodeClass = RoadNode

    @property
    def alpha(self):
        """Returns the alpha parameter for the BPR function."""
        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        """Change the alpha parameter for the BPR function."""
        self._alpha = alpha

    @property
    def beta(self):
        """Returns the beta parameter for the BPR function."""
        return self._beta

    @beta.setter
    def beta(self, beta):
        """Change the alpha parameter for the BPR function."""
        self._beta = beta

    @property
    def free_flow_time(self):
        """Returns the free flow time of the edge."""
        return self.attributes.get('length', self.length())/self.free_flow_speed

    @property
    def free_flow_speed(self):
        """Returns the free flow speed of the edge."""
        return self.attributes['free_flow_speed']

    @free_flow_speed.setter
    def free_flow_speed(self, free_flow_speed):
        """Change the free flow speed of the edge."""
        self.attributes['free_flow_speed'] = free_flow_speed

    @property
    def capacity(self):
        """Returns the capacity of the edge."""
        return self.attributes['capacity']

    @capacity.setter
    def capacity(self, capacity):
        """Change the capacity of the edge."""
        self.attributes['capacity'] = capacity

    @property
    def cost(self):
        """Returns the cost of using the edge."""
        return self._cost

    @cost.setter
    def cost(self, cost):
        """Change the cost of using the edge."""
        self._cost = cost

    @property
    def volume(self):
        """Returns the traffic volume of the edge."""
        return self._volume

    @volume.setter
    def volume(self, volume):
        """Change the traffic volume of the edge."""
        self._volume = volume

    def weight(self, weight='weight', mode='BPR'):
        """Returns the weight of the edge.

        Per default the attribute with the key 'weight' is used as
        weight. Should there be no such attribute, a new one will be crated
        where the weight is based on the :py:meth:`cost_function`.

        If an other attribute should be used as weight, the option weight has to
        be changed.

        If the weight option is disabled with False or None also the weight is
        calculated based on the :py:meth:`cost_function`.

        Parameters
        ----------
        weight : str, optional (default = 'weight')
            The weight parameter defines which attribute is used as weight. Per
            default the attribute 'weight' is used. If None or False is chosen,
            the weight will be calculated based on the
            :py:meth:`cost_function`. Also any other attribute of the edge can
            be used as a weight

        mode : str, optional (default = 'BPR')
            This parameter defines the type of the used cost function. (At the
            moment only the 'BPR' cost function is implemented!)

        Returns
        -------
        weight : attribute
            Returns the attribute value associated with the keyword.

        Example
        -------
        Create new edge and get the weight.

        >>> ab =
        >>> nc.RoadEdge('ab','a','b',p1=(0,0),p2=(0,1000),capacity=500,
        >>>             free_flow_speed=25, my_weight = 10)
        >>> ab.weight()
        40
        >>> ab.weight('my_weight')
        10
        >>> ab.weight('not_defined')
        1

        """
        if weight is None:
            weight = False
        if not weight:
            self.cost = self.cost_function(self.volume, mode=mode)
            return self.cost
        elif isinstance(weight, str) and weight != 'weight':
            return self.attributes.get(weight, 1.0)
        else:
            self.cost = self.cost_function(self.volume, mode=mode)
            return self.cost

    def cost_function(self, volume, mode='BPR'):
        """Returns the cost of traveling on the road segment.

        Parameters
        ----------
        volume : float
            The traffic volume for which the costs should be calculated.

        mode : str, optional (default = 'BPR')
            Type of the cost function. Currently only the BPR model is
            implemented.

        Returns
        -------
        cost : float
            Cost to travel on the road segment.


        **BPR Model**

        The Bureau of Public Roads (BPR) developed a link (arc) congestion (or
        volume-delay, or link performance) function:

        .. math::

            S_e(v_e) = t_e (1 + \\alpha (v_e/C_e)^\\beta)

        with

        -  `t_e` = free flow travel time on link `e` per unit of time
        -  `v_e` = volume of traffic on link a per unit of time (somewhat more accurately: flow attempting to use link `e`).
        -  `C_e` = capacity of link `e` per unit of time
        -  `S_e(v_e)` is the average travel time for a vehicle on link `e`

        """
        if mode == 'BPR':
            cost = self.free_flow_time * \
                (1 + self.alpha * (volume/self.capacity) ** self.beta)
        else:
            log.error('The cost function "{}" is not implemented!'.format(mode))
            raise NotImplementedError
        return cost


class RoadNode(SpatialNode):
    """Base class for road intersections.

    Note
    ----
    See also :py:class:`SpatialNode`!

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

    >>> u = cn.RoadNode('u')
    [WARNING] No suitable coordinate was found for node "u"! Coordinate was set to "(0,0)"!

    Create a proper node

    >>> v = cn.RoadNode('u',x=1,y=2)
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
    Node, SpatialNode
    """

    def __init__(self, u, **attr):
        SpatialNode.__init__(self, u, **attr)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
