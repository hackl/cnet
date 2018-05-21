#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : logger.py 
# Creation  : 30 Apr 2018
# Time-stamp: <Fre 2018-05-04 09:27 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : Module to log output information
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
import logging
from cnet import config

# check if logging is enabled in the config file
if config.logging.enabled:
    # check if the path to the logging file exists
    if not os.path.exists(os.path.dirname(config.logging.logfile)):
        # if not create new path
        os.makedirs(os.path.dirname(config.logging.logfile))

    # initialize basic config for the written logger
    logging.basicConfig(level=logging._nameToLevel[config.logging.level],
                        format='%(asctime)s - %(name)12s:%(lineno)4d - %(levelname)8s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=config.logging.logfile,
                        filemode='w')
else:
    # if logging is not enabled
    logging.basicConfig()

# check if logger should write to the terminal
if config.logging.verbose:

    # create stream handler
    console = logging.StreamHandler()

    # set level according to the config file
    console.setLevel(logging._nameToLevel[config.logging.level])

    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(asctime)s: %(levelname)-5s] %(message)s',
                              datefmt='%m-%d %H:%M:%S')

    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

def logger(name,level=None):
    """A function to generate logger for the modules."""

    # initialize new logger
    logger = logging.getLogger(name)

    # if no level is defined the config level will be used
    if level is None:
        logger.setLevel(logging._nameToLevel[config.logging.level])
    else:
        logger.setLevel(logging._nameToLevel[level])
    return logger




# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:  
