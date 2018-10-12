#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_pytras.py -- Test environment for the pytras converter
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-10-11
# Time-stamp: <Fre 2018-10-12 11:01 juergen>
#
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
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import pytest
import os
import sys

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet

# Path to the test data files
filepath = wk_dir + '/data/pytras/'

node_map = {
    (679909.3904012402, 4831236.176461053): 'N01',
    (684732.055713237, 4830618.74355952): 'N02',
    (679686.0096544777, 4826823.210793456): 'N03',
    (680827.0275615142, 4825897.167274702): 'N04',
    (683228.0520302313, 4825927.869586106): 'N05',
    (684854.1632824523, 4827336.048402464): 'N06',
    (686279.1061323378, 4825978.1616866905): 'N07',
    (684837.3992489246, 4825760.229250826): 'N08',
    (683261.5800972863, 4824519.690769748): 'N09',
    (683278.3441308144, 4823798.837328041): 'N10',
    (680897.8513698283, 4823647.9610262895): 'N11',
    (679322.0322181903, 4823614.432959233): 'N12',
    (679406.7464676201, 4820339.810996656): 'N13',
    (680930.749515625, 4822011.981007662): 'N14',
    (683343.7543416347, 4822054.314425663): 'N15',
    (684910.0908076407, 4824065.1517806705): 'N16',
    (684910.0908076409, 4823451.317219668): 'N17',
    (686285.9268926464, 4824107.485198671): 'N18',
    (684973.5909346413, 4822160.147970662): 'N19',
    (684952.4242256412, 4820572.644795658): 'N20',
    (683386.0877596351, 4820466.811250656): 'N21',
    (683364.9210506348, 4821271.14619266): 'N22',
    (680951.9162246246, 4821165.312647659): 'N23',
    (680973.0829336253, 4820403.311123656): 'N24'
}

node_map = {(round(u, 2), round(v, 2)): n for (u, v), n in node_map.items()}

edge_map = {
    ('N01', 'N02'): 'E01',
    ('N01', 'N03'): 'E02',
    ('N02', 'N01'): 'E03',
    ('N02', 'N06'): 'E04',
    ('N03', 'N01'): 'E05',
    ('N03', 'N04'): 'E06',
    ('N03', 'N12'): 'E07',
    ('N04', 'N03'): 'E08',
    ('N04', 'N05'): 'E09',
    ('N04', 'N11'): 'E10',
    ('N05', 'N04'): 'E11',
    ('N05', 'N06'): 'E12',
    ('N05', 'N09'): 'E13',
    ('N06', 'N02'): 'E14',
    ('N06', 'N05'): 'E15',
    ('N06', 'N08'): 'E16',
    ('N07', 'N08'): 'E17',
    ('N07', 'N18'): 'E18',
    ('N08', 'N06'): 'E19',
    ('N08', 'N07'): 'E20',
    ('N08', 'N09'): 'E21',
    ('N08', 'N16'): 'E22',
    ('N09', 'N05'): 'E23',
    ('N09', 'N08'): 'E24',
    ('N09', 'N10'): 'E25',
    ('N10', 'N09'): 'E26',
    ('N10', 'N11'): 'E27',
    ('N10', 'N15'): 'E28',
    ('N10', 'N16'): 'E29',
    ('N10', 'N17'): 'E30',
    ('N11', 'N04'): 'E31',
    ('N11', 'N10'): 'E32',
    ('N11', 'N12'): 'E33',
    ('N11', 'N14'): 'E34',
    ('N12', 'N03'): 'E35',
    ('N12', 'N11'): 'E36',
    ('N12', 'N13'): 'E37',
    ('N13', 'N12'): 'E38',
    ('N13', 'N24'): 'E39',
    ('N14', 'N11'): 'E40',
    ('N14', 'N15'): 'E41',
    ('N14', 'N23'): 'E42',
    ('N15', 'N10'): 'E43',
    ('N15', 'N14'): 'E44',
    ('N15', 'N19'): 'E45',
    ('N15', 'N22'): 'E46',
    ('N16', 'N08'): 'E47',
    ('N16', 'N10'): 'E48',
    ('N16', 'N17'): 'E49',
    ('N16', 'N18'): 'E50',
    ('N17', 'N10'): 'E51',
    ('N17', 'N16'): 'E52',
    ('N17', 'N19'): 'E53',
    ('N18', 'N07'): 'E54',
    ('N18', 'N16'): 'E55',
    ('N18', 'N20'): 'E56',
    ('N19', 'N15'): 'E57',
    ('N19', 'N17'): 'E58',
    ('N19', 'N20'): 'E59',
    ('N20', 'N18'): 'E60',
    ('N20', 'N19'): 'E61',
    ('N20', 'N21'): 'E62',
    ('N20', 'N22'): 'E63',
    ('N21', 'N20'): 'E64',
    ('N21', 'N22'): 'E65',
    ('N21', 'N24'): 'E66',
    ('N22', 'N15'): 'E67',
    ('N22', 'N20'): 'E68',
    ('N22', 'N21'): 'E69',
    ('N22', 'N23'): 'E70',
    ('N23', 'N14'): 'E71',
    ('N23', 'N22'): 'E72',
    ('N23', 'N24'): 'E73',
    ('N24', 'N13'): 'E74',
    ('N24', 'N21'): 'E75',
    ('N24', 'N23'): 'E76'}


def test_network():
    ptc = cnet.PytrasConverter()
    network = ptc.network(filepath + 'network.pkl',
                          node_map=node_map, edge_map=edge_map)
    network.summary()

    network.save('ref_network.pkl')


def test_paths():
    ptc = cnet.PytrasConverter()
    network = ptc.network(filepath + 'network.pkl',
                          node_map=node_map, edge_map=edge_map)

    paths = ptc.paths(filepath + 'paths.pkl', network=network)

    # print(len(paths))
    # s = 0
    # for p in paths:
    #     s += p['flow']

    # print(s)


test_network()
# test_paths()
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
