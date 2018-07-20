#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : ex_simple_markov.py -- Example for Markov transitions
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-20
# Time-stamp: <Fre 2018-07-20 14:19 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
from network2tikz import plot
from ex_networks import sioux_falls

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet


def main():
    network = sioux_falls()
    network.summary()

    layout = network.nodes['coordinate']
    visual_style = {}
    visual_style['layout'] = layout
    visual_style['node_label_as_id'] = True
    visual_style['node_color'] = 'red'
    visual_style['node_opacity'] = 1
    visual_style['edge_label'] = [e for e in network.edges]
    visual_style['edge_curved'] = 0.1
    visual_style['canvas'] = (15, 15)

    plot(network, **visual_style)


if __name__ == '__main__':
    main()


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
