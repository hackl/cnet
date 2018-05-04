#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : config.py 
# Creation  : 30 Apr 2018
# Time-stamp: <Fre 2018-05-04 09:27 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : Module to read and parse configuration files
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

import os
import sys
import collections
import configparser

class DotDict(collections.OrderedDict):
    """
    A string-valued dictionary that can be accessed with the "." notation
    """
    def __getattr__(self, key):
        try:
            if self[key] == 'True':
                return True
            elif self[key] == 'False':
                return False
            elif self.is_number(self[key]):
                if self.is_int(self[key]):
                    return int(self[key])
                else:
                    return float(self[key])
            else:
                return self[key]
        except KeyError:
            raise AttributeError(key)

    def is_number(self, s):
        """Check if input is a float number."""
        try:
            float(s)
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    def is_int(self,x):
        """Check if input is an integer number."""
        try:
            a = float(x)
            b = int(a)
        except ValueError:
            return False
        else:
            return a == b

# initialize config dictionary
config = DotDict()

# add the default config file
d = os.path.dirname
base = os.path.join(d(d(__file__)), 'config.cfg')

config.paths = [base,'config.cfg']

def read(*paths, **validators):
    """
    Load the configuration, make each section available in a separate dict.

    The configuration location is where the script is executed:
       - cnet.cfg

    If this file is missing, the fallback is the source code:
       - cnet/config.cfg

    Please note: settings in the site configuration file are overridden
    by settings with the same key names in the config.cfg.
    """
    paths = config.paths + list(paths)
    parser = configparser.SafeConfigParser()
    found = parser.read(os.path.normpath(os.path.expanduser(p)) for p in paths)
    if not found:
        raise IOError('No configuration file found in %s' % str(paths))
    config.found = found
    config.clear()
    for section in parser.sections():
        config[section] = sec = DotDict(parser.items(section))
        for k, v in sec.items():
            sec[k] = validators.get(k, lambda x: x)(v)

config.read = read

config.read()

# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
