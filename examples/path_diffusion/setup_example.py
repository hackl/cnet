#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : setup.py -- Methods to setup the example
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-01
# Time-stamp: <Mit 2018-08-01 11:13 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os


class SetupExample(object):
    """Base class to setup the example

    """

    def __init__(self, *args, **kwds):
        """Initialize the setup class."""
        self.args = args
        self.data_dir = kwds.get('data_dir', './data/')
        self.results_dir = kwds.get('results_dir', './results/')
        self.temp_dir = kwds.get('temp_dir', './temp/')
        pass

    def initialize(self):
        """Check if folders and files exist and if not create new ones"""
        # check if folders exist, if not create new folders
        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)
        if not os.path.isdir(self.results_dir):
            os.mkdir(self.results_dir)
        if not os.path.isdir(self.temp_dir):
            os.mkdir(self.temp_dir)

        # check if the tikz-network libary is available
        url = 'https://github.com/hackl/tikz-network/' + \
              'blob/master/tikz-network.sty'
        if not os.path.exists(self.results_dir + 'tikz-network.sty'):
            os.system('wget -P {} "{}"'.format(self.results_dir, url))
        if not os.path.exists(self.temp_dir + 'tikz-network.sty'):
            os.system('cp {}tikz-network.sty {}'.format(self.results_dir,
                                                        self.temp_dir))

    def clean(self, all_files=False):
        """Clean the example."""
        os.system('rm -rf {}*'.format(self.temp_dir))
        if all_files:
            os.system('rm -rf {}'.format(self.data_dir))
            os.system('rm -rf {}'.format(self.results_dir))
            os.system('rm -rf {}'.format(self.temp_dir))


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
