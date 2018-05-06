#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : helpers.py 
# Creation  : 24 Jan 2018
# Time-stamp: <Son 2018-05-06 11:06 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : Some little helpers to make life easier
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

from math import radians, cos, sin, asin, sqrt

from cnet import config,logger
log = logger(__name__)

def haversine(pos_1,pos_2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    lat1, lon1  = pos_1
    lat2, lon2 = pos_2
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km * 1000





def remove_duplicates(sequence):
    """ Removes duplicates from list, whilst preserving order

    Parameters
    ----------
    sequence: list

    Returns
    -------
    sequence : list
        A python list, where duplicate entries are removed

    Examples
    --------
    >>> removes_duplicates([2,3,5,5,1,1,7,8,8,2,2])
    [2,3,5,1,7,8,2]
    """
    seen = set()
    seen_add = seen.add
    return [x for x in sequence if not (x in seen or seen_add(x))]

def sort_large_file(filename):
    """ Sort large file with linux sort command (very fast) """
    # (head -n 1 paths.csv && tail -n +2 paths.csv | sort -t $',' -k 1) > paths_sorted.csv
    os.system("(head -n 1 "+filename+" && tail -n +2 "+filename+" | sort -t $',' -k 1) > "+filename)

def is_last_row(itr):
    old = next(itr)
    for new in itr:
        yield False, old
        old = new
    yield True, old



# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# End: 

 
