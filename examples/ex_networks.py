#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : ex_networks.py -- Example networks
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-06-29
# Time-stamp: <Fre 2018-06-29 13:26 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
from network2tikz import plot

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet


def scholtes():
    """Example network used in the lecture Complex Networks by Ingo Scholtes.

    Name:		Scholtes
    Type:		RoadNetwork
    Directed:		False
    Number of nodes:	7
    Number of edges:	9

    """
    net = cnet.RoadNetwork(name='Scholtes', directed=False)

    net.add_node('a', x=0, y=0)
    net.add_node('b', x=4000, y=3000)
    net.add_node('c', x=8000, y=0)
    net.add_node('d', x=4000, y=7000)
    net.add_node('e', x=8000, y=10000)
    net.add_node('f', x=4000, y=10000)
    net.add_node('g', x=0, y=10000)

    net.add_edge('ab', 'a', 'b',
                 length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('ac', 'a', 'c',
                 length=8000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('bc', 'b', 'c',
                 length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('bd', 'b', 'd',
                 length=4000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('de', 'd', 'e',
                 length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('df', 'd', 'f',
                 length=3000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('dg', 'd', 'g',
                 length=5000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('ef', 'e', 'f',
                 length=4000.0, capacity=3600, free_flow_speed=27.78)
    net.add_edge('fg', 'f', 'g',
                 length=4000.0, capacity=3600, free_flow_speed=27.78)
    return net


def scholtes_second_order():
    """Second order representation of the Scholtes network.

    Name:		Scholtes 2nd order
    Type:		SpatialNetwork
    Directed:		False
    Number of nodes:	9
    Number of edges:	13

    """

    net = cnet.SpatialNetwork(name='Scholtes 2nd order', directed=False)

    # nodes
    net.add_node('ac', x=40, y=0)
    net.add_node('ab', x=20, y=15)
    net.add_node('bc', x=60, y=15)
    net.add_node('bd', x=40, y=30)
    net.add_node('de', x=80, y=60)
    net.add_node('df', x=40, y=60)
    net.add_node('dg', x=0, y=60)
    net.add_node('ef', x=60, y=75)
    net.add_node('fg', x=20, y=75)

    # edges
    net.add_edge('a-c-b', 'ac', 'bc')
    net.add_edge('c-a-b', 'ac', 'ab')
    net.add_edge('a-b-c', 'ab', 'bc')
    net.add_edge('a-b-d', 'ab', 'bd')
    net.add_edge('c-b-d', 'bc', 'bd')
    net.add_edge('b-d-e', 'bd', 'de')
    net.add_edge('b-d-f', 'bd', 'df')
    net.add_edge('b-d-g', 'bd', 'dg')
    net.add_edge('d-e-f', 'de', 'ef')
    net.add_edge('d-f-e', 'df', 'ef')
    net.add_edge('d-f-g', 'df', 'fg')
    net.add_edge('d-g-f', 'dg', 'fg')
    net.add_edge('e-f-g', 'ef', 'fg')
    return net


def sioux_falls():
    """Sioux Falls Network.

    Source https://github.com/bstabler/TransportationNetworks/tree/master/SiouxFalls

    WARNING: The Sioux-Falls network is not considered as a realistic
    one. However, this network was used in many publications. It is good for
    code debugging.

    Name:		Sioux Falls
    Type:		RoadNetwork
    Directed:		True
    Number of nodes:	24
    Number of edges:	76

    """
    net = cnet.RoadNetwork(name='Sioux Falls', directed=True)

    # nodes
    net.add_node('N01', x=679909.3904012402, y=4831236.176461053)
    net.add_node('N02', x=684732.055713237, y=4830618.74355952)
    net.add_node('N03', x=679686.0096544777, y=4826823.210793456)
    net.add_node('N04', x=680827.0275615142, y=4825897.167274702)
    net.add_node('N05', x=683228.0520302313, y=4825927.869586106)
    net.add_node('N06', x=684854.1632824523, y=4827336.048402464)
    net.add_node('N07', x=686279.1061323378, y=4825978.1616866905)
    net.add_node('N08', x=684837.3992489246, y=4825760.229250826)
    net.add_node('N09', x=683261.5800972863, y=4824519.690769748)
    net.add_node('N10', x=683278.3441308144, y=4823798.837328041)
    net.add_node('N11', x=680897.8513698283, y=4823647.9610262895)
    net.add_node('N12', x=679322.0322181903, y=4823614.432959233)
    net.add_node('N13', x=679406.7464676201, y=4820339.810996656)
    net.add_node('N14', x=680930.749515625, y=4822011.981007662)
    net.add_node('N15', x=683343.7543416347, y=4822054.314425663)
    net.add_node('N16', x=684910.0908076407, y=4824065.1517806705)
    net.add_node('N17', x=684910.0908076409, y=4823451.317219668)
    net.add_node('N18', x=686285.9268926464, y=4824107.485198671)
    net.add_node('N19', x=684973.5909346413, y=4822160.147970662)
    net.add_node('N20', x=684952.4242256412, y=4820572.644795658)
    net.add_node('N21', x=683386.0877596351, y=4820466.811250656)
    net.add_node('N22', x=683364.9210506348, y=4821271.14619266)
    net.add_node('N23', x=680951.9162246246, y=4821165.312647659)
    net.add_node('N24', x=680973.0829336253, y=4820403.311123656)

    # edges
    net.add_edge('E01', 'N01', 'N02', length=4862.029, capacity=5583.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E02', 'N01', 'N03', length=4418.616, capacity=5208.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car,bus,pt')
    net.add_edge('E03', 'N02', 'N01', length=4862.029, capacity=5541.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E04', 'N02', 'N06', length=3284.965, capacity=1604.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E05', 'N03', 'N01', length=4418.616, capacity=5283.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car,bus,pt')
    net.add_edge('E06', 'N03', 'N04', length=1469.516, capacity=1776.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E07', 'N03', 'N12', length=3229.355, capacity=5142.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E08', 'N04', 'N03', length=1469.516, capacity=1710.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E09', 'N04', 'N05', length=2401.221, capacity=1948.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E10', 'N04', 'N11', length=2250.321, capacity=1964.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E11', 'N05', 'N04', length=2401.221, capacity=1670.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E12', 'N05', 'N06', length=2151.094, capacity=1974.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E13', 'N05', 'N09', length=1408.578, capacity=1792.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E14', 'N06', 'N02', length=3284.965, capacity=1662.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E15', 'N06', 'N05', length=2151.094, capacity=1670.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E16', 'N06', 'N08', length=1575.908, capacity=1602.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E17', 'N07', 'N08', length=1458.085, capacity=1678.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E18', 'N07', 'N18', length=1870.689, capacity=5355.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E19', 'N08', 'N06', length=1575.908, capacity=1810.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E20', 'N08', 'N07', length=1458.085, capacity=1828.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E21', 'N08', 'N09', length=2005.528, capacity=1806.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E22', 'N08', 'N16', length=1696.635, capacity=1728.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E23', 'N09', 'N05', length=1408.578, capacity=1680.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E24', 'N09', 'N08', length=2005.528, capacity=1878.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E25', 'N09', 'N10', length=721.048, capacity=1950.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E26', 'N10', 'N09', length=721.048, capacity=1704.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E27', 'N10', 'N11', length=2385.269, capacity=1610.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E28', 'N10', 'N15', length=1745.749, capacity=1912.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E29', 'N10', 'N16', length=1653.336, capacity=1668.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E30', 'N10', 'N17', length=1668.343, capacity=1878.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E31', 'N11', 'N04', length=2250.321, capacity=1940.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E32', 'N11', 'N10', length=2385.269, capacity=1866.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E33', 'N11', 'N12', length=1576.176, capacity=1814.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E34', 'N11', 'N14', length=1636.311, capacity=1772.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E35', 'N12', 'N03', length=3229.355, capacity=5196.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E36', 'N12', 'N11', length=1576.176, capacity=1782.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E37', 'N12', 'N13', length=3275.718, capacity=5655.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E38', 'N13', 'N12', length=3275.718, capacity=5502.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E39', 'N13', 'N24', length=1567.623, capacity=1742.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E40', 'N14', 'N11', length=1636.311, capacity=1950.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E41', 'N14', 'N15', length=2413.376, capacity=1888.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E42', 'N14', 'N23', length=846.933, capacity=1666.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E43', 'N15', 'N10', length=1745.749, capacity=1632.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E44', 'N15', 'N14', length=2413.376, capacity=1986.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E45', 'N15', 'N19', length=1633.269, capacity=1688.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E46', 'N15', 'N22', length=783.454, capacity=1914.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E47', 'N16', 'N08', length=1696.635, capacity=1758.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E48', 'N16', 'N10', length=1653.336, capacity=1824.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E49', 'N16', 'N17', length=613.835, capacity=1828.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E50', 'N16', 'N18', length=1376.487, capacity=1618.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E51', 'N17', 'N10', length=1668.343, capacity=1626.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E52', 'N17', 'N16', length=613.835, capacity=1834.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E53', 'N17', 'N19', length=1292.73, capacity=1662.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E54', 'N18', 'N07', length=1870.689, capacity=5436.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E55', 'N18', 'N16', length=1376.487, capacity=1776.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E56', 'N18', 'N20', length=3778.006, capacity=5682.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E57', 'N19', 'N15', length=1633.269, capacity=1926.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E58', 'N19', 'N17', length=1292.73, capacity=1808.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E59', 'N19', 'N20', length=1587.644, capacity=1898.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E60', 'N20', 'N18', length=3778.006, capacity=5178.0,
                 free_flow_speed=25.0, lanes=3, oneway=1, modes='car')
    net.add_edge('E61', 'N20', 'N19', length=1587.644, capacity=1924.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E62', 'N20', 'N21', length=1569.908, capacity=1668.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E63', 'N20', 'N22', length=1734.379, capacity=1900.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E64', 'N21', 'N20', length=1569.908, capacity=1984.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E65', 'N21', 'N22', length=804.613, capacity=1774.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E66', 'N21', 'N24', length=2413.84, capacity=1672.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E67', 'N22', 'N15', length=783.454, capacity=1610.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E68', 'N22', 'N20', length=1734.379, capacity=1768.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E69', 'N22', 'N21', length=804.613, capacity=1934.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E70', 'N22', 'N23', length=2415.325, capacity=1624.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E71', 'N23', 'N14', length=846.933, capacity=1866.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E72', 'N23', 'N22', length=2415.325, capacity=1752.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E73', 'N23', 'N24', length=762.295, capacity=1742.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E74', 'N24', 'N13', length=1567.623, capacity=1652.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')
    net.add_edge('E75', 'N24', 'N21', length=2413.84, capacity=1724.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car')
    net.add_edge('E76', 'N24', 'N23', length=762.295, capacity=1868.0,
                 free_flow_speed=13.9, lanes=2, oneway=1, modes='car,bus,pt')

    return net

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
