#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py • cnet -- Basic classes for HONs
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-25
# Time-stamp: <Mit 2018-07-25 17:11 juergen>
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
from cnet.classes.path_network import PathNode, PathEdge, PathNetwork
from cnet.utils.exceptions import CnetError, CnetNotImplemented
from cnet import config, logger
log = logger(__name__)


class HigherOrderNetwork(Network, Node):
    """Documentation for HigherOrderNetwork

    """

    def __init__(self, u, directed=True, **attr):
        Node.__init__(self, u, **attr)
        Network.__init__(self, name=u, directed=directed, **attr)


class HigherOrderPathNetwork(PathNetwork, PathNode):
    """Documentation for HigherOrderNetwork

    """

    def __init__(self, u, path=None, directed=True, **attr):
        PathNode.__init__(self, u, path=path, **attr)
        PathNetwork.__init__(self, name=u, directed=directed, **attr)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
